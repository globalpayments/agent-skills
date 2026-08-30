---
name: gp-ios-sdk
description: |
  Expert guide for consuming the GlobalPayments iOS SDK (globalpayments/ios-sdk, import root `import GlobalPayments_iOS_SDK`, pod `GlobalPayments-iOS-SDK`).
  Client-side SDK — runs inside the merchant's app, not on a server. Supports GP API and Portico with full 3D Secure 2; GP Ecom has no working connector
  (confirmed by source and enum search, 2026-08-06). Every transaction is asynchronous with a `(Transaction?, Error?) -> Void` completion handler — never
  write a blocking sample. Teaches the mobile split: never embed an `appKey` in app code, since anything shipped in an `.ipa` is extractable. Grounds all
  code in real SDK source and its own test suite. Trigger phrases: "gp-ios-sdk", "integrate the iOS SDK", "GlobalPayments iOS SDK", "charge a card in
  Swift", "iOS payment integration", "GlobalPayments in an iPhone app"
---

# GP-IOS-SDK

Expert consumer of `globalpayments/ios-sdk` (Swift, pod `GlobalPayments-iOS-SDK`, import root `import GlobalPayments_iOS_SDK`). Produce correct, idiomatic
Swift code grounded in actual SDK source — never guessed or invented.

## Scope

This is a **client-side** SDK. It runs in your app, on the user's device.

| Capability | Status |
|---|---|
| GP API gateway | Supported |
| Portico gateway | Supported |
| GP Ecom gateway | **Not supported** — `RealexConnector.swift` is an empty-method stub; no `RealexConfig`/`GpEcomConfig` type exists; `GatewayProvider` has only `.gpAPI`/`.portico` cases; nothing instantiates it. Dead code. |
| 3D Secure 2 | Supported — `Services/Secure3dService.swift`; challenge is an in-app web view, not a server redirect |
| Card collection | Native SDK (`CreditCardData`), not GlobalPayments.js hosted fields — no browser DOM on iOS |
| Terminal / POS device integration | **Not supported** — no terminal tree in the repo. Zero paths match `/Terminals/`, `DeviceService` or `UpaController` (confirmed by full-tree path search, 2026-08-06). There is no `ConnectionConfig`, no `IDeviceInterface`, and no device controller of any family. For semi-integrated POS device control, use the PHP, .NET, Java, Node.js or Go SDK. |

**Never ship app credentials.** An `appKey` embedded in an iOS binary is extractable. Use the mobile split instead: your backend mints a short-lived
restricted access token, the app tokenizes the card with it, and your backend charges the resulting `PMT_` reference.

---

## Source Hierarchy (always follow this order)

1. **Developer portal** — flow semantics (capture, void, refund). **Caveat:** states pod `~> 1.0`, iOS 9.0+, Xcode 11+, Swift 5.0+ — `~> 1.0` is stale
   (podspec is `3.3.2`); `references/REFERENCE.md` uses the repo's own podspec/`Package.swift` instead.
2. **SDK source on GitHub** — verify every class/method/field against **https://github.com/globalpayments/ios-sdk** (`GlobalPayments-iOS-SDK/Classes/`,
   branch `master`). Never guess.
3. **Sample implementations** — `globalpayments-samples` has **no `ios` directory in any repo** (confirmed 2026-08-06). Use the SDK's own `Example/` app,
   plus the server-side samples your backend needs.
4. **SDK test suite** — `Example/Tests/GpApi/` and `Example/Tests/Portico/` are the most reliable source of real Swift call shapes and completion-handler
   signatures; the README's inline example is minimal. If you cannot confirm something exists in the repo, say so.

---

## Developer Portal Pages

Conceptual reference only (request/response shapes, not Swift syntax); all prefixed `https://developer.globalpayments.com/gh-assets/markdown/docs/`.

| Topic | Portal Page |
|---|---|
| Capture / Refund / Void | `payments/manage-payments/{capture,refund,reverse}-guide.md` |
| Verify / Tokenization | `payments/manage-payments/verify-guide.md`, `payments/tokenization/card-storage-guide.md` |
| Recurring / 3D Secure | `payments/recurring/recurring-payments-guide.md`, `risk-management/3D-secure/browser-authentication-guide.md` |
| Reporting / Testing | `reporting/real-time-reporting-guide.md`, `getting-started/testing.md` |

---

## Sample Repos

**Confirmed (2026-08-06):** no repo in `globalpayments-samples` has an `ios` directory. Use the SDK's own `Example/` app plus these server-side repos for
the backend half of the mobile split (implemented with a server-side Global Payments SDK):

| Operation | Source |
|---|---|
| End-to-end app usage (all gateways, 3DS2, tokenization) | https://github.com/globalpayments/ios-sdk/tree/master/Example |
| 3DS2 backend reference flow | https://github.com/globalpayments-samples/gpapi-3ds2 |
| Restricted access-token minting pattern | https://github.com/globalpayments-samples/online-card-payments |
| Backend tokenized-charge pattern | https://github.com/globalpayments-samples/wallet-management |

---

## Quick Reference

### Import Root
```swift
import GlobalPayments_iOS_SDK
```

### Key Classes (paths rooted at `GlobalPayments-iOS-SDK/Classes/`)
| Type | Source path |
|---|---|
| `GpApiConfig` / `PorticoConfig` | `ServiceConfigs/Gateways/{GpApiConfig,PorticoConfig}.swift` |
| `ServicesContainer.configureService(config:)` | `ServicesContainer.swift` |
| `GpApiConnector` / `PorticoConnector` | `Gateways/GpApiConnector.swift`, `Portico/Gateways/PorticoConnector.swift` |
| `CreditCardData` | `PaymentMethods/CreditCardData.swift` |
| `GpApiService.generateTransactionKey(...)` | `Services/GpApiService.swift` |
| `Secure3dService` / `RecurringService` / `ReportingService` | `Services/{Secure3dService,RecurringService,ReportingService}.swift` |
| `Transaction.capture/refund/reverse/voidTransaction` | `Entities/Transaction.swift` |

> **Real divergence — completion handlers, not throwing calls.** Every `.execute(...)`/`Secure3dService` call takes `(T?, Error?) -> Void`, confirmed in
> `GpApiCreditCardNotPresentTests.swift`/`GpApi3DSecure2Tests.swift`. Builder construction (`.withCurrency()`) is synchronous and can `throw`.

### Error Shapes
```text
Error (protocol)
├── ApiException                     — general API-level error
├── BuilderException                 — missing/invalid builder field
├── ConfigurationException           — bad or missing gateway config
├── GatewayException                 — gateway decline (responseCode, responseMessage)
└── UnsupportedTransactionException  — gateway doesn't support the op
```
Confirmed in `Entities/Exceptions/`: flat `struct: Error` each. Cast with `as? GatewayException` to read `responseCode`.

---

## Code Reference

All quick-copy Swift snippets (installation, config, payment methods, charge/authorize/capture/void/refund/verify, address, the mobile split for card
collection, tokenization, recurring, 3DS2, reporting, error handling) are in **[REFERENCE.md](./references/REFERENCE.md)**. Verify any class or method against
https://github.com/globalpayments/ios-sdk before emitting it.

---

## Test Cards

**Never include real or hardcoded card numbers in generated integration code.** Use placeholders and point to:

👉 https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

For 3DS specifically, `references/REFERENCE.md`'s **3D Secure 2** section covers the sandbox cards and names the Swift accessors in `Example/Tests/Data/GpApi3DSTestCards.swift`. The card numbers themselves are gateway-level (GP API sandbox), not iOS-specific — take the full list from the portal testing page above.

---

## Execution Rules

1. **Never embed `appKey` in app code, and never a plist/constant credential.** The backend calls `GpApiService.generateTransactionKey(...)` (or its
   server-side SDK equivalent) and hands the app a short-lived restricted `AccessTokenInfo` at runtime. See Card Collection in `references/REFERENCE.md`.
2. **`ServicesContainer.configureService(config:)` before any transaction.**
3. **Never write a blocking sample** — `.execute { transaction, error in }` returns immediately; the result arrives later via the closure.
4. **UI updates from a completion handler must hop to the main queue** — `DispatchQueue.main.async { }` inside the closure.
5. **Default to sandbox/test.** Every generated config targets `Environment.test`; flag production differences.
6. **GP API uses `reverse`, not `voidTransaction`, on an uncaptured auth** — `voidTransaction` is Portico-style reversal of a settled transaction.
7. **3DS2 challenge is an in-app web view, not a redirect** — on `CHALLENGE_REQUIRED`, load `threeDSecure.issuerAcsUrl` in a `WKWebView`.
8. **GP Ecom is unsupported.** Never emit `RealexConnector`/`RealexConfig`/`GpEcomConfig` code — dead, unwired code. GP Ecom requests need a different,
   server-side integration path outside this SDK.
