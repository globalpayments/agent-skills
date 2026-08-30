---
name: gp-android-sdk
description: |
  Expert guide for consuming the GlobalPayments Android SDK, grounded in its real Kotlin/Java source and samples. Confirmed Maven artifact: `com.heartlandpaymentsystems:globalpayments-android-sdk:1.1.36`. GP Ecom is supported; Portico is not evidenced. Never embed appId/appKey in an app. Trigger phrases: "gp-android-sdk", "integrate the Android SDK", "GlobalPayments Android SDK", "charge a card in Kotlin", "Android payment integration", "GlobalPayments in an Android app"
---

# GP-ANDROID-SDK

Expert consumer of the GlobalPayments Android SDK (Kotlin/Java, artifact `com.heartlandpaymentsystems:globalpayments-android-sdk`).
Produce correct, idiomatic Kotlin integration code grounded in the `android-demo-app` monorepo's actual source —
never transliterated from another SDK's code.

## Scope

This is a **client-side** SDK distributed as a Maven artifact, with **no public source repository** of its own —
`github.com/globalpayments/android-sdk` redirects to `globalpayments/android-demo-app`.
That repo is, unusually, a monorepo containing the actual `globalpayments-android-sdk/` library module alongside two
sample apps, so more real library source was readable here than expected — but it is still not the SDK's own
dedicated repo, and everything below is bounded by what that one tree contains.

| Capability | Status |
|---|---|
| GP API gateway | Supported |
| GP Ecom gateway | Supported — `GpEcomConfig`, dedicated demo screens (`gpecom3ds/`) |
| Portico gateway | **Not evidenced** in this tree — zero hits, case-insensitive, across all 292 Kotlin/Java files |
| Card collection | Native SDK (`CreditCardData`, `CardFormView`) **and** a WebView-hosted GlobalPayments.js dialog (`HostedFieldsDialog`) — two real, distinct paths |
| Google Pay | Supported |
| Transaction reporting | Supported |
| Stored payments / tokenization | Supported |
| 3D Secure 2 | `Secure3dService` for the network legs, plus the **Netcetera 3DS SDK** for on-device fingerprinting and native challenge presentation — not a straight swap of one for the other |
| Terminal / POS device integration | **Not evidenced** — zero paths match `/Terminals/`, `DeviceService` or `UpaController` across the monorepo (full-tree path search, 2026-08-06). Recorded as not-evidenced rather than confirmed-absent, since the underlying Java SDK dependency's own source was out of scope for this skill. For semi-integrated POS device control, use the PHP, .NET, Java, Node.js or Go SDK. |

**Evidence basis:** everything in this skill is grounded in the developer portal Android page, the
`globalpayments/android-demo-app` sources (including its `globalpayments-android-sdk/` library module), and the
published Maven artifact. Symbols that could not be confirmed from one of those three are omitted — see
`references/VERIFICATION.md`. When in doubt, read the demo app.

**Artifact coordinate — evidence overrides the portal page.** The developer portal page states
`com.globalpayments.android:globalpayments-android-sdk:1.0` via `jcenter()` — jcenter has been shut down since 2021
and that instruction cannot be followed today. Maven Central has zero results for group `com.globalpayments.android`.
The demo repo's own publish script (`PublishConventionPlugin.kt`) hardcodes `groupId = "com.heartlandpaymentsystems"`
and the repo's own `libs.versions.toml` pins the SDK at `1.1.36` — both confirmed live on Maven Central. Use
`com.heartlandpaymentsystems:globalpayments-android-sdk:1.1.36`. See `references/VERIFICATION.md` for the full query output.

**Never ship app credentials.** Use the mobile split: your backend mints a short-lived restricted access token, the
app tokenizes the card, your backend charges the `PMT_` reference. **The demo app itself does not do this** — it
calls `GpApiService.generateTransactionKey(...)` directly on-device with `appId`/`appKey` read from `BuildConfig`,
for local testing convenience. Do not copy that pattern into real integration code.

---

## Source Hierarchy (always follow this order)

1. **Developer portal** — `https://developer.globalpayments.com/docs/integration-options/sdk/android.md`. States
   Android SDK 21+, Android Studio 4.2+, Java 1.8. **Caveat:** its install snippet uses a defunct `jcenter()`
   repository and a stale, non-resolving group id — do not use it. Conceptual background only.
2. **SDK source** — no dedicated SDK repo exists. `github.com/globalpayments/android-sdk` redirects (301) to
   `github.com/globalpayments/android-demo-app`, branch `main`, Kotlin. That monorepo's `globalpayments-android-sdk/`
   module **is** the real published library source — verify symbols there first, then in `sample-app/` and
   `merchant3ds/` for call-site usage.
3. **`globalpayments-samples` org** — not checked for this task; no `android` topic/directory is known to exist. Use
   the demo app's own `sample-app/` and `merchant3ds/` as the sample repos.
4. **Published Maven artifact** — `com.heartlandpaymentsystems:globalpayments-android-sdk` on Maven Central. No
   javadoc jar confirmed resolvable independently, though `withJavadocJar()` exists in the publish config.

If you cannot confirm a symbol in `globalpayments-android-sdk/` or a real call site in `sample-app/`/`merchant3ds/`,
say so — never guess, and never port a class name from another SDK.

---

## Developer Portal Pages

Conceptual reference only (general flow semantics) — use the demo app for real Kotlin/Java call shapes.

| Topic | Portal Page |
|---|---|
| Android SDK overview | `https://developer.globalpayments.com/docs/integration-options/sdk/android.md` |
| Capture / Refund / Void | `.../payments/manage-payments/{capture,refund,reverse}-guide.md` |
| Recurring / 3D Secure | `.../payments/recurring/recurring-payments-guide.md`, `.../risk-management/3D-secure/browser-authentication-guide.md` (server-side concepts; the Android challenge itself is native — see 3D Secure 2 in `references/REFERENCE.md`) |
| Reporting / Testing | `.../reporting/real-time-reporting-guide.md`, `.../getting-started/testing.md` |

All prefixed `https://developer.globalpayments.com/gh-assets/markdown/docs/`.

---

## Sample Repos

**No `globalpayments-samples` entry confirmed for Android.** The only real, verified samples are inside the demo
monorepo itself:

| Operation | Source |
|---|---|
| GP API (access token, hosted fields, Google Pay, ACH, EBT, BNPL, Click to Pay, reporting) | `https://github.com/globalpayments/android-demo-app/tree/main/sample-app` |
| GP Ecom + native card form + DCC | `https://github.com/globalpayments/android-demo-app/tree/main/sample-app` (`gpecom3ds/`, `ui/cardform/`) |
| Netcetera 3DS challenge against a real backend | `https://github.com/globalpayments/android-demo-app/tree/main/merchant3ds` |
| The SDK library itself | `https://github.com/globalpayments/android-demo-app/tree/main/globalpayments-android-sdk` |
| 3DS backend reference (paired with the merchant3ds app) | `https://github.com/globalpayments/java-sdk/tree/master/examples/iOS-Hybrid-App-Java-Server` — despite the `iOS-` name this is a plain Java server, and the backend half of a 3DS flow is platform-agnostic; it is the correct reference for an Android merchant backend too |

---

## Quick Reference

### Import Root
```kotlin
import com.globalpayments.android.sdk.ui.cardform.CardFormView   // native card entry (library module)
import com.globalpayments.android.sdk.ui.hf.HostedFieldsDialog   // WebView hosted fields (library module)
import com.global.api.paymentMethods.CreditCardData              // underlying Java library, api() dependency
import com.global.api.serviceConfigs.GpApiConfig
import com.global.api.services.GpApiService
```

| Type | Source path |
|---|---|
| `CardFormView` / `CardFormDialogFragment` | `globalpayments-android-sdk/.../ui/cardform/CardFormView.kt`, `CardFormDialogFragment.kt` |
| `HostedFieldsDialog` | `globalpayments-android-sdk/.../ui/hf/HostedFieldsDialog.kt` |
| `GpApiConfig` / `GpEcomConfig` | `com.global.api.serviceConfigs.*` — from the underlying Java library, pulled in as an `api()` dependency |
| `GpApiService.generateTransactionKey(...)` | `com.global.api.services.GpApiService` — called from `AccessTokenRepository.kt` |
| `Secure3dService` | `com.global.api.services.Secure3dService` — called from `Secure3DSRepository.kt` |
| Netcetera `ThreeDS2Service` / `Transaction` | `com.netcetera.threeds.sdk.*` — a separate SDK, not part of this artifact; see `merchant3ds/.../netcetera/NetceteraHolder.kt` |
| `ReportingService` | `com.global.api.services.ReportingService` — called from `TransactionsListViewModel.kt`, `PaymentMethodsListViewModel.kt` |

> **Real divergence — this artifact is a thin UI layer glued to a separate transaction library.** The
> `globalpayments-android-sdk` Maven artifact itself is a thin Android UI layer (native card form, WebView
> hosted-fields dialog, Click to Pay, DCC view). All transaction, config, and reporting logic is the underlying
> Java library (`com.heartlandpaymentsystems:globalpayments-sdk`, pinned to `14.0.0` in `libs.versions.toml`),
> pulled in as an `api()` dependency and imported directly as `com.global.api.*`.
> Confirmed: `globalpayments-android-sdk/build.gradle.kts`.

---

## Code Reference

All quick-copy Kotlin snippets (installation, gateway config, payment methods, core transactions, address, the
mobile split for card collection, Google Pay, tokenization, recurring, 3DS2, reporting, error handling) are in
**[REFERENCE.md](./references/REFERENCE.md)**. Verify any class or method against `globalpayments-android-sdk/` or a real
call site in `sample-app/`/`merchant3ds/` before emitting it.

---

## Test Cards

**Never include real or hardcoded card numbers in generated integration code.** Use placeholders and point to:

👉 https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

Sandbox numbers from the demo app's own `README.md` and `PaymentCardModel.java` enum are listed in `references/REFERENCE.md`'s
Test Cards section — published test data, not cardholder data.

---

## Execution Rules

1. **Never embed `appId`/`appKey` in app code** — not in `gradle.properties`, `BuildConfig`, or a constant. The demo
   does this for its own local testing (`GPAPIConfiguration.fromBuildConfig()`); never replicate it. The backend
   mints a short-lived restricted token via `GpApiService.generateTransactionKey(...)` and hands the app only the
   token — see Card Collection in `references/REFERENCE.md`.
2. **Network calls never run on the main thread.** Every real call site wraps SDK calls in
   `withContext(Dispatchers.IO)` inside `viewModelScope.launch` — match that shape.
3. **3DS challenges are presented by the Netcetera SDK**, which needs its own `ThreeDS2Service.initialize(...)` call, separate from `ServicesContainer.configureService(...)` and done once, not per-transaction.
4. **Min SDK 21** (Android 5.0, Lollipop), confirmed on the portal page and in both demo README's Requirements sections.
5. **Default to the sandbox/TEST environment.** Every generated `GpApiConfig`/`GpEcomConfig` should target `Environment.TEST`; flag production differences in prose.
6. **If a symbol is not in `globalpayments-android-sdk/` or a real demo call site, do not emit it** — point the reader at the demo app instead of guessing.
7. **Portico is not evidenced in this tree.** Say plainly it wasn't found in the SDK's source or the portal page, and point the user at a server-side Global Payments SDK if they need it.
