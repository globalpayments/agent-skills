# GP .NET SDK — Code Reference

Quick-copy C# snippets for the `globalpayments/dotnet-sdk`. All class names and method chains are verified against the SDK source at https://github.com/globalpayments/dotnet-sdk and its test suite at `tests/GlobalPayments.Api.Tests/`.

---

## Installation

```bash
dotnet add package GlobalPayments.Api
```

```xml
<ItemGroup>
  <PackageReference Include="GlobalPayments.Api" Version="11.3.1" />
</ItemGroup>
```

Target framework: `netstandard1.3` (works with .NET Framework 4.6.1+, .NET Core 1.0+, and modern .NET via netstandard compatibility). Source: `src/GlobalPayments.Api/GlobalPayments.Api.csproj`.

---

## Gateway Configuration

### GP API
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/integration-options/sdk/net.md

```csharp
using GlobalPayments.Api;
using GlobalPayments.Api.Entities;

var config = new GpApiConfig {
    AppId       = "YOUR_APP_ID",
    AppKey      = "YOUR_APP_KEY",
    Environment = Environment.TEST,        // Environment.PRODUCTION for live
    Country     = "US",
    Channel     = Channel.CardNotPresent,  // Channel.CardPresent for in-person
};

ServicesContainer.ConfigureService(config);
```

Optional GP API fields:
```csharp
config.MerchantId               = "MER_xxx";
config.MerchantContactUrl       = "https://yoursite.com/about";        // required for 3DS
config.MethodNotificationUrl    = "https://yoursite.com/3ds/method";
config.ChallengeNotificationUrl = "https://yoursite.com/3ds/challenge";
config.SecondsToExpire          = 3600;
config.IntervalToExpire         = IntervalToExpire.WEEK;
config.DataResidency            = DataResidency.EU; // EU data residency
```

`Validate()` (`src/GlobalPayments.Api/ServiceConfigs/Gateways/GpApiConfig.cs`) requires either `AccessTokenInfo` or both `AppId` and `AppKey` to be set — a `ConfigurationException` is thrown otherwise.

### GP Ecom (Realex)

```csharp
using GlobalPayments.Api;
using GlobalPayments.Api.Entities;

var config = new GpEcomConfig {
    MerchantId   = "YOUR_MERCHANT_ID",
    AccountId    = "internet",
    SharedSecret = "YOUR_SECRET",
    Environment  = Environment.TEST,
};

ServicesContainer.ConfigureService(config);
```

`Validate()` (`src/GlobalPayments.Api/ServiceConfigs/Gateways/GpEcomConfig.cs`) requires `MerchantId` and `SharedSecret`; if a 3DS `Secure3dVersion` is set to `Two` or `Any`, `ChallengeNotificationUrl` and `MethodNotificationUrl` are also required.

### Portico (Heartland) — secret API key

```csharp
using GlobalPayments.Api;
using GlobalPayments.Api.Entities;

var config = new PorticoConfig {
    SecretApiKey = "skapi_cert_YOUR_KEY",
    Environment  = Environment.TEST,
};

ServicesContainer.ConfigureService(config);
```

### Portico — 5-point credentials

```csharp
var config = new PorticoConfig {
    SiteId      = 12345,
    LicenseId   = 67890,
    DeviceId    = 11223,
    Username    = "USERNAME",
    Password    = "PASSWORD",
    Environment = Environment.TEST,
};

ServicesContainer.ConfigureService(config);
```

`PorticoConfig.Validate()` throws `ConfigurationException` if both `SecretApiKey` and the 5-point fields (`SiteId`, `LicenseId`, `DeviceId`, `Username`, `Password`) are set — they are mutually exclusive. If any one of the 5-point fields is set, all five are required.

### Portico via GP API (`PorticoTokenConfig`)

`GpApiConfig` can carry legacy Portico credentials in a nested `PorticoTokenConfig` object (`src/GlobalPayments.Api/Entities/GpApi/PorticoTokenConfig.cs`) — used when a GP API integration needs to authenticate against Portico token services:

```csharp
using GlobalPayments.Api.Entities.GpApi;

var config = new GpApiConfig {
    AppId       = "YOUR_APP_ID",
    AppKey      = "YOUR_APP_KEY",
    Environment = Environment.TEST,
    PorticoTokenConfig = new PorticoTokenConfig {
        SiteId       = 12345,
        LicenseId    = 67890,
        DeviceId     = 11223,
        Username     = "USERNAME",
        Password     = "PASSWORD",
        // — or — SecretApiKey = "skapi_cert_YOUR_KEY",
    },
};

ServicesContainer.ConfigureService(config);
```

---

## Payment Methods

### Credit Card (manual entry)

```csharp
using GlobalPayments.Api.PaymentMethods;

var card = new CreditCardData {
    Number         = "CARD_NUMBER", // see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
    ExpMonth       = 12,
    ExpYear        = 2026,
    Cvn            = "123",
    CardHolderName = "Jane Smith",
};
```

### Credit Card (token)

```csharp
var card = new CreditCardData {
    Token = "PMT_TOKEN",
};
```

### Track Data (card present)

```csharp
using GlobalPayments.Api.PaymentMethods;
using GlobalPayments.Api.Entities;

var track = new CreditTrackData {
    Value       = "TRACK_DATA_STRING", // see sandbox track data: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
    EntryMethod = EntryMethod.Swipe,
};
```

### eCheck / ACH

```csharp
using GlobalPayments.Api.PaymentMethods;
using GlobalPayments.Api.Entities;

var check = new eCheck {
    AccountNumber   = "ACCOUNT_NUMBER",
    RoutingNumber   = "ROUTING_NUMBER",
    AccountType     = AccountType.CHECKING,
    CheckType       = CheckType.PERSONAL,
    SecCode         = SecCode.PPD,
    CheckHolderName = "Jane Smith",
};
```

> Note: the class name in source is `eCheck` (lowercase `e`) — `src/GlobalPayments.Api/PaymentMethods/eCheck.cs`.

### Gift Card

```csharp
using GlobalPayments.Api.PaymentMethods;

var gift = new GiftCard {
    Number = "GIFT_CARD_NUMBER",
};
```

---

## Core Transactions
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/online/api-guide.md

### Charge (sale — auth + capture)

```csharp
var response = card.Charge(29.99m)
    .WithCurrency("USD")
    .WithDescription("Order #1234")
    .Execute();

var transactionId = response.TransactionId;
var status        = response.ResponseMessage; // "CAPTURED" or "SUCCESS"
var authCode      = response.AuthorizationCode;
```

### Authorize (hold, capture later)
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/capture-guide.md

```csharp
var response = card.Authorize(29.99m)
    .WithCurrency("USD")
    .Execute();

var transactionId = response.TransactionId;
```

### Capture

```csharp
using GlobalPayments.Api.Entities;

var transaction = Transaction.FromId(transactionId);
var response     = transaction.Capture(29.99m).Execute();
```

### Void / Reverse
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/reverse-guide.md

**Gateway differences:**
- **GP API** — use `.Reverse()`. `GpApiManagementRequestBuilder` (`src/GlobalPayments.Api/Builders/RequestBuilder/GpApi/GpApiManagementRequestBuilder.cs`) has no branch for `TransactionType.Void` — only `Capture`, `Refund`, `Reversal`, `TokenUpdate`, `TokenDelete`, and several others are handled. A `.Void()` call against a GP API config falls through unhandled.
- **Portico / GP Ecom** — use `.Void()`. Both `PorticoConnector` and `GpEcomConnector` handle `TransactionType.Void` explicitly.

```csharp
using GlobalPayments.Api.Entities;

// GP API — reverse a transaction
var transaction = Transaction.FromId(transactionId);
var response     = transaction.Reverse(29.99m).Execute();

// Portico / GP Ecom — void a transaction
var transaction2 = Transaction.FromId(transactionId);
var response2     = transaction2.Void().Execute();
```

### Refund
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/refund-guide.md

```csharp
using GlobalPayments.Api.Entities;

// Refund a settled transaction by ID
var transaction = Transaction.FromId(transactionId);
var response     = transaction.Refund(10.00m)
    .WithCurrency("USD")
    .Execute();

// Standalone credit (refund directly to a payment method)
var response2 = card.Refund(10.00m)
    .WithCurrency("USD")
    .Execute();
```

### Verify
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/verify-guide.md

```csharp
var response = card.Verify()
    .WithCurrency("USD")
    .Execute();
```

---

## Address Verification (AVS)

```csharp
using GlobalPayments.Api.Entities;

var address = new Address {
    StreetAddress1 = "1 Main Street",
    City           = "Atlanta",
    State          = "GA",
    PostalCode     = "30301",
    Country        = "US",
};

var response = card.Charge(100.00m)
    .WithCurrency("USD")
    .WithAddress(address)
    .Execute();

var avsResult = response.AvsResponseCode;
var cvnResult = response.CvnResponseCode;
```

`Address`, `AvsResponseCode` and `CvnResponseCode` are plain `string` properties — there is no dedicated AVS/CVN result enum in the SDK; the gateway returns raw codes. Source: `src/GlobalPayments.Api/Entities/Address.cs`, `src/GlobalPayments.Api/Entities/Transaction.cs`.

---

## Hosted Fields (PCI-Compliant Card Collection)
> GlobalPayments.js hosted fields — raw card numbers never flow through the merchant server.

**PCI guidance:** For server-to-server integrations (like console apps or backend test suites) passing `CreditCardData` with a raw card number is acceptable. For any web-facing integration, use hosted fields so card data is collected inside GP-hosted iframes and your server only ever sees a `PMT_` payment reference token.

### Step 1 — Generate a restricted access token (C#, server-side)

```csharp
using GlobalPayments.Api;
using GlobalPayments.Api.Entities;
using GlobalPayments.Api.Services;

var config = new GpApiConfig {
    AppId       = "YOUR_APP_ID",
    AppKey      = "YOUR_APP_KEY",
    Environment = Environment.TEST,
    Channel     = Channel.CardNotPresent,
    Country     = "US",
    Permissions = new[] { "PMT_POST_Create_Single" }, // restrict to single-use tokenisation only
};

var tokenInfo   = GpApiService.GenerateTransactionKey(config);
var accessToken = tokenInfo.Token; // short-lived token — safe to expose to the browser
```

Return `accessToken` as JSON to the browser. **Never expose your `AppKey` or a full-permission token to client-side code.**

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
// amount is the display amount; the .NET SDK handles numeric conversion server-side.
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

### Step 3 — Charge the token (C#, server-side)

```csharp
using GlobalPayments.Api.PaymentMethods;

var card = new CreditCardData {
    Token = request.PaymentToken, // PMT_ reference from GlobalPayments.js
};

var response = card.Charge(19.99m)
    .WithCurrency("USD")
    .Execute();

var transactionId = response.TransactionId;  // TRN_...
var status        = response.ResponseMessage; // CAPTURED
var authCode      = response.AuthorizationCode;
```

---

## Tokenization
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/tokenization/card-storage-guide.md

### Store a card

```csharp
var response = card.Tokenize();
var token     = response.Token; // starts with "PMT_"
```

### Charge a stored token

```csharp
var tokenCard = new CreditCardData { Token = token };

var response = tokenCard.Charge(50.00m)
    .WithCurrency("USD")
    .Execute();
```

### Update token expiry

```csharp
var tokenCard = new CreditCardData {
    Token    = existingToken,
    ExpMonth = 12,
    ExpYear  = 2027,
};

tokenCard.UpdateTokenExpiry();
```

`UpdateTokenExpiry()` (`src/GlobalPayments.Api/PaymentMethods/Credit.cs`) throws `BuilderException` if `Token` is null or empty.

---

## Recurring Billing
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/recurring/recurring-payments-guide.md

```csharp
using GlobalPayments.Api.Entities;
using GlobalPayments.Api.PaymentMethods;

// Create customer
var customer = new Customer {
    Id        = "cust-001",
    FirstName = "Jane",
    LastName  = "Smith",
    Email     = "jane@example.com",
};
customer.Create();

// Add and persist a payment method for the customer
var rpm = customer.AddPaymentMethod("pm-001", card);
rpm.Create();

// Charge the stored method
var storedMethod = new RecurringPaymentMethod("cust-001", "pm-001");
var response      = storedMethod.Charge(19.99m)
    .WithCurrency("USD")
    .Execute();
```

`Customer.AddPaymentMethod(paymentId, paymentMethod)` (`src/GlobalPayments.Api/Entities/Customer.cs`) only builds a local `RecurringPaymentMethod` object — it does not call the gateway. Call `.Create()` on the returned `RecurringPaymentMethod` (inherited from `RecurringEntity<TResult>.Create()`, `src/GlobalPayments.Api/Entities/RecurringEntity.cs`) to actually persist it. `AddPaymentMethod()` alone does not reach the gateway — a common source of silently-unpersisted payment methods.

---

## 3D Secure 2
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/risk-management/3D-secure/browser-authentication-guide.md
> Reference implementation: https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/dotnet
> Verified test chains: `tests/GlobalPayments.Api.Tests/GpApi/GpApi3DSecure2Test.cs`

**Regional default:** 3DS is **required by default in all regions except the United States**. Always implement the full 3DS2 flow for non-US merchants. US merchants may opt in.

### Config Requirements for 3DS

Three additional fields are required on `GpApiConfig` for any 3DS flow:

```csharp
using GlobalPayments.Api;
using GlobalPayments.Api.Entities;

var config = new GpApiConfig {
    AppId       = "YOUR_APP_ID",
    AppKey      = "YOUR_APP_KEY",
    Environment = Environment.TEST,
    Country     = "GB",                 // non-US → 3DS is required
    Channel     = Channel.CardNotPresent,

    // Required for 3DS — HTTPS URLs
    MerchantContactUrl        = "https://yoursite.com/about",                     // shown in ACS UI
    MethodNotificationUrl     = "https://yoursite.com/3ds-method-notification",
    ChallengeNotificationUrl  = "https://yoursite.com/3ds-challenge-notification", // must be HTTPS
};

ServicesContainer.ConfigureService(config, "my-config");
```

### Imports

```csharp
using GlobalPayments.Api.Services;
using GlobalPayments.Api.Entities;
using GlobalPayments.Api.Entities.Enums;
```

### Step 1 — Check Enrollment

Call this before rendering the payment form. The response tells you whether the card is enrolled in 3DS and provides the `ServerTransactionId` that ties all subsequent steps together.

```csharp
var secureEcom = Secure3dService.CheckEnrollment(card)
    .WithAmount(10.00m)
    .WithCurrency("GBP")
    .Execute("my-config");

// Map response fields
var serverTransId  = secureEcom.ServerTransactionId;
var enrolled       = secureEcom.Enrolled;      // "ENROLLED" | "NOT_ENROLLED" | "ERROR"
var messageVersion = secureEcom.MessageVersion;
var methodUrl       = secureEcom.IssuerAcsUrl;  // present when ACS method is available
var methodData       = secureEcom.PayerAuthenticationRequest;
```

### Step 2 — Initiate Authentication

Send browser fingerprint data collected from the user's browser. This may resolve frictionlessly (no user interaction) or return `CHALLENGE_REQUIRED`.

```csharp
// Collect from browser via JS (navigator / screen properties)
var browserData = new BrowserData {
    AcceptHeader        = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    ColorDepth           = ColorDepth.TWENTY_FOUR_BITS,
    IpAddress            = "127.0.0.1",
    JavaEnabled          = false,
    JavaScriptEnabled    = true,
    Language             = "en-GB",
    ScreenHeight         = 1080,
    ScreenWidth          = 1920,
    ChallengeWindowSize  = ChallengeWindowSize.FULL_SCREEN,
    Timezone             = "0",
    UserAgent            = Request.Headers["User-Agent"].ToString(),
};

// Shipping address (required for initiate-auth)
var shippingAddress = new Address {
    StreetAddress1 = "1 Test Street",
    City           = "London",
    PostalCode     = "SW1A 1AA",
    CountryCode    = "826", // ISO 3166-1 numeric
};

var initAuth = Secure3dService.InitiateAuthentication(card, secureEcom)
    .WithAmount(10.00m)
    .WithCurrency("GBP")
    .WithAuthenticationSource(AuthenticationSource.BROWSER)
    .WithMethodUrlCompletion(MethodUrlCompletion.UNAVAILABLE) // YES | NO | UNAVAILABLE
    .WithOrderCreateDate(DateTime.Now)
    .WithAddress(shippingAddress, AddressType.Shipping)
    .WithBrowserData(browserData)
    .Execute("my-config");

var status          = initAuth.Status;            // "SUCCESS_AUTHENTICATED" | "CHALLENGE_REQUIRED" | "FAILED" | etc.
var acsChallengeUrl = initAuth.IssuerAcsUrl;
var eci              = initAuth.Eci;
var authValue         = initAuth.AuthenticationValue;
var challengeMandated = initAuth.ChallengeMandated;
```

### Step 3 — Handle Challenge (when `Status == "CHALLENGE_REQUIRED"`)

When a challenge is required, redirect the browser to the ACS. On return, call `GetAuthenticationData` (Step 3b) to retrieve the final result.

```csharp
if (initAuth.Status == Secure3dStatus.CHALLENGE_REQUIRED.ToString()) {
    // Retrieve challenge details
    var challengeRequestUrl     = initAuth.IssuerAcsUrl;
    var encodedChallengeRequest = initAuth.PayerAuthenticationRequest; // base64-encoded CReq
    var messageType              = initAuth.MessageType ?? "creq";

    // Build and POST the CReq form to the ACS URL
    // Your ChallengeNotificationUrl receives the CRes when the user completes the challenge
}
```

### Step 3b — Get Authentication Result

Call this after the ACS posts back to your `ChallengeNotificationUrl` (or immediately after a frictionless `SUCCESS_AUTHENTICATED` to confirm final state):

```csharp
var finalResult = Secure3dService.GetAuthenticationData()
    .WithServerTransactionId(serverTransId)
    .Execute("my-config");

var finalStatus = finalResult.Status;                          // "SUCCESS_AUTHENTICATED" | "FAILED" | etc.
var finalEci     = finalResult.Eci;
var authValue     = finalResult.AuthenticationValue;
var dsTransRef     = finalResult.DirectoryServerTransactionId;
```

### Step 4 — Charge with 3DS Data Attached

```csharp
using GlobalPayments.Api.PaymentMethods;

var card = new CreditCardData { Token = "PMT_TOKEN" }; // from hosted fields tokenisation

// Attach the completed ThreeDSecure object before charging
card.ThreeDSecure = finalResult;

var transaction = card.Charge(10.00m)
    .WithCurrency("GBP")
    .Execute("my-config");

var transactionId = transaction.TransactionId;
var status         = transaction.ResponseMessage; // "CAPTURED"
var resultCode      = transaction.ResponseCode;
```

### Full Hosted Fields + 3DS Combined Flow

The recommended pattern for web integrations combines Hosted Fields tokenisation with the 3DS flow. Raw card numbers never touch your server.

**Server exposes these endpoints (ASP.NET controller actions, naming is illustrative):**

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

Use expiry any future date and CVV `123` (per SDK test fixtures). Source: `tests/GlobalPayments.Api.Tests/GpApi/GpApi3DSTestCards.cs` in https://github.com/globalpayments/dotnet-sdk — the same fixture set backs https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/dotnet.

| Card number | Constant name | Expected result | ECI |
|---|---|---|---|
| `4263970000005262` | `CARD_AUTH_SUCCESSFUL_V2_1` | Frictionless success | `05` |
| `4222000006724235` | `CARD_AUTH_SUCCESSFUL_NO_METHOD_URL_V2_1` | Frictionless success, no method URL | — |
| `4012001038488884` | `CARD_CHALLENGE_REQUIRED_V2_1` | Challenge required | — |
| `4012001037167778` | `CARD_AUTH_ATTEMPTED_BUT_NOT_SUCCESSFUL_V2_1` | Attempted, not successful | — |
| `4012001037461114` | `CARD_AUTH_FAILED_V2_1` | Authentication failed | — |
| `4012001038443335` | `CARD_AUTH_ISSUER_REJECTED_V2_1` | Issuer rejected | — |
| `4012001037484447` | `CARD_AUTH_COULD_NOT_BE_PREFORMED_V2_1` | Authentication could not be performed | — |

For the full test card list, see: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

---

## Reporting
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/reporting/real-time-reporting-guide.md

```csharp
using GlobalPayments.Api.Services;
using GlobalPayments.Api.Entities;

// Single transaction detail
var detail = ReportingService.TransactionDetail(transactionId).Execute();

// Paged transaction search
var summary = ReportingService.FindTransactionsPaged(1, 10)
    .OrderBy(TransactionSortProperty.TimeCreated, SortDirection.Descending)
    .Where(SearchCriteria.StartDate, new DateTime(2025, 1, 1))
    .And(SearchCriteria.EndDate, new DateTime(2025, 12, 31))
    .Execute();

foreach (var txn in summary.Results) {
    Console.WriteLine($"{txn.TransactionId} {txn.TransactionStatus}");
}

// Deposits (paged)
var deposits = ReportingService.FindDepositsPaged(1, 10).Execute();

// Disputes (paged)
var disputes = ReportingService.FindDisputesPaged(1, 10).Execute();
```

`ReportingService` methods are static (`src/GlobalPayments.Api/Services/ReportingService.cs`). `.Where(criteria, value)` returns a `SearchCriteriaBuilder<TResult>`; chain further filters with `.And(criteria, value)` (`src/GlobalPayments.Api/Entities/Reporting/SearchCriteria.cs`) — not `AndWith`, which does not exist on this builder.

---

## Error Handling
> Always catch from most specific to least specific.

```csharp
using GlobalPayments.Api.Entities;

try {
    var response = card.Charge(100.00m)
        .WithCurrency("USD")
        .Execute();

    if (response.ResponseCode == "00" || response.ResponseMessage == "SUCCESS") {
        // approved
    }
}
catch (BuilderException e) {
    // Missing required builder field (e.g., no currency)
    Console.Error.WriteLine($"Builder error: {e.Message}");
}
catch (ConfigurationException e) {
    // Bad or incomplete config
    Console.Error.WriteLine($"Config error: {e.Message}");
}
catch (GatewayTimeoutException e) {
    // Gateway did not respond within the given timeout
    Console.Error.WriteLine($"Gateway timeout: {e.Message}");
}
catch (GatewayException e) {
    // Gateway declined or returned an error
    Console.Error.WriteLine($"Gateway error [{e.ResponseCode}]: {e.Message}");
}
catch (UnsupportedTransactionException e) {
    // Gateway or payment method doesn't support this operation
    Console.Error.WriteLine($"Unsupported: {e.Message}");
}
catch (ValidationException e) {
    // SDK-side validation failed before the request was sent
    Console.Error.WriteLine($"Validation error: {string.Join(", ", e.ValidationErrors)}");
}
catch (ApiException e) {
    // Catch-all
    Console.Error.WriteLine($"API error: {e.Message}");
}
```

`GatewayTimeoutException` extends `GatewayException` — catch it first if you need to distinguish a timeout from a declined/error response. Source: `src/GlobalPayments.Api/Entities/Exceptions.cs`.

---

## Terminal Operations
> Semi-integrated, card-present device support (PAX, UPA, HPA, Genius, Diamond terminals). This is a **separate code path** from every gateway operation above — read "Gateway vs. Terminal" before mixing patterns.

### Gateway vs. Terminal: two distinct code paths

Terminal transactions do **not** go through `ServicesContainer.ConfigureService(config)` + a payment-method's `.Execute()` the way gateway charges do. They go through a parallel registration and execution path:

- **Gateway path:** `ServicesContainer.ConfigureService(gatewayConfig)` registers a gateway client on `ConfiguredServices`; `AuthorizationBuilder.Execute()` calls `ServicesContainer.Instance.GetClient(configName).ProcessAuthorization(this)` (`src/GlobalPayments.Api/Builders/AuthorizationBuilder.cs`, line 1382).
- **Terminal path:** `DeviceService.Create(connectionConfig)` calls `ServicesContainer.ConfigureService(config, configName)`, which (via `ConnectionConfig.ConfigureContainer()`) sets `ConfiguredServices.DeviceController` — assigning that property also builds and caches the matching `IDeviceInterface` (`ServicesContainer.cs` line 37: `DeviceInterface = value.ConfigureInterface();`). `TerminalAuthBuilder.Execute()` and `TerminalManageBuilder.Execute()` both call `ServicesContainer.Instance.GetDeviceController(configName)` and then `.ProcessTransaction(this)` / `.ManageTransaction(this)` on it (`src/GlobalPayments.Api/Terminals/Builders/TerminalAuthBuilder.cs`, line 318; `TerminalManageBuilder.cs`, line 162) — never `GetClient()`.

Both builder families end in `.Execute()` and both derive from the same `TransactionBuilder<TResult>` ancestry (`TerminalBuilder<T>` extends `Builders.TransactionBuilder<ITerminalResponse>`, `src/GlobalPayments.Api/Terminals/Builders/TerminalBuilder.cs`), so the call shape looks identical. What differs is which registry entry `Execute()` reaches into — `DeviceController`, not the gateway client. Do not call `ServicesContainer.ConfigureService()` directly with a `ConnectionConfig` and expect a payment-method object's `.Charge()` to work against a terminal; use the `IDeviceInterface` returned by `DeviceService.Create()` instead.

### Creating a Device

```csharp
using GlobalPayments.Api.Services;
using GlobalPayments.Api.Terminals;
using GlobalPayments.Api.Terminals.Abstractions;

var config = new ConnectionConfig {
    DeviceType      = DeviceType.PAX_DEVICE,
    ConnectionMode  = ConnectionModes.TCP_IP,
    IpAddress       = "192.168.1.70",
    Port            = "10009",
    Timeout         = 30000, // ConnectionConfig() sets Timeout = -1 by default
    RequestIdProvider = new RandomIdProvider(), // your IRequestIdProvider implementation
};

var device = DeviceService.Create(config);
```

`DeviceService.Create(ConnectionConfig config, string configName = "default"): IDeviceInterface` (`src/GlobalPayments.Api/Services/DeviceService.cs`) calls `ServicesContainer.ConfigureService(config, configName)`, and — if `config.GatewayConfig` is set — also registers that gateway config under the fixed name `"_upa_passthrough"`, then returns `ServicesContainer.Instance.GetDeviceInterface(configName)`.

### `ConnectionConfig`
> `src/GlobalPayments.Api/Terminals/ConnectionConfig.cs` — extends `Configuration`, implements `ITerminalConfiguration`.

| Field | Type | Notes |
|---|---|---|
| `DeviceType` | `DeviceType` | Required. Selects which controller `ConfigureContainer()` wires up — see Device Families below. |
| `ConnectionMode` | `ConnectionModes` | `SERIAL`, `TCP_IP`, `SSL_TCP`, `HTTP`, `MIC`, `MEET_IN_THE_CLOUD`, `DIAMOND_CLOUD` (enum declared in `ConnectionConfig.cs`). |
| `IpAddress`, `Port` | `string` | Required by `Validate()` when `ConnectionMode` is `TCP_IP` or `HTTP` — throws `ApiException` if either is missing. |
| `BaudRate`, `Parity`, `StopBits`, `DataBits` | enums | Serial connection settings (also declared in `ConnectionConfig.cs`). |
| `RequestIdProvider` | `IRequestIdProvider` | One method, `int GetRequestId()` (`Terminals/Abstractions/IRequestIdProvider.cs`). Optional — `Validate()` does not require it for any `DeviceType`, including `HPA_ISC250`; `HpaController` simply falls back to a default int request ID when it's null (`src/GlobalPayments.Api/Terminals/HPA/HpaController.cs`). |
| `LogManagementProvider` | `IRequestLogger` | e.g. `RequestConsoleLogger` (`src/GlobalPayments.Api/Utils/Logging/`). |
| `GatewayConfig` | `GatewayConfig` | Set when the device needs an underlying gateway config registered alongside it (e.g. UPA passthrough — see "Creating a Device" above). |
| `GeniusMitcConfig` | `Genius.ServiceConfigs.MitcConfig` | Required by `Validate()` when `ConnectionMode == ConnectionModes.MEET_IN_THE_CLOUD` — throws `ConfigurationException` if null. Despite the name, this field is on the base `ConnectionConfig`, not scoped to Genius devices only. |
| `Timeout` | `int` | Inherited from `Configuration`. `ConnectionConfig()`'s constructor sets it to `-1`. |

`ConnectionConfig.Validate()` (internal override) throws `ApiException` when `ConnectionMode` is `TCP_IP`/`HTTP` without both `IpAddress` and `Port`, and `ConfigurationException` when `ConnectionMode` is `MEET_IN_THE_CLOUD` without `GeniusMitcConfig`. **`DIAMOND_CLOUD` mode has no validation at all on plain `ConnectionConfig`** — that check lives only on the subclass below.

**Diamond Cloud is a separate config class.** `IsvID` and `SecretKey` are not fields on `ConnectionConfig` itself — they're declared on `DiamondCloudConfig : ConnectionConfig` (`src/GlobalPayments.Api/Terminals/DiamondCloudConfig.cs`), which also adds `Region`, `PosID`, and a lowercase-named `statusUrl` property (verified spelling — not `StatusUrl`). Its own `Validate()` override calls `base.Validate()` then additionally throws `ConfigurationException` when `ConnectionMode == ConnectionModes.DIAMOND_CLOUD` and either `IsvID` or `SecretKey` is empty. Use `DiamondCloudConfig`, not a plain `ConnectionConfig`, when `ConnectionMode` is `DIAMOND_CLOUD` — a plain `ConnectionConfig` won't throw even with `IsvID`/`SecretKey` unset, because it has no such fields or checks.

### Device Families

All routing below is read directly from `ConnectionConfig.ConfigureContainer()`'s `switch (DeviceType)` statement.

| Family | `DeviceType` constants | Controller |
|---|---|---|
| PAX | `PAX_DEVICE` | `src/GlobalPayments.Api/Terminals/PAX/PaxController.cs` |
| HPA | `HPA_ISC250`, `HPA_LANE3000` | `src/GlobalPayments.Api/Terminals/HPA/HpaController.cs` |
| UPA | `UPA_DEVICE` | `src/GlobalPayments.Api/Terminals/UPA/UpaController.cs` |
| Diamond | `PAX_ARIES8`, `PAX_A80`, `PAX_A35`, `PAX_A920`, `PAX_A77`, `NEXGO_N5` | `src/GlobalPayments.Api/Terminals/Diamond/DiamondController.cs` |
| Genius | `GENIUS_VERIFONE_P400` | `src/GlobalPayments.Api/Terminals/Genius/GeniusController.cs` |

Three things to watch — all confirmed by reading `ConnectionConfig.ConfigureContainer()` directly, not inferred from constant names:

- **Diamond devices use `PAX_*`-named constants.** `PAX_ARIES8`, `PAX_A80`, `PAX_A35`, `PAX_A920`, and `PAX_A77` route to `DiamondController`, not `PaxController` — the constant name is not a reliable guide to which controller handles it.
- **Five `PAX_*` constants are declared but completely unrouted.** `DeviceType.PAX_D200`, `PAX_D210`, `PAX_S300`, `PAX_PX5`, and `PAX_PX7` all exist as enum members (`src/GlobalPayments.Api/Entities/Enums.cs`) and read like real PAX hardware model names, but none of them appear as a `case` in `ConfigureContainer()`'s switch — only bare `PAX_DEVICE` is wired to `PaxController`. An unmatched `DeviceType` falls through to `default: break;`, leaving `ConfiguredServices.DeviceController` unset and `DeviceService.Create()` returns a broken/uninitialized device interface. Do not set `DeviceType` to any of these five expecting a working `PaxController`.
- **`DeviceType.GENIUS` is declared but its switch case is commented out.** The source literally has `//case DeviceType.GENIUS: //services.DeviceController = new GeniusController(this); //break;` — dead code, not a live route. Only `GENIUS_VERIFONE_P400` is wired to `GeniusController`. `DeviceType.NUCLEUS_SATURN_1000` is likewise declared with no case anywhere in the switch. Setting `DeviceType` to `GENIUS` or `NUCLEUS_SATURN_1000` also falls through to `default: break;` with no controller registered.

### `IDeviceInterface` Operations
> `src/GlobalPayments.Api/Terminals/Abstractions/IDeviceInterface.cs` — roughly 90 members. The base `DeviceInterface<T>` implementation (`src/GlobalPayments.Api/Terminals/DeviceInterface.cs`) throws `UnsupportedTransactionException` for any method a given device family doesn't override — expect that exception, not a fatal error, when calling an operation a device doesn't support.

**Sales / auth (return `TerminalAuthBuilder`):**
`Sale()`, `Authorize()`, `Verify()`, `Refund()`, `AddValue()`, `Balance()`, `Withdrawal()`, `Tokenize()`, `AuthCompletion()`, `ContinueTransaction()`, `CompleteTransaction()`, `ProcessTransaction()`, `CreditSale()`, `CreditRefund()`, `DebitSale()`.

**Management (return `TerminalManageBuilder`):**
`Void()`, `Capture()`, `TipAdjust()`, `DeletePreAuth()`, `IncreasePreAuth()`, `Reverse()`, `RefundById()`, `CreditVoid()`, `DebitVoid()`, `VoidRefund()`, `UpdateTaxInfo()`, `UpdateLodginDetail()` (verified spelling — not `UpdateLodgingDetail`).

**Batch / reporting:**
`BatchClose(): IBatchCloseResponse`, `BatchClear(): IBatchClearResponse`, `EndOfDay(): IEODResponse`, `GetLastEOD(): IBatchCloseResponse`, `LocalDetailReport()`, `GetSAFReport()`, `GetBatchReport()`, `GetBatchDetailsReport()`, `GetOpenTabDetails()`, `FindBatches()` (all return `TerminalReportBuilder`), `GetBatchDetails(batchId, printReport): ITerminalReport`, `GetTransactionDetails(transactionType, transactionId, transactionIdType)`.

**Device / connectivity admin:**
`Ping()`, `Reboot()`, `Reset()`, `Initialize()`, `CommunicationCheck()`, `Logon()`, `CloseLane()`, `OpenLane()`, `GetAppInfo()`, `GetBatteryPercentage()`, `GetEncryptionType()`, `SetTimeZone()`, `SetParam()`, `GetParams()`, `SetDebugLevel()`, `GetDebugLevel()`, `GetDebugInfo()`, `ReturnToIdle()`, `DisableHostResponseBeep()`, `ClearDataLake()`.

**Card / signature / UI:**
`StartCard()`, `StartCardTransaction()`, `RemoveCard()`, `Cancel()`, `GetSignatureFile(): ISignatureResponse`, `PromptForSignature()`, `PromptAndGetSignatureFile()`, `EnterPin()`, `LineItem()`, `DisplayMessage()`, `Prompt()`, `ShowMessage()`, `ShowTextBox()`, `ClearMessage()`, `Print()`, `Scan()`, `ReturnDefaultScreen()`, `GetGenericEntry()`, `LoadUDData()` / `RemoveUDData()` / `ExecuteUDDataFile()` / `InjectUDDataFile()`, `InputAccount()`.

**Store-and-forward:**
`SendStoreAndForward(): ISAFResponse`, `SetStoreAndForwardMode(...)` (three overloads), `GetStoreAndForwardParams(): ISafParamsResponse`, `GetSafSummaryReport(): ISafSummaryReport`, `SafUpload(): ISafUploadResponse`, `DeleteStoreAndForwardFile(): ISafDeleteFileResponse`, `DeleteSaf()`.

### Worked Example: PAX Credit Sale
> Traced to `tests/GlobalPayments.Api.Tests/Terminals/Pax/PaxCreditTests.cs` — the SDK's own working pattern for this device family.

```csharp
using GlobalPayments.Api.Entities;
using GlobalPayments.Api.PaymentMethods;
using GlobalPayments.Api.Services;
using GlobalPayments.Api.Terminals;
using GlobalPayments.Api.Terminals.Abstractions;

// A minimal IRequestIdProvider implementation.
public class RandomIdProvider : IRequestIdProvider {
    public int GetRequestId() => new Random().Next(1, 999999);
}

var device = DeviceService.Create(new ConnectionConfig {
    DeviceType        = DeviceType.PAX_DEVICE,
    ConnectionMode    = ConnectionModes.TCP_IP,
    IpAddress         = "192.168.1.70",
    Port              = "10009",
    Timeout           = 30000,
    RequestIdProvider = new RandomIdProvider(),
});

// Card-present: the terminal itself prompts for and reads the card.
// No CreditCardData object is needed — the device is the entry point.
var response = device.Sale(20m)
    .WithAllowDuplicates(true)
    .Execute();

var transactionId = response.TransactionId;
var responseCode  = response.ResponseCode; // "00" on approval

// Manual/keyed entry on the same device: attach a CreditCardData explicitly.
var card = new CreditCardData {
    Number   = "CARD_NUMBER", // see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
    ExpMonth = 12,
    ExpYear  = 2026,
    Cvn      = "123",
};

var address = new Address {
    StreetAddress1 = "1 Global Payments Way",
    PostalCode     = "95124",
};

var response2 = device.Sale(11m)
    .WithAllowDuplicates(true)
    .WithPaymentMethod(card)
    .WithAddress(address)
    .Execute();
```

`TerminalAuthBuilder.Execute(string configName = "default"): ITerminalResponse` and `TerminalManageBuilder.Execute(string configName = "default"): ITerminalResponse` are the terminal builders' own overrides of the base `TransactionBuilder<ITerminalResponse>.Execute()` — same method name as gateway builders, different implementation (see "Gateway vs. Terminal" above).
