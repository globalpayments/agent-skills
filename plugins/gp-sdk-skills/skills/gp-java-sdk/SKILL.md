---
name: gp-java-sdk
description: |
  Expert guide for consuming the GlobalPayments Java SDK (globalpayments/java-sdk, Maven coordinates `com.globalpayments:globalpayments-sdk`, package root `com.global.api`). Covers installation, gateway configuration (GP API, GP Ecom, Portico), all payment operations (charge, authorize, capture, void/reverse, refund, tokenization, recurring billing, 3DS), reporting, and error handling. 3DS2 is the default for all non-US regions — full 4-step flow (enrollment, initiate-auth with BrowserData, optional challenge redirect, get-auth-result) is grounded in the `gpapi-3ds2` sample repo reference implementation and the SDK's own `GpApi3DSecure2Test` suite. Grounds all code in real SDK source and patterns. Trigger phrases: "gp-java-sdk", "integrate the Java SDK", "GlobalPayments Java SDK", "charge a card in Java", "set up GlobalPayments in Spring Boot", "Java payment integration"
---

# GP-JAVA-SDK

You are an expert consumer of the `globalpayments/java-sdk` (Maven `com.globalpayments:globalpayments-sdk`, package root `com.global.api`, Java 8+ source/target). Your job is to produce correct, runnable Java integration code grounded in the actual SDK source — not documentation summaries.

## Source Hierarchy (always follow this order)

1. **Developer portal** — consult the relevant portal page first for the API flow, required fields, and expected responses. Markdown pages follow the pattern: `https://developer.globalpayments.com/gh-assets/markdown/docs/...md`
2. **SDK source on GitHub** — verify every class name, constructor, method chain, and config field against the actual source at **https://github.com/globalpayments/java-sdk** (browse `src/main/java/com/global/api/` tree). Never guess — check the repo.
3. **Sample implementations** — working, runnable Java integrations live in the **https://github.com/globalpayments-samples** org. Filter by the `lang-java` topic. These are the closest thing to a canonical answer for "how do I wire this up end to end". See the Sample Repos table below.
4. **SDK test suite** — `src/test/java/com/global/api/tests/` in the same repo is a rich source of working Java patterns when portal examples don't include Java, especially `tests/gpapi/` for GP API and 3DS2 method chains.

Never rely on memory alone. If you cannot confirm something exists in the repo, say so.

---

## Developer Portal Pages

Use these as your first reference for each topic:

| Topic | Portal Page |
|---|---|
| Java SDK install & setup | https://developer.globalpayments.com/gh-assets/markdown/docs/integration-options/sdk/java.md |
| Take a payment (charge/authorize) | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/online/api-guide.md |
| Capture | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/capture-guide.md |
| Refund | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/refund-guide.md |
| Void / Reverse | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/reverse-guide.md |
| Verify | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/verify-guide.md |
| Tokenization | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/tokenization/card-storage-guide.md |
| Recurring payments | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/recurring/recurring-payments-guide.md |
| 3D Secure | https://developer.globalpayments.com/gh-assets/markdown/docs/risk-management/3D-secure/browser-authentication-guide.md |
| Reporting | https://developer.globalpayments.com/gh-assets/markdown/docs/reporting/real-time-reporting-guide.md |
| Testing & test cards | https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md |
| Getting started / credentials | https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/overview.md |

---

## Sample Repos

Working Java implementations in the `globalpayments-samples` org. Each repo below was confirmed to have a `java/` directory. Prefer these over invented examples.

| Operation | Sample repo |
|---|---|
| 3DS2 on GP API | https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/java |
| 3DS2 on GP Ecom | https://github.com/globalpayments-samples/gpecom-3ds2/tree/main/java |
| Hosted fields / drop-in UI | https://github.com/globalpayments-samples/online-card-payments/tree/main/java |
| Auth + delayed capture | https://github.com/globalpayments-samples/online-payments-auth-and-delayed-capture/tree/main/java |
| Refunds | https://github.com/globalpayments-samples/basic-refund-tool/tree/main/java |
| Tokenization / wallet | https://github.com/globalpayments-samples/wallet-management/tree/main/java |
| Save & reuse payment methods | https://github.com/globalpayments-samples/save-and-reuse-payment-methods/tree/main/java |
| Recurring payments | https://github.com/globalpayments-samples/online-recurring-payments/tree/main/java |
| Reporting | https://github.com/globalpayments-samples/reporting-service/tree/main/java |
| ACH / eCheck | https://github.com/globalpayments-samples/online-check-payments/tree/main/java |
| Google Pay | https://github.com/globalpayments-samples/google-pay-payments/tree/main/java |
| Pay by Link | https://github.com/globalpayments-samples/pay-by-link/tree/main/java |
| Network tokenization | https://github.com/globalpayments-samples/network-tokenization/tree/main/java |
| MOTO virtual terminal | https://github.com/globalpayments-samples/virtual-terminal/tree/main/java |

---

## Quick Reference

### Package Root
```java
com.global.api
```

### Key Classes
| Class | Package |
|---|---|
| `GpApiConfig` | `com.global.api.serviceConfigs.GpApiConfig` |
| `GpEcomConfig` | `com.global.api.serviceConfigs.GpEcomConfig` |
| `PorticoConfig` | `com.global.api.serviceConfigs.PorticoConfig` |
| `ServicesContainer` | `com.global.api.ServicesContainer` |
| `CreditCardData` | `com.global.api.paymentMethods.CreditCardData` |
| `CreditTrackData` | `com.global.api.paymentMethods.CreditTrackData` |
| `eCheck` | `com.global.api.paymentMethods.eCheck` |
| `GiftCard` | `com.global.api.paymentMethods.GiftCard` |
| `RecurringPaymentMethod` | `com.global.api.paymentMethods.RecurringPaymentMethod` |
| `ReportingService` | `com.global.api.services.ReportingService` |
| `Secure3dService` | `com.global.api.services.Secure3dService` |
| `GpApiService` | `com.global.api.services.GpApiService` |
| `Transaction` | `com.global.api.entities.Transaction` |
| `Address` | `com.global.api.entities.Address` |
| `Customer` | `com.global.api.entities.Customer` |
| `ThreeDSecure` | `com.global.api.entities.ThreeDSecure` |
| `BrowserData` | `com.global.api.entities.BrowserData` |
| `DeviceService` | `com.global.api.services.DeviceService` |
| `ConnectionConfig` | `com.global.api.terminals.ConnectionConfig` |
| `DiamondCloudConfig` | `com.global.api.terminals.diamond.DiamondCloudConfig` |
| `IDeviceInterface` | `com.global.api.terminals.abstractions.IDeviceInterface` |
| `DeviceController` | `com.global.api.terminals.DeviceController` |
| `PaxController` / `HpaController` / `UpaController` / `GeniusController` / `DiamondController` | `com.global.api.terminals.{pax,hpa,upa,genius,diamond}` |
| `TerminalAuthBuilder` / `TerminalManageBuilder` | `com.global.api.terminals.builders` |

> Note: the SDK's ACH payment method class is named `eCheck` (lowercase `e`) in source — not `ECheck`. `src/main/java/com/global/api/paymentMethods/eCheck.java`.

### Exception Hierarchy
```text
ApiException (extends java.lang.Exception — checked)
├── BuilderException                — missing required builder fields
├── ConfigurationException          — bad config (missing creds, wrong env, conflicting credential sets)
│   └── UnsupportedConnectionModeException
├── GatewayException                — gateway-level errors / declined (carries getResponseCode(), getResponseText())
│   ├── GatewayTimeoutException     — gateway did not respond within the given timeout
│   ├── GatewayComsException        — communication failure talking to the gateway
│   └── GatewayDuplicateException   — gateway flagged the request as a duplicate
├── MessageException                — a message to/from a device caused an error
│   └── PositiveScenarioTimeoutException
├── UnsupportedTransactionException — gateway or payment method doesn't support the operation
├── UnsupportedPaymentMethodException
└── BatchFullException              — device/terminal batch is full
```

> Note: there is **no `ValidationException`** class in `com.global.api.entities.exceptions` — confirmed by directory listing. SDK-side field validation failures surface as `BuilderException`.

> **`ApiException` is a checked exception** (`extends java.lang.Exception`, not `RuntimeException`). Every `.execute()` call and every builder method that can fail declares `throws ApiException` (or a subtype). Calling code must either `catch` it or declare `throws` on the enclosing method — the compiler enforces this.

---

## Code Reference

All quick-copy Java snippets (installation, config, payment methods, charge, authorize, capture, void/reverse, refund, verify, tokenization, recurring, 3DS, reporting, error handling) are in **[REFERENCE.md](./references/REFERENCE.md)**.

Use `references/REFERENCE.md` as your snippet source when generating code for users. Verify any class or method against https://github.com/globalpayments/java-sdk before emitting it.

---

## Test Cards

**Do not include real or hardcoded card numbers in code samples.** Direct users to the portal testing page for the full list of sandbox cards:

👉 https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

**Sandbox card rule:** Any future-dated card number that passes a Luhn/mod-10 check will be accepted in the sandbox environment. Use the portal testing page for specific cards that trigger particular responses (declines, AVS mismatches, 3DS scenarios, etc.).

---

## Execution Rules

1. **Portal first.** For every operation, link to the relevant portal page before generating Java code. The portal defines the API contract (required fields, response shape, expected status values).
2. **Verify against GitHub.** Before emitting any class, constructor, or method chain, confirm it exists in the SDK source at https://github.com/globalpayments/java-sdk (`src/main/java/com/global/api/` tree). If you can't confirm, say so and point the user to the repo.
3. **Use the test suite as a code reference.** `src/test/java/com/global/api/tests/gpapi/` at https://github.com/globalpayments/java-sdk contains working Java patterns for every operation, especially GP API and 3DS2 — prefer these over invented examples.
4. **No hardcoded card numbers.** Always use placeholder values (`"CARD_NUMBER"`, `"CVV"`, etc.) and point users to https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md for sandbox cards.
5. **Config validation.** After generating config code, verify required fields match the `validate()` method in the config class on GitHub (e.g. `GpApiConfig.validate()` requires `accessTokenInfo` or both `appId`/`appKey`; `PorticoConfig.validate()` rejects mixing `secretApiKey` with the 5-point fields).
6. **Builder chains.** Every transaction ends with `.execute()` or `.execute(configName)`. Never skip it.
7. **`import` statements mandatory.** Always include the exact `import com.global.api...;` lines for every class used — don't make the user guess the package.
8. **`ServicesContainer.configureService(config)` throws `ConfigurationException`.** It's a checked exception — show it handled, either with a `try`/`catch (ConfigurationException e)` block or a `throws ConfigurationException` on the enclosing method/constructor. Never emit a bare call that would fail to compile.
9. **Amounts are `BigDecimal`, never `double`.** Write `new BigDecimal("29.99")`. `AuthorizationBuilder.withAmount(BigDecimal)` and `charge(BigDecimal)`/`authorize(BigDecimal)`/`refund(BigDecimal)`/`reverse(BigDecimal)` all take `BigDecimal`. (Some methods have a `double` overload for convenience — never use it; always construct `BigDecimal` from a `String` to avoid binary floating-point rounding.)
10. **Catch `ApiException` last.** Order exception catches from specific to general: `BuilderException`, `ConfigurationException`, `GatewayException` (or its subclasses `GatewayTimeoutException`, `GatewayComsException`, `GatewayDuplicateException`), `UnsupportedTransactionException`, then `ApiException`. There is no `ValidationException` in this SDK — don't invent one.
11. **Test vs. Production.** Default all generated code to `Environment.TEST`. Flag where `Environment.PRODUCTION` applies.
12. **One config per service.** `ServicesContainer.configureService(config)` (or `configureService(config, configName)` for a named/multi-gateway setup) must be called before any transaction. Show this explicitly in every snippet.
13. **Setters, not property assignment.** Config and entity classes use Lombok-generated (or explicit) setters — `config.setAppId(...)`, `card.setNumber(...)`. Some classes (`PorticoConfig`, `GpEcomConfig`, `Address`, `BrowserData`, `eCheck`) are annotated `@Accessors(chain = true)` at the class level so every setter returns `this` and can be chained; others (`GpApiConfig`, `CreditCardData`) only chain on individually-annotated fields. **Always emit one `.setX(...)` statement per line** rather than relying on chaining — it's correct regardless of which fields happen to be chainable, and it matches what the SDK's own tests do.
14. **When the user has a partial snippet**, identify which step they're on, fill in what's missing, validate the whole flow end-to-end, and link to the relevant portal page.
15. **Void vs. Reverse — method name and gateway behavior.** `void` is a reserved word in Java, so the SDK method is `.voidTransaction()`, never `.void()`. For GP API, prefer `.reverse()` (`Transaction.reverse(amount)` / `Credit.reverse(amount)`) to match portal terminology. Java's `GpApiManagementRequestBuilder` (`src/main/java/com/global/api/builders/requestbuilder/gpApi/GpApiManagementRequestBuilder.java`, line 93) handles `TransactionType.Reversal` and `TransactionType.Void` in the *same* branch, so `.voidTransaction()` also works against GP API in this SDK, even though `.reverse()` is the portal-aligned recommended call. For Portico and GP Ecom, both `TransactionType.Void` and `TransactionType.Reversal` are handled explicitly by their connectors — use `.voidTransaction()`.
16. **Hosted fields for web-facing integrations.** If the user is building a web page or form, recommend GlobalPayments.js hosted fields over passing raw `CreditCardData` to the server. The pattern: (1) Java generates a restricted `GpApiService.generateTransactionKey(config)` token scoped to `PMT_POST_Create_Single`; (2) browser mounts `GlobalPayments.creditCard.form()` iframes; (3) on `token-success` the server receives only a `PMT_` reference and calls `.charge()` with it. Raw card numbers never touch the merchant server. See the Hosted Fields section in `references/REFERENCE.md`.
17. **Gateway vs. terminal is a separate registration and execution path — do not mix them.** `ServicesContainer.configureService(config, configName)` is the single generic entry point for both, but a gateway config (`GpApiConfig`, `GpEcomConfig`, `PorticoConfig`) registers an `IPaymentGateway` that `AuthorizationBuilder.execute()` reaches via `ServicesContainer.getGateway(configName)`, while a `ConnectionConfig` (or `DiamondCloudConfig`) registers a `DeviceController`/`IDeviceInterface` pair that `TerminalAuthBuilder`/`TerminalManageBuilder.execute()` reach via `getDeviceController(configName)`. Never call a payment method's `.charge()`/`.authorize()` against a `configName` that was configured with a `ConnectionConfig` — use `DeviceService.create(connectionConfig)` to get an `IDeviceInterface`, then call its own operations (`.sale()`, `.authorize()`, `.refund()`, etc.). See the Terminal Operations section in `references/REFERENCE.md`.
18. **3DS is the default outside the US.** For any non-US merchant (`config.getCountry()` ≠ `"US"`), always implement the full 3DS2 flow — do not skip it. The flow has four distinct server-side steps: (1) `Secure3dService.checkEnrollment(card)`, (2) `Secure3dService.initiateAuthentication(card, secureEcom)` with `BrowserData`, (3) optionally handle a `CHALLENGE_REQUIRED` status by redirecting to the ACS URL, then (4) `Secure3dService.getAuthenticationData()` to retrieve the final result, after which attach the `ThreeDSecure` object via the payment method's `setThreeDSecure(...)` before charging. Three `GpApiConfig` fields are required: `merchantContactUrl`, `methodNotificationUrl`, `challengeNotificationUrl` (must be HTTPS). Reference implementation (Java): https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/java — verified test chains: `src/test/java/com/global/api/tests/gpapi/GpApi3DSecure2Test.java` in the SDK repo. See the full 3DS section in `references/REFERENCE.md`.
