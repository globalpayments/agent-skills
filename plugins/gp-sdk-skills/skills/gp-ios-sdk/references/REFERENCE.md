# GP-IOS-SDK — Code Reference

Every symbol below is traced to a real path in `globalpayments/ios-sdk`
(branch `master`, confirmed 2026-08-06). This reference lists the verified
symbol surface only; APIs confirmed absent from the SDK are omitted, not
stubbed.

## Installation

The repo supports **three** install paths — CocoaPods, manual, and Swift
Package Manager. Real version floors come from the repo's own
`GlobalPayments-iOS-SDK.podspec` and `Package.swift`, not the portal page.

**CocoaPods** (`GlobalPayments-iOS-SDK.podspec`: `s.version = '3.3.2'`,
`s.swift_version = '5.0'`, `s.ios.deployment_target = '9.0'`):

```ruby
pod 'GlobalPayments-iOS-SDK', '~> 3.3'
```

Then `pod install`. Note: the portal's install page states `~> 1.0` — that
constraint is stale against the current podspec version (3.3.2) and would
resolve to a version over three major releases old. Use `~> 3.3`.

**Manual** — download a release from
https://github.com/globalpayments/ios-sdk/releases and drag the
`GlobalPayments-iOS-SDK` folder into your Xcode project. iOS 9.0+ per the
podspec's deployment target.

**Swift Package Manager** — `Package.swift` exists at the repo root and
declares a real library product:

```swift
.package(url: "https://github.com/globalpayments/ios-sdk.git", from: "3.3.2")
```

`Package.swift` declares `swift-tools-version:5.8` and `platforms: [.iOS(.v12)]`
— a **higher iOS floor (12.0) than the podspec/manual path (9.0)**. This is a
real divergence between install methods, not a typo: pick SPM only if your
app already targets iOS 12+; use CocoaPods or manual install for iOS 9–11
support. Neither the podspec nor `Package.swift` states a minimum Xcode
version; the portal's "Xcode 11+" claim predates the SPM manifest's
`swift-tools-version:5.8`, which needs a substantially newer Xcode toolchain
to build via SPM specifically — treat "Xcode 11+" as unverified for the SPM
path.

```swift
import GlobalPayments_iOS_SDK
```

---

## Gateway Configuration

Two working gateways: GP API and Portico. Both configs subclass `GatewayConfig`
and are registered the same way.

```swift
import GlobalPayments_iOS_SDK

// GP API — the only correct app-side construction. `accessTokenInfo` holds
// a short-lived, restricted token your backend minted (see Card Collection);
// the app never holds appId/appKey. `GpApiConfig`'s designated initializer
// accepts `accessTokenInfo:` in place of `appId:`/`appKey:` for exactly
// this reason.
let accessTokenInfo = AccessTokenInfo()
accessTokenInfo.token = backendIssuedToken   // from your backend, not a literal

let config = GpApiConfig(accessTokenInfo: accessTokenInfo)
config.environment = .test

try ServicesContainer.configureService(config: config)
```

The `appId:`/`appKey:` initializer parameters on `GpApiConfig` exist for the
one caller who is allowed to hold real credentials: your backend, minting a
token via `GpApiService.generateTransactionKey(...)` or a server-side GP SDK.
That code never ships in the iOS binary — see Card Collection below for the
full three-stage pattern.

```swift
import GlobalPayments_iOS_SDK

// Portico
let config = PorticoConfig(
    secretApiKey: "skapi_cert_YOUR_KEY"
)
config.environment = .test

try ServicesContainer.configureService(config: config)
```

Confirmed fields — `GpApiConfig` (`ServiceConfigs/Gateways/GpApiConfig.swift`):
`appId`, `appKey`, `secondsToExpire`, `intervalToExpire`, `channel`,
`language`, `country`, `accessTokenInfo`, `challengeNotificationUrl`,
`methodNotificationUrl`, `merchantContactUrl`, `permissions`,
`accessTokenProvider`, `dynamicHeaders`, `merchantId`, `statusUrl`,
`porticoTokenConfig`, `restrictedToken`. `PorticoConfig`
(`ServiceConfigs/Gateways/PorticoConfig.swift`): `siteId`, `licenseId`,
`deviceId`, `username`, `password`, `developerId`, `versionNumber`,
`secretApiKey`, `uniqueDeviceId`, `sdkNameVersion`, `certificationStr`,
`terminalID`, `X509CertificatePath`, `X509CertificateBase64String`,
`proPayUS`.

**GP Ecom is not configurable.** `Classes/Gateways/RealexConnector.swift`
exists (Realex was GP Ecom's pre-rebrand name) but every protocol method body
is empty — `processAuthorization`, `manageTransaction`, `serializeRequest`,
`processReport` all no-op or return `nil`. No `RealexConfig`/`GpEcomConfig`
type exists anywhere in the tree, and `GatewayProvider`
(`Entities/Enums/GatewayProvider.swift`) has only two cases: `.gpAPI` and
`.portico`. Neither `GpApiConfig.configureContainer()` nor
`PorticoConfig.configureContainer()` ever construct a `RealexConnector`. It
is unreachable dead code, not a usable gateway.

---

## Payment Methods

Real types confirmed in `Classes/PaymentMethods/`:

| Type | Use |
|---|---|
| `CreditCardData` | Manually entered card (number, expMonth, expYear, cvn, cardHolderName) |
| `CreditTrackData` | Magnetic-stripe track data (card-present) |
| `Debit` / `DebitTrackData` | Debit card / debit track data |
| `EBT` / `EBTCardData` / `EBTTrackData` | EBT (SNAP/cash benefits) |
| `GiftCard` | Stored-value gift card |
| `eCheck` | ACH / eCheck |
| `RecurringPaymentMethod` | A stored payment method on a recurring schedule |
| `BankPayment` | Open banking / bank transfer |
| `AlternatePaymentMethod` | Wallets/APMs |
| `BNPL` | Buy-now-pay-later |
| `Cash` | Cash tender |
| `Installment` / `InstallmentData` | Installment payment plans |

```swift
let card = CreditCardData()
card.number = "CARD_NUMBER"       // placeholder — see Test Cards
card.expMonth = 12
card.expYear = 2027
card.cvn = "123"
card.cardHolderName = "Joe Smith"
```

---

## Core Transactions

All confirmed in `Example/Tests/GpApi/GpApiCreditCardNotPresentTests.swift`
and `Example/Tests/Portico/PorticoCreditTest.swift`. Every operation is
asynchronous — the completion closure is `(Transaction?, Error?) -> Void`.

```swift
// Charge (sale — auth + capture in one call)
card.charge(amount: 19.99)
    .withCurrency("USD")
    .execute { transaction, error in
        if let error = error {
            // handle error — see Error Handling
            return
        }
        guard let transaction = transaction else { return }
        DispatchQueue.main.async {
            // update UI with transaction.responseCode / transaction.authorizationCode
        }
    }
```

```swift
// Authorize (no capture yet)
card.authorize(amount: 14)
    .withCurrency("USD")
    .withAllowDuplicates(true)
    .execute { transaction, error in
        // transaction?.responseCode == "SUCCESS" on preauthorized
    }
```

```swift
// Capture a prior authorization
transaction.capture(amount: 16)
    .withGratuity(2)
    .execute { capture, error in
        // capture?.responseCode
    }
```

```swift
// Reverse an uncaptured authorization (GP API — not voidTransaction)
transaction.reverse(amount: 12.99)
    .execute { reversal, error in
        // reversal?.responseCode
    }
```

```swift
// Void a settled transaction (Transaction.voidTransaction — Portico-style
// reversal; confirmed as a real method on Transaction, distinct from reverse)
transaction.voidTransaction(amount: 12.99)
    .execute { voided, error in
        // voided?.responseCode
    }
```

```swift
// Refund a prior charge
chargeResult.refund(amount: 10.95)
    .withCurrency("USD")
    .execute { refund, error in
        // refund?.responseCode
    }
```

```swift
// Verify (account/CVV verification, no funds moved)
card.verify()
    .withCurrency("USD")
    .execute { transaction, error in
        // transaction?.responseMessage == "VERIFIED"
    }
```

Confirmed protocol sources: `Chargeable.charge(amount:)`
(`PaymentMethods/PaymentProtocols/Chargable.swift`),
`Refundable.refund(amount:)` (`.../Refundable.swift`),
`Reversable.reverse(amount:)` (`.../Reversable.swift`),
`Verifiable.verify()` (`.../Verifiable.swift`) — each returns
`AuthorizationBuilder`. `Transaction.capture/refund/reverse/voidTransaction`
(`Entities/Transaction.swift`) each return `ManagementBuilder`.

---

## Address Verification

```swift
let address = Address()
address.streetAddress1 = "123 Main St."
address.city = "Downtown"
address.state = "NJ"          // alias of `province`
address.country = "US"
address.postalCode = "12345"

card.charge(amount: 19.99)
    .withCurrency("USD")
    .withAddress(address)
    .execute { transaction, error in
        // transaction?.avsResponseCode / avsResponseMessage
    }
```

Confirmed fields — `Address` (`Entities/Address.swift`): `type`,
`streetAddress1`, `streetAddress2`, `streetAddress3`, `city`, `state`
(getter/setter alias for `province`), `name`, `province`, `postalCode`,
`country`, `countryCode`.

---

## Card Collection

The mobile split — the architecture this SDK requires. Never mint or embed
`appId`/`appKey` in the app. Three numbered stages:

### 1. Backend mints a restricted access token

Plain HTTP contract your backend implements with a server-side Global Payments
SDK. Your backend holds the real `appId`/`appKey` and calls the GP API `/accesstoken` endpoint
(or its SDK's equivalent, e.g. `GpApiService.generateTransactionKey(...)` if
your backend happens to be Swift) with `permissions` scoped narrowly and
`restrictedToken: true`, then returns only the resulting token to the app:

```text
POST https://your-backend.example.com/api/mobile-session
Response 200:
{
  "accessToken": "...",
  "secondsToExpire": 600
}
```

### 2. The app configures the SDK with that token and tokenizes the card

The app never sees `appId`/`appKey` — only the short-lived token from step 1.

```swift
import GlobalPayments_iOS_SDK

let accessTokenInfo = AccessTokenInfo()
accessTokenInfo.token = backendIssuedToken   // from step 1's response

let config = GpApiConfig(accessTokenInfo: accessTokenInfo)
config.environment = .test
try ServicesContainer.configureService(config: config)

let card = CreditCardData()
card.number = customerEnteredNumber
card.expMonth = customerEnteredExpMonth
card.expYear = customerEnteredExpYear
card.cvn = customerEnteredCvn

card.tokenize { token, error in
    guard let token = token else {
        // handle error
        return
    }
    // token starts with "PMT_" — send it to the backend, step 3
}
```

### 3. The app sends the `PMT_` reference to the backend, which charges it

```text
POST https://your-backend.example.com/api/charge
Body: { "paymentToken": "PMT_...", "amount": "19.99", "currency": "USD" }
```

The backend (a server-side GP SDK, with its real `appId`/`appKey`) charges
the token exactly as it would any other `CreditCardData` with `.token` set —
raw card data never transits or persists on the merchant's own server, and
the `appKey` never leaves the backend.

---

## Tokenization

```swift
card.tokenize { token, error in
    if let error = error as? ApiException {
        // handle
        return
    }
    // token is a "PMT_..." reference; store it server-side against the customer
}
```

```swift
// Charge a previously tokenized card
let tokenizedCard = CreditCardData()
tokenizedCard.token = storedToken

tokenizedCard.charge(amount: 50.0)
    .withCurrency("USD")
    .execute { transaction, error in
        // transaction?.responseCode
    }
```

Confirmed: `CreditCardData.tokenize(completion:)` — signature
`(String?, Error?) -> Void` — and `.token: String?` property, both from
`Tokenizable` (`PaymentMethods/PaymentProtocols/Tokenizable.swift`) and
`CreditCardData` itself. Confirmed call pattern in
`Example/Tests/GpApi/GpApiTokenManagementTests.swift`.

---

## Recurring Billing

`RecurringPaymentMethod`, `RecurringService` and `Schedule` all exist, but
**recurring is wired on GP API only**. `GpApiConfig.configureContainer(services:)`
sets `services.recurringConnector = gateway` (`GpApiConfig.swift:116`);
`PorticoConfig.configureContainer(services:)` never sets it, and
`PorticoConnector` conforms to no recurring service type. A Portico merchant
who copies the sample below gets code that compiles and then throws
`ApiException` ("...not configured for recurring processing") at runtime — use
GP API for recurring on iOS, or perform it from your backend.

The recurring type definitions (`RecurringPaymentMethod`, `RecurringService`, `Schedule`) exist independent of gateway —
only the connector wiring, confirmed above, is limited to GP API.

```swift
let recurringMethod = RecurringPaymentMethod(paymentMethod: tokenizedCard)
recurringMethod.customerKey = "CUSTOMER_KEY"

RecurringService.create(entity: recurringMethod) { entity, error in
    guard let entity = entity else { return }
    let schedule = entity.addSchedule(scheduleId: "SCHEDULE_ID")
    // configure `schedule` fields, then RecurringService.create(entity: schedule) { ... }
}
```

Confirmed: `RecurringPaymentMethod` (`PaymentMethods/RecurringPaymentMethod.swift`)
conforms to `Chargeable`/`Authable`/`Verifiable`/`Refundable`/`Secure3d`;
`.addSchedule(scheduleId:)` returns a `Schedule`. `RecurringService`
(`Services/RecurringService.swift`) has generic static
`create<T: Recurring>`, `delete<T:>`, `edit<T:>`, `get<T:>`, `search<T>()`,
each taking/returning `(T?, Error?) -> Void`.

---

## 3D Secure 2

Four steps via `Secure3dService` (`Services/Secure3dService.swift`), all
completion-handler based. **iOS presents the challenge itself: on
`CHALLENGE_REQUIRED` there is no server redirect — the app loads the ACS
challenge in its own in-app web view.**

```swift
// 1. Check enrollment
Secure3dService
    .checkEnrollment(paymentMethod: card)
    .withCurrency(currency)
    .withAmount(amount)
    .execute { threeDSecure, error in
        // threeDSecure?.issuerAcsUrl
    }
```

```swift
// 2. Initiate authentication
Secure3dService
    .initiateAuthentication(paymentMethod: card, secureEcom: threeDSecure)
    .withAmount(amount)
    .withCurrency(currency)
    .withAuthenticationSource(.browser)
    .withAddress(billingAddress, .billing)
    .withBrowserData(browserData)
    .execute { authResult, error in
        if authResult?.status == "CHALLENGE_REQUIRED" {
            // 3. Present authResult.issuerAcsUrl in a WKWebView inside your
            // app's own UI — see the SDK's own reference implementation:
            // Example/GlobalPayments-iOS-SDK/Modules/Authentications/Views/ACSWebView.swift
            // There is no server redirect to build on iOS.
        }
    }
```

```swift
// 4. After the challenge completes in your WKWebView, get the final result
Secure3dService
    .getAuthenticationData()
    .withServerTransactionId(serverTransactionId)
    .execute { authThreeDSecure, error in
        card.threeDSecure = authThreeDSecure
        // now charge card as usual — the ThreeDSecure result rides along
        card.charge(amount: amount)
            .withCurrency(currency)
            .execute { transaction, error in }
    }
```

Confirmed call chain in `Example/Tests/GpApi/GpApi3DSecure2Tests.swift`:
`checkEnrollment` → `initiateAuthentication` (status `CHALLENGE_REQUIRED` or
`SUCCESS_AUTHENTICATED`) → app-presented challenge → `getAuthenticationData`
→ attach `ThreeDSecure` to the card before charging. The named accessors
`GpApi3DSTestCards.cardChallengeRequiredV22` and `.cardAuthSuccessfulV22` live
in this SDK's own test data (`Example/Tests/Data/GpApi3DSTestCards.swift`), not
in `gpapi-3ds2` — that repo has no `ios` directory. The underlying card numbers
are gateway-level (GP API sandbox) rather than language-specific, so the
`gpapi-3ds2` tables apply here unchanged; only the Swift accessor names are
local to this repo.

---

## Reporting

```swift
ReportingService
    .findTransactions()
    .withStartDate(startDate)
    .withEndDate(endDate)
    .execute { summaries, error in
        // summaries: [TransactionSummary]?
    }
```

Confirmed statics on `ReportingService` (`Services/ReportingService.swift`):
`findTransactions()`, `findTransactionsPaged(page:pageSize:transactionId:)`,
`findSettlementTransactions()`, `findSettlementTransactionsPaged(...)`,
`transactionDetail(transactionId:)`, `findDeposits()`,
`findDepositsPaged(...)`, `depositDetail(depositReference:)`,
`findDisputes()`, `findDisputesPaged(...)` — each returns a
`TransactionReportBuilder<T>` (`Builders/TransactionReportBuilder.swift`).

**Reporting from a mobile client is usually a backend concern.** A
merchant's settlement/dispute dashboard typically belongs on the server,
not in the consumer-facing app; consider calling `ReportingService` from
your backend's own SDK rather than shipping report-pulling code into the
iOS binary, unless the app itself is an internal/merchant-facing tool.

---

## Error Handling

Every completion closure is `(T?, Error?) -> Void`. There is no `try`/`catch`
around the async call itself — only builder construction can `throw`.
Exceptions are flat `struct: Error` types, not a class hierarchy; use
conditional casts to branch on error kind.

```swift
do {
    try ServicesContainer.configureService(config: config)
} catch let error as ConfigurationException {
    // bad/missing config
} catch {
    // unexpected
}

card.charge(amount: 19.99)
    .withCurrency("USD")
    .execute { transaction, error in
        if let gatewayError = error as? GatewayException {
            // gatewayError.responseCode, gatewayError.responseMessage
            return
        }
        if let apiError = error as? ApiException {
            // apiError.message
            return
        }
        if let error = error {
            // BuilderException / UnsupportedTransactionException / other
            return
        }
        guard let transaction = transaction else { return }
        // success
    }
```

Confirmed struct shapes — `GlobalPayments-iOS-SDK/Classes/Entities/Exceptions/`:
`ApiException(message:)`, `BuilderException(message:)`,
`ConfigurationException(message:)`,
`GatewayException(message:responseCode:responseMessage:)`,
`UnsupportedTransactionException(message:)`. All conform to `Error`; none
share a common base type beyond that protocol.
