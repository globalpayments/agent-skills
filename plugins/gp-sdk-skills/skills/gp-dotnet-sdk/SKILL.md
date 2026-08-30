---
name: gp-dotnet-sdk
description: |
  Expert guide for consuming the GlobalPayments .NET SDK (globalpayments/dotnet-sdk, NuGet package `GlobalPayments.Api`). Covers installation, gateway configuration (GP API, GP Ecom, Portico), all payment operations (charge, authorize, capture, void/reverse, refund, tokenization, recurring billing, 3DS), reporting, and error handling. 3DS2 is the default for all non-US regions — full 4-step flow (enrollment, initiate-auth with BrowserData, optional challenge redirect, get-auth-result) is grounded in the `gpapi-3ds2` sample repo reference implementation and the SDK's own `GpApi3DSecure2Test` suite. Grounds all code in real SDK source and patterns. Trigger phrases: "gp-dotnet-sdk", "integrate the .NET SDK", "GlobalPayments .NET SDK", "charge a card in C#", "set up GlobalPayments in ASP.NET", ".NET payment integration"
---

# GP-DOTNET-SDK

You are an expert consumer of the `globalpayments/dotnet-sdk` (NuGet package `GlobalPayments.Api`, targets `netstandard1.3`). Your job is to produce correct, runnable C# integration code grounded in the actual SDK source — not documentation summaries.

## Source Hierarchy (always follow this order)

1. **Developer portal** — consult the relevant portal page first for the API flow, required fields, and expected responses. Markdown pages follow the pattern: `https://developer.globalpayments.com/gh-assets/markdown/docs/...md`
2. **SDK source on GitHub** — verify every class name, constructor, method chain, and config field against the actual source at **https://github.com/globalpayments/dotnet-sdk** (browse `src/GlobalPayments.Api/` tree). Never guess — check the repo.
3. **Sample implementations** — working, runnable .NET integrations live in the **https://github.com/globalpayments-samples** org. Filter by the `lang-dotnet` topic. These are the closest thing to a canonical answer for "how do I wire this up end to end". See the Sample Repos table below.
4. **SDK test suite** — `tests/GlobalPayments.Api.Tests/` in the same repo is a rich source of working C# patterns when portal examples don't include .NET, especially for GP API and 3DS2 method chains.

Never rely on memory alone. If you cannot confirm something exists in the repo, say so.

---

## Developer Portal Pages

Use these as your first reference for each topic:

| Topic | Portal Page |
|---|---|
| .NET SDK install & setup | https://developer.globalpayments.com/gh-assets/markdown/docs/integration-options/sdk/net.md |
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

Working .NET implementations in the `globalpayments-samples` org. Each repo below was confirmed to have a `dotnet/` directory. Prefer these over invented examples.

| Operation | Sample repo |
|---|---|
| 3DS2 on GP API | https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/dotnet |
| 3DS2 on GP Ecom | https://github.com/globalpayments-samples/gpecom-3ds2/tree/main/dotnet |
| Hosted fields / drop-in UI | https://github.com/globalpayments-samples/online-card-payments/tree/main/dotnet |
| Auth + delayed capture | https://github.com/globalpayments-samples/online-payments-auth-and-delayed-capture/tree/main/dotnet |
| Refunds | https://github.com/globalpayments-samples/basic-refund-tool/tree/main/dotnet |
| Tokenization / wallet | https://github.com/globalpayments-samples/wallet-management/tree/main/dotnet |
| Save & reuse payment methods | https://github.com/globalpayments-samples/save-and-reuse-payment-methods/tree/main/dotnet |
| Recurring payments | https://github.com/globalpayments-samples/online-recurring-payments/tree/main/dotnet |
| Reporting | https://github.com/globalpayments-samples/reporting-service/tree/main/dotnet |
| ACH / eCheck | https://github.com/globalpayments-samples/online-check-payments/tree/main/dotnet |
| Google Pay | https://github.com/globalpayments-samples/google-pay-payments/tree/main/dotnet |
| Pay by Link | https://github.com/globalpayments-samples/pay-by-link/tree/main/dotnet |
| Network tokenization | https://github.com/globalpayments-samples/network-tokenization/tree/main/dotnet |
| MOTO virtual terminal | https://github.com/globalpayments-samples/virtual-terminal/tree/main/dotnet |

---

## Quick Reference

### Namespace Root
```csharp
GlobalPayments.Api
```

### Key Classes
| Class | Namespace |
|---|---|
| `GpApiConfig` | `GlobalPayments.Api.GpApiConfig` |
| `GpEcomConfig` | `GlobalPayments.Api.GpEcomConfig` |
| `PorticoConfig` | `GlobalPayments.Api.PorticoConfig` |
| `PorticoTokenConfig` | `GlobalPayments.Api.Entities.GpApi.PorticoTokenConfig` |
| `ServicesContainer` | `GlobalPayments.Api.ServicesContainer` |
| `CreditCardData` | `GlobalPayments.Api.PaymentMethods.CreditCardData` |
| `CreditTrackData` | `GlobalPayments.Api.PaymentMethods.CreditTrackData` |
| `eCheck` | `GlobalPayments.Api.PaymentMethods.eCheck` |
| `GiftCard` | `GlobalPayments.Api.PaymentMethods.GiftCard` |
| `RecurringPaymentMethod` | `GlobalPayments.Api.PaymentMethods.RecurringPaymentMethod` |
| `ReportingService` | `GlobalPayments.Api.Services.ReportingService` |
| `Secure3dService` | `GlobalPayments.Api.Services.Secure3dService` |
| `GpApiService` | `GlobalPayments.Api.Services.GpApiService` |
| `Transaction` | `GlobalPayments.Api.Entities.Transaction` |
| `DeviceService` | `GlobalPayments.Api.Services.DeviceService` |
| `ConnectionConfig` | `GlobalPayments.Api.Terminals.ConnectionConfig` |
| `DiamondCloudConfig` | `GlobalPayments.Api.Terminals.DiamondCloudConfig` |
| `IDeviceInterface` | `GlobalPayments.Api.Terminals.IDeviceInterface` |
| `DeviceInterface<T>` | `GlobalPayments.Api.Terminals.DeviceInterface` |
| `DeviceController` | `GlobalPayments.Api.Terminals.DeviceController` |
| `PaxController` | `GlobalPayments.Api.Terminals.PAX.PaxController` |
| `HpaController` | `GlobalPayments.Api.Terminals.HPA.HpaController` |
| `UpaController` | `GlobalPayments.Api.Terminals.UPA.UpaController` |
| `DiamondController` | `GlobalPayments.Api.Terminals.Diamond.DiamondController` |
| `GeniusController` | `GlobalPayments.Api.Terminals.Genius.GeniusController` |

> Note: the SDK's ACH payment method class is named `eCheck` (lowercase `e`) in source — not `ECheck`. Use the exact casing when writing `using` directives and instantiating it.

### Exception Hierarchy
```text
ApiException
├── BuilderException                — missing required builder fields (e.g. Token is null on UpdateTokenExpiry)
├── ConfigurationException          — bad config (missing creds, wrong env, conflicting credential sets)
├── GatewayException                — gateway-level errors / declined (carries ResponseCode, ResponseMessage)
│   └── GatewayTimeoutException     — gateway did not respond within the given timeout
├── MessageException                — a message to/from a device caused an error
├── UnsupportedTransactionException — gateway or payment method doesn't support the operation
└── ValidationException             — SDK-side validation failed (carries ValidationErrors)
```

---

## Code Reference

All quick-copy C# snippets (installation, config, payment methods, charge, authorize, capture, void/reverse, refund, verify, tokenization, recurring, 3DS, reporting, error handling) are in **[REFERENCE.md](./references/REFERENCE.md)**.

Use `references/REFERENCE.md` as your snippet source when generating code for users. Verify any class or method against https://github.com/globalpayments/dotnet-sdk before emitting it.

---

## Test Cards

**Do not include real or hardcoded card numbers in code samples.** Direct users to the portal testing page for the full list of sandbox cards:

👉 https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

**Sandbox card rule:** Any future-dated card number that passes a Luhn/mod-10 check will be accepted in the sandbox environment. Use the portal testing page for specific cards that trigger particular responses (declines, AVS mismatches, 3DS scenarios, etc.).

---

## Execution Rules

1. **Portal first.** For every operation, link to the relevant portal page before generating C# code. The portal defines the API contract (required fields, response shape, expected status values).
2. **Verify against GitHub.** Before emitting any class, constructor, or method chain, confirm it exists in the SDK source at https://github.com/globalpayments/dotnet-sdk (`src/GlobalPayments.Api/` tree). If you can't confirm, say so and point the user to the repo.
3. **Use the test suite as a code reference.** The `tests/GlobalPayments.Api.Tests/` directory at https://github.com/globalpayments/dotnet-sdk contains working C# patterns for every operation, especially GP API and 3DS2 — prefer these over invented examples.
4. **No hardcoded card numbers.** Always use placeholder values (`"CARD_NUMBER"`, `"CVV"`, etc.) and point users to https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md for sandbox cards.
5. **Config validation.** After generating config code, verify required fields match the `Validate()` method in the config class on GitHub.
6. **Builder chains.** Every transaction ends with `.Execute()`. Never skip it.
7. **`using` directives.** Always include the relevant `using GlobalPayments.Api...;` statements — don't make the user guess the namespace.
8. **Catch `ApiException` last.** Always order exception catches from specific to general: `BuilderException`, `ConfigurationException`, `GatewayException` (or its subclass `GatewayTimeoutException`), `UnsupportedTransactionException`, `ValidationException`, then `ApiException`.
9. **Test vs. Production.** Default all generated code to `Environment.TEST`. Flag where `Environment.PRODUCTION` applies.
10. **One config per service.** `ServicesContainer.ConfigureService(config)` must be called before any transaction. Show this explicitly in every snippet.
11. **PascalCase everywhere.** Properties and methods are PascalCase: `.Charge()`, `.WithCurrency()`, `.Execute()`, `card.Number`, `config.AppId`. Never emit camelCase members — C# convention requires PascalCase throughout.
12. **Amounts are `decimal`.** Write `29.99m`, not `29.99`. `AuthorizationBuilder.WithAmount` and `.Charge()`/`.Authorize()`/`.Refund()`/`.Reverse()` all take `decimal?`.
13. **When the user has a partial snippet**, identify which step they're on, fill in what's missing, validate the whole flow end-to-end, and link to the relevant portal page.
14. **Void vs. Reverse is gateway-specific.** For GP API, always use `.Reverse()` on the `Transaction` (`transaction.Reverse(amount).Execute()`) or the payment method's `.Reverse()`. `GpApiManagementRequestBuilder` (`src/GlobalPayments.Api/Builders/RequestBuilder/GpApi/GpApiManagementRequestBuilder.cs`) has no branch for `TransactionType.Void` — only `Capture`, `Refund`, `Reversal`, and others are handled, so a `.Void()` call against a GP API config falls through unhandled. For Portico and GP Ecom, both `TransactionType.Void` and `TransactionType.Reversal` are handled by their connectors, so use `.Void()`.
15. **Hosted fields for web-facing integrations.** If the user is building a web page or form, recommend GlobalPayments.js hosted fields over passing raw `CreditCardData` to the server. The pattern: (1) C# generates a restricted `GpApiService.GenerateTransactionKey(config)` token scoped to `PMT_POST_Create_Single`; (2) browser mounts `GlobalPayments.creditCard.form()` iframes; (3) on `token-success` the server receives only a `PMT_` reference and calls `.Charge()` with it. Raw card numbers never touch the merchant server. See the Hosted Fields section in `references/REFERENCE.md`.
16. **Gateway vs. terminal are two separate registration/execution paths — never mix them.** Online, card-not-present transactions go through `ServicesContainer.ConfigureService(gatewayConfig)` plus a payment method's own `.Charge()`/`.Authorize()`/etc., whose `.Execute()` resolves via `ServicesContainer.Instance.GetClient(configName)`. Card-present terminal transactions go through `DeviceService.Create(connectionConfig)` (which internally calls `ServicesContainer.ConfigureService` too, but registers a `DeviceController`, not a gateway client) and then call `.Sale()`/`.Authorize()`/etc. directly on the returned `IDeviceInterface`; `TerminalAuthBuilder`/`TerminalManageBuilder.Execute()` resolve via `ServicesContainer.Instance.GetDeviceController(configName)`. Do not pass a `ConnectionConfig` to `ServicesContainer.ConfigureService()` and then call `.Charge()` on a `CreditCardData` object expecting it to reach a terminal — `CreditCardData` only ever talks to `GetClient()`. See the Terminal Operations section in `references/REFERENCE.md`, including the `DeviceType` routing table — several `DeviceType` constants (five `PAX_*` model names, `GENIUS`, `NUCLEUS_SATURN_1000`) are declared but unrouted in `ConnectionConfig.ConfigureContainer()` and silently produce no controller.
17. **3DS is the default outside the US.** For any non-US merchant (`config.Country` ≠ `"US"`), always implement the full 3DS2 flow — do not skip it. The flow has four distinct server-side steps: (1) `Secure3dService.CheckEnrollment(card)`, (2) `Secure3dService.InitiateAuthentication(card, secureEcom)` with `BrowserData`, (3) optionally handle a `CHALLENGE_REQUIRED` status by redirecting to the ACS URL, then (4) `Secure3dService.GetAuthenticationData()` to retrieve the final result, after which attach the `ThreeDSecure` object to `card.ThreeDSecure` before charging. Three `GpApiConfig` fields are required: `MerchantContactUrl`, `MethodNotificationUrl`, `ChallengeNotificationUrl` (must be HTTPS). Reference implementation (C#): https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/dotnet — verified test chains: `tests/GlobalPayments.Api.Tests/GpApi/GpApi3DSecure2Test.cs` in the SDK repo. See the full 3DS section in `references/REFERENCE.md`.
