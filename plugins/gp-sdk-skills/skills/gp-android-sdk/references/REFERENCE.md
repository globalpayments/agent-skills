# GP-ANDROID-SDK — Code Reference

Every symbol below is traced to a real path in `globalpayments/android-demo-app` (branch `main`, confirmed
2026-08-06) — either the `globalpayments-android-sdk/` library module itself, or a real call site in `sample-app/`
or `merchant3ds/`. See `VERIFICATION.md` for the full symbol table and the omitted/absent items.

## Installation

**Use the coordinate confirmed by the demo repo's own publish script and Maven Central, not the portal page.**

The developer portal (`.../sdk/android.md`) tells you to add `jcenter()` and depend on
`com.globalpayments.android:globalpayments-android-sdk:1.0`. jcenter has been shut down since 2021 and that
coordinate has zero results on Maven Central (confirmed by direct query, see `VERIFICATION.md`). The demo repo's own
`build-logic/convention/src/main/kotlin/PublishConventionPlugin.kt` hardcodes the real group id, and
`gradle/libs.versions.toml` pins the real version:

```kotlin
// PublishConventionPlugin.kt, verbatim
val sdkGroupId = "com.heartlandpaymentsystems"
val sdkArtifactId = "globalpayments-android-sdk"
val sdkVersion: String = libs.findVersion("globalPayments-android").get().toString() // "1.1.36"
```

Both the group id and the `1.1.36` version resolve live on Maven Central today. The demo's own root `README.md`
independently confirms the group id (`com.heartlandpaymentsystems`) but shows a stale version (`1.0`) — use `1.1.36`.

**Groovy:**
```groovy
allprojects {
    repositories {
        mavenCentral()
    }
}

dependencies {
    implementation 'com.heartlandpaymentsystems:globalpayments-android-sdk:1.1.36'
}
```

**Kotlin DSL:**
```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

// app build.gradle.kts
dependencies {
    implementation("com.heartlandpaymentsystems:globalpayments-android-sdk:1.1.36")
}
```

**Requirements** (portal page + both demo README Requirements sections, in agreement): Android 5.0+ (API 21), Android
Studio 4.2+, Java 1.8. The demo repo itself is built with Kotlin 1.9.25, AGP 8.5.2, and JVM target 17 for the
build-logic/library modules (`gradle/libs.versions.toml`) — a newer toolchain than the "Java 1.8" floor the portal
states for *consuming* the SDK; that floor is about the language level your app code can target, not the toolchain
that builds the SDK itself.

The artifact pulls in the underlying Java library transitively as an **`api()`** dependency, so
`com.heartlandpaymentsystems:globalpayments-sdk:14.0.0` classes (`com.global.api.*`) are available to your app code
without a separate `implementation` line. Confirmed: `globalpayments-android-sdk/build.gradle.kts`.

```kotlin
import com.global.api.paymentMethods.CreditCardData
import com.global.api.serviceConfigs.GpApiConfig
import com.global.api.services.GpApiService
import com.globalpayments.android.sdk.ui.cardform.CardFormView
import com.globalpayments.android.sdk.ui.hf.HostedFieldsDialog
```

---

## Gateway Configuration

Two working gateways confirmed by real usage: **GP API** and **GP Ecom**. Both config classes are the underlying
Java library's (`com.global.api.serviceConfigs.*`), registered through the same `ServicesContainer`.

### GP API

```kotlin
import com.global.api.ServicesContainer
import com.global.api.entities.enums.Environment
import com.global.api.entities.gpApi.entities.AccessTokenInfo
import com.global.api.serviceConfigs.GpApiConfig

val accessTokenInfo = AccessTokenInfo()
accessTokenInfo.token = backendIssuedToken   // minted by your backend — see Card Collection below

val gpApiConfig = GpApiConfig().apply {
    setAccessTokenInfo(accessTokenInfo)
    setEnvironment(Environment.TEST)
    setAndroid(true)   // confirmed real setter, GPAPIConfigurationUtils.java — flags the request as mobile
}

ServicesContainer.configureService(gpApiConfig, "default")
```

`GpApiConfig.setAndroid(true)` is a real, Android-specific setter confirmed in
`sample-app/.../utils/configuration/GPAPIConfigurationUtils.java` — call it before configuring the service. The
same file also sets custom headers for gateway analytics (`x-gp-library`, `x-gp-sdk`) via `setDynamicHeaders(...)`;
optional, but confirms the config accepts a `HashMap<String, String>` there if you need custom headers.

**The demo app itself constructs `GpApiConfig` with a real `appId`/`appKey` read from `BuildConfig`
(`GPAPIConfiguration.fromBuildConfig()`), for local testing.** Never do this in integration code you generate — the
`appId:`/`appKey:` setters exist for your backend, which mints the `AccessTokenInfo` and hands the app only the
token. See Card Collection.

### GP Ecom

**Confirmed supported** — `com.global.api.serviceConfigs.GpEcomConfig`, real and wired, called from
`sample-app/.../utils/configuration/GPEcomConfigurationUtils.java`:

```kotlin
import com.global.api.ServicesContainer
import com.global.api.entities.enums.Channel
import com.global.api.serviceConfigs.GpEcomConfig

val gpEcomConfig = GpEcomConfig().apply {
    accountId = "ACCOUNT_ID"           // optional per-account routing
    merchantId = "MERCHANT_ID"
    channel = Channel.Ecom.toString()
    sharedSecret = "SHARED_SECRET"
    rebatePassword = "REBATE_PASSWORD"
    refundPassword = "REFUND_PASSWORD"
}

ServicesContainer.configureService(gpEcomConfig, "default")
```

Confirmed fields (`GPEcomConfigurationUtils.buildDefaultGpEcomConfig`): `accountId`, `merchantId`, `rebatePassword`,
`refundPassword`, `sharedSecret`, `channel`, `shaHashType`, `requestLogger`. The demo's own README instructs
switching the sample app to GP Ecom by setting `useEcom=true` in `configuration.properties` — confirming this is a
real, developer-selectable second gateway path, not leftover dead code.

### Portico

**Not evidenced in this tree.** A case-insensitive search of all 292 Kotlin/Java files across the entire
`android-demo-app` monorepo (library module + both sample apps) found zero occurrences of `portico`. This is not
the same as a confirmed absence at the SDK level — the underlying Java library dependency
(`com.heartlandpaymentsystems:globalpayments-sdk:14.0.0`) may support Portico even though nothing in this Android
repo exercises it, and that dependency's own source was out of scope for this task. If a user needs Portico on
Android, say plainly it was not found here, and point them at a server-side Global Payments SDK.

---

## Payment Methods

Real types confirmed by demo usage, all from `com.global.api.paymentMethods.*` (the underlying Java library):

| Type | Use | Confirmed in |
|---|---|---|
| `CreditCardData` | Manually entered or tokenized card | `CardFormView.kt`, `Secure3DSRepository.kt`, `GooglePayViewModel.kt` |
| `EBTCardData` | EBT (SNAP/cash benefits) | `EbtViewModel.kt` |
| `eCheck` | ACH | `AchViewModel.kt` |
| `RecurringPaymentMethod` | A stored payment method charged on a schedule | `Secure3DSRepository.kt` |

```kotlin
import com.global.api.paymentMethods.CreditCardData

val card = CreditCardData().apply {
    number = "CARD_NUMBER"      // placeholder — see Test Cards
    expMonth = 12
    expYear = 2027
    cvn = "123"
    cardHolderName = "Joe Smith"
}
```

No BNPL, PayPal, or Click to Pay *payment method type* was traced — the demo's `bnpl/`, `paypal/`, and `ctp/` screens
exist as GP API request flows in the sample app's own model layer, not as `com.global.api.paymentMethods` classes;
out of scope for this Section Contract and not emitted here.

---

## Core Transactions

Confirmed in `GooglePayViewModel.kt`, `Secure3DSRepository.kt`, and the reporting/hosted-fields view models. Every
call runs inside `withContext(Dispatchers.IO)` in the demo — never call `.execute(...)` from the main thread.

```kotlin
// Charge (sale — auth + capture in one call), against a config named "default"
val response = card
    .charge(amount)
    .withCurrency("USD")
    .execute("default")

val transactionId = response.transactionId
val responseMessage = response.responseMessage
```

```kotlin
// Charge a tokenized card with 3DS result attached (confirmed shape, Secure3DSRepository.kt)
val tokenizedCard = CreditCardData(cardToken)
tokenizedCard.threeDSecure = authenticationData   // from Secure3dService.getAuthenticationData(), see 3D Secure 2

tokenizedCard
    .charge(amount)
    .withCurrency("USD")
    .execute("default")
```

```kotlin
// Recurring/subsequent charge with stored-credential markers (confirmed shape, Secure3DSRepository.kt)
import com.global.api.entities.StoredCredential
import com.global.api.entities.enums.StoredCredentialInitiator
import com.global.api.entities.enums.StoredCredentialReason
import com.global.api.entities.enums.StoredCredentialSequence
import com.global.api.entities.enums.StoredCredentialType

val storedCredential = StoredCredential().apply {
    initiator = StoredCredentialInitiator.CardHolder
    type = StoredCredentialType.Recurring
    sequence = StoredCredentialSequence.Subsequent
    reason = StoredCredentialReason.Incremental
}

val response = tokenizedCard
    .charge(amount)
    .withCurrency("USD")
    .withStoredCredential(storedCredential)
    .withCardBrandStorage(StoredCredentialInitiator.Merchant, cardBrandTransactionId)
    .execute("default")
```

**Authorize, capture, void, refund, and verify (standalone) are not evidenced client-side in this demo.** Every
transaction call site traced here is `charge(amount)` — a sale, auth+capture in one step. `verify()` is used, but
only internally as part of the 3DS enrollment check (`Secure3DSRepository.checkCardEnrollment`), not exposed as a
standalone "verify a card" screen. This is a not-evidenced finding, not a confirmed-absent one — the underlying Java
library exposes `authorize`, `capture`, `voidTransaction`, `refund`, and standalone `verify` on the same
`CreditCardData`/`Transaction` types this SDK re-exports, so they are very likely reachable with the same method
chains, but no real Android call site was found to confirm the exact chain. If your app needs auth-then-capture,
void, or refund workflows, prefer running them from your backend with a server-side Global Payments SDK, and treat
the app as charge-only.

---

## Address Verification

**Not evidenced in a transaction call site.** `com.global.api.entities.Address` is used in the demo
(`gpapi/utils/Creators.kt`'s `createEmptyAddress()`, and `Secure3DSRepository.kt`'s 3DS `.withAddress(...)` calls for
billing/shipping), but no charge/authorize call site in this repo attaches an `Address` for AVS. Confirmed `Address`
fields from `Creators.kt`: `streetAddress1`, `streetAddress2`, `streetAddress3`, `city`, `postalCode`, `countryCode`,
`state`.

```kotlin
import com.global.api.entities.Address

val address = Address().apply {
    streetAddress1 = "123 Main St."
    city = "Downtown"
    state = "NJ"
    countryCode = "US"
    postalCode = "12345"
}

// Not evidenced: attaching `address` to `.charge(...)` in a real Android call site.
// The underlying Java library supports `.withAddress(address)` on a charge builder;
// treat this as likely-reachable but unverified for Android specifically.
```

---

## Card Collection

Two real, distinct native card-collection paths exist in the shipped `globalpayments-android-sdk/` library module —
plus Google Pay as a third. **Never mint or embed `appId`/`appKey` in the app.** The mobile split below is the
architecture this SDK requires; the demo app itself violates it for local testing (`BuildConfig.APP_ID`/`APP_KEY`) —
do not copy that.

### 1. Backend mints a restricted access token

Plain HTTP contract your backend implements with a server-side Global Payments SDK. Your backend holds the real `appId`/`appKey` and calls
`GpApiService.generateTransactionKey(...)` (confirmed shape, `AccessTokenRepository.kt` — though that file calls it
from the app itself for demo purposes; your backend should be the caller) with `permissions` scoped narrowly, then
returns only the resulting token:

```text
POST https://your-backend.example.com/api/mobile-session
Response 200:
{
  "accessToken": "...",
  "secondsToExpire": 600
}
```

Confirmed real permission strings from the demo's own token-minting call: `"PMT_POST_Create_Single"`,
`"ACC_GET_Single"` (`AccessTokenRepository.kt`).

### 2a. Native form path — `CardFormView`

`globalpayments-android-sdk/.../ui/cardform/CardFormView.kt` is a real, shipped `LinearLayout` widget backed
directly by `CreditCardData` — no WebView, no browser SDK. It also performs live DCC (Dynamic Currency Conversion)
rate lookups as the card number is typed, a GP Ecom-associated feature (`Transaction.dccRateData`).

```kotlin
import com.globalpayments.android.sdk.ui.cardform.CardFormDialogFragment

val cardFormDialog = CardFormDialogFragment.newInstance(configName = "default")
cardFormDialog.onSubmitClicked = { creditCardData ->
    // creditCardData: com.global.api.paymentMethods.CreditCardData, fully populated
    // from the form. Send it to your backend, or tokenize it directly if the app
    // itself holds a short-lived restricted token (step 1 above).
}
cardFormDialog.onCheckDccRate = { creditCardData -> /* trigger a DCC rate lookup transaction */ }
cardFormDialog.show(supportFragmentManager, "card_form")
```

### 2b. WebView hosted-fields path — `HostedFieldsDialog`

`globalpayments-android-sdk/.../ui/hf/HostedFieldsDialog.kt` wraps a `WebView` that loads a local HTML asset running
GlobalPayments.js, initialized with the token from step 1, and returns a card token through a JavaScript bridge —
confirmed real, not a stub:

```kotlin
import com.globalpayments.android.sdk.ui.hf.HostedFieldsDialog

val hostedFieldsDialog = HostedFieldsDialog.newInstance(accessToken = backendIssuedToken)
hostedFieldsDialog.onTokenReceived = { token, cardType ->
    // token starts with "PMT_" — send it to the backend, step 3
}
hostedFieldsDialog.show(supportFragmentManager, "hosted_fields")
```

Internally, `HostedFieldsDialog` calls `initGlobalPayments('$accessToken')` via `webView.evaluateJavascript(...)`
after the local page loads, and exposes a `JSBridge` with `onLoadingStarted()`, `onTokenizationError(tag, error)`,
and `onTokenizationSuccess(token, cardType)` — confirmed verbatim in source.

### 3. The app sends the resulting token to the backend, which charges it

```text
POST https://your-backend.example.com/api/charge
Body: { "paymentToken": "PMT_...", "amount": "19.99", "currency": "USD" }
```

The backend charges the token exactly as it would any other `CreditCardData` with `.token` set — raw card data never
transits or persists on the merchant's own server, and the `appKey` never leaves the backend.

### Google Pay

A genuine Android differentiator, fully covered by the demo (`processpayment/googlepay/`). Google's own
`PaymentsClient` collects the card; the resulting Google Pay token is wrapped in a `CreditCardData` and charged
through the GP API exactly like any other tokenized card, with one modifier flag.

```kotlin
import com.google.android.gms.wallet.PaymentsClient
import com.google.android.gms.wallet.Wallet
import com.google.android.gms.wallet.IsReadyToPayRequest
import com.google.android.gms.wallet.PaymentDataRequest

val paymentsClient: PaymentsClient = Wallet.getPaymentsClient(
    context,
    Wallet.WalletOptions.Builder().setEnvironment(WalletConstants.ENVIRONMENT_TEST).build()
)

// 1. Check availability (JSON request shapes per Google Pay API — see GooglePayUtils.kt for the full builder)
paymentsClient.isReadyToPay(IsReadyToPayRequest.fromJson(isReadyToPayJson))
    .addOnCompleteListener { task -> /* task.getResult(ApiException::class.java) */ }

// 2. Request payment data, then extract the Google-issued token from the result
paymentsClient.loadPaymentData(PaymentDataRequest.fromJson(paymentDataRequestJson))
    .addOnCompleteListener { task ->
        if (task.isSuccessful) {
            val json = JSONObject(task.result.toJson())
            val googlePayToken = json
                .getJSONObject("paymentMethodData")
                .getJSONObject("tokenizationData")
                .getString("token")
            // 3. below
        }
    }
```

```kotlin
// 3. Wrap the Google Pay token in CreditCardData and charge — confirmed shape, GooglePayViewModel.kt
import com.global.api.entities.enums.MobilePaymentMethodType
import com.global.api.entities.enums.TransactionModifier
import com.global.api.paymentMethods.CreditCardData

val card = CreditCardData().apply {
    token = googlePayToken
    mobileType = MobilePaymentMethodType.GOOGLEPAY
}

val response = card
    .charge(amount)
    .withCurrency("USD")
    .withModifier(TransactionModifier.EncryptedMobile)
    .execute("default")
```

`TransactionModifier.EncryptedMobile` on the charge builder is the confirmed real divergence versus a plain hosted-
fields token charge — it tells GP API the token is an encrypted mobile-wallet payload, not a GlobalPayments.js token.

---

## Tokenization

```kotlin
// Tokenize a manually entered card — confirmed shape, Secure3DSRepository.kt
val card = CreditCardData().apply {
    number = "CARD_NUMBER"
    expMonth = expMonth
    expYear = expYear
    cardHolderName = cardHolderName
    isCardPresent = true
}
val token = card.tokenize(true, "default")   // token starts with "PMT_"
```

```kotlin
// Reconstruct a tokenized card for a later charge
val tokenizedCard = CreditCardData(storedToken)
val response = tokenizedCard.charge(amount).withCurrency("USD").execute("default")
```

### Stored payment methods (reporting)

`ReportingService.findStoredPaymentMethodsPaged(page, pageSize)` — confirmed real, `PaymentMethodsListViewModel.kt`:

```kotlin
import com.global.api.services.ReportingService

val storedMethods = ReportingService
    .findStoredPaymentMethodsPaged(1, 25)
    .apply { withStoredPaymentMethodId(id) }
    .execute("default")

for (method in storedMethods.results) {
    // method.id, method.status, method.reference, method.timeCreated
}
```

---

## Recurring Billing

**Charging a `RecurringPaymentMethod` is evidenced; creating/managing the recurring schedule itself is not.**
`Secure3DSRepository.kt` charges a `RecurringPaymentMethod` directly (`paymentMethod.charge(amount).withCurrency(...).execute()`)
with the same `StoredCredential` shape shown in Core Transactions, but no call site in this repo constructs or saves
a `RecurringPaymentMethod`/`Schedule` — that management surface (a `RecurringService`-equivalent) was not exercised
anywhere in the demo. Treat schedule creation as a backend concern — use a server-side Global Payments SDK to
create and manage the schedule, and only charge the resulting `RecurringPaymentMethod` reference from the app if
you must.

---

## 3D Secure 2

**`Secure3dService` drives the network legs (`checkEnrollment`, `initiateAuthentication`,
`getAuthenticationData`), but the device-fingerprint and challenge-presentation legs run through the separate
Netcetera 3DS SDK — not a browser redirect or WebView.** Confirmed end-to-end in
`sample-app/.../repository/Secure3DSRepository.kt`, `sample-app/.../hostedfields/HostedFieldsViewModel.kt`, and the
`merchant3ds` app's `NetceteraHolder.kt`/`ProcessingViewModel.kt`.

### 1. Initialize the Netcetera SDK once (separately from `ServicesContainer`)

```kotlin
import com.netcetera.threeds.sdk.ThreeDS2ServiceInstance
import com.netcetera.threeds.sdk.api.ThreeDS2Service
import com.netcetera.threeds.sdk.api.configparameters.builder.ConfigurationBuilder
import com.netcetera.threeds.sdk.api.configparameters.builder.SchemeConfiguration

val threeDS2Service: ThreeDS2Service = ThreeDS2ServiceInstance.get()

val configParams = ConfigurationBuilder()
    .apiKey(netceteraApiKey)   // separate credential from appId/appKey — from Global Payments support
    .configureScheme(
        SchemeConfiguration.visaSchemeConfiguration()
            .encryptionPublicKeyFromAssetCertificate(context.assets, "acs2022.pem")
            .rootPublicKeyFromAssetCertificate(context.assets, "acs2022.pem")
            .build()
    ).build()

threeDS2Service.initialize(context, configParams, Locale.getDefault().language, uiCustomizationMap)
```

### 2. Check enrollment via `Secure3dService`

```kotlin
import com.global.api.entities.enums.AuthenticationSource
import com.global.api.services.Secure3dService

val enrollmentResult = Secure3dService
    .checkEnrollment(tokenizedCard)
    .withCurrency("USD")
    .withAmount(amount)
    .withAuthenticationSource(AuthenticationSource.MobileSDK)
    .execute("default")
// enrollmentResult.enrolledStatus == "ENROLLED" ?
```

### 3. Create a Netcetera transaction and get its on-device fingerprint params

```kotlin
val netceteraTransaction = threeDS2Service.createTransaction(dsRidForCardBrand, enrollmentResult.messageVersion)
val netceteraParams = netceteraTransaction.authenticationRequestParameters
```

### 4. Initiate authentication, carrying the Netcetera device data

```kotlin
import com.global.api.entities.MobileData
import com.global.api.entities.enums.SdkInterface
import com.global.api.entities.enums.SdkUiType
import com.global.api.utils.JsonDoc

val authResponse = Secure3dService
    .initiateAuthentication(tokenizedCard, enrollmentResult)
    .withAuthenticationSource(AuthenticationSource.MobileSDK)
    .withAmount(amount)
    .withCurrency("USD")
    .withMobileData(MobileData().apply {
        applicationReference = netceteraParams.sdkAppID
        sdkTransReference = netceteraParams.sdkTransactionID
        referenceNumber = netceteraParams.sdkReferenceNumber
        sdkInterface = SdkInterface.Both
        encodedData = netceteraParams.deviceData
        maximumTimeout = 15
        ephemeralPublicKey = JsonDoc.parse(netceteraParams.sdkEphemeralPublicKey)
        setSdkUiTypes(*SdkUiType.entries.toTypedArray())
    })
    .execute("default")

if (authResponse.status != "CHALLENGE_REQUIRED") {
    // skip to step 6 — charge directly, no challenge needed
}
```

### 5. Present the challenge natively via Netcetera (not a WebView, not a redirect)

```kotlin
import com.netcetera.threeds.sdk.api.transaction.challenge.ChallengeParameters
import com.netcetera.threeds.sdk.api.transaction.challenge.ChallengeStatusReceiver

val challengeParams = ChallengeParameters().apply {
    acsRefNumber = authResponse.acsReferenceNumber
    acsSignedContent = authResponse.payerAuthenticationRequest
    acsTransactionID = authResponse.acsTransactionId
    set3DSServerTransactionID(authResponse.providerServerTransRef)
}

netceteraTransaction.doChallenge(activity, challengeParams, object : ChallengeStatusReceiver {
    override fun completed(event: CompletionEvent?) { /* proceed to step 6 */ }
    override fun cancelled() { /* user backed out */ }
    override fun timedout() { /* handle timeout */ }
    override fun protocolError(event: ProtocolErrorEvent?) { /* handle */ }
    override fun runtimeError(event: RuntimeErrorEvent?) { /* handle */ }
}, 5)
```

### 6. Fetch the final authentication result and charge

```kotlin
import com.global.api.entities.enums.Secure3dVersion

val threeDSecureResult = Secure3dService
    .getAuthenticationData()
    .withServerTransactionId(authResponse.serverTransactionId)
    .execute(Secure3dVersion.TWO, "default")

tokenizedCard.threeDSecure = threeDSecureResult
val transaction = tokenizedCard.charge(amount).withCurrency("USD").execute("default")
```

**The `merchant3ds` app runs the same six steps with the network legs (2, 4, 6) proxied through the merchant's own
backend** (`Merchant3DSApi` — a Retrofit interface with `checkEnrollment`, `initiateAuthentication`,
`getAuthenticationData`, and a final `authorizationData` call) instead of calling `Secure3dService` directly from
the app — the more production-realistic pattern, and consistent with never holding `appId`/`appKey` on-device.

**Test cards** — cited to `gpapi-3ds2/tree/main`, gateway-level (not language-specific): see Test Cards below. The
`merchant3ds` app's own README additionally lists `4012001038488884` (Visa, forces a Challenge) and
`4263970000005262` (Visa, Frictionless) at exp `12/2025`, CVN `123`.

---

## Reporting

Confirmed real, `com.global.api.services.ReportingService`, called from `TransactionsListViewModel.kt` and
`PaymentMethodsListViewModel.kt`:

```kotlin
import com.global.api.entities.reporting.SearchCriteria
import com.global.api.services.ReportingService

val report = ReportingService
    .findTransactionsPaged(1, 25)
    .apply {
        where(SearchCriteria.TransactionStatus, transactionStatus)
        where(SearchCriteria.CardBrand, brand)
    }
    .execute("default")

for (summary in report.results) {
    // summary.transactionId, summary.transactionDate, summary.transactionStatus, summary.transactionType
}
```

Also confirmed: `ReportingService.findSettlementTransactionsPaged(page, pageSize)` (deposit/settlement view, same
`SearchCriteria`/`DataServiceCriteria` builder pattern) and `ReportingService.findStoredPaymentMethodsPaged(...)`
(see Tokenization above). Every reporting call in the demo runs from `Dispatchers.IO` inside a `viewModelScope`
coroutine — treat reporting as a background-thread operation like any other SDK call.

**Reporting from a mobile client is usually a backend concern.** The demo exposes it directly from the app for
developer/QA convenience; consider calling `ReportingService` from your backend's own SDK instead of shipping
report-pulling code into a consumer-facing Android app, unless the app itself is an internal/merchant-facing tool.

---

## Error Handling

**No Android-specific exception hierarchy was found.** Every real call site catches a generic `Exception` inside its
coroutine and surfaces `exception.message` to the UI (confirmed pattern across `HostedFieldsViewModel.kt`,
`GooglePayViewModel.kt`, `TransactionsListViewModel.kt`, `CreateAccessTokenViewModel.kt`). Only one specific
exception type is directly confirmed by an Android demo import: `ConfigurationException`
(`com.global.api.entities.exceptions.ConfigurationException`, caught in `GPAPIConfigurationUtils.java` and
`GPEcomConfigurationUtils.java` around `ServicesContainer.configureService(...)`).

```kotlin
import com.global.api.entities.exceptions.ConfigurationException

try {
    ServicesContainer.configureService(gpApiConfig, "default")
} catch (configError: ConfigurationException) {
    // bad or missing config — confirmed real catch site, GPAPIConfigurationUtils.java
}
```

```kotlin
// The general shape used everywhere else in the demo — catch broadly, surface exception.message
viewModelScope.launch(Dispatchers.IO) {
    try {
        val response = card.charge(amount).withCurrency("USD").execute("default")
        // success
    } catch (exception: Exception) {
        // exception.message shown directly to the UI in every real call site
    }
}
```

Because `com.global.api.*` here is the exact same underlying library used for all transaction, config, and
reporting logic (an `api()` dependency, not a fork), a fuller exception hierarchy — `ApiException`,
`BuilderException`, `GatewayException`, `GatewayTimeoutException`, `UnsupportedTransactionException` — is very
likely reachable unchanged on Android. But only `ConfigurationException` was independently confirmed via a real
Android import in this task's evidence; treat the rest as likely-applicable rather than independently verified
here.

---

## Test Cards

**Do not hardcode real card numbers in generated integration code.** Use placeholders and point users to
https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md. The tables below are
published directly in the demo repo's own `README.md` and `PaymentCardModel.java` — sandbox test data, not
cardholder data.

### General GP API / GP Ecom test cards (`README.md`, `sample-app` root)

| Brand | Number | Exp Month | Exp Year | CVN |
|---|---|---|---|---|
| Visa | `4263970000005262` | 12 | 2025 | 123 |
| MasterCard | `2223000010005780` | 12 | 2019 | 900 |
| MasterCard | `5425230000004415` | 12 | 2025 | 123 |
| Discover | `6011000000000087` | 12 | 2025 | 123 |
| Amex | `374101000000608` | 12 | 2025 | 1234 |
| JCB | `3566000000000000` | 12 | 2025 | 123 |
| Diners Club | `36256000000725` | 12 | 2025 | 123 |

### `PaymentCardModel.java` enum (`globalpayments-android-sdk/` library module)

| Name | Number | Exp Month | Exp Year | CVN |
|---|---|---|---|---|
| `VISA_SUCCESSFUL` | `4263970000005262` | 5 | 2025 | 123 |
| `MASTERCARD_SUCCESSFUL` | `5425230000004415` | 5 | 2025 | 852 |
| `AMEX_SUCCESSFUL` | `374101000000608` | 5 | 2025 | 8522 |
| `VISA_DECLINED` | `4000120000001154` | 5 | 2025 | 852 |
| `MASTERCARD_DECLINED` | `5114610000004778` | 5 | 2025 | 852 |
| `AMEX_DECLINED` | `376525000000010` | 5 | 2025 | 8522 |

### Netcetera 3DS challenge cards (`merchant3ds/README.md`)

| Brand | Number | Exp Month | Exp Year | CVN | Type |
|---|---|---|---|---|---|
| Visa | `4012001038488884` | 12 | 2025 | 123 | Forces a Challenge |
| Visa | `4263970000005262` | 12 | 2025 | 123 | Frictionless |

Source: `globalpayments/android-demo-app` @ `main`, confirmed 2026-08-06.
