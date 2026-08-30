# GP Java SDK — Code Reference

Quick-copy Java snippets for the `globalpayments/java-sdk`. All class names and method chains are verified against the SDK source at https://github.com/globalpayments/java-sdk and its test suite at `src/test/java/com/global/api/tests/gpapi/`.

---

## Installation

### Maven

```xml
<dependency>
    <groupId>com.globalpayments</groupId>
    <artifactId>globalpayments-sdk</artifactId>
    <version>15.3.3</version>
</dependency>
```

### Gradle

```groovy
implementation 'com.globalpayments:globalpayments-sdk:15.3.3'
```

Source/target: Java 8 (`<source>8</source>` / `<target>8</target>` in `pom.xml`). Package root is `com.global.api` — note this differs from the Maven `groupId` (`com.globalpayments`). Source: `pom.xml` at the repo root.

---

## Gateway Configuration

### GP API

> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/integration-options/sdk/java.md

```java
import com.global.api.ServicesContainer;
import com.global.api.serviceConfigs.GpApiConfig;
import com.global.api.entities.enums.Environment;
import com.global.api.entities.enums.Channel;
import com.global.api.entities.exceptions.ConfigurationException;

GpApiConfig config = new GpApiConfig();
config.setAppId("YOUR_APP_ID");
config.setAppKey("YOUR_APP_KEY");
config.setEnvironment(Environment.TEST);       // Environment.PRODUCTION for live
config.setCountry("US");
config.setChannel(Channel.CardNotPresent);     // Channel.CardPresent for in-person

try {
    ServicesContainer.configureService(config);
} catch (ConfigurationException e) {
    // bad/incomplete config — see Error Handling below
}
```

Optional GP API fields:
```java
import com.global.api.entities.enums.IntervalToExpire;
import com.global.api.entities.enums.DataResidency;

config.setMerchantId("MER_xxx");
config.setMerchantContactUrl("https://yoursite.com/about");        // required for 3DS
config.setMethodNotificationUrl("https://yoursite.com/3ds/method");
config.setChallengeNotificationUrl("https://yoursite.com/3ds/challenge");
config.setSecondsToExpire(3600);
config.setIntervalToExpire(IntervalToExpire.WEEK);
config.setDataResidency(DataResidency.EU); // EU data residency
```

`validate()` (`src/main/java/com/global/api/serviceConfigs/GpApiConfig.java`) requires either `accessTokenInfo` or both `appId` and `appKey` to be set — a `ConfigurationException` is thrown otherwise.

### GP Ecom (Realex)

```java
import com.global.api.ServicesContainer;
import com.global.api.serviceConfigs.GpEcomConfig;
import com.global.api.entities.enums.Environment;
import com.global.api.entities.exceptions.ConfigurationException;

GpEcomConfig config = new GpEcomConfig();
config.setMerchantId("YOUR_MERCHANT_ID");
config.setAccountId("internet");
config.setSharedSecret("YOUR_SECRET");
config.setEnvironment(Environment.TEST);

try {
    ServicesContainer.configureService(config);
} catch (ConfigurationException e) {
    // bad/incomplete config
}
```

### Portico (Heartland) — secret API key

```java
import com.global.api.ServicesContainer;
import com.global.api.serviceConfigs.PorticoConfig;
import com.global.api.entities.enums.Environment;
import com.global.api.entities.exceptions.ConfigurationException;

PorticoConfig config = new PorticoConfig();
config.setSecretApiKey("skapi_cert_YOUR_KEY");
config.setEnvironment(Environment.TEST);

try {
    ServicesContainer.configureService(config);
} catch (ConfigurationException e) {
    // bad/incomplete config
}
```

### Portico — 5-point credentials

```java
PorticoConfig config = new PorticoConfig();
config.setSiteId(12345);
config.setLicenseId(67890);
config.setDeviceId(11223);
config.setUsername("USERNAME");
config.setPassword("PASSWORD");
config.setEnvironment(Environment.TEST);

ServicesContainer.configureService(config);
```

`PorticoConfig.validate()` (`src/main/java/com/global/api/serviceConfigs/PorticoConfig.java`) throws `ConfigurationException` if both `secretApiKey` and the 5-point fields (`siteId`, `licenseId`, `deviceId`, `username`, `password`) are set — they are mutually exclusive. If any one of the 5-point fields is set, all five are required.

### Portico via GP API (`PorticoTokenConfig`)

`GpApiConfig` carries legacy Portico credentials in a nested `PorticoTokenConfig` object — used when a GP API integration needs to authenticate against Portico token services. `porticoTokenConfig` is declared as a public field, but the class-level `@Getter @Setter` on `GpApiConfig` still generates `setPorticoTokenConfig(...)` for it — use the setter, as the SDK's own test suite does. Unlike most other `GpApiConfig` fields, it has no `@Accessors(chain = true)`, so the setter returns `void`, not `this` (not chainable):

```java
import com.global.api.serviceConfigs.GpApiConfig;
import com.global.api.entities.gpApi.entities.PorticoTokenConfig;

PorticoTokenConfig porticoToken = new PorticoTokenConfig();
porticoToken.setSiteId(12345);
porticoToken.setLicenseId(67890);
porticoToken.setDeviceId(11223);
porticoToken.setUsername("USERNAME");
porticoToken.setPassword("PASSWORD");
// — or — porticoToken.setSecretApiKey("skapi_cert_YOUR_KEY");

GpApiConfig config = new GpApiConfig();
config.setAppId("YOUR_APP_ID");
config.setAppKey("YOUR_APP_KEY");
config.setEnvironment(Environment.TEST);
config.setPorticoTokenConfig(porticoToken);

ServicesContainer.configureService(config);
```

Source: `src/main/java/com/global/api/serviceConfigs/GpApiConfig.java` (`public PorticoTokenConfig porticoTokenConfig;`, no per-field `@Accessors(chain = true)`), `src/main/java/com/global/api/entities/gpApi/entities/PorticoTokenConfig.java`, `src/test/java/com/global/api/tests/gpapi/GpApiCreateTokenWithPorticoCredentialTests.java` (`.setPorticoTokenConfig(...)` used throughout, e.g. lines 45, 57, 74, 91, 104, 122, 140).

---

## Payment Methods

### Credit Card (manual entry)

```java
import com.global.api.paymentMethods.CreditCardData;

CreditCardData card = new CreditCardData();
card.setNumber("CARD_NUMBER"); // see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
card.setExpMonth(12);
card.setExpYear(2026);
card.setCvn("123");
card.setCardHolderName("Jane Smith");
```

### Credit Card (token)

```java
CreditCardData card = new CreditCardData();
card.setToken("PMT_TOKEN");
```

### Track Data (card present)

```java
import com.global.api.paymentMethods.CreditTrackData;
import com.global.api.entities.enums.EntryMethod;

CreditTrackData track = new CreditTrackData();
track.setValue("TRACK_DATA_STRING"); // see sandbox track data: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
track.setEntryMethod(EntryMethod.Swipe);
```

### eCheck / ACH

```java
import com.global.api.paymentMethods.eCheck;
import com.global.api.entities.enums.AccountType;
import com.global.api.entities.enums.CheckType;
import com.global.api.entities.enums.SecCode;

eCheck check = new eCheck();
check.setAccountNumber("ACCOUNT_NUMBER");
check.setRoutingNumber("ROUTING_NUMBER");
check.setAccountType(AccountType.Checking);
check.setCheckType(CheckType.Personal);
check.setSecCode(SecCode.Ppd);
check.setCheckHolderName("Jane Smith");
```

> Note: the class name in source is `eCheck` (lowercase `e`) — `src/main/java/com/global/api/paymentMethods/eCheck.java`. Enum constants (`AccountType.Checking`, `CheckType.Personal`, `SecCode.Ppd`) are PascalCase in Java — verify exact casing against the enum source before emitting.

### Gift Card

```java
import com.global.api.paymentMethods.GiftCard;

GiftCard gift = new GiftCard();
gift.setNumber("GIFT_CARD_NUMBER");
```

---

## Core Transactions
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/online/api-guide.md

### Charge (sale — auth + capture)

```java
import java.math.BigDecimal;
import com.global.api.entities.Transaction;
import com.global.api.entities.exceptions.ApiException;

try {
    Transaction response = card.charge(new BigDecimal("29.99"))
        .withCurrency("USD")
        .withDescription("Order #1234")
        .execute();

    String transactionId = response.getTransactionId();
    String status        = response.getResponseMessage(); // "CAPTURED" or "SUCCESS"
    String authCode      = response.getAuthorizationCode();
} catch (ApiException e) {
    // see Error Handling below
}
```

### Authorize (hold, capture later)
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/capture-guide.md

```java
Transaction response = card.authorize(new BigDecimal("29.99"))
    .withCurrency("USD")
    .execute();

String transactionId = response.getTransactionId();
```

### Capture

```java
import com.global.api.entities.Transaction;

Transaction transaction = Transaction.fromId(transactionId);
Transaction response    = transaction.capture(new BigDecimal("29.99")).execute();
```

### Void / Reverse
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/reverse-guide.md

**Gateway differences:** `void` is a reserved word in Java, so the SDK method is `.voidTransaction()`, never `.void()`.

- **GP API** — prefer `.reverse()` to match portal terminology. `GpApiManagementRequestBuilder` handles `TransactionType.Reversal` and `TransactionType.Void` in the same branch (`src/main/java/com/global/api/builders/requestbuilder/gpApi/GpApiManagementRequestBuilder.java`, line 93), so `.voidTransaction()` also works against GP API in this SDK — but `.reverse()` remains the recommended, portal-aligned call.
- **Portico / GP Ecom** — use `.voidTransaction()`. Both `PorticoConnector` (`case Void:`) and `GpEcomConnector` (`case Void:` mapped alongside `case Reversal:`) handle it explicitly.

```java
import com.global.api.entities.Transaction;
import java.math.BigDecimal;

// GP API — reverse a transaction
Transaction transaction = Transaction.fromId(transactionId);
Transaction response    = transaction.reverse(new BigDecimal("29.99")).execute();

// Portico / GP Ecom — void a transaction
Transaction transaction2 = Transaction.fromId(transactionId);
Transaction response2    = transaction2.voidTransaction().execute();
```

### Refund
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/refund-guide.md

```java
import com.global.api.entities.Transaction;
import java.math.BigDecimal;

// Refund a settled transaction by ID
Transaction transaction = Transaction.fromId(transactionId);
Transaction response    = transaction.refund(new BigDecimal("10.00"))
    .withCurrency("USD")
    .execute();

// Standalone credit (refund directly to a payment method)
Transaction response2 = card.refund(new BigDecimal("10.00"))
    .withCurrency("USD")
    .execute();
```

### Verify
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/verify-guide.md

```java
Transaction response = card.verify()
    .withCurrency("USD")
    .execute();
```

---

## Address Verification (AVS)

```java
import com.global.api.entities.Address;
import java.math.BigDecimal;

Address address = new Address();
address.setStreetAddress1("1 Main Street");
address.setCity("Atlanta");
address.setState("GA");
address.setPostalCode("30301");
address.setCountry("US");

Transaction response = card.charge(new BigDecimal("100.00"))
    .withCurrency("USD")
    .withAddress(address)
    .execute();

String avsResult = response.getAvsResponseCode();
String cvnResult = response.getCvnResponseCode();
```

`getAvsResponseCode()`/`getCvnResponseCode()` return plain `String` values — there is no dedicated AVS/CVN result enum in the SDK; the gateway returns raw codes. Source: `src/main/java/com/global/api/entities/Address.java`, `src/main/java/com/global/api/entities/Transaction.java`.

---

## Hosted Fields (PCI-Compliant Card Collection)
> GlobalPayments.js hosted fields — raw card numbers never flow through the merchant server.

**PCI guidance:** For server-to-server integrations (like batch jobs or backend test suites) passing `CreditCardData` with a raw card number is acceptable. For any web-facing integration, use hosted fields so card data is collected inside GP-hosted iframes and your server only ever sees a `PMT_` payment reference token.

### Step 1 — Generate a restricted access token (Java, server-side)

```java
import com.global.api.serviceConfigs.GpApiConfig;
import com.global.api.entities.enums.Environment;
import com.global.api.entities.enums.Channel;
import com.global.api.entities.gpApi.entities.AccessTokenInfo;
import com.global.api.services.GpApiService;
import com.global.api.entities.exceptions.GatewayException;

GpApiConfig config = new GpApiConfig();
config.setAppId("YOUR_APP_ID");
config.setAppKey("YOUR_APP_KEY");
config.setEnvironment(Environment.TEST);
config.setChannel(Channel.CardNotPresent);
config.setCountry("US");
config.setPermissions(new String[]{ "PMT_POST_Create_Single" }); // restrict to single-use tokenisation only

try {
    AccessTokenInfo tokenInfo = GpApiService.generateTransactionKey(config);
    String accessToken = tokenInfo.getAccessToken(); // short-lived token — safe to expose to the browser
} catch (GatewayException e) {
    // token generation failed
}
```

Return `accessToken` as JSON to the browser. **Never expose your `appKey` or a full-permission token to client-side code.**

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
// amount is the display amount; the Java SDK handles BigDecimal conversion server-side.
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

### Step 3 — Charge the token (Java, server-side)

```java
import com.global.api.paymentMethods.CreditCardData;
import java.math.BigDecimal;

CreditCardData card = new CreditCardData();
card.setToken(request.getPaymentToken()); // PMT_ reference from GlobalPayments.js

Transaction response = card.charge(new BigDecimal("19.99"))
    .withCurrency("USD")
    .execute();

String transactionId = response.getTransactionId();  // TRN_...
String status        = response.getResponseMessage(); // CAPTURED
String authCode      = response.getAuthorizationCode();
```

---

## Tokenization
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/tokenization/card-storage-guide.md

### Store a card

```java
String token = card.tokenize(); // throws ApiException — starts with "PMT_"
```

`Credit.tokenize()` (`src/main/java/com/global/api/paymentMethods/Credit.java`) is a convenience method that runs a `Verify` transaction with `withRequestMultiUseToken(true)` and returns `response.getToken()` directly — it does not return a `Transaction`.

### Charge a stored token

```java
CreditCardData tokenCard = new CreditCardData();
tokenCard.setToken(token);

Transaction response = tokenCard.charge(new BigDecimal("50.00"))
    .withCurrency("USD")
    .execute();
```

### Update token expiry

```java
CreditCardData tokenCard = new CreditCardData();
tokenCard.setToken(existingToken);
tokenCard.setExpMonth(12);
tokenCard.setExpYear(2027);

tokenCard.updateTokenExpiry(); // throws ApiException, returns boolean
```

---

## Recurring Billing
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/recurring/recurring-payments-guide.md

```java
import com.global.api.entities.Customer;
import com.global.api.paymentMethods.RecurringPaymentMethod;
import java.math.BigDecimal;

// Create customer
Customer customer = new Customer();
customer.setId("cust-001");
customer.setFirstName("Jane");
customer.setLastName("Smith");
customer.setEmail("jane@example.com");
customer.create();

// Add and persist a payment method for the customer
RecurringPaymentMethod rpm = customer.addPaymentMethod("pm-001", card);
rpm.create();

// Charge the stored method
RecurringPaymentMethod storedMethod = new RecurringPaymentMethod("cust-001", "pm-001");
Transaction response = storedMethod.charge(new BigDecimal("19.99"))
    .withCurrency("USD")
    .execute();
```

`Customer.addPaymentMethod(paymentId, paymentMethod)` (`src/main/java/com/global/api/entities/Customer.java`) only builds a local `RecurringPaymentMethod` object — it does not call the gateway. Call `.create()` on the returned `RecurringPaymentMethod` (`src/main/java/com/global/api/paymentMethods/RecurringPaymentMethod.java`) to actually persist it. `addPaymentMethod()` alone does not reach the gateway — a common source of silently-unpersisted payment methods.

---

## 3D Secure 2
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/risk-management/3D-secure/browser-authentication-guide.md
> Reference implementation: https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/java
> Verified test chains: `src/test/java/com/global/api/tests/gpapi/GpApi3DSecure2Test.java`

**Regional default:** 3DS is **required by default in all regions except the United States**. Always implement the full 3DS2 flow for non-US merchants. US merchants may opt in.

### Config Requirements for 3DS

Three additional fields are required on `GpApiConfig` for any 3DS flow:

```java
import com.global.api.serviceConfigs.GpApiConfig;
import com.global.api.entities.enums.Environment;
import com.global.api.entities.enums.Channel;
import com.global.api.ServicesContainer;

GpApiConfig config = new GpApiConfig();
config.setAppId("YOUR_APP_ID");
config.setAppKey("YOUR_APP_KEY");
config.setEnvironment(Environment.TEST);
config.setCountry("GB");                 // non-US → 3DS is required
config.setChannel(Channel.CardNotPresent);

// Required for 3DS — HTTPS URLs
config.setMerchantContactUrl("https://yoursite.com/about");                     // shown in ACS UI
config.setMethodNotificationUrl("https://yoursite.com/3ds-method-notification");
config.setChallengeNotificationUrl("https://yoursite.com/3ds-challenge-notification"); // must be HTTPS

ServicesContainer.configureService(config, "my-config");
```

### Imports

```java
import com.global.api.services.Secure3dService;
import com.global.api.entities.ThreeDSecure;
import com.global.api.entities.Address;
import com.global.api.entities.BrowserData;
import com.global.api.entities.enums.AddressType;
import com.global.api.entities.enums.AuthenticationSource;
import com.global.api.entities.enums.ChallengeWindowSize;
import com.global.api.entities.enums.ColorDepth;
import com.global.api.entities.enums.MethodUrlCompletion;
```

> Enum casing in this SDK is PascalCase, not `SCREAMING_SNAKE_CASE`: `AuthenticationSource.Browser`, `MethodUrlCompletion.Yes` / `.No` / `.Unavailable`, `ColorDepth.TwentyFourBit`, `ChallengeWindowSize.FullScreen`, `AddressType.Shipping`. Verify exact casing per enum against `src/main/java/com/global/api/entities/enums/` before emitting — some enums in this SDK (e.g. `Environment`, `DataResidency`, `IntervalToExpire`) are all-caps while most others are PascalCase.

### Step 1 — Check Enrollment

Call this before rendering the payment form. The response tells you whether the card is enrolled in 3DS and provides the `serverTransactionId` that ties all subsequent steps together.

```java
import java.math.BigDecimal;

ThreeDSecure secureEcom = Secure3dService.checkEnrollment(card)
    .withAmount(new BigDecimal("10.00"))
    .withCurrency("GBP")
    .execute("my-config");

// Map response fields
String serverTransId  = secureEcom.getServerTransactionId();
boolean enrolled      = secureEcom.isEnrolled();
String messageVersion = secureEcom.getMessageVersion();
String methodUrl      = secureEcom.getIssuerAcsUrl();  // present when ACS method is available
String methodData     = secureEcom.getPayerAuthenticationRequest();
```

### Step 2 — Initiate Authentication

Send browser fingerprint data collected from the user's browser. This may resolve frictionlessly (no user interaction) or return `CHALLENGE_REQUIRED`.

```java
import org.joda.time.DateTime;

// Collect from browser via JS (navigator / screen properties)
BrowserData browserData = new BrowserData();
browserData.setAcceptHeader("text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8");
browserData.setColorDepth(ColorDepth.TwentyFourBit);
browserData.setIpAddress("127.0.0.1");
browserData.setJavaEnabled(false);
browserData.setJavaScriptEnabled(true);
browserData.setLanguage("en-GB");
browserData.setScreenHeight(1080);
browserData.setScreenWidth(1920);
browserData.setChallengeWindowSize(ChallengeWindowSize.FullScreen);
browserData.setTimezone("0");
browserData.setUserAgent(request.getHeader("User-Agent"));

// Shipping address (required for initiate-auth)
Address shippingAddress = new Address();
shippingAddress.setStreetAddress1("1 Test Street");
shippingAddress.setCity("London");
shippingAddress.setPostalCode("SW1A 1AA");
shippingAddress.setCountryCode("826"); // ISO 3166-1 numeric

ThreeDSecure initAuth = Secure3dService.initiateAuthentication(card, secureEcom)
    .withAmount(new BigDecimal("10.00"))
    .withCurrency("GBP")
    .withAuthenticationSource(AuthenticationSource.Browser)
    .withMethodUrlCompletion(MethodUrlCompletion.Unavailable) // Yes | No | Unavailable
    .withOrderCreateDate(DateTime.now())
    .withAddress(shippingAddress, AddressType.Shipping)
    .withBrowserData(browserData)
    .execute("my-config");

String status           = initAuth.getStatus();            // "SUCCESS_AUTHENTICATED" | "CHALLENGE_REQUIRED" | "FAILED" | etc.
String acsChallengeUrl  = initAuth.getIssuerAcsUrl();
String eci              = initAuth.getEci();
String authValue        = initAuth.getAuthenticationValue();
boolean challengeMandated = initAuth.isChallengeMandated();
```

`withOrderCreateDate` takes a Joda-Time `org.joda.time.DateTime` (the SDK's test suite uses Joda-Time throughout, not `java.time`) — confirmed via `import org.joda.time.DateTime;` in `GpApi3DSecure2Test.java`.

### Step 3 — Handle Challenge (when `getStatus()` returns `"CHALLENGE_REQUIRED"`)

When a challenge is required, redirect the browser to the ACS. On return, call `getAuthenticationData` (Step 3b) to retrieve the final result.

```java
if ("CHALLENGE_REQUIRED".equals(initAuth.getStatus())) {
    // Retrieve challenge details
    String challengeRequestUrl     = initAuth.getIssuerAcsUrl();
    String encodedChallengeRequest = initAuth.getPayerAuthenticationRequest(); // base64-encoded CReq
    String messageType             = initAuth.getMessageType() != null ? initAuth.getMessageType() : "creq";

    // Build and POST the CReq form to the ACS URL
    // Your challengeNotificationUrl receives the CRes when the user completes the challenge
}
```

### Step 3b — Get Authentication Result

Call this after the ACS posts back to your `challengeNotificationUrl` (or immediately after a frictionless `SUCCESS_AUTHENTICATED` to confirm final state):

```java
ThreeDSecure finalResult = Secure3dService.getAuthenticationData()
    .withServerTransactionId(serverTransId)
    .execute("my-config");

String finalStatus = finalResult.getStatus();                          // "SUCCESS_AUTHENTICATED" | "FAILED" | etc.
String finalEci     = finalResult.getEci();
String authValue     = finalResult.getAuthenticationValue();
String dsTransRef    = finalResult.getDirectoryServerTransactionId();
```

### Step 4 — Charge with 3DS Data Attached

```java
import com.global.api.paymentMethods.CreditCardData;

CreditCardData card = new CreditCardData();
card.setToken("PMT_TOKEN"); // from hosted fields tokenisation

// Attach the completed ThreeDSecure object before charging
card.setThreeDSecure(finalResult);

Transaction transaction = card.charge(new BigDecimal("10.00"))
    .withCurrency("GBP")
    .execute("my-config");

String transactionId = transaction.getTransactionId();
String status         = transaction.getResponseMessage(); // "CAPTURED"
String resultCode      = transaction.getResponseCode();
```

### Full Hosted Fields + 3DS Combined Flow

The recommended pattern for web integrations combines Hosted Fields tokenisation with the 3DS flow. Raw card numbers never touch your server.

**Server exposes these endpoints (Spring/Jakarta controller methods, naming is illustrative):**

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

Use expiry any future date and CVV `123` (per SDK test fixtures). Source: `src/test/java/com/global/api/tests/gpapi/BaseGpApiTest.java` (nested `GpApi3DSTestCards` enum) in https://github.com/globalpayments/java-sdk — the same sandbox fixture set backs https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/java. Same card numbers as the V2.1 constants used by the SDK's other language implementations.

| Card number | Constant name | Expected result | ECI |
|---|---|---|---|
| `4263970000005262` | `CARD_AUTH_SUCCESSFUL_V2_1` | Frictionless success | — |
| `4222000006724235` | `CARD_AUTH_SUCCESSFUL_NO_METHOD_URL_V2_1` | Frictionless success, no method URL | — |
| `4012001038488884` | `CARD_CHALLENGE_REQUIRED_V2_1` | Challenge required | — |
| `4012001037167778` | `CARD_AUTH_ATTEMPTED_BUT_NOT_SUCCESSFUL_V2_1` | Attempted, not successful | — |
| `4012001037461114` | `CARD_AUTH_FAILED_V2_1` | Authentication failed | — |
| `4012001038443335` | `CARD_AUTH_ISSUER_REJECTED_V2_1` | Issuer rejected | — |
| `4012001037484447` | `CARD_AUTH_COULD_NOT_BE_PREFORMED_V2_1` | Authentication could not be performed | — |

ECI `05` is confirmed in the Java test suite for the **V2.2** frictionless-success card `CARD_AUTH_SUCCESSFUL_V2_2` (`4222000006285344`) — `GpApi3DSecure2Test.CardHolderEnrolled_Frictionless_v2_Initiate`, `assertEquals("05", initAuth.getEci())`. No ECI assertion was found for the V2.1 cards in this SDK's test file, so those cells are left as `—` rather than guessed.

For the full test card list, see: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

---

## Reporting
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/reporting/real-time-reporting-guide.md

```java
import com.global.api.services.ReportingService;
import com.global.api.entities.TransactionSummary;
import com.global.api.entities.enums.TransactionSortProperty;
import com.global.api.entities.enums.SortDirection;
import com.global.api.entities.reporting.SearchCriteria;
import com.global.api.entities.reporting.TransactionSummaryPaged;
import com.global.api.entities.reporting.DepositSummaryPaged;
import com.global.api.entities.reporting.DisputeSummaryPaged;
import com.global.api.utils.DateUtils;
import java.util.Date;

// Single transaction detail
TransactionSummary detail = ReportingService.transactionDetail(transactionId).execute();

// Paged transaction search — last 30 days
Date startDate = DateUtils.atStartOfDay(DateUtils.addDays(new Date(), -30));
Date endDate   = DateUtils.atEndOfDay(new Date());

TransactionSummaryPaged summary = ReportingService.findTransactionsPaged(1, 10)
    .orderBy(TransactionSortProperty.TimeCreated, SortDirection.Descending)
    .where(SearchCriteria.StartDate, startDate)
    .and(SearchCriteria.EndDate, endDate)
    .execute();

for (TransactionSummary txn : summary.getResults()) {
    System.out.println(txn.getTransactionId() + " " + txn.getTransactionStatus());
}

// Deposits (paged)
DepositSummaryPaged deposits = ReportingService.findDepositsPaged(1, 10).execute();

// Disputes (paged)
DisputeSummaryPaged disputes = ReportingService.findDisputesPaged(1, 10).execute();
```

`ReportingService` methods are static (`src/main/java/com/global/api/services/ReportingService.java`). `TransactionReportBuilder.where(criteria, value)` (`src/main/java/com/global/api/builders/TransactionReportBuilder.java`) returns a `SearchCriteriaBuilder<TResult>`; chain further filters with `.and(criteria, value)` (`src/main/java/com/global/api/entities/reporting/SearchCriteriaBuilder.java`) — not `andWith`. `TransactionSummary` lives at `com.global.api.entities.TransactionSummary` (not under the `reporting` package); `TransactionSummaryPaged` extends `PagedResult<TransactionSummary>` (`com.global.api.entities.gpApi.PagedResult`), whose results field is exposed via `.getResults()`.

---

## Error Handling
> Always catch from most specific to least specific.

```java
import com.global.api.entities.Transaction;
import com.global.api.entities.exceptions.ApiException;
import com.global.api.entities.exceptions.BuilderException;
import com.global.api.entities.exceptions.ConfigurationException;
import com.global.api.entities.exceptions.GatewayException;
import com.global.api.entities.exceptions.GatewayTimeoutException;
import com.global.api.entities.exceptions.UnsupportedTransactionException;
import java.math.BigDecimal;

try {
    Transaction response = card.charge(new BigDecimal("100.00"))
        .withCurrency("USD")
        .execute();

    if ("00".equals(response.getResponseCode()) || "SUCCESS".equals(response.getResponseMessage())) {
        // approved
    }
} catch (BuilderException e) {
    // Missing required builder field (e.g., no currency)
    System.err.println("Builder error: " + e.getMessage());
} catch (ConfigurationException e) {
    // Bad or incomplete config
    System.err.println("Config error: " + e.getMessage());
} catch (GatewayTimeoutException e) {
    // Gateway did not respond within the given timeout
    System.err.println("Gateway timeout: " + e.getMessage());
} catch (GatewayException e) {
    // Gateway declined or returned an error
    System.err.println("Gateway error [" + e.getResponseCode() + "]: " + e.getMessage());
} catch (UnsupportedTransactionException e) {
    // Gateway or payment method doesn't support this operation
    System.err.println("Unsupported: " + e.getMessage());
} catch (ApiException e) {
    // Catch-all — ApiException is checked, so this must be present even if
    // every subtype above is already caught, unless the enclosing method
    // itself declares `throws ApiException`.
    System.err.println("API error: " + e.getMessage());
}
```

`GatewayTimeoutException` extends `GatewayException` — catch it first if you need to distinguish a timeout from a declined/error response. There is no `ValidationException` in this SDK — SDK-side validation failures surface as `BuilderException`. Source: `src/main/java/com/global/api/entities/exceptions/`.

---

## Terminal Operations
> Semi-integrated, card-present device support (PAX, UPA, HPA, Genius, Diamond terminals). This is a **separate code path** from every gateway operation above — read "Gateway vs. Terminal" before mixing patterns.
> The developer portal has no Java-specific semi-integration page; every class and method below is verified directly against `src/main/java/com/global/api/terminals/` (175 files) and `src/main/java/com/global/api/services/DeviceService.java` in `globalpayments/java-sdk`.

### Gateway vs. Terminal: two distinct code paths

Both gateway and terminal configuration flow through the same generic entry point, `ServicesContainer.configureService(config, configName)` (`src/main/java/com/global/api/ServicesContainer.java`) — but what happens inside is polymorphic, and what comes back out is different:

- **Gateway path:** `configureService()` calls `config.configureContainer(cs)`; for a gateway config this calls `cs.setGatewayConnector(...)`. `AuthorizationBuilder.execute(configName)` later calls `ServicesContainer.getInstance().getGateway(configName)` (`src/main/java/com/global/api/builders/AuthorizationBuilder.java`, line 1282) to get an `IPaymentGateway` and send the request.
- **Terminal path:** `DeviceService.create(connectionConfig)` (`src/main/java/com/global/api/services/DeviceService.java`) calls the *same* `ServicesContainer.configureService(config, configName)`. `ConnectionConfig.configureContainer(cs)` calls `cs.setDeviceController(new PaxController(this))` (or the matching controller for the device family — see Device Families below), which internally derives `cs.deviceInterface` via `deviceController.configureInterface()` (`src/main/java/com/global/api/ConfiguredServices.java`, `setDeviceController()`). `DeviceService.create()` then returns `ServicesContainer.getInstance().getDeviceInterface(configName)`. `TerminalAuthBuilder.execute(configName)` and `TerminalManageBuilder.execute(configName)` instead call `ServicesContainer.getInstance().getDeviceController(configName)` and invoke `.processTransaction(this)` / the manage-side equivalent on it (`src/main/java/com/global/api/terminals/builders/TerminalAuthBuilder.java`, line 337).

`TerminalAuthBuilder` and `TerminalManageBuilder` both extend `TerminalBuilder<T> extends TransactionBuilder<TerminalResponse>` (`src/main/java/com/global/api/terminals/builders/TerminalBuilder.java`) — the same `TransactionBuilder` ancestor `AuthorizationBuilder` extends — so every terminal call ends in `.execute(configName)` exactly like a gateway call. What differs is which `ConfiguredServices` slot gets populated (`gatewayConnector` vs. `deviceController`/`deviceInterface`) and which accessor `execute()` reaches for. `DeviceService.create()` is a checked-exception-throwing factory method — it does **not** return a payment-method object. Calling `card.charge(...)` against a `ConnectionConfig`-configured `configName` will not route to a terminal; use the `IDeviceInterface` returned by `DeviceService.create()` and call its own operations (`.sale()`, `.authorize()`, etc.) instead.

### Creating a Device

```java
import com.global.api.entities.enums.ConnectionModes;
import com.global.api.entities.enums.DeviceType;
import com.global.api.entities.exceptions.ApiException;
import com.global.api.services.DeviceService;
import com.global.api.terminals.ConnectionConfig;
import com.global.api.terminals.abstractions.IDeviceInterface;

ConnectionConfig deviceConfig = new ConnectionConfig();
deviceConfig.setDeviceType(DeviceType.PAX_DEVICE);
deviceConfig.setConnectionMode(ConnectionModes.TCP_IP);
deviceConfig.setIpAddress("192.168.0.5");
deviceConfig.setPort(10009);

IDeviceInterface device = DeviceService.create(deviceConfig);
```

`DeviceService.create(ConnectionConfig config)` and its overload `DeviceService.create(ConnectionConfig config, String configName)` both `throws ApiException` (`src/main/java/com/global/api/services/DeviceService.java`). The single-arg form delegates to the two-arg form with `configName = "default"`. It calls `ServicesContainer.configureService(config, configName)` and, if `config.getGatewayConfig()` is set, also registers that gateway config under a fixed internal name `"_upa_passthrough"` — then returns `ServicesContainer.getInstance().getDeviceInterface(configName)`.

### `ConnectionConfig`
> `src/main/java/com/global/api/terminals/ConnectionConfig.java` — extends `Configuration` (`src/main/java/com/global/api/serviceConfigs/Configuration.java`), implements `ITerminalConfiguration`. Class-level `@Getter @Setter` (Lombok) — setters return `void`, not chainable; write one `.setX(...)` call per line, matching the SDK's own terminal tests.

| Field | Type | Notes |
|---|---|---|
| `deviceType` | `DeviceType` | Required. Selects which controller `configureContainer()` wires up — see Device Families below. |
| `connectionMode` | `ConnectionModes` | `SERIAL`, `TCP_IP`, `SSL_TCP`, `HTTP`, `MEET_IN_THE_CLOUD`, `DIAMOND_CLOUD`, `AIDL` (`src/main/java/com/global/api/entities/enums/ConnectionModes.java`). |
| `ipAddress`, `port` | `String`, `int` | Required by `validate()` when `connectionMode` is `TCP_IP` or `HTTP`. |
| `baudRate`, `parity`, `stopBits`, `dataBits` | enums | Serial connection settings. |
| `requestIdProvider` | `IRequestIdProvider` | Interface with one method, `int getRequestId()` (`src/main/java/com/global/api/terminals/IRequestIdProvider.java`). Not enforced by `validate()` for any specific `deviceType` in this SDK (unlike the TCP/IP and Diamond Cloud checks below) — the SDK's own PAX and HPA terminal tests set it regardless. |
| `geniusMitcConfig` | `MitcConfig` (`com.global.api.terminals.genius.serviceConfigs`) | Required (or `gatewayConfig`) when `connectionMode == ConnectionModes.MEET_IN_THE_CLOUD`. |
| `gatewayConfig` | `GatewayConfig` | Set when the device needs an underlying gateway config registered alongside it (e.g. Meet-in-the-Cloud, or UPA passthrough via `DeviceService.create()`). |
| `aidlService` | `IAidlService` | AIDL connections only — `validate()` throws `ConfigurationException` if `connectionMode == AIDL` and `deviceType != DeviceType.UPA_DEVICE`. |
| `secretKey`, `isvId`, `posId`, `region` | `String` (`protected`, exposed via the class-level Lombok accessors) | Diamond Cloud fields, declared directly on `ConnectionConfig` itself — not on a separate subclass. |
| `timeout` | `int` | Inherited from `Configuration`; `ConnectionConfig`'s constructor sets it to `30000`. |

`validate()` (in `ConnectionConfig`) throws `ConfigurationException` when: `TCP_IP`/`HTTP` mode is set without both `ipAddress` and `port`; `MEET_IN_THE_CLOUD` mode is set without `geniusMitcConfig` or `gatewayConfig`; or `AIDL` mode is set with a `deviceType` other than `UPA_DEVICE`.

**Diamond Cloud is a config subclass, not a separate field owner.** `DiamondCloudConfig extends ConnectionConfig` (`src/main/java/com/global/api/terminals/diamond/DiamondCloudConfig.java`) adds only `statusUrl` as a new field — `isvId`, `secretKey`, `posId`, and `region` already live on the base `ConnectionConfig`. `DiamondCloudConfig` overrides `validate()` to additionally throw `ConfigurationException` when `connectionMode == DIAMOND_CLOUD` and either `isvId` or `secretKey` is blank, and overrides `configureContainer()` to resolve a `serviceUrl` (test vs. production, region-aware) before delegating to `super.configureContainer()`. Use `DiamondCloudConfig`, not a plain `ConnectionConfig`, when `connectionMode` is `DIAMOND_CLOUD`.

### Device Families

All routing below is read directly from `ConnectionConfig.configureContainer(ConfiguredServices services)`'s `switch (deviceType)` statement.

| Family | `DeviceType` constants | Controller |
|---|---|---|
| PAX | `PAX_DEVICE` | `src/main/java/com/global/api/terminals/pax/PaxController.java` |
| HPA | `HPA_ISC250` | `src/main/java/com/global/api/terminals/hpa/HpaController.java` |
| UPA | `UPA_DEVICE` | `src/main/java/com/global/api/terminals/upa/UpaController.java` |
| Genius | `GENIUS_VERIFONE_P400` | `src/main/java/com/global/api/terminals/genius/GeniusController.java` |
| Diamond | `PAX_ARIES8`, `PAX_A80`, `PAX_A35`, `PAX_A920`, `PAX_A77`, `NEXGO_N5` | `src/main/java/com/global/api/terminals/diamond/DiamondController.java` |

Two traps found, confirmed by reading the full `switch` statement in `ConnectionConfig.configureContainer()` — both independently verified in Java's own source, not assumed from another SDK:

- **Diamond devices use `PAX_*`-named constants.** `PAX_ARIES8`, `PAX_A80`, `PAX_A35`, `PAX_A920`, and `PAX_A77` route to `DiamondController`, not `PaxController` — the constant name is not a reliable guide to which controller handles it.
- **`UPA_SATURN_1000` and `UPA_VERIFONE_T650P` are declared but unrouted.** `DeviceType` (`src/main/java/com/global/api/entities/enums/DeviceType.java`) declares 12 constants, including `UPA_SATURN_1000` and `UPA_VERIFONE_T650P` — but the `switch` in `configureContainer()` has no `case` for either; only `case UPA_DEVICE:` is handled for the UPA family. An unmatched `deviceType` falls through to `default: break;` and no controller is registered — `DeviceService.create()` will then throw `ApiException` ("The specified configuration has not been configured for terminal interaction.") from `ServicesContainer.getDeviceInterface()`. Do not set `deviceType = DeviceType.UPA_SATURN_1000` or `DeviceType.UPA_VERIFONE_T650P` expecting a working controller — use `DeviceType.UPA_DEVICE`.

### `IDeviceInterface` Operations
> `src/main/java/com/global/api/terminals/abstractions/IDeviceInterface.java`. Every method declares `throws ApiException` (checked). A handful of methods are annotated `@Deprecated` in favor of a differently-cased or differently-scoped sibling (e.g. `Print(PrintData)` deprecated in favor of `print(PrintData)`, `Void()` deprecated in favor of `voidTransaction()`) — prefer the non-deprecated form.

**Processing (return `TerminalAuthBuilder`):**
`sale(BigDecimal)`, `authorize(BigDecimal)`, `verify()`, `refund()`, `refund(BigDecimal)`, `addValue()`, `addValue(BigDecimal)`, `balance()`, `withdrawal()`, `withdrawal(BigDecimal)`, `startTransaction(BigDecimal, TransactionType)`.

**Management (return `TerminalManageBuilder`):**
`voidTransaction()`, `capture()`, `capture(BigDecimal)`, `tipAdjust(BigDecimal)`, `deletePreAuth()`, `increasePreAuth(BigDecimal)`, `reverse()`, `refundById()`, `refundById(BigDecimal)`, `updateTaxInfo(BigDecimal)`, `updateLodgingDetails(BigDecimal)`.

**Batch / store-and-forward / reporting:**
`batchClose(): IBatchCloseResponse`, `endOfDay(): IEODResponse`, `findBatches(): IBatchReportResponse`, `getBatchDetails(...): IBatchReportResponse`, `getBatchReport(): TerminalReportBuilder`, `getBatchDetailsReport(): TerminalReportBuilder`, `getOpenTabDetails(): IBatchReportResponse`, `localDetailReport(): TerminalReportBuilder`, `getTransactionDetails(TransactionType, String, TransactionIdType)`, `safDelete(...)`, `safSummaryReport(...)`, `safSummaryReportInBackground(...)`, `safUpload(...)`, `sendStoreAndForward()`, `setStoreAndForwardMode(...)`.

**Device / connectivity admin:**
`broadcastConfiguration(boolean)`, `cancel()`, `closeLane()`, `openLane()`, `deleteImage(String)`, `getConfigContents(TerminalConfigType)`, `getDebugInfo(Enum)`, `getDebugLevel()`, `setDebugLevel(DebugLevel[], Enum)`, `getParams(): String`, `initialize(): IInitializeResponse`, `reboot()`, `reset()`, `returnToIdle()`, `sendFile(SendFileType, String)`, `sendReady()`, `communicationCheck()`, `logOn()`, `saveConfigFile(UpaConfigContent)`, `setLogoCarouselInterval(int, boolean)`, `getBatteryPercentage()`, `updateResource(...)`.

**Card / signature / UI / user-defined data:**
`startCard(PaymentMethodType)`, `getSignatureFile(): ISignatureResponse`, `getSignatureFile(SignatureData): ISignatureResponse`, `promptForSignature()`, `promptForSignature(String)`, `lineItem(String, String)`, `lineItem(String, String, String, String)`, `print(PrintData)`, `scan(ScanData)`, `loadUDDataFile(UDData)`, `removeUDDataFile(UDData)`, `executeUDDataFile(UDData)`, `injectUDDataFile(UDData)`.

### Worked Example: PAX Credit Sale
> Traced to `src/test/java/com/global/api/tests/terminals/pax/PaxCreditTests.java` — the SDK's own working pattern for this device family.

```java
import com.global.api.entities.Address;
import com.global.api.entities.enums.ConnectionModes;
import com.global.api.entities.enums.DeviceType;
import com.global.api.entities.exceptions.ApiException;
import com.global.api.paymentMethods.CreditCardData;
import com.global.api.services.DeviceService;
import com.global.api.terminals.ConnectionConfig;
import com.global.api.terminals.IRequestIdProvider;
import com.global.api.terminals.TerminalResponse;
import com.global.api.terminals.abstractions.IDeviceInterface;

import java.math.BigDecimal;

ConnectionConfig deviceConfig = new ConnectionConfig();
deviceConfig.setDeviceType(DeviceType.PAX_DEVICE);
deviceConfig.setConnectionMode(ConnectionModes.TCP_IP);
deviceConfig.setIpAddress("192.168.0.5");
deviceConfig.setPort(10009);
deviceConfig.setRequestIdProvider(new IRequestIdProvider() {
    public int getRequestId() {
        return (int) (Math.random() * 90000) + 10000;
    }
});

IDeviceInterface device = DeviceService.create(deviceConfig);

// Card-present: the terminal itself prompts for and reads the card.
// No CreditCardData object is needed — the device is the entry point.
TerminalResponse response = device.sale(new BigDecimal("10.00"))
    .withAllowDuplicates(true)
    .execute();

String transactionId = response.getTransactionId();
String responseCode  = response.getResponseCode(); // "00" on approval

// Manual/keyed entry on the same device: attach a CreditCardData explicitly.
CreditCardData card = new CreditCardData();
card.setNumber("CARD_NUMBER"); // see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
card.setExpMonth(12);
card.setExpYear(2026);
card.setCvn("123");

Address address = new Address();
address.setStreetAddress1("1 GlobalPayments Way");
address.setPostalCode("95124");

TerminalResponse manualResponse = device.sale(new BigDecimal("10.00"))
    .withAllowDuplicates(true)
    .withPaymentMethod(card)
    .withAddress(address)
    .execute();
```

`TerminalAuthBuilder.execute(String configName): TerminalResponse` and `TerminalManageBuilder.execute(String configName): TerminalResponse` are the terminal builders' own overrides of `TransactionBuilder.execute()` — same method name as `AuthorizationBuilder.execute()`, different implementation underneath (see "Gateway vs. Terminal" above). Both declare `throws ApiException`.
