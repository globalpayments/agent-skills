---
name: gp-python-sdk
description: |
  Expert guide for consuming the GlobalPayments Python SDK (globalpayments/python-sdk, PyPI distribution `GlobalPayments.Api`, Python 3.11+). Covers installation, gateway configuration (GP API, Portico, and GP Ecom — reached through `PorticoConfig`, not a dedicated config class), payment operations (charge, authorize, capture, void, reverse, refund, tokenization, recurring billing, 3DS), reporting, and error handling. Connectors and `ServicesContainer` live inside monolithic `globalpayments/api/__init__.py` and `globalpayments/api/gateways/__init__.py` files rather than per-class modules. Grounds all code in real SDK source and patterns. Trigger phrases: "gp-python-sdk", "integrate the Python SDK", "GlobalPayments Python SDK", "charge a card in Python", "set up GlobalPayments in Django", "Python payment integration"
---

# GP-PYTHON-SDK

You are an expert consumer of the `globalpayments/python-sdk` (PyPI distribution `GlobalPayments.Api`, requires Python `>=3.11,<4.0`). Your job is to produce correct, runnable Python integration code grounded in the actual SDK source — not documentation summaries, and not guessed or assumed API shapes.

## Source Hierarchy (always follow this order)

1. **Developer portal** — consult the relevant portal page first for the API flow, required fields, and expected responses. Markdown pages follow the pattern: `https://developer.globalpayments.com/gh-assets/markdown/docs/...md`
2. **SDK source on GitHub** — verify every class name, constructor, method chain, and config field against the actual source at **https://github.com/globalpayments/python-sdk** (default branch `master`, browse `globalpayments/api/`). Never guess — check the repo. This SDK is unusually consolidated: `ServicesContainer`, `GpApiConfig`, and `PorticoConfig` all live in `globalpayments/api/__init__.py`, and every gateway connector (`GpApiConnector`, `PorticoConnector`, `RealexConnector`, `PayPlanConnector`) lives in `globalpayments/api/gateways/__init__.py`. Do not assume a per-class file layout.
3. **Sample implementations** — working, runnable Python integrations live in the **https://github.com/globalpayments-samples** org. Filter by the `lang-python` topic. See the Sample Repos table below — only 6 of the 7 plausible repos actually carry a `python/` directory.
4. **SDK test suite** — `tests/integration/gateways/` in the same repo is a rich source of working Python patterns, especially `tests/integration/gateways/GpApi_connector/` for GP API and `tests/integration/gateways/realex_connector/` for GP Ecom. Some test files in this repo have their entire contents commented out (e.g. `gpapi_test_3ds_2.py`) — treat those as inactive documentation of intent, not as passing, currently-exercised tests. Prefer an active test file (e.g. `gpapi_test_3DSecure.py`) when one exists for the same flow.

Never rely on memory alone. If you cannot confirm something exists in the repo, say so.

---

## Developer Portal Pages

Use these as your first reference for each topic:

| Topic | Portal Page |
|---|---|
| Python SDK install & setup | https://github.com/globalpayments/python-sdk#readme — no portal SDK page exists for Python |
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

Working Python implementations in the `globalpayments-samples` org. Each repo below was confirmed (2026-08-06, `contents/python` API check) to have a `python/` directory — a flat Flask app (`server.py`, `requirements.txt`, `Dockerfile`). Prefer these over invented examples.

| Operation | Sample repo |
|---|---|
| 3DS2 reference (GP Ecom, see caveat below) | https://github.com/globalpayments-samples/gpecom-3ds2/tree/main/python |
| Reporting | https://github.com/globalpayments-samples/reporting-service/tree/main/python |
| Network tokenization | https://github.com/globalpayments-samples/network-tokenization/tree/main/python |
| Pay by Link | https://github.com/globalpayments-samples/pay-by-link/tree/main/python |
| Portico card payments | https://github.com/globalpayments-samples/portico-online-card-payments/tree/main/python |
| Hosted fields (integrated partner) | https://github.com/globalpayments-samples/integrated-partner-online-payments-with-hosted-fields-api/tree/main/python |

**Confirmed absent, not just unchecked:** `gpapi-3ds2` and `online-recurring-payments` have no `python/` directory (`contents/python` returns 404 for both; `online-recurring-payments`'s root lists only `dotnet/`, `java/`, `nodejs/`, `php/`). Don't point users at a Python example for GP API 3DS2 or recurring payments; use the SDK's own test suite instead (see Test Cards / 3D Secure 2 sections in `references/REFERENCE.md`).

**A real caveat on the 3DS2 sample:** `gpecom-3ds2/python/server.py` is generic, uncustomized Flask boilerplate (confirmed by reading the complete 147-line file) — it configures `PorticoConfig` with `secret_api_key` (a plain Portico credential, not GP Ecom's `merchant_id`/`shared_secret`) and its `/process-payment` endpoint is a single `card.charge(...)` call with a `# TODO: Add your payment processing logic here` comment; it does not call `check_enrollment`/`initiate_authentication`/`get_authentication_data`. Don't present it to a user as a working 3DS2 flow. For real 3DS2 method chains, use the SDK's own `tests/integration/gateways/GpApi_connector/gpapi_test_3DSecure.py` (active, targets **GP API**) — see the 3D Secure 2 section in `references/REFERENCE.md`.

---

## Quick Reference

### Import Root
```text
globalpayments.api
```

### Key Classes
| Class | Import path |
|---|---|
| `GpApiConfig` | `from globalpayments.api import GpApiConfig` |
| `PorticoConfig` | `from globalpayments.api import PorticoConfig` (also used for GP Ecom — see below) |
| `ServicesContainer` | `from globalpayments.api import ServicesContainer` |
| `CreditCardData` | `from globalpayments.api.payment_methods import CreditCardData` |
| `CreditTrackData` | `from globalpayments.api.payment_methods import CreditTrackData` |
| `ECheck` | `from globalpayments.api.payment_methods import ECheck` |
| `GiftCard` | `from globalpayments.api.payment_methods import GiftCard` |
| `DebitTrackData` | `from globalpayments.api.payment_methods import DebitTrackData` |
| `RecurringPaymentMethod` | `from globalpayments.api.entities import RecurringPaymentMethod` |
| `Customer` | `from globalpayments.api.entities import Customer` |
| `Transaction` | `from globalpayments.api.entities import Transaction` |
| `Address` | `from globalpayments.api.entities import Address` |
| `BrowserData` | `from globalpayments.api.entities.browser_data import BrowserData` |
| `ThreeDSecure` | `from globalpayments.api.entities import ThreeDSecure` |
| `ReportingService` | `from globalpayments.api.services import ReportingService` |
| `Secure3dService` | `from globalpayments.api.services.secure_3d_service import Secure3dService` |
| `TransactionReportBuilder` | `from globalpayments.api.builders import TransactionReportBuilder` (only needed directly for deposits/disputes — see Reporting) |

> **Real divergence — `RecurringPaymentMethod` lives in `entities/`, not `payment_methods/`.** Confirmed: `globalpayments/api/entities/__init__.py` line 427, `class RecurringPaymentMethod(RecurringEntity)`. Don't look for it alongside `CreditCardData`/`ECheck`/`GiftCard` in `payment_methods/`.

> **Real divergence — GP Ecom has no dedicated config class.** There is no `GpEcomConfig` anywhere in the source tree. GP Ecom (internally still named "Realex") is reached by setting `merchant_id` and `shared_secret` on **`PorticoConfig`** — `ServicesContainer.configure()` inspects `config.merchant_id` at runtime and routes to `RealexConnector` instead of `PorticoConnector` when it is set (`globalpayments/api/__init__.py`, lines 271–297). Leaving `merchant_id` unset and setting `secret_api_key` or the 5-point legacy fields routes to Portico instead. See Gateway Configuration in `references/REFERENCE.md` for the full pattern, confirmed against a real GP Ecom test (`tests/integration/gateways/realex_connector/test_credit.py`).

### Exception Hierarchy
```text
ApiException
├── BuilderException                — missing required builder fields
├── ConfigurationException          — bad config (missing creds, wrong env)
├── GatewayException                — gateway-level errors / declined (carries response_code, response_message)
├── MessageException                — device message error
└── UnsupportedTransactionException — gateway doesn't support operation

ArgumentException                   — NOT a subclass of ApiException; extends Exception directly
```

> **Real quirk, confirmed by reading the complete 87-line `exceptions.py`.** `ArgumentException` does not extend `ApiException` the way every other exception class in the file does — it extends the built-in `Exception`. A `try`/`except ApiException` block will **not** catch it. If you're catching broadly, add a separate `except ArgumentException` clause.

---

## Code Reference

All quick-copy Python snippets (installation, config, payment methods, charge, authorize, capture, void, refund, verify, tokenization, recurring, 3DS, reporting, error handling) are in **[REFERENCE.md](./references/REFERENCE.md)**.

Use `references/REFERENCE.md` as your snippet source when generating code for users. Verify any class or method against https://github.com/globalpayments/python-sdk before emitting it.

---

## Test Cards

**Do not include real or hardcoded card numbers in code samples.** Direct users to the portal testing page for the full list of sandbox cards:

👉 https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

**Sandbox card rule:** Any future-dated card number that passes a Luhn/mod-10 check will be accepted in the sandbox environment. Use the portal testing page for specific cards that trigger particular responses (declines, AVS mismatches, 3DS scenarios, etc.).

---

## Execution Rules

1. **Portal first.** For every operation, link to the relevant portal page before generating Python code. The portal defines the API contract (required fields, response shape, expected status values).
2. **Verify against GitHub.** Before emitting any class, constructor, or method chain, confirm it exists in the SDK source at https://github.com/globalpayments/python-sdk. Remember the layout: `GpApiConfig`/`PorticoConfig`/`ServicesContainer` are in `globalpayments/api/__init__.py`; connectors are in `globalpayments/api/gateways/__init__.py`. If you can't confirm something, say so and point the user to the repo.
3. **Use the test suite as a code reference — but check whether it's active.** `tests/integration/gateways/` contains working Python patterns for every operation. Some files (e.g. `gpapi_test_3ds_2.py`) are entirely commented out; verify a test file is live code, not disabled scaffolding, before citing it as proof a chain works.
4. **No hardcoded card numbers.** Always use placeholder values (`"CARD_NUMBER"`, `"CVV"`, etc.) and point users to https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md for sandbox cards.
5. **Methods and fields are snake_case throughout — use the exact names confirmed in source.** Do not assume a name carries over unchanged in casing — verify every name against source. Examples confirmed directly against source: `with_currency`, `with_amount`, `with_address`, `check_enrollment`, `initiate_authentication`, `get_authentication_data`, `and_with`. One confirmed exception: `SearchCriteriaBuilder`'s internal attribute names (`accountId`, `startDate`, etc., in `entities/reporting/search_criteria_builder.py`) are camelCase, matching the `SearchCriteria` enum's string values — this is an intentional pass-through, not a naming bug, and you never set those attributes directly; you go through `.where()`/`.and_with()`.
6. **Connectors and `ServicesContainer` live in `globalpayments/api/__init__.py`, not in per-file modules.** Import with `from globalpayments.api import GpApiConfig, PorticoConfig, ServicesContainer`, not a deep `ServiceConfigs.Gateways.*` path.
7. **`ServicesContainer.configure(config, config_name="default")` — not `configureService`.** Confirmed in `globalpayments/api/__init__.py`. Call it before any transaction. Multiple gateways can be configured under different `config_name` values in the same process (e.g. `"default"` and `"realex"`), confirmed by the SDK's own Realex test suite.
8. **GP Ecom has no dedicated config class — use `PorticoConfig` with `merchant_id` + `shared_secret`.** Setting `secret_api_key` or the 5-point legacy fields (`site_id`/`license_id`/`device_id`/`username`/`password`) on the same `PorticoConfig` class routes to Portico instead; setting `merchant_id` (plus `shared_secret`, and typically `account_id`) routes to GP Ecom via `RealexConnector`. These are mutually exclusive on the same config instance — don't set both a Portico credential set and `merchant_id` on one object.
9. **Python version floor: 3.11.** Confirmed from `pyproject.toml`: `python = "^3.11"` (and PyPI's `requires_python: ">=3.11,<4.0"`). Do not write code depending on a stdlib feature introduced after 3.11 unless the user has confirmed a newer interpreter.
10. **Builder chains.** Every transaction ends with `.execute()` or `.execute(config_name)`. Never skip it. `.execute()` is synchronous — this SDK has no async/await surface.
11. **`Credit` (base of `CreditCardData`/`CreditTrackData`) has no `.void()` method — only `.reverse()`.** Confirmed by reading the complete `payment_methods/credit.py`. `Transaction.void()` does exist (`entities/__init__.py`), but see rule 12 for where it actually works.
12. **Void vs. Reverse is gateway-specific, and GP API's `.void()` fails silently, not with a clean exception.** `GpApiManagementRequestBuilder.build_request()` (`builders/request_builder/GpApi/GpApiManagementRequestBuilder.py`) has no `elif` branch for `TransactionType.Void` — confirmed by reading its full `if`/`elif` chain. When no branch matches, the method falls through to its initialized defaults (`endpoint = ""`, `verb = HttpVerb.POST`) and returns a malformed request instead of raising — there is no `TypeError`, no `UnsupportedTransactionException`, just a broken HTTP call. **Always use `.reverse()` on GP API.** Portico's `PorticoConnector` handles `TransactionType.Void` and `TransactionType.Reversal` as distinct operations (`CreditVoid` vs `CreditReversal`). GP Ecom's `RealexConnector` maps *both* `Void` and `Reversal` to the same `"void"` operation — confirmed in `gateways/__init__.py`, and confirmed working end-to-end in `tests/integration/gateways/realex_connector/test_credit.py` (`response.void().execute("realex")`). Use `.void()` for Portico and GP Ecom.
13. **`ECheck` supports only `.charge()` — no `.authorize()`/`.refund()`/`.reverse()`/`.verify()`.** Confirmed by reading the complete 72-line `payment_methods/echeck.py`. Don't offer a refund/void flow for ACH in this SDK unless the user confirms a newer source version adds it.
14. **`ReportingService` exposes only four static methods** — `.activity()`, `.transaction_detail()`, `.find_transactions_paged()`, `.find_transactions()` (confirmed, complete 48-line `services/reporting_service.py`). There is no `.find_deposits_paged()`/`.find_disputes_paged()` facade. The `ReportType` enum does define `FindDepositsPaged`/`FindDisputesPaged` values, and `TransactionReportBuilder` does have `.with_deposit_id()`/`.with_settlement_dispute_id()` setters — to run those reports, construct `TransactionReportBuilder(ReportType.FindDepositsPaged)` directly rather than going through `ReportingService`. See Reporting in `references/REFERENCE.md`.
15. **`Customer.add_payment_method()` only builds a local object — it does not call the gateway.** A separate `.create()` call (inherited from `RecurringEntity`) is required to persist it — skipping it is a common source of silently-unpersisted payment methods.
16. **Test vs. Production.** Default all generated code to `Environment.Test`. Flag where `Environment.Production` applies. Confirmed casing: `Environment.Test`, `Environment.Production`, `Environment.Qa` (`entities/enums.py`).
17. **3DS is 4 server-side steps, grounded in GP API's own (active) test suite, not the `gpecom-3ds2` sample.** `Secure3dService.check_enrollment(card)` → `Secure3dService.initiate_authentication(card, secure_ecom)` with `BrowserData` → optionally handle `CHALLENGE_REQUIRED` → `Secure3dService.get_authentication_data()`, then set `card.three_d_secure = result` before charging. Three `GpApiConfig` fields are required: `merchant_contact_url`, `method_notification_url`, `challenge_notification_url`. Reference: `tests/integration/gateways/GpApi_connector/gpapi_test_3DSecure.py` (active) targets **GP API**, not GP Ecom — the only Python sample-repo hit for the "3ds2" topic (`gpecom-3ds2`) is boilerplate that doesn't implement the flow (see Sample Repos). See the full 3DS section in `references/REFERENCE.md`.
18. **When the user has a partial snippet**, identify which step they're on, fill in what's missing, validate the whole flow end-to-end, and link to the relevant portal page.
