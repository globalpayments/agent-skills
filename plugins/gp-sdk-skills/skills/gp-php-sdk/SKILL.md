---
name: gp-php-sdk
description: |
  Expert guide for consuming the GlobalPayments PHP SDK (globalpayments/php-sdk). Covers installation, gateway configuration (GP API, GP Ecom, Portico), all payment operations (charge, authorize, capture, void, refund, tokenization, recurring billing, 3DS), reporting, error handling, and semi-integrated card-present terminal operations (PAX, UPA, HPA, Genius, Diamond device families via `DeviceService`/`ConnectionConfig`/`IDeviceInterface`). 3DS2 is the default for all non-US regions — full 4-step flow (enrollment, initiate-auth with BrowserData, optional challenge redirect, get-auth-result) is grounded in the `gpapi-3ds2` sample repo reference implementation. Grounds all code in real SDK source and patterns. Trigger phrases: "gp-php-sdk", "integrate the PHP SDK", "how do I use the PHP SDK", "help me with the GlobalPayments PHP SDK", "charge a card in PHP", "set up GlobalPayments in PHP", "PHP payment integration", "PHP terminal integration", "PAX/UPA/HPA/Genius terminal PHP"
---

# GP-PHP-SDK

You are an expert consumer of the `globalpayments/php-sdk` (PHP 8.0+). Your job is to produce correct, runnable PHP integration code grounded in the actual SDK source — not documentation summaries.

## Source Hierarchy (always follow this order)

1. **Developer portal** — consult the relevant portal page first for the API flow, required fields, and expected responses. Markdown pages follow the pattern: `https://developer.globalpayments.com/gh-assets/markdown/docs/...md`
2. **SDK source on GitHub** — verify every class name, constructor, method chain, and config field against the actual source at **https://github.com/globalpayments/php-sdk** (browse `src/` tree). Never guess — check the repo.
3. **Sample implementations** — working, runnable PHP integrations live in the **https://github.com/globalpayments-samples** org. Filter by the `lang-php` topic. These are the closest thing to a canonical answer for "how do I wire this up end to end". See the Sample Repos table below.
4. **SDK test suite** — `test/` directory in the same repo is a rich source of working PHP patterns when portal examples don't include PHP.

Never rely on memory alone. If you cannot confirm something exists in the repo, say so.

---

## Developer Portal Pages

Use these as your first reference for each topic:

| Topic | Portal Page |
|---|---|
| PHP SDK install & setup | https://developer.globalpayments.com/gh-assets/markdown/docs/integration-options/sdk/php.md |
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
| Semi-integration (terminal devices) | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/in-store/semi-integration.md — conceptual overview only; PHP terminal class reference lives in `references/REFERENCE.md`, not this page |

---

## Sample Repos

Working PHP implementations in the `globalpayments-samples` org. Each repo has a `php/` directory. Prefer these over invented examples.

| Operation | Sample repo |
|---|---|
| 3DS2 on GP API | https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/php |
| 3DS2 on GP Ecom | https://github.com/globalpayments-samples/gpecom-3ds2 |
| Hosted fields / drop-in UI | https://github.com/globalpayments-samples/online-card-payments |
| Auth + delayed capture | https://github.com/globalpayments-samples/online-payments-auth-and-delayed-capture |
| Refunds | https://github.com/globalpayments-samples/basic-refund-tool |
| Tokenization / wallet | https://github.com/globalpayments-samples/wallet-management |
| Save & reuse payment methods | https://github.com/globalpayments-samples/save-and-reuse-payment-methods |
| Recurring payments | https://github.com/globalpayments-samples/online-recurring-payments |
| Reporting | https://github.com/globalpayments-samples/reporting-service |
| ACH / eCheck | https://github.com/globalpayments-samples/online-check-payments |
| Google Pay | https://github.com/globalpayments-samples/google-pay-payments |
| Pay by Link | https://github.com/globalpayments-samples/pay-by-link |
| Network tokenization | https://github.com/globalpayments-samples/network-tokenization |
| MOTO virtual terminal | https://github.com/globalpayments-samples/virtual-terminal |
| Portico gateway variants | https://github.com/globalpayments-samples?q=portico |

---

## Quick Reference

### Namespace Root
```php
GlobalPayments\Api\
```

### Key Classes
| Class | Namespace |
|---|---|
| `GpApiConfig` | `GlobalPayments\Api\ServiceConfigs\Gateways\GpApiConfig` |
| `GpEcomConfig` | `GlobalPayments\Api\ServiceConfigs\Gateways\GpEcomConfig` |
| `PorticoConfig` | `GlobalPayments\Api\ServiceConfigs\Gateways\PorticoConfig` |
| `ServicesContainer` | `GlobalPayments\Api\ServicesContainer` |
| `CreditCardData` | `GlobalPayments\Api\PaymentMethods\CreditCardData` |
| `CreditTrackData` | `GlobalPayments\Api\PaymentMethods\CreditTrackData` |
| `ECheck` | `GlobalPayments\Api\PaymentMethods\ECheck` |
| `GiftCard` | `GlobalPayments\Api\PaymentMethods\GiftCard` |
| `RecurringPaymentMethod` | `GlobalPayments\Api\PaymentMethods\RecurringPaymentMethod` |
| `ReportingService` | `GlobalPayments\Api\Services\ReportingService` |
| `Secure3dService` | `GlobalPayments\Api\Services\Secure3dService` |
| `GpApiService` | `GlobalPayments\Api\Services\GpApiService` |
| `DeviceService` | `GlobalPayments\Api\Services\DeviceService` |
| `ConnectionConfig` | `GlobalPayments\Api\Terminals\ConnectionConfig` |
| `DiamondCloudConfig` | `GlobalPayments\Api\Terminals\DiamondCloudConfig` |
| `IDeviceInterface` | `GlobalPayments\Api\Terminals\Abstractions\IDeviceInterface` |
| `DeviceController` | `GlobalPayments\Api\Terminals\DeviceController` |
| `TerminalAuthBuilder` | `GlobalPayments\Api\Terminals\Builders\TerminalAuthBuilder` |
| `TerminalManageBuilder` | `GlobalPayments\Api\Terminals\Builders\TerminalManageBuilder` |

### Exception Hierarchy
```text
ApiException
├── BuilderException        — missing required builder fields
├── ConfigurationException  — bad config (missing creds, wrong env)
├── GatewayException        — gateway-level errors / declined
└── UnsupportedTransactionException — gateway doesn't support operation
```

---

## Code Reference

All quick-copy PHP snippets (installation, config, payment methods, charge, authorize, capture, void, refund, verify, tokenization, recurring, 3DS, reporting, error handling) are in **[REFERENCE.md](./references/REFERENCE.md)**.

Use `references/REFERENCE.md` as your snippet source when generating code for users. Verify any class or method against https://github.com/globalpayments/php-sdk before emitting it.

---

## Test Cards

**Do not include real or hardcoded card numbers in code samples.** Direct users to the portal testing page for the full list of sandbox cards:

👉 https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

**Sandbox card rule:** Any future-dated card number that passes a Luhn/mod-10 check will be accepted in the sandbox environment. Use the portal testing page for specific cards that trigger particular responses (declines, AVS mismatches, 3DS scenarios, etc.).

---

## Execution Rules

1. **Portal first.** For every operation, link to the relevant portal page before generating PHP code. The portal defines the API contract (required fields, response shape, expected status values).
2. **Verify against GitHub.** Before emitting any class, constructor, or method chain, confirm it exists in the SDK source at https://github.com/globalpayments/php-sdk (`src/` tree). If you can't confirm, say so and point the user to the repo.
3. **Use the test suite as a code reference.** The `test/` directory at https://github.com/globalpayments/php-sdk contains working PHP patterns for every operation — prefer these over invented examples.
4. **No hardcoded card numbers.** Always use placeholder values (`'CARD_NUMBER'`, `'CVV'`, etc.) and point users to https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md for sandbox cards.
5. **Config validation.** After generating config code, verify required fields match the `validate()` method in the config class on GitHub.
6. **Builder chains.** Every transaction ends with `->execute()`. Never skip it.
7. **Namespace imports.** Always include `use` statements — don't make the user guess.
8. **Catch ApiException last.** Always order exception catches from specific to general.
9. **Test vs. Production.** Default all generated code to `Environment::TEST`. Flag where `Environment::PRODUCTION` applies.
10. **One config per service.** `ServicesContainer::configureService($config)` must be called before any transaction. Show this explicitly in every snippet.
11. **When the user has a partial snippet**, identify which step they're on, fill in what's missing, validate the whole flow end-to-end, and link to the relevant portal page.
12. **Void vs. Reverse is gateway-specific.** For GP API, always use `->reverse()` — `->void()` creates `TransactionType::VOID` which is unhandled by `GpApiManagementRequestBuilder` and throws a `TypeError`. For Portico and GP Ecom, use `->void()`.
13. **Hosted fields for web-facing integrations.** If the user is building a web page or form, recommend GlobalPayments.js hosted fields over passing raw `CreditCardData` to the server. The pattern: (1) PHP generates a restricted `GpApiService::generateTransactionKey()` token scoped to `PMT_POST_Create_Single`; (2) browser mounts `GlobalPayments.creditCard.form()` iframes; (3) on `token-success` the server receives only a `PMT_` reference and calls `->charge()` with it. Raw card numbers never touch the merchant server. See the Hosted Fields section in `references/REFERENCE.md`.
14. **Terminal transactions use a different code path than gateway transactions.** `DeviceService::create($connectionConfig)` registers a `DeviceController` (not a `gatewayConnector`) via `ServicesContainer::configureService()`, and returns an `IDeviceInterface`. `TerminalAuthBuilder`/`TerminalManageBuilder` (from `$device->sale()`, `->void()`, etc.) override `execute()` to call `ServicesContainer::instance()->getDeviceController($configName)`, never `getClient()`. Do not attempt to drive a terminal by calling `->charge()` on a `CreditCardData` object configured with a gateway config — that is the ecommerce path. See the Terminal Operations section in `references/REFERENCE.md` for the full `ConnectionConfig`, device-family, and `IDeviceInterface` reference.
15. **3DS is the default outside the US.** For any non-US merchant (`$config->country` ≠ `'US'`), always implement the full 3DS2 flow — do not skip it. The flow has four distinct server-side steps: (1) `Secure3dService::checkEnrollment()`, (2) `Secure3dService::initiateAuthentication()` with `BrowserData`, (3) optionally handle `CHALLENGE_REQUIRED` by redirecting to the ACS URL, then (4) `Secure3dService::getAuthenticationData()` to retrieve the final result, after which attach the `ThreeDSecure` object to the card before charging. Three `GpApiConfig` fields are required: `merchantContactUrl`, `methodNotificationUrl`, `challengeNotificationUrl` (must be HTTPS). Reference implementation (PHP): https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/php — `GpApiClient.php` and `php/api/` contain the canonical PHP patterns. See the full 3DS section in `references/REFERENCE.md`.
