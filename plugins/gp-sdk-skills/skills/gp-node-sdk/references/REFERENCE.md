# GP Node.js SDK — Code Reference

Quick-copy TypeScript snippets for `globalpayments/node-sdk` (npm package `globalpayments-api`). All class names, method chains, and enum values are verified against the SDK source at https://github.com/globalpayments/node-sdk (`master`) and its integration test suite at `test/Integration/Gateways/`.

Every `.execute()` call returns a `Promise` (`src/Builders/BaseBuilder.ts`). For brevity, most snippets below omit the enclosing `async` function and show a bare top-level `await` — place each one inside your own `async` function (with `try`/`catch` where it matters) before running it; only a few snippets, chosen to show the full shape once, include that wrapper explicitly. `ServicesContainer.configureService(config)` itself is synchronous and is never awaited.

---

## Installation

```bash
npm install globalpayments-api
```

```bash
yarn add globalpayments-api
```

Minimum Node version: **>=16.20.2** (`engines.node` in `package.json`). Package name, version, and entry points, from `package.json` at the repo root:

```json
{
  "name": "globalpayments-api",
  "version": "3.11.1",
  "main": "./lib/src/index.js",
  "typings": "./lib/src/index"
}
```

The package ships its own compiled `.d.ts` typings (`typings` field) — no separate `@types/globalpayments-api` install is needed.

### Import forms

```typescript
// ES module / TypeScript (used throughout the rest of this document)
import { GpApiConfig, ServicesContainer, CreditCardData } from "globalpayments-api";
```

```javascript
// CommonJS
const { GpApiConfig, ServicesContainer, CreditCardData } = require("globalpayments-api");
```

Everything is exported from the single package root — `src/index.ts` re-exports `./Entities`, `./PaymentMethods`, `./Services`, `./ServiceConfigs`, `./Builders`, `./Gateways`, `./Mapping`, `./Terminals`, and `./Utils` via `export *`. There are no deep import paths to learn.

---

## Gateway Configuration

### GP API

> Portal: https://github.com/globalpayments/node-sdk#readme (the portal has no Node.js SDK page)

```typescript
import { GpApiConfig, ServicesContainer, Environment, Channel, ConfigurationError } from "globalpayments-api";

const config = new GpApiConfig();
config.appId = "YOUR_APP_ID";
config.appKey = "YOUR_APP_KEY";
config.environment = Environment.Test;       // Environment.Production for live
config.country = "US";
config.channel = Channel.CardNotPresent;     // Channel.CardPresent for in-person

try {
  ServicesContainer.configureService(config);
} catch (e) {
  if (e instanceof ConfigurationError) {
    // bad/incomplete config — see Error Handling below
  }
}
```

Optional GP API fields:
```typescript
import { IntervalToExpire, DataResidency } from "globalpayments-api";

config.merchantId = "MER_xxx";
config.merchantContactUrl = "https://yoursite.com/about";                 // required for 3DS
config.methodNotificationUrl = "https://yoursite.com/3ds/method";
config.challengeNotificationUrl = "https://yoursite.com/3ds/challenge";
config.secondsToExpire = 3600;
config.intervalToExpire = IntervalToExpire.WEEK;
config.dataResidency = DataResidency.EU;     // EU data residency
config.permissions = ["PMT_POST_Create_Single"]; // restrict an access token's scope
```

`GpApiConfig.validate()` (`src/ServiceConfigs/Gateways/GpApiConfig.ts`) throws `ConfigurationError` unless at least one of these is true: `accessTokenInfo` is set, **or** both `appId` and `appKey` are set, **or** Portico credentials are present (`secretApiKey`, or all five of `siteId`/`licenseId`/`porticoDeviceId`/`porticoUsername`/`porticoPassword`).

> **Portico fields are flat, not nested.** **Node's `GpApiConfig` carries the Portico credentials directly as flat fields**: `secretApiKey`, `siteId`, `licenseId`, `porticoDeviceId`, `porticoUsername`, `porticoPassword` (confirmed in `src/ServiceConfigs/Gateways/GpApiConfig.ts`). There is a `PorticoTokenConfig` entity class in this SDK too (`src/Entities/GpApi/...`, referenced internally by `GpApiConnector.ts`), but `GpApiConfig` does not expose a field of that type — set the flat fields instead:

```typescript
// GP API authenticating against Portico token services — flat fields, not a nested object
config.secretApiKey = "skapi_cert_YOUR_KEY";
// — or —
config.siteId = "12345";
config.licenseId = "67890";
config.porticoDeviceId = "11223";
config.porticoUsername = "USERNAME";
config.porticoPassword = "PASSWORD";
```

### GP Ecom (Realex)

```typescript
import { GpEcomConfig, ServicesContainer, Environment, ConfigurationError } from "globalpayments-api";

const config = new GpEcomConfig();
config.merchantId = "YOUR_MERCHANT_ID";
config.accountId = "internet";
config.sharedSecret = "YOUR_SECRET";
config.environment = Environment.Test;

try {
  ServicesContainer.configureService(config);
} catch (e) {
  if (e instanceof ConfigurationError) {
    // bad/incomplete config
  }
}
```

`GpEcomConfig.validate()` (`src/ServiceConfigs/Gateways/GpEcomConfig.ts`) throws `ConfigurationError` if `merchantId` or `sharedSecret` is missing.

> Note: `GpEcomConfig.channel` is typed as a plain `string`, not the `Channel` enum used by `GpApiConfig.channel` — confirmed by the field declaration `public channel: string;` in source. Don't assign a `Channel` enum member to it.

### Portico (Heartland) — secret API key

```typescript
import { PorticoConfig, ServicesContainer, Environment, ConfigurationError } from "globalpayments-api";

const config = new PorticoConfig();
config.secretApiKey = "skapi_cert_YOUR_KEY";
config.environment = Environment.Test;

try {
  ServicesContainer.configureService(config);
} catch (e) {
  if (e instanceof ConfigurationError) {
    // bad/incomplete config
  }
}
```

### Portico — 5-point legacy credentials

```typescript
const config = new PorticoConfig();
config.siteId = "12345";
config.licenseId = "67890";
config.deviceId = "11223";
config.username = "USERNAME";
config.password = "PASSWORD";
config.environment = Environment.Test;

ServicesContainer.configureService(config);
```

`PorticoConfig.validate()` (`src/ServiceConfigs/Gateways/PorticoConfig.ts`) throws `ConfigurationError` if both `secretApiKey` and any of the 5-point fields are set (mutually exclusive), and throws if only some — not all five — of `siteId`/`licenseId`/`deviceId`/`username`/`password` are set.

---

## Payment Methods

All payment-method fields are plain public TypeScript class properties — assign directly, there are no setter methods.

### Credit Card (manual entry)

```typescript
import { CreditCardData } from "globalpayments-api";

const card = new CreditCardData();
card.number = "CARD_NUMBER"; // see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
card.expMonth = "12";
card.expYear = "2026";
card.cvn = "123";
card.cardHolderName = "Jane Smith";
```

`CreditCardData.expMonth`/`expYear` are typed `string`, not `number` (`src/PaymentMethods/CreditCardData.ts`).

### Credit Card (token)

```typescript
const card = new CreditCardData();
card.token = "PMT_TOKEN";
```

### Track Data (card present)

```typescript
import { CreditTrackData, EntryMethod } from "globalpayments-api";

const track = new CreditTrackData();
track.value = "TRACK_DATA_STRING"; // see sandbox track data: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
track.entryMethod = EntryMethod.Swipe;
```

Confirmed `EntryMethod` values (`src/Entities/Enums.ts`): `Swipe`, `Proximity`, `Manual`.

### ECheck / ACH

```typescript
import { ECheck, AccountType, CheckType, SecCode } from "globalpayments-api";

const check = new ECheck();
check.accountNumber = "ACCOUNT_NUMBER";
check.routingNumber = "ROUTING_NUMBER";
check.accountType = AccountType.Checking;
check.checkType = CheckType.Personal;
check.secCode = SecCode.PPD;
check.checkHolderName = "Jane Smith";
```

> **Class name casing.** The class is `ECheck` (capital `E`) — `src/PaymentMethods/ECheck.ts`, `export class ECheck extends PaymentMethod`. Do not use the lowercase `eCheck` spelling. `ECheck` only exposes `.charge(amount?)` and `.refund(amount?)` — it does not have `.authorize()`, `.reverse()`, or `.verify()` (confirmed: the whole class body is 68 lines and defines exactly those two methods plus its fields).

> **`SecCode` casing.** Node's `SecCode` is a real TypeScript `enum` with mostly-uppercase members and one PascalCase outlier confirmed in source (`src/Entities/Enums.ts`): `PPD = "PPD"`, `CCD = "CCD"`, `POP = "POP"`, `WEB = "WEB"`, `TEL = "TEL"`, `EBronze = "EBronze"` — verify exact casing per member against source before emitting, especially `EBronze`, which breaks the all-caps pattern of its siblings.

### Gift Card

```typescript
import { GiftCard } from "globalpayments-api";

const gift = new GiftCard();
gift.number = "GIFT_CARD_NUMBER";
```

`GiftCard.number`/`.token`/`.alias`/`.trackData` are TypeScript accessor properties (get/set pairs backed by internal `value`/`valueType` fields) — they behave like plain fields from the caller's side; assign them directly (`src/PaymentMethods/GiftCard.ts`).

---

## Core Transactions
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/online/api-guide.md

### Charge (sale — auth + capture)

```typescript
import { CreditCardData, Transaction, GatewayError } from "globalpayments-api";

async function chargeCard(card: CreditCardData): Promise<Transaction> {
  try {
    const response = await card
      .charge("29.99")
      .withCurrency("USD")
      .withDescription("Order #1234")
      .execute();

    const transactionId = response.transactionId;
    const status = response.responseMessage;       // "CAPTURED" or "SUCCESS"
    const authCode = response.authorizationCode;

    return response;
  } catch (e) {
    if (e instanceof GatewayError) {
      // see Error Handling below
    }
    throw e;
  }
}
```

### Authorize (hold, capture later)
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/capture-guide.md

```typescript
const response = await card
  .authorize("29.99")
  .withCurrency("USD")
  .execute();

const transactionId = response.transactionId;
```

### Capture

```typescript
import { Transaction } from "globalpayments-api";

const transaction = Transaction.fromId(transactionId);
const response = await transaction.capture("29.99").execute();
```

### Void / Reverse
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/reverse-guide.md

**Gateway differences.** `Transaction.void()` (`src/Entities/Transaction.ts`) is a real, callable method — `void` is not a reserved identifier when used as a property/method name in TypeScript — but whether it *works* depends on the gateway:

- **GP API** — use `.reverse()`. `GpApiManagementRequestBuilder` (`src/Builders/RequestBuilder/GpApi/GpApiManagementRequestBuilder.ts`) switches on `builder.transactionType` and has a `case TransactionType.Reversal:` but **no `case TransactionType.Void:`** anywhere in the file (confirmed by grepping every `case TransactionType.` in the switch) — calling `.void()` against a GP API config produces an unbuildable request.
- **Portico / GP Ecom** — use `.void()`. Both `PorticoConnector.mapTransactionType()` (`case TransactionType.Reversal:` line 1141, `case TransactionType.Void:` line 1164) and `GpEcomConnector` (`case TransactionType.Void:` / `case TransactionType.Reversal:` handled together, lines 671-672) map it explicitly. Confirmed working in the SDK's own Portico test suite: `test/Integration/Gateways/PorticoConnector/Credit.test.ts` calls `Transaction.fromId(auth.transactionId).void()`.

```typescript
import { Transaction } from "globalpayments-api";

// GP API — reverse a transaction
const transaction = Transaction.fromId(transactionId);
const response = await transaction.reverse("29.99").execute();

// Portico / GP Ecom — void a transaction
const transaction2 = Transaction.fromId(transactionId);
const response2 = await transaction2.void().execute();
```

### Refund
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/refund-guide.md

```typescript
import { Transaction } from "globalpayments-api";

// Refund a settled transaction by ID
const transaction = Transaction.fromId(transactionId);
const response = await transaction.refund("10.00").withCurrency("USD").execute();

// Standalone credit (refund directly to a payment method)
const response2 = await card.refund("10.00").withCurrency("USD").execute();
```

### Verify
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/verify-guide.md

```typescript
const response = await card.verify().withCurrency("USD").execute();
```

---

## Address Verification (AVS)

```typescript
import { Address } from "globalpayments-api";

const address = new Address();
address.streetAddress1 = "1 Main Street";
address.city = "Atlanta";
address.state = "GA";           // proxies to `province` internally
address.postalCode = "30301";
address.country = "US";

const response = await card
  .charge("100.00")
  .withCurrency("USD")
  .withAddress(address)
  .execute();

const avsResult = response.avsResponseCode;
const cvnResult = response.cvnResponseCode;
```

`Address.state` is a getter/setter pair that reads and writes the underlying `province` field (`src/Entities/Address.ts`) — either `address.state = "GA"` or `address.province = "GA"` works; they're the same storage. `avsResponseCode`/`cvnResponseCode` on `Transaction` are plain `string` fields — there is no dedicated AVS/CVN result enum in this SDK; the gateway returns raw codes.

---

## Hosted Fields (PCI-Compliant Card Collection)
> GlobalPayments.js hosted fields — raw card numbers never flow through the merchant server.

**PCI guidance:** For server-to-server integrations (like batch jobs or backend test suites) passing `CreditCardData` with a raw card number is acceptable. For any web-facing integration, use hosted fields so card data is collected inside GP-hosted iframes and your server only ever sees a `PMT_` payment reference token.

### Step 1 — Generate a restricted access token (Node, server-side)

```typescript
import { GpApiConfig, Environment, Channel, GpApiService, GatewayError, AccessTokenInfo } from "globalpayments-api";

async function getHostedFieldsToken(): Promise<string> {
  const config = new GpApiConfig();
  config.appId = "YOUR_APP_ID";
  config.appKey = "YOUR_APP_KEY";
  config.environment = Environment.Test;
  config.channel = Channel.CardNotPresent;
  config.country = "US";
  config.permissions = ["PMT_POST_Create_Single"]; // restrict to single-use tokenisation only

  try {
    const tokenInfo: AccessTokenInfo = await GpApiService.generateTransactionKey(config);
    return tokenInfo.accessToken; // short-lived token — safe to expose to the browser
  } catch (e) {
    if (e instanceof GatewayError) {
      // token generation failed
    }
    throw e;
  }
}
```

Return the access token as JSON to the browser. **Never expose your `appKey` or a full-permission token to client-side code.**

### Step 2 — Mount hosted card iframes (JavaScript, browser-side)

```html
<!-- Load GlobalPayments.js -->
<!-- Read latest version of JS library from this file in its source repository:
     https://github.com/globalpayments/globalpayments-js/blob/master/packages/globalpayments-js/src/lib/version.ts -->
<script src="https://js.globalpay.com/5.1.0/globalpayments.js"></script>

<!-- Single container div. GlobalPayments.js renders card number, expiry,
     CVV, and a submit button as iframes inside here.
     Do NOT add separate input fields or a submit button. -->
<div id="credit-card-form"></div>

<script>
GlobalPayments.configure({
    accessToken: ACCESS_TOKEN_FROM_YOUR_BACKEND,
    env: 'sandbox',          // 'production' for live
    apiVersion: '2021-03-22',
});

// Single container — GlobalPayments.js renders card number, expiry, CVV,
// and a submit button as iframes inside this div. No separate button needed.
// style: 'gp-default' includes the submit button automatically.
const cardForm = GlobalPayments.creditCard.form('#credit-card-form', {
    style: 'gp-default',
    amount: '19.99',
});

// token-success fires after the user clicks the built-in submit button
// and GP tokenises the card. No cardForm.submit() call needed.
cardForm.on('token-success', async (resp) => {
    // resp.paymentReference is a PMT_ token — no raw card data here
    await fetch('/api/charge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paymentToken: resp.paymentReference }),
    });
});

cardForm.on('token-error', (resp) => { console.error(resp); });
</script>
```

### Step 3 — Charge the token (Node, server-side)

```typescript
import { CreditCardData } from "globalpayments-api";

async function chargeToken(paymentToken: string) {
  const card = new CreditCardData();
  card.token = paymentToken; // PMT_ reference from GlobalPayments.js

  const response = await card.charge("19.99").withCurrency("USD").execute();

  const transactionId = response.transactionId;  // TRN_...
  const status = response.responseMessage;         // CAPTURED
  return response;
}
```

---

## Tokenization
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/tokenization/card-storage-guide.md

### Store a card

```typescript
import { PaymentMethodUsageMode } from "globalpayments-api";

// Verifies the card and requests a multi-use token in one call
const response = await card
  .tokenize(true, PaymentMethodUsageMode.MULTIPLE) // defaults match: verifyCard=true, usageMode=MULTIPLE
  .withCurrency("USD")
  .execute();

const token = response.token; // starts with "PMT_"
```

`Credit.tokenize(verifyCard = true, usageMode = PaymentMethodUsageMode.MULTIPLE)` (`src/PaymentMethods/Credit.ts`) builds an `AuthorizationBuilder` with `withRequestMultiUseToken(true)` and `withPaymentMethodUsageMode(usageMode)`; when `verifyCard` is truthy it runs a `Verify` transaction, otherwise a `Tokenize` transaction — either way it returns the full `Transaction` response — not a bare token string. Read the token off `response.token`.

### Charge a stored token

```typescript
const tokenCard = new CreditCardData();
tokenCard.token = token;

const response = await tokenCard.charge("50.00").withCurrency("USD").execute();
```

### Update token expiry

```typescript
const tokenCard = new CreditCardData();
tokenCard.token = existingToken;
tokenCard.expMonth = "12";
tokenCard.expYear = "2027";

const updated = await tokenCard.updateTokenExpiry(); // Promise<boolean>, throws BuilderError if token is null
```

### Delete / detokenize

```typescript
const deleted = await tokenCard.deleteToken();       // Promise<boolean>
const original = await tokenCard.detokenize();        // Promise<Transaction> — reveals the underlying PAN details
```

`updateTokenExpiry()`, `deleteToken()`, and `detokenize()` are all `async` methods on `Credit` (`src/PaymentMethods/Credit.ts`) that throw `BuilderError` synchronously if `.token` is not set before you can even reach the `await`.

---

## Recurring Billing
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/recurring/recurring-payments-guide.md

```typescript
import { Customer, RecurringPaymentMethod } from "globalpayments-api";

// Create customer
const customer = new Customer();
customer.id = "cust-001";
customer.firstName = "Jane";
customer.lastName = "Smith";
customer.email = "jane@example.com";
await customer.create();

// Add and persist a payment method for the customer
const rpm = customer.addPaymentMethod("pm-001", card);
await rpm.create();

// Charge the stored method
const storedMethod = new RecurringPaymentMethod("cust-001", "pm-001");
const response = await storedMethod.charge("19.99").withCurrency("USD").execute();
```

`Customer.addPaymentMethod(paymentId, paymentMethod)` (`src/Entities/Customer.ts`) only builds a local `RecurringPaymentMethod` object — it does **not** call the gateway. Call `.create()` on the returned `RecurringPaymentMethod` (inherited from `RecurringEntity<T>.create(configName = "default")`, `src/Entities/RecurringEntity.ts`) to actually persist it. `addPaymentMethod()` alone does not reach the gateway — a common source of silently-unpersisted payment methods. `RecurringEntity.create()` delegates to `RecurringService.create(entity, configName)`, which returns a `Promise` — always `await` it.

---

## 3D Secure 2
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/risk-management/3D-secure/browser-authentication-guide.md
> Reference implementation: https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/nodejs
> Verified test chains: `test/Integration/Gateways/GpApiConnector/3DS2.test.ts`

**Regional default:** 3DS is **required by default in all regions except the United States**. Always implement the full 3DS2 flow for non-US merchants. US merchants may opt in.

### Config Requirements for 3DS

Three additional fields are required on `GpApiConfig` for any 3DS flow:

```typescript
import { GpApiConfig, ServicesContainer, Environment, Channel } from "globalpayments-api";

const config = new GpApiConfig();
config.appId = "YOUR_APP_ID";
config.appKey = "YOUR_APP_KEY";
config.environment = Environment.Test;
config.country = "GB";                 // non-US → 3DS is required
config.channel = Channel.CardNotPresent;

// Required for 3DS — HTTPS URLs in production
config.merchantContactUrl = "https://yoursite.com/about";                       // shown in ACS UI
config.methodNotificationUrl = "https://yoursite.com/3ds-method-notification";
config.challengeNotificationUrl = "https://yoursite.com/3ds-challenge-notification";

ServicesContainer.configureService(config, "my-config");
```

### Imports

```typescript
import {
  Secure3dService,
  ThreeDSecure,
  Address,
  BrowserData,
  AddressType,
  AuthenticationSource,
  ChallengeWindowSize,
  ColorDepth,
  MethodUrlCompletion,
  Secure3dStatus,
} from "globalpayments-api";
```

> **Enum casing** in this SDK is PascalCase keys with `SCREAMING_SNAKE_CASE` string values for most 3DS enums: `AuthenticationSource.Browser` → `"BROWSER"`, `MethodUrlCompletion.Yes`/`.No`/`.Unavailable`, `ChallengeWindowSize.FullScreen` → `"FULL_SCREEN"`. **`ColorDepth` uses plural "Bits"** — `ColorDepth.TwentyFourBits` → `"TWENTY_FOUR_BITS"`. Verify exact casing per enum against `src/Entities/Enums.ts` before emitting.

### Step 1 — Check Enrollment

Call this before rendering the payment form. The response tells you whether the card is enrolled in 3DS and provides the `serverTransactionId` that ties all subsequent steps together.

```typescript
const secureEcom = await Secure3dService.checkEnrollment(card)
  .withAmount("10.00")
  .withCurrency("GBP")
  .execute("my-config");

if (secureEcom instanceof ThreeDSecure) {
  const serverTransId = secureEcom.serverTransactionId;
  const enrolled = secureEcom.enrolled;         // a Secure3dStatus value, not a boolean
  const messageVersion = secureEcom.messageVersion;
}
```

### Step 2 — Initiate Authentication

Send browser fingerprint data collected from the user's browser. This may resolve frictionlessly (no user interaction) or return `CHALLENGE_REQUIRED`.

```typescript
// Collect from browser via JS (navigator / screen properties)
const browserData = new BrowserData();
browserData.acceptHeader = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
browserData.colorDepth = ColorDepth.TwentyFourBits;
browserData.ipAddress = "127.0.0.1";
browserData.javaEnabled = false;
browserData.javaScriptEnabled = true;
browserData.language = "en-GB";
browserData.screenHeight = 1080;
browserData.screenWidth = 1920;
browserData.challengWindowSize = ChallengeWindowSize.FullScreen; // NB: "challeng" — matches the SDK's field name typo exactly, do not "fix" it
browserData.timeZone = "0";                                       // NB: capital Z — not `timezone`
browserData.userAgent = req.headers["user-agent"] as string;

// Shipping address (required for initiate-auth)
const shippingAddress = new Address();
shippingAddress.streetAddress1 = "1 Test Street";
shippingAddress.city = "London";
shippingAddress.postalCode = "SW1A 1AA";
shippingAddress.countryCode = "826"; // ISO 3166-1 numeric

const now = new Date();
const orderCreateDate = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()} ${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}`;

const initAuth = await Secure3dService.initiateAuthentication(card, secureEcom)
  .withAmount("10.00")
  .withCurrency("GBP")
  .withAuthenticationSource(AuthenticationSource.Browser)
  .withMethodUrlCompletion(MethodUrlCompletion.Unavailable) // Yes | No | Unavailable
  .withOrderCreateDate(orderCreateDate)
  .withAddress(shippingAddress, AddressType.Shipping)
  .withBrowserData(browserData)
  .execute("my-config");

if (initAuth instanceof ThreeDSecure) {
  const status = initAuth.status;                 // Secure3dStatus.SuccessAuthenticated | .ChallengeRequired | .Failed | etc.
  const acsChallengeUrl = initAuth.issuerAcsUrl;
  const eci = initAuth.eci;
  const authValue = initAuth.authenticationValue;
  const challengeMandated = initAuth.challengeMandated;
}
```

> **`withOrderCreateDate()` takes a formatted `string`**, not a `Date` object (`SecureBuilder.withOrderCreateDate(value: string)`, `src/Builders/SecureBuilder.ts`). Build the string yourself, matching the format the SDK's own tests use.
>
> **`BrowserData.challengWindowSize` and `BrowserData.timeZone`** are the exact field names in source (`src/Entities/BrowserData.ts`) — `challengWindowSize` is missing the second "e" in "Challenge", and `timeZone` capitalizes the "Z". Both are confirmed typos/casing quirks in the SDK itself, not documentation errors — emit them exactly as shown or the assignment won't compile against the SDK's own `.d.ts`.

### Step 3 — Handle Challenge (when `.status` is `Secure3dStatus.ChallengeRequired`)

```typescript
if (initAuth instanceof ThreeDSecure && initAuth.status === Secure3dStatus.ChallengeRequired) {
  const challengeRequestUrl = initAuth.issuerAcsUrl;
  const encodedChallengeRequest = initAuth.payerAuthenticationRequest; // base64-encoded CReq
  const messageType = initAuth.messageType ?? "creq";

  // Build and POST the CReq form to the ACS URL
  // Your challengeNotificationUrl receives the CRes when the user completes the challenge
}
```

### Step 3b — Get Authentication Result

Call this after the ACS posts back to your `challengeNotificationUrl` (or immediately after a frictionless success to confirm final state):

```typescript
const finalResult = await Secure3dService.getAuthenticationData()
  .withServerTransactionId(secureEcom.serverTransactionId)
  .withAmount("10.00")
  .execute("my-config");

if (finalResult instanceof ThreeDSecure) {
  const finalStatus = finalResult.status;
  const finalEci = finalResult.eci;
  const authValue = finalResult.authenticationValue;
  const dsTransRef = finalResult.directoryServerTransactionId;
}
```

### Step 4 — Charge with 3DS Data Attached

```typescript
import { CreditCardData } from "globalpayments-api";

const chargeCard = new CreditCardData();
chargeCard.token = "PMT_TOKEN"; // from hosted fields tokenisation

// Attach the completed ThreeDSecure object before charging
chargeCard.threeDSecure = finalResult as ThreeDSecure;

const transaction = await chargeCard
  .charge("10.00")
  .withCurrency("GBP")
  .execute("my-config");

const transactionId = transaction.transactionId;
const status = transaction.responseMessage; // "CAPTURED"
const resultCode = transaction.responseCode;
```

### Full Hosted Fields + 3DS Combined Flow

The recommended pattern for web integrations combines Hosted Fields tokenisation with the 3DS flow. Raw card numbers never touch your server.

**Server exposes these endpoints (Express route handlers, naming is illustrative):**

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/tokenization-config` | Returns short-lived `PMT_POST_Create_Single` token for Hosted Fields |
| POST | `/api/check-enrollment` | Step 1 — 3DS enrollment check |
| POST | `/api/initiate-auth` | Step 2 — Initiate authentication with browser data |
| POST | `/api/get-auth-result` | Step 3b — Retrieve final auth result |
| POST | `/api/authorize-payment` | Step 4 — Charge the tokenised card |

**Request shape for `/api/check-enrollment`:**
```json
{
  "payment_method_id": "PMT_...",
  "amount": "10.00",
  "currency": "GBP"
}
```

**Request shape for `/api/initiate-auth`:**
```json
{
  "payment_method_id": "PMT_...",
  "amount": "10.00",
  "currency": "GBP",
  "server_trans_id": "...",
  "method_url_completion": "UNAVAILABLE",
  "browser_data": {
    "accept_header": "...",
    "color_depth": 24,
    "ip": "127.0.0.1",
    "java_enabled": false,
    "javascript_enabled": true,
    "language": "en-GB",
    "screen_height": 1080,
    "screen_width": 1920,
    "challenge_window_size": "FULL_SCREEN",
    "timezone": "0",
    "user_agent": "..."
  }
}
```

**Request shape for `/api/authorize-payment`:**
```json
{
  "payment_method_id": "PMT_...",
  "amount": "10.00",
  "currency": "GBP",
  "authentication_id": "<server_trans_ref from initiate-auth response>"
}
```

### 3DS Test Cards

Use expiry any future date and CVN `131` (per SDK test fixtures — `test/Integration/Gateways/GpApiConnector/3DS2.test.ts` uses `card.cvn = "131"`). Source: `test/Data/GpApi3DSTestCards.ts` in https://github.com/globalpayments/node-sdk — the same sandbox fixture set backs https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/nodejs.

| Card number | Constant name | Expected result | ECI |
|---|---|---|---|
| `4263970000005262` | `CARD_AUTH_SUCCESSFUL_V2_1` | Frictionless success | — |
| `4222000006724235` | `CARD_AUTH_SUCCESSFUL_NO_METHOD_URL_V2_1` | Frictionless success, no method URL | — |
| `4012001038488884` | `CARD_CHALLENGE_REQUIRED_V2_1` | Challenge required | — |
| `4012001037167778` | `CARD_AUTH_ATTEMPTED_BUT_NOT_SUCCESSFUL_V2_1` | Attempted, not successful | — |
| `4012001037461114` | `CARD_AUTH_FAILED_V2_1` | Authentication failed | — |
| `4012001038443335` | `CARD_AUTH_ISSUER_REJECTED_V2_1` | Issuer rejected | — |
| `4012001037484447` | `CARD_AUTH_COULD_NOT_BE_PREFORMED_V2_1` | Authentication could not be performed | — |

ECI `05` is confirmed in the Node test suite for the **V2.2** frictionless-success card `CARD_AUTH_SUCCESSFUL_V2_2` (`4222000006285344`) — `test/Integration/Gateways/GpApiConnector/3DS2.test.ts`, `expect("05").toBe(String(initAuth.eci));`, in the test named `"card holder enrolled challenge required - frictionless - v2 initiate"`. No ECI assertion was found for the V2.1 cards in this SDK's test file, so those cells are left as `—` rather than guessed.

For the full test card list, see: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

---

## Reporting
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/reporting/real-time-reporting-guide.md

```typescript
import {
  ReportingService,
  SearchCriteria,
  TransactionSortProperty,
  SortDirection,
} from "globalpayments-api";

// Single transaction detail
const detail = await ReportingService.transactionDetail(transactionId).execute();

// Paged transaction search — last 30 days
const startDate = new Date();
startDate.setDate(startDate.getDate() - 30);
const endDate = new Date();

const summary = await ReportingService.findTransactionsPaged(1, 10)
  .orderBy(TransactionSortProperty.TIME_CREATED, SortDirection.Desc)
  .where(SearchCriteria.StartDate, startDate)
  .andWith(SearchCriteria.EndDate, endDate)
  .execute();

for (const txn of summary.result) {
  console.log(txn.transactionId, txn.transactionStatus);
}

// Deposits (paged)
const deposits = await ReportingService.findDepositsPaged(1, 10).execute();

// Disputes (paged)
const disputes = await ReportingService.findDisputesPaged(1, 10).execute();
```

> **Search-criteria method name.** Node's `SearchCriteriaBuilder.andWith(criteria, value)` (`src/Entities/Reporting/SearchCriteriaBuilder.ts`) is the method that chains additional filters. `TransactionReportBuilder.where(criteria, value)` (`src/Builders/TransactionReportBuilder.ts`) sets the first criterion and returns the `SearchCriteriaBuilder` for chaining; confirmed real usage in `test/Integration/Gateways/GpApiConnector/ReportingTransactions.test.ts`: `.where(SearchCriteria.StartDate, startDate).andWith(SearchCriteria.EndDate, endDate).execute()`.
>
> **`TransactionSortProperty` values are `SCREAMING_SNAKE_CASE`** — confirmed in `src/Entities/Enums.ts`: `TIME_CREATED`, `STATUS`, `TYPE`, `DEPOSIT_ID`, `ID`.
>
> `TransactionReportBuilder` also exposes direct fluent setters that skip `SearchCriteria` entirely for the most common filters — `.withTransactionId()`, `.withBatchId()`, `.withStartDate()`, `.withEndDate()`, `.withDepositId()`, `.withDisputeId()`, `.withPaging(page, pageSize)` — these are used internally by `ReportingService`'s static factory methods (e.g. `transactionDetail(id)` calls `.withTransactionId(id)` for you).

`ReportingService` methods are static (`src/Services/ReportingService.ts`): `.activity()`, `.batchDetail()`, `.transactionDetail(id)`, `.findTransactions()`, `.findTransactionsPaged(page, pageSize, transactionId?)`, `.findStoredPaymentMethodsPaged(page, pageSize)`, `.storedPaymentMethodDetail(id)`, `.disputeDetail(id)`, `.findDisputesPaged(page, pageSize)`, `.documentDisputeDetail(id)`, `.settlementDisputeDetail(id)`, `.findSettlementDisputesPaged(page, pageSize)`, `.findSettlementTransactionsPaged(page, pageSize, transactionId?)`, `.findDepositsPaged(page, pageSize)`, `.depositDetail(id)`. Paged results implement `PagedResult` — read the array off `.result` (confirmed field name on the paged-result shape used in the test suite, e.g. `summary.result.length`).

---

## Error Handling
> TypeScript has no typed `catch` clauses — narrow with `instanceof`, most specific to least specific.

```typescript
import {
  CreditCardData,
  BuilderError,
  ConfigurationError,
  GatewayError,
  UnsupportedTransactionError,
  ArgumentError,
  NotImplementedError,
  ApiError,
} from "globalpayments-api";

async function chargeWithHandling(card: CreditCardData): Promise<void> {
  try {
    const response = await card.charge("100.00").withCurrency("USD").execute();

    if (response.responseCode === "00" || response.responseMessage === "SUCCESS") {
      // approved
    }
  } catch (e) {
    if (e instanceof BuilderError) {
      // Missing required builder field (e.g., no currency)
      console.error("Builder error:", e.message);
    } else if (e instanceof ConfigurationError) {
      // Bad or incomplete config
      console.error("Config error:", e.message);
    } else if (e instanceof GatewayError) {
      // Gateway declined or returned an error — carries responseCode/responseMessage
      console.error(`Gateway error [${e.responseCode}]:`, e.responseMessage ?? e.message);
    } else if (e instanceof UnsupportedTransactionError) {
      // Gateway or payment method doesn't support this operation
      console.error("Unsupported:", e.message);
    } else if (e instanceof ArgumentError) {
      // A required argument was null/missing at the SDK call site
      console.error("Argument error:", e.message);
    } else if (e instanceof NotImplementedError) {
      // SDK/gateway doesn't implement the requested operation (e.g. an unsupported report orderBy)
      console.error("Not implemented:", e.message);
    } else if (e instanceof ApiError) {
      // Catch-all for any other SDK-thrown error
      console.error("API error:", e.message);
    } else {
      // A non-SDK error (network failure, JSON parse error, etc.)
      throw e;
    }
  }
}
```

`GatewayError` (`src/Entities/Errors.ts`) carries `responseCode` and `responseMessage` fields, set only when the constructor receives them — check for `undefined` before using. There is **no `ValidationError`** and **no `GatewayTimeoutError`** in this SDK — confirmed by reading the complete `src/Entities/Errors.ts` file, which defines exactly seven classes: `ApiError`, `ArgumentError`, `BuilderError`, `ConfigurationError`, `GatewayError`, `NotImplementedError`, `UnsupportedTransactionError`. A gateway timeout surfaces as a plain `GatewayError` or a lower-level network error from the underlying HTTP transport — distinguish it by inspecting `message`/`responseCode`, not by a dedicated subclass. Real usage of this narrowing pattern is confirmed in the SDK's own test suite, `test/Integration/Gateways/GpApiConnector/AccessToken.test.ts`: `expect(error instanceof GatewayError).toBe(true); expect(error?.responseCode).toBe("40119");`.

---

## Terminal Operations
> Semi-integrated, card-present device support. `src/Terminals/` (60 files) implements exactly one device family — **UPA**. This is a **separate code path** from every gateway operation above — read "Gateway vs. Terminal" before mixing patterns.

### Gateway vs. Terminal: two distinct code paths

Terminal transactions do **not** go through `ServicesContainer.configureService(config)` + a payment-method's `.charge()` the way gateway transactions do. They go through a parallel registration and execution path:

- **Gateway path:** `ServicesContainer.configureService(gatewayConfig)` registers a `gatewayConnector` on `ConfiguredServices` (`src/ConfiguredServices.ts`); `AuthorizationBuilder.execute()` reaches it through `ServicesContainer.instance().getClient(configName)`.
- **Terminal path:** `DeviceService.create(connectionConfig)` (`src/Services/DeviceService.ts`) calls `ServicesContainer.configureService(config, configName)`, which — via `ConnectionConfig.configureContainer(services)` (`src/Terminals/ConnectionConfig.ts`) — sets `services.deviceController = new UpaController(this)`. The `ConfiguredServices.deviceController` setter (`src/ConfiguredServices.ts`) immediately calls `deviceController.configureInterface()` and caches the result on `services.deviceInterface`. `TerminalAuthBuilder.execute()` and `TerminalManageBuilder.execute()` (`src/Terminals/Builders/TerminalAuthBuilder.ts`, `TerminalManageBuilder.ts`) call `ServicesContainer.instance().getDeviceController(configName)` and then `.processTransaction(this)` / `.manageTransaction(this)` on it — never `getClient()`.

Both builder families' `.execute()` methods return a `Promise` and both extend `TransactionBuilder` (`TerminalBuilder extends TransactionBuilder<ITerminalResponse>`, `src/Terminals/Builders/TerminalBuilder.ts`), so the call shape looks identical to a gateway builder. What differs is which registry entry `execute()` reaches into — `getDeviceController()`, not `getClient()`. Do not call `ServicesContainer.configureService()` directly with a `ConnectionConfig` and expect a payment-method object's `.charge()` to reach a terminal; use the `IDeviceInterface` returned by `DeviceService.create()` instead.

### Creating a Device

```typescript
import { ConnectionConfig, ConnectionModes, DeviceService, DeviceType } from "globalpayments-api";

const config = new ConnectionConfig();
config.deviceType = DeviceType.UPA_DEVICE;
config.connectionMode = ConnectionModes.TCP_IP;
config.ipAddress = "192.168.0.5";
config.port = "10009";

const device = DeviceService.create(config);
```

`DeviceService.create(config: ConnectionConfig, configName: string = "default"): IDeviceInterface` (`src/Services/DeviceService.ts`) is synchronous — it does not return a `Promise`. It calls `ServicesContainer.configureService(config, configName)` and, when `config.gatewayConfig` is set, also calls `config.setConfigName(configName)` and registers that gateway config under the same name, then returns `ServicesContainer.instance().getDeviceInterface(configName)`.

### `ConnectionConfig`
> `src/Terminals/ConnectionConfig.ts` — extends `Configuration`, implements `ITerminalConfiguration` (`src/Terminals/Abstractions/ITerminalConfiguration.ts`).

| Field | Type | Notes |
|---|---|---|
| `deviceType` | `DeviceType` | Required. Selects which controller `configureContainer()` wires up — see Device Families below. |
| `connectionMode` | `ConnectionModes` | `SERIAL`, `TCP_IP`, `SSL_TCP`, `HTTP`, `MEET_IN_THE_CLOUD` (`src/Terminals/Enums.ts`). |
| `ipAddress`, `port` | `string` | Required by `validate()` when `connectionMode` is `TCP_IP` or `HTTP`. |
| `parity` | `Parity` | `None`, `Odd`, `Even` (`src/Terminals/Enums.ts`) — serial connection setting. |
| `requestIdProvider` | `IRequestIdProvider` | Not required by `validate()` for any `deviceType` in this SDK — `validate()` only checks `ipAddress`/`port`. Interface: `src/Terminals/Abstractions/IRequestIdProvider.ts` — one method, `getRequestId(): number`. Supply one anyway; `UpaController` reads `config.requestIdProvider` in its constructor and several request builders fall back to it when a caller doesn't pass an explicit reference number. |
| `gatewayConfig` | `GatewayConfig` | Set when the device needs an underlying gateway config registered alongside it — this is the real pattern the SDK's own UPA test helpers use for GP API's Meet-in-the-Cloud mode (`test/Unit/Terminals/UPA/UpaHelpertest.ts`, `buildConfig()`: `config.gatewayConfig = gpApiConfig`). |
| `configName` | `string` | Set via `setConfigName()`/read via `getConfigName()`; `DeviceService.create()` sets it for you. |
| `timeout` | `number` | Inherited from `Configuration`. `ConnectionConfig.connectionConfig()` sets it to `-1` (no timeout) — this method is not called from the constructor in the source read; do not assume it runs automatically. |

`validate()` (`ConnectionConfig`, calls `super.validate()` first) throws `ApiError` — not a `ConfigurationError` — when `connectionMode` is `TCP_IP` or `HTTP` and either `ipAddress` or `port` is missing. No other `deviceType`-specific validation exists in this file, confirmed by reading the full method.

### Device Families
> Read directly from `ConnectionConfig.configureContainer()`'s `switch (this.deviceType)` in `src/Terminals/ConnectionConfig.ts`.

The `DeviceType` enum (`src/Entities/Enums.ts`) declares twelve constants: `PAX_DEVICE`, `PAX_D200`, `PAX_D210`, `PAX_S300`, `PAX_PX5`, `PAX_PX7`, `HPA_ISC250`, `HPA_LANE3000`, `UPA_DEVICE`, `GENIUS`, `NUCLEUS_SATURN_1000`, `GENIUS_VERIFONE_P400`. **`configureContainer()`'s switch has exactly one case — `DeviceType.UPA_DEVICE`, which registers `new UpaController(this)` — every other constant falls through to `default: break;` and no controller is registered.** This is confirmed by reading the complete switch statement, not inferred from the constant names.

| Family | `DeviceType` constants | Controller |
|---|---|---|
| UPA | `UPA_DEVICE` | `src/Terminals/UPA/UpaController.ts` |
| *(declared, unrouted)* | `PAX_DEVICE`, `PAX_D200`, `PAX_D210`, `PAX_S300`, `PAX_PX5`, `PAX_PX7`, `HPA_ISC250`, `HPA_LANE3000`, `GENIUS`, `NUCLEUS_SATURN_1000`, `GENIUS_VERIFONE_P400` | none — falls through to `default: break;` |

**Confirmed absent:** the eleven non-UPA `DeviceType` constants above have no corresponding directory or controller anywhere in this repo — `grep -iE "pax|hpa|genius|diamond|nexgo" ` over the full recursive repo tree returns zero matches outside the enum declaration itself. Setting `config.deviceType` to any of them produces no compile error (the enum member exists) but silently leaves `services.deviceController` unset, so `DeviceService.create()` returns `ServicesContainer.instance().getDeviceInterface(configName)` as `undefined` — do not set `deviceType` to a non-`UPA_DEVICE` constant expecting a working controller. For PAX, HPA, Genius or Diamond devices, use the .NET, Java or PHP SDK.

### `IDeviceInterface` Operations
> `src/Terminals/Abstractions/IDeviceInterface.ts`. The base `DeviceInterface` implementation (`src/Terminals/DeviceInterface.ts`) throws `UnsupportedTransactionError` for any method the concrete device doesn't override — expect that rejection, not a crash, when calling an operation the family doesn't support.

**Sales / auth (return `TerminalAuthBuilder`, called with `.execute()`):**
`sale(amount?)`, `authorize(amount?)`, `refund(amount?)`, `verify()`, `balance()`, `tokenize()`.

**Management (return `TerminalManageBuilder`, called with `.execute()`):**
`capture(amount?)`, `refundById(amount)`, `void()`, `reverse()`, `deletePreAuth()`, `updateLodginDetail(amount?)` — method name confirmed exactly as spelled in the interface, not a typo introduced here.

**Batch / reporting (return `TerminalReportBuilder<ITerminalReport>` or a `Promise` directly):**
`getSAFReport()`, `getBatchReport()`, `getOpenTabDetails()`, `findBatches()` (all return `TerminalReportBuilder<ITerminalReport>`); `getBatchDetails(batchId, printReport?)`, `endOfDay()`, `sendStoreAndForward(printSafReports?)`, `deleteSaf(safReferenceNumber?, tranNo?)` (all return a `Promise` directly, no builder).

**Device / connectivity / other:**
`ping(): Promise<IDeviceResponse>`, `reboot(): Promise<IDeviceResponse>`, `cancel(): Promise<void>`, `lineItem(leftText, rightText?, runningLeftText?, runningRightText?): Promise<IDeviceResponse>`, `registerPOS(posData): Promise<IDeviceResponse>`, `getSignature(prompt1, prompt2?, displayOption?): Promise<ISignatureResponse>`, `startCardTransaction(param?, indicator?, transData?): Promise<IDeviceResponse>`.

### Worked Example: UPA Sale
> Traced to `test/Unit/Terminals/UPA/UpaHelpertest.ts` (`createTestDevice()`, `createLiveSale()`) — the SDK's own working pattern for this device family, using its Meet-in-the-Cloud connection mode against GP API.

```typescript
import {
  ConnectionConfig,
  ConnectionModes,
  DeviceService,
  DeviceType,
  GpApiConfig,
  Environment,
  Channel,
} from "globalpayments-api";

async function runUpaSale(): Promise<void> {
  const config = new ConnectionConfig();
  config.deviceType = DeviceType.UPA_DEVICE;
  config.connectionMode = ConnectionModes.MEET_IN_THE_CLOUD;
  config.requestIdProvider = { getRequestId: () => Math.floor(Math.random() * 10000) };

  // Meet-in-the-Cloud routes the UPA session through GP API — attach the gateway config.
  const gpApiConfig = new GpApiConfig();
  gpApiConfig.appId = "YOUR_APP_ID";
  gpApiConfig.appKey = "YOUR_APP_KEY";
  gpApiConfig.environment = Environment.Test;
  gpApiConfig.channel = Channel.CardPresent;
  gpApiConfig.country = "US";
  config.gatewayConfig = gpApiConfig;

  const device = DeviceService.create(config);
  device.ecrId = "13";

  // Card-present: the terminal itself prompts for and reads the card.
  const response = await device
    .sale(1.0)
    .withGratuity(0)
    .withEcrId(13)
    .withClerkId(123)
    .execute();

  const transactionId = response.transactionId;
  const deviceResponseCode = response.deviceResponseCode; // "00" on approval
  const terminalRefNumber = response.terminalRefNumber;
}
```

`TerminalAuthBuilder.execute(configName: string = "default"): Promise<ITerminalResponse>` and `TerminalManageBuilder.execute(configName?: string): Promise<ITerminalResponse>` are the terminal builders' own overrides — same method name as gateway builders, `await`ed the same way, but routed through `getDeviceController()` (see "Gateway vs. Terminal" above). `ITerminalResponse` (`src/Terminals/Abstractions/IDeviceResponse.ts`) carries `transactionId`, `terminalRefNumber`, `responseCode`, `deviceResponseCode`, `authorizationCode`, `maskedCardNumber`, and related fields — confirmed by reading the interface directly.
