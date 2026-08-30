# gp-android-sdk — Verification Log

No public source repo. Evidence basis:
1. https://developer.globalpayments.com/docs/integration-options/sdk/android.md
2. https://github.com/globalpayments/android-demo-app @ main — a monorepo that, unusually, contains the actual
   `globalpayments-android-sdk/` library module (the source published to Maven Central) alongside `sample-app/` and
   `merchant3ds/`. All 292 `.kt`/`.java` files in the tree were fetched and searched; specific files were read in
   full where cited below.
3. Maven Central (`search.maven.org`), queried directly (see Group-id finding below).

**This is still the weakest evidence base of the eight GP SDK skills.** There is no dedicated SDK repo, no
`globalpayments-samples` entry confirmed for Android, and the underlying Java library dependency
(`com.heartlandpaymentsystems:globalpayments-sdk`) that this library wraps was cross-referenced against external
documentation for exception-hierarchy context only — not independently re-verified from its own source in this
task.

Verified: 2026-08-06

---

## Group-id finding (Step 2, verbatim)

```bash
curl -s "https://search.maven.org/solrsearch/select?q=a:globalpayments-android-sdk&rows=20&wt=json" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('numFound:', data['response']['numFound'])
for d in data['response']['docs']:
    print(d.get('g'), d.get('a'), d.get('latestVersion'))
"
```
Output:
```
numFound: 1
com.heartlandpaymentsystems globalpayments-android-sdk 1.1.36
```

Follow-up query, group `com.globalpayments.android` (the coordinate this task's brief stated as "confirmed"):
```bash
curl -s "https://search.maven.org/solrsearch/select?q=g:com.globalpayments.android&rows=20&wt=json" | python3 -c "..."
```
Output:
```
numFound: 0
```

**This directly contradicts the brief's stated anchor.** `com.globalpayments.android` does not exist on Maven
Central — zero published artifacts under that group, at any version. The only artifact named
`globalpayments-android-sdk` on Maven Central is `com.heartlandpaymentsystems:globalpayments-android-sdk`, currently
at `1.1.36`.

Three further, independent sources in the demo repo itself corroborate `com.heartlandpaymentsystems` as the real,
currently-used group id — this is not merely "the README says so":

1. **`build-logic/convention/src/main/kotlin/PublishConventionPlugin.kt`** — the actual Gradle plugin this repo uses
   to publish the SDK to Maven Central. Hardcodes, verbatim:
   ```kotlin
   val sdkGroupId = "com.heartlandpaymentsystems"
   val sdkArtifactId = "globalpayments-android-sdk"
   val sdkVersion: String = libs.findVersion("globalPayments-android").get().toString()
   ```
   with a `repositories { maven { url = URI.create("https://oss.sonatype.org/service/local/staging/deploy/maven2/") } }`
   block — the standard Sonatype OSSRH staging URL that publishes to Maven Central.
2. **`gradle/libs.versions.toml`** pins `globalPayments-android = "1.1.36"` — the exact version
   `PublishConventionPlugin.kt` reads via `libs.findVersion(...)`, and the exact version Maven Central reports as
   `latestVersion`. All three numbers agree.
3. **`README.md`** (repo root): `implementation 'com.heartlandpaymentsystems:globalpayments-android-sdk:1.0'` —
   confirms the group id independently, though its version (`1.0`) is stale against the real current release
   (`1.1.36`).

The **portal page** (`developer.globalpayments.com/docs/integration-options/sdk/android.md`) is the one source that
disagrees — it states group `com.globalpayments.android`, version `1.0`, via a `jcenter()` repository declaration.
JCenter was deprecated in 2021 and fully shut down; that installation instruction cannot be followed today, and the
group id it names does not exist on Maven Central. **Verdict: the portal page is stale on both the repository
(dead jcenter) and the group id. Use `com.heartlandpaymentsystems:globalpayments-android-sdk:1.1.36`, confirmed
live on Maven Central and matching the demo repo's own publish configuration.**

This is a correction to the brief's "Verified anchors" section, not merely a restatement of it — the brief's stated
coordinate (`com.globalpayments.android:...:1.0`) does not resolve anywhere and was not used in this skill.

---

## Symbols traced

| Symbol | Source path |
|---|---|
| `CardFormView` (fields/callbacks: `onSubmitClicked`, `onCheckDccRate`, `onDccRateSelected`, `onDccRateReceived(Transaction?)`; backed by `com.global.api.paymentMethods.CreditCardData`) | `globalpayments-android-sdk/src/main/java/com/globalpayments/android/sdk/ui/cardform/CardFormView.kt` |
| `CardFormDialogFragment` (`newInstance(configName)`, `onSubmitClicked`, `onCheckDccRate`, `onDccRateSelected`, `onDccRateReceived`) | `globalpayments-android-sdk/.../ui/cardform/CardFormDialogFragment.kt` |
| `HostedFieldsDialog` (`newInstance(accessToken)`, `onTokenReceived: (String, String) -> Unit`; internal `JSBridge.onLoadingStarted/onTokenizationError/onTokenizationSuccess`; calls `initGlobalPayments('$accessToken')` via `evaluateJavascript`) | `globalpayments-android-sdk/.../ui/hf/HostedFieldsDialog.kt` |
| `PaymentCardModel` enum (`VISA_SUCCESSFUL`, `MASTERCARD_SUCCESSFUL`, `AMEX_SUCCESSFUL`, `VISA_DECLINED`, `MASTERCARD_DECLINED`, `AMEX_DECLINED`, each with number/expMonth/expYear/cvn) | `globalpayments-android-sdk/.../model/PaymentCardModel.java` |
| `GpApiConfig` (setters used: `setAccessTokenInfo`, `setAppId`, `setAppKey`, `setChannel`, `setDynamicHeaders`, `setCountry`, `setChallengeNotificationUrl`, `setMethodNotificationUrl`, `setMerchantContactUrl`, `setServiceUrl`, `setStatusUrl`, `setSecondsToExpire`, `setIntervalToExpire`, `setEnvironment`, `setRequestLogger`, `setMerchantId`, `setAndroid(true)` — Android-specific setter) | `sample-app/.../utils/configuration/GPAPIConfigurationUtils.java` (class itself: `com.global.api.serviceConfigs.GpApiConfig`, from the underlying Java library) |
| `GpEcomConfig` (setters used: `setAccountId`, `setChannel`, `setMerchantId`, `setRebatePassword`, `setRefundPassword`, `setSharedSecret`, `setShaHashType`, `setRequestLogger`) | `sample-app/.../utils/configuration/GPEcomConfigurationUtils.java` (class itself: `com.global.api.serviceConfigs.GpEcomConfig`) |
| `ServicesContainer.configureService(config, configName)` throwing `ConfigurationException` | `GPAPIConfigurationUtils.java`, `GPEcomConfigurationUtils.java` |
| `GpApiService.generateTransactionKey(GpApiConfig)` → `AccessTokenInfo` | `sample-app/.../repository/AccessTokenRepository.kt`, `sample-app/.../gpapi/screens/accesstoken/CreateAccessTokenViewModel.kt` |
| `AccessTokenInfo` (`.token`) | `com.global.api.entities.gpApi.entities.AccessTokenInfo`, constructed in `CreateAccessTokenViewModel.kt`, `GPAPIConfigurationUtils.java` |
| `CreditCardData` (`.number`, `.expMonth`, `.expYear`, `.cvn`, `.cardHolderName`, `.isCardPresent`, `.token`, `.mobileType`, `.threeDSecure`; `.tokenize(Boolean, String)`, `.charge(BigDecimal)`, `.verify()`) | `CardFormView.kt`, `Secure3DSRepository.kt`, `GooglePayViewModel.kt` |
| `EBTCardData` (`.number`, `.expMonth`, `.expYear`, `.pinBlock`, `.cardHolderName`, `.isCardPresent`) | `sample-app/.../processpayment/ebt/EbtViewModel.kt` |
| `eCheck` (ACH payment method, constructed with no-arg constructor) | `sample-app/.../processpayment/ach/AchViewModel.kt` |
| `RecurringPaymentMethod` (`.charge(amount)`, chargeable with `StoredCredential`) | `Secure3DSRepository.kt` |
| `MobilePaymentMethodType.GOOGLEPAY`, `TransactionModifier.EncryptedMobile` | `sample-app/.../processpayment/googlepay/GooglePayViewModel.kt` |
| `Secure3dService.checkEnrollment(paymentMethod)`, `.initiateAuthentication(paymentMethod, secureEcom)`, `.getAuthenticationData()`, imported from `com.global.api.services.Secure3dService` | `sample-app/.../repository/Secure3DSRepository.kt` |
| `AuthenticationSource.MobileSDK` | `Secure3DSRepository.kt` |
| `MobileData` (`.applicationReference`, `.sdkTransReference`, `.referenceNumber`, `.sdkInterface`, `.encodedData`, `.maximumTimeout`, `.ephemeralPublicKey`, `.setSdkUiTypes(...)`) | `Secure3DSRepository.kt` |
| `Secure3dVersion.TWO` (passed to `getAuthenticationData().execute(version, configName)`) | `Secure3DSRepository.kt` |
| Netcetera `ThreeDS2ServiceInstance.get()` → `ThreeDS2Service`; `.initialize(context, ConfigParameters, locale, uiCustomizationMap)`; `.createTransaction(dsRid, messageVersion)` | `merchant3ds/.../netcetera/NetceteraHolder.kt` |
| Netcetera `ConfigurationBuilder().apiKey(...).configureScheme(SchemeConfiguration.visaSchemeConfiguration()...).build()` | `NetceteraHolder.kt` |
| Netcetera `Transaction.authenticationRequestParameters`; `.doChallenge(activity, ChallengeParameters, ChallengeStatusReceiver, timeoutMinutes)` | `NetceteraHolder.kt` (wrapped in a `startChallenge` extension function in the same file) |
| `ChallengeParameters` (`.acsRefNumber`, `.acsSignedContent`, `.acsTransactionID`, `.set3DSServerTransactionID(...)`) | `NetceteraHolder.kt`, `Secure3DSRepository`-adjacent call site in `HostedFieldsViewModel.kt` |
| `ChallengeStatusReceiver` (`completed`, `cancelled`, `timedout`, `protocolError`, `runtimeError`) | `NetceteraHolder.kt` |
| `ReportingService.findTransactionsPaged(page, pageSize)`, `.findSettlementTransactionsPaged(page, pageSize)`, `.findStoredPaymentMethodsPaged(page, pageSize)` — each with `.where(SearchCriteria/DataServiceCriteria, value)` and `.execute(configName)` | `sample-app/.../reporting/transactions/list/TransactionsListViewModel.kt`, `.../reporting/paymentmethods/list/PaymentMethodsListViewModel.kt` |
| `Address` (`.streetAddress1/2/3`, `.city`, `.postalCode`, `.countryCode`, `.state`) | `sample-app/.../gpapi/utils/Creators.kt` |
| `ConfigurationException` (`com.global.api.entities.exceptions.ConfigurationException`) | `GPAPIConfigurationUtils.java`, `GPEcomConfigurationUtils.java` |
| `StoredCredential` (`.initiator`, `.type`, `.sequence`, `.reason`); `StoredCredentialInitiator.CardHolder`/`.Merchant`; `StoredCredentialType.Recurring`; `StoredCredentialSequence.Subsequent`; `StoredCredentialReason.Incremental` | `Secure3DSRepository.kt` |
| `Channel.Ecom`, `Channel.CardNotPresent` | `GPEcomConfiguration.kt`, `GPAPIConfiguration.kt` |
| `GPEcomConfiguration`/`GPEcomConfigurationUtils` real fields: `accountId`, `merchantId`, `rebatePassword`, `refundPassword`, `sharedSecret`, `channel`, `challengeNotificationUrl`, `merchantContactUrl`, `methodNotificationUrl`, `secure3dVersion`, `shaHashType`, `apiKey` | `sample-app/.../utils/configuration/GPEcomConfiguration.kt` |
| `Merchant3DSApi` (Retrofit interface: `checkEnrollment`, `initiateAuthentication`, `getAuthenticationData`, `authorizationData`) — the backend-proxied variant of the 3DS flow | `merchant3ds/.../networking/Merchant3DSApi.kt` (interface referenced from `ProcessingViewModel.kt`; body not read in full) |

---

## Omitted

| Item | Reason |
|---|---|
| Standalone `authorize`, `capture`, `voidTransaction`, `refund`, standalone `verify` call chains | Not evidenced in any Android call site — every real transaction call in this repo is `charge(amount)`. The underlying Java library exposes all of these on the same types, so they are likely reachable, but no confirmed Android call site exists; documented as a not-evidenced gap in REFERENCE.md's Core Transactions section, not asserted as either present or absent. |
| Address attached to a charge builder (`.withAddress(...)` on `.charge(...)`) | `Address` construction is confirmed (`Creators.kt`) and `.withAddress(...)` is confirmed on 3DS builders (`Secure3DSRepository.kt`), but no transaction call site chains `.withAddress(...)` onto `.charge(...)` specifically. Documented as likely-reachable-but-unverified in REFERENCE.md. |
| `RecurringPaymentMethod`/`Schedule` creation and management (`RecurringService` equivalent) | Not evidenced — only *charging* an already-constructed `RecurringPaymentMethod` was found (`Secure3DSRepository.kt`). No call site builds or persists one. |
| Portico gateway (`PorticoConfig` or equivalent) | Not evidenced — zero case-insensitive hits for "portico" across all 292 `.kt`/`.java` files in the tree (see Portico search below). Not asserted as confirmed-absent, since the underlying Java library dependency's own source was out of scope. |
| GP Ecom / Realex-branded connector class name | Not searched directly as a separate item — GP Ecom is confirmed present and working via `GpEcomConfig`/`GpEcomConfigurationUtils`, so no absence claim was needed here. |
| Full field list of `GpApiConfig` beyond what `GPAPIConfigurationUtils.java` sets | Only the setters actually called in that one file were read; the class's full field inventory was not re-verified independently for this task. |
| Javadoc artifact resolvability | `withJavadocJar()` is declared in `globalpayments-android-sdk/build.gradle.kts`'s publishing block, confirming a javadoc jar is *configured* to publish, but no direct Maven Central query for the javadoc classifier was run — not claimed as confirmed-resolvable. |
| BNPL, PayPal, Click to Pay, Pay by Link, Unified Payments API screens | Real demo screens exist (`bnpl/`, `paypal/`, `ctp/`, `paybylink/`, `unifiedpaymentsapi/`) but fall outside the Section Contract's eleven headings; not read in full or emitted into `REFERENCE.md`. Mentioned only in `../SKILL.md`'s Sample Repos table as evidence of what the sample app covers. |

---

## Portico search (Step 6, verbatim)

```bash
# All 292 .kt/.java files in the tree fetched locally, then:
grep -lriE 'portico' android-src/
grep -lriE 'realex' android-src/
grep -lriE 'gpecom' android-src/ | wc -l
grep -lE 'sharedSecret|SharedSecret' android-src/
```
Output:
```
portico: (no matches)
realex: sample-app_..._gpecom3ds_GPEcom3DSViewModel.kt   (one hit)
gpecom: 14 files
sharedSecret: 6 files (ConfigViewModel.kt, GPEcomConfiguration.kt, ConfigScreenModel.kt,
               GlobalpaymentsSampleAppConfig.kt, ConfigScreen.kt, GPEcomConfigurationUtils.java)
```

The single `realex` hit was read in context: it is a customer-name string generator
(`"%s-Realex"`/`"Realex Payments"` used as fake test-customer metadata in `GPEcom3DSViewModel.kt`), not a gateway or
connector reference — no `RealexConnector` or similarly-named class exists anywhere in this tree. Also confirmed:
GitHub's code-search API requires authentication and could not be used unauthenticated (`401 Requires
authentication`); the full-tree local grep above was used instead as a complete substitute, since all 292
`.kt`/`.java` files were fetched.

**Finding: Portico — not evidenced in the demo app or the portal page.** This is a "not evidenced" finding, not a
"confirmed absent" one: the search covers the entire `android-demo-app` monorepo (including the shipped
`globalpayments-android-sdk/` library module itself), but the underlying Java library dependency
(`com.heartlandpaymentsystems:globalpayments-sdk:14.0.0`, pulled in via `api(libs.globalPayments.java)`) is a
separate artifact whose own source was not read for this task — it could in principle expose a Portico connector
that nothing in this Android repo happens to call. Recommend treating Portico as unavailable on Android until
confirmed otherwise.

**Finding: GP Ecom — confirmed supported**, not merely not-evidenced-absent. This is a stronger claim than the
Portico finding because real, wired configuration code was found and read in full: `GpEcomConfigurationUtils.java`
constructs a real `com.global.api.serviceConfigs.GpEcomConfig` and calls `ServicesContainer.configureService(...)`
with it (not a stub, not dead code). Five dedicated
demo screens exist (`GPEcom3DSScreen.kt`, `GPEcom3DSScreenModel.kt`, `GPEcom3DSViewModel.kt`,
`GPEcomConfiguration.kt`, `GPEcomConfigurationUtils.java`), and the repo's own root `README.md` documents a
developer-facing toggle: `"If you want to use the sample-app with GP-Ecom and Netcetera 3DS SDK make sure to set the
useEcom=true in the configuration.properties and set the appropriate fields for GP-Ecom."`

---

## Portal page vs. repo source (Step-adjacent cross-check)

| Claim | Portal (`.../sdk/android.md`) | Repo source | Verdict |
|---|---|---|---|
| Repository | `jcenter()` | `mavenCentral()` (README, `settings.gradle.kts`) | Portal is stale — jcenter shut down 2021. Use `mavenCentral()`. |
| Group id | `com.globalpayments.android` | `com.heartlandpaymentsystems` (README, `PublishConventionPlugin.kt`, Maven Central) | Portal is wrong, not just stale — that group has zero Maven Central artifacts. |
| Version | `1.0` | `1.1.36` (`libs.versions.toml`, Maven Central `latestVersion`) | Portal and README both show `1.0`; the real current release is `1.1.36`. Use `1.1.36`. |
| Min SDK | API 21 (Lollipop) | API 21, confirmed in both demo README Requirements sections | Matches. |
| Android Studio | 4.2+ | Not independently stated in repo source | Not re-verified; portal claim carried forward as unconfirmed-but-plausible, per the brief's own "Verified anchors." |
| Java version | 1.8 | 1.8, confirmed in both demo README Requirements sections | Matches — this is the language-level floor for consuming code; the repo's own build toolchain (AGP 8.5.2, JVM target 17 for build-logic) is separately newer than that floor. |
| Gateway support | Vague — "direct connections to the Gateway and also for Ecommerce" | GP API + GP Ecom confirmed; Portico not evidenced | Portal is directionally consistent (mentions "Ecommerce," i.e. GP Ecom) but not specific enough to confirm or deny Portico either way. |
| 3DS | Not mentioned | Netcetera SDK + `Secure3dService`, confirmed end-to-end | Portal page is silent; no contradiction, just no coverage. |

---

## Known Coverage Gaps

Recorded 2026-08-06 by a surface survey of the `android-demo-app` monorepo tree. **None found** — every substantial area of the tree maps to a section in this skill or to a row in the Scope table.

Caveat on the strength of that result: this SDK's own source is thin because much behaviour comes from the underlying Java SDK dependency, whose tree was out of scope. A capability could be reachable from an Android app without appearing in this repo's file paths. Treat this as *no gaps found in the surveyed tree*, not as *no gaps exist*.
