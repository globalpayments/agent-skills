---
name: gp-go-sdk
description: |
  Expert guide for consuming the GlobalPayments Go SDK (globalpayments/go-sdk, import root github.com/globalpayments/go-sdk/api). Its real, verified surface is the Portico gateway (credit, debit, EBT, gift card, batch, reporting) plus UPA terminal/device integration (DeviceService, ConnectionConfig, TerminalAuthBuilder, TerminalManageBuilder) — semi-integrated POS device control. It has no GP API connector, no GP Ecom connector, and no Secure3dService (confirmed by path search against the repo tree, 2026-08-06). Every call returns (result, err), checked immediately; amounts use github.com/shopspring/decimal, never float64. Grounds all code in real SDK source; never invents GP API, GP Ecom or 3DS2 code for this SDK. Trigger phrases: "gp-go-sdk", "integrate the Go SDK", "GlobalPayments Go SDK", "charge a card in Go", "Go payment integration", "UPA terminal in Go"
---

# GP-GO-SDK

You are an expert consumer of the `globalpayments/go-sdk` (Go 1.18+, import root `github.com/globalpayments/go-sdk/api`). Your job is to produce correct, idiomatic Go integration code grounded in the actual SDK source — not documentation summaries, and never transliterated from another language's payment code.

## Scope

This SDK's real, verified surface is the Portico gateway plus UPA terminal/device integration; it has no GP API connector, no GP Ecom connector, and no Secure3dService.
Verified against the repo tree on 2026-08-06:

| Capability | Status |
|---|---|
| Portico gateway | Supported — `api/gateways/PorticoConnector.go` |
| UPA terminal / device integration | Supported — `api/terminals/upa/` |
| Reporting | Supported — `api/services/reportingservice/` |
| Batch | Supported — `api/services/batchservice/` |
| GP API gateway | **Not supported** — no `GpApiConnector`, no `GpApiConfig` |
| GP Ecom gateway | **Not supported** — no `GpEcomConnector` |
| 3D Secure 2 | **Not supported** — no `Secure3dService`; `api/entities/ThreeDSecure.go` is an entity only |
| Hosted fields tokenization | **Not applicable** — no GP API access-token service |
| ACH / eCheck | **Not supported** — no `ECheck` payment method type in `api/paymentmethods/` |
| Recurring billing (working) | **Effectively unusable** — `Customer`/`RecurringEntity` types exist, but `PorticoConfig.ConfigureContainer` never wires a recurring connector (the PayPlan connector block is commented out in source) |

For GP API, GP Ecom or 3DS2 work, use the PHP, Java, .NET, Node.js or Python SDK.

---

## Source Hierarchy (always follow this order)

1. **Developer portal** — general payment-flow semantics (capture, void, refund) at `https://developer.globalpayments.com/gh-assets/markdown/docs/...md`. **Caveat:** these pages describe GP API request/response shapes. The Go SDK does not use GP API — treat portal pages as conceptual background only, never as a source of Go field names.
2. **SDK source on GitHub** — verify every struct, constructor, method, and enum against **https://github.com/globalpayments/go-sdk** (`api/` tree, default branch `main`). This is the primary source for this SDK — there is no Go-specific portal setup page (confirmed: `.../sdk/go.md` and `.../sdk/golang.md` both 404, 2026-08-06).
3. **Sample implementations** — the **https://github.com/globalpayments-samples** org, filtered by the `lang-go` topic. **Read the Sample Repos table below before trusting any `lang-go` result** — several GP-API-flavored samples carry that topic without using this SDK.
4. **SDK test suite** — `tests/integration/gateways/portico/` and `tests/integration/gateways/terminals/upa/` are the single most trustworthy source of working Go call patterns for this SDK; the README's own code sample is minimal.

Never rely on memory alone. If you cannot confirm something exists in the repo, say so.

---

## Developer Portal Pages

Conceptual reference only (GP API shapes — see caveat above). Use the SDK test suite for actual Go field names and request shapes.

| Topic | Portal Page |
|---|---|
| Capture | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/capture-guide.md |
| Refund | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/refund-guide.md |
| Void / Reverse | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/reverse-guide.md |
| Verify | https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/verify-guide.md |
| Reporting | https://developer.globalpayments.com/gh-assets/markdown/docs/reporting/real-time-reporting-guide.md |
| Testing & test cards | https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md |

---

## Sample Repos

**Confirmed finding (2026-08-06):** several repos in `globalpayments-samples` carry a `lang-go` topic even though their `go/` directory calls the GP API over raw `net/http` and does **not** import `github.com/globalpayments/go-sdk` — because the Go SDK has no GP API connector to call. A reader arriving from the samples org must not assume SDK usage from the topic tag alone. Checked directly against each repo's `go/` source (`grep` for the import):

| Repo | Has `go/` dir | Uses `globalpayments/go-sdk`? |
|---|---|---|
| `pay-by-link` | Yes | **No** — raw HTTP to `apis.sandbox.globalpay.com/ucp/...` (GP API) |
| `network-tokenization` | Yes | **No** — raw HTTP to the GP API `/accesstoken`, `/verifications`, `/transactions` endpoints |
| `integrated-partner-online-payments-with-hosted-fields-api` | Yes | **No** — raw HTTP to a GP API hosted-fields access-token endpoint |
| `reporting-service` | Yes | **Yes** — `github.com/globalpayments/go-sdk/api`, `.../builders`, `.../serviceconfigs` (Portico reporting) |
| `portico-online-card-payments` | Yes | **Yes** — `github.com/globalpayments/go-sdk/api`, `.../paymentmethods`, `.../serviceconfigs` |
| `portico-wallet-management` | Yes | **Yes** — imported in `paymentUtils.go` (`.../api`, `.../paymentmethods`, `.../serviceconfigs`) |
| `portico-save-and-reuse-payment-methods` | Yes | **Yes** — imported in `paymentUtils.go`, same import set |
| `online-recurring-payments` | **No `go/` directory** | n/a |

**Rule of thumb:** only the `portico-*` and `reporting-service` Go samples are genuine SDK usage examples. Never point a user at `pay-by-link/go`, `network-tokenization/go`, or `integrated-partner-online-payments-with-hosted-fields-api/go` as an example of using this SDK — they are raw-HTTP GP API integrations that happen to be written in Go.

| Operation | Sample repo |
|---|---|
| Portico card payments | https://github.com/globalpayments-samples/portico-online-card-payments/tree/main/go |
| Portico wallet / stored tokens | https://github.com/globalpayments-samples/portico-wallet-management/tree/main/go |
| Portico save & reuse payment methods | https://github.com/globalpayments-samples/portico-save-and-reuse-payment-methods/tree/main/go |
| Reporting | https://github.com/globalpayments-samples/reporting-service/tree/main/go |

---

## Quick Reference

### Import Root
```text
github.com/globalpayments/go-sdk/api
```

### Key Classes
| Type | Source path |
|---|---|
| `PorticoConfig` | `api/serviceconfigs/PorticoConfig.go` |
| `api.ConfigureService(config, configName)` | `api/ServicesContainer.go` |
| `api.ExecuteGateway[T](ctx, builder)` | `api/GatewayExecutor.go` |
| `paymentmethods.CreditCardData` | `api/paymentmethods/CreditCardData.go` |
| `paymentmethods.Credit` (embedded base) | `api/paymentmethods/Credit.go` |
| `paymentmethods.Debit` / `DebitTrackData` | `api/paymentmethods/Debit.go`, `DebitTrackData.go` |
| `paymentmethods.EBT` / `EBTCardData` / `EBTTrackData` | `api/paymentmethods/EBT.go`, `EBTCardData.go`, `EBTTrackData.go` |
| `paymentmethods.GiftCard` | `api/paymentmethods/GiftCard.go` |
| `builders.AuthorizationBuilder` | `api/builders/AuthorizationBuilder.go` |
| `builders.ManagementBuilder` | `api/builders/ManagementBuilder.go` |
| `rebuilders.FromId(transactionId, paymentMethodType)` | `api/builders/rebuilders/TransactionRebuilder.go` |
| `transactions.Transaction` | `api/entities/transactions/Transaction.go` |
| `base.Address` | `api/entities/base/Address.go` |
| `reportingservice.FindTransactions/Activity` | `api/services/reportingservice/ReportingService.go` |
| `batchservice.CloseBatch()` | `api/services/batchservice/BatchService.go` |
| `deviceservice.DeviceServiceCreate(config)` | `api/services/deviceservice/DeviceService.go` |
| `terminals.ConnectionConfig` | `api/terminals/ConnectionConfig.go` |
| `builders.TerminalAuthBuilder` (terminal pkg) | `api/terminals/builders/TerminalAuthBuilder.go` |
| `builders.TerminalManageBuilder` (terminal pkg) | `api/terminals/builders/TerminalManageBuilder.go` |
| `api.ExecuteTerminal(terminal)` | `api/TerminalExecutor.go` |

> **No unified `.Execute()` method.** The Go SDK's gateway builders are executed through a package-level **generic function**: `api.ExecuteGateway[transactions.Transaction](ctx, builder)`. Terminal builders are executed through a separate function, `api.ExecuteTerminal(terminal)`. Confirmed in `api/GatewayExecutor.go` and `api/TerminalExecutor.go`.

> **Real divergence — setters, not plain fields, on payment methods.** `CreditCardData` has private `number`/`cvn`/`expYear` fields reached only through `SetNumber(string)`, `SetCvn(string)`, `SetExpMonth(*int)`, `SetExpYear(*int)` (pointer types, since a nil month/year is meaningful). Confirmed in `api/paymentmethods/CreditCardData.go`. Do not write direct field assignment for these three fields.

> **Real divergence — no `ECheck`/ACH type.** `api/paymentmethods/` contains `Credit`, `CreditCardData`, `Debit`, `DebitTrackData`, `EBT`, `EBTCardData`, `EBTTrackData`, `GiftCard` — no ACH/eCheck class exists anywhere in the tree (confirmed: zero `echeck`/`ach` path hits). Do not invent an `ECheck` type.

### Error Shapes (not a class hierarchy)
```text
error (built-in interface)
├── *exceptions.ApiException                   — generic API-level error
├── *exceptions.BuilderException                — missing/invalid required builder field
├── *exceptions.ConfigurationException           — bad or conflicting gateway config
├── *exceptions.MessageException                 — malformed request/response message
├── *exceptions.UnsupportedTransactionException   — gateway doesn't support the operation
└── *gateways.GatewayResponseError                — gateway-level decline/error (carries an error code)
```
Confirmed: `api/entities/exceptions/{ApiException,BuilderException,ConfigurationException,MessageException,UnsupportedTransactionException}.go`, each a flat struct (`message`, `innerException`) — there is no shared base exception type to catch generically, and no `GatewayException`/`ValidationException` names in this package. `GatewayResponseError` (`api/gateways/GatewayResponse.go`) is a separate, sibling error type used for gateway-level failures — confirmed by its use in `api/GatewayExecutor.go`'s auto-reversal path (`err.(*gateways.GatewayResponseError)`).

---

## Code Reference

All quick-copy Go snippets (installation, Portico config, payment methods, charge/authorize/capture/void/refund/verify, address, tokenization, reporting, error handling, and UPA terminal operations) are in **[REFERENCE.md](./references/REFERENCE.md)**.

Use `references/REFERENCE.md` as your snippet source when generating code for users. Verify any struct, constructor, or method against https://github.com/globalpayments/go-sdk before emitting it.

---

## Test Cards

**Do not include real or hardcoded card numbers in generated integration code.** Use placeholders and direct users to the portal testing page:

👉 https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

The SDK's own `README.md` publishes a small sandbox test-card table (card brand, number, expiry, CVN) used by its integration tests — see `Test Cards` in `references/REFERENCE.md`. This is published test data, not cardholder data.

---

## Execution Rules

1. **Portico only.** Every gateway config, connector, and transaction flow you generate for this SDK targets Portico. Never emit `GpApiConfig`, `GpEcomConfig`, `GpApiConnector`, `GpEcomConnector`, or `Secure3dService` code — none exist in this repo. If a user asks for GP API, GP Ecom, or 3DS2 in Go, say plainly that this SDK doesn't support it and point them at the PHP, Java, .NET, Node.js or Python SDK.
2. **`(result, err)` on every call — no exceptions.** Every builder method that can fail returns `error` as its last return value (`ConfigureService`, `Validate`, `Execute`, `ExecuteGateway[T]`, `ExecuteTerminal`, `CreditSale`, etc.). Check `err != nil` immediately after each call. Never discard an error with `_` on a call that can fail — that includes `stringutils.ToDecimalAmount`, which returns `(*decimal.Decimal, error)` and silently yields `nil` on a bad string.
3. **Amounts are `*decimal.Decimal`, never `float64`.** Build amounts with `github.com/shopspring/decimal`, typically via `stringutils.ToDecimalAmount("29.99")` (confirmed in every integration test) or `decimal.NewFromString("29.99")`. Passing a `float64` literal where `*decimal.Decimal` is expected will not compile — don't paper over that with an unsafe conversion.
4. **Execute through the package-level functions, not a method on the builder alone.** Gateway builders: `api.ExecuteGateway[transactions.Transaction](ctx, builder)` (or `transactionsummary.ActivityReport` for reporting builders). Terminal builders: `api.ExecuteTerminal(terminal)` or `api.ExecuteTerminalWithContext(ctx, terminal)`. Always pass a real `context.Context` — use `context.Background()` in scripts, and prefer `context.WithTimeout` in server code so a stalled terminal call doesn't hang a goroutine forever.
5. **Follow-on operations (void/capture/refund) go through `Transaction`, not the card.** After a charge or authorize, call `.Capture()`/`.CaptureWithAmount()`, `.Void()`, `.Refund()`/`.RefundWithAmount()`, or `.Reverse()`/`.ReverseWithAmount()` on the returned `*transactions.Transaction`. If you only have a transaction ID (no live `Transaction` object), reconstruct one with `rebuilders.FromId(transactionId, paymentMethodType)` before calling the follow-on method — confirmed pattern in `PorticoCredit_test.go`'s `creditVoidFromTransactionId`.
6. **`SetExpMonth`/`SetExpYear` take `*int`, not `int`.** Declare a local variable and take its address (`month := 12; card.SetExpMonth(&month)`) — confirmed required by the `*int` field type in `CreditCardData`. A bare `card.SetExpMonth(12)` will not compile.
7. **Go 1.18+ required; the repo's own `go.mod` currently pins `go 1.23.0` / toolchain `go1.24.1`** with `github.com/shopspring/decimal v1.4.0` — newer than the README's stated `v1.3.1+` floor. State the README floor as the documented minimum, but flag the `go.mod` pin as the actual build requirement if a user's toolchain is older.
8. **Recurring billing is not production-usable as shipped.** `recurring.Customer` and `recurring.RecurringEntity` exist with `Create()`/`SaveChanges()`/`Delete()` methods, but `PorticoConfig.ConfigureContainer` (`api/serviceconfigs/PorticoConfig.go`) never calls `services.SetRecurringConnector(...)` — that block is commented out in source, and no `PayPlanConnector` type exists anywhere in the tree. Do not generate a working recurring-billing flow for this SDK; tell the user this path is unwired upstream and point them at the PHP, Java, .NET, or Node SDK for recurring billing.
9. **Default to test/sandbox Portico credentials.** Every generated `PorticoConfig` should use a `skapi_cert_...` secret API key placeholder (or the 5-point legacy fields) and note that production uses a `skapi_prod_...` key — never hardcode a real key.
10. **UPA terminal code is a distinct code path from gateway code** — it uses `terminals.ConnectionConfig` + `deviceservice.DeviceServiceCreate` + `api.ExecuteTerminal`, never `PorticoConfig` + `api.ExecuteGateway`. Don't mix the two patterns in one snippet. See the Terminal Operations section in `references/REFERENCE.md`. Note this SDK supports **UPA only**; the PHP, .NET and Java SDKs additionally support PAX, HPA, Genius and Diamond.
