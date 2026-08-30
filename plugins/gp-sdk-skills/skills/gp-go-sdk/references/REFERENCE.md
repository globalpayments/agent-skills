# GP Go SDK — Code Reference

Quick-copy Go snippets for the `globalpayments/go-sdk`. All struct names, constructors, and method chains are verified against the SDK source at https://github.com/globalpayments/go-sdk (default branch `main`) and its integration test suite at `tests/integration/gateways/`. This SDK covers **Portico only** — see the Scope table in `../SKILL.md` for what is out of scope.

---

## Installation

```bash
go get github.com/globalpayments/go-sdk
```

Requirements per `README.md`: Go 1.18+, `github.com/shopspring/decimal` v1.3.1+.

**Note the repo's actual pin is newer than the README floor.** `go.mod` (confirmed 2026-08-06) specifies `go 1.23.0` with `toolchain go1.24.1`, and pulls `github.com/shopspring/decimal v1.4.0`. Treat 1.18+ as the documented minimum but expect a current checkout to require a newer local Go toolchain.

```go
import (
    "github.com/globalpayments/go-sdk/api"
    "github.com/globalpayments/go-sdk/api/serviceconfigs"
    "github.com/globalpayments/go-sdk/api/paymentmethods"
    "github.com/globalpayments/go-sdk/api/entities/transactions"
    "github.com/shopspring/decimal"
)
```

---

## Gateway Configuration

### Portico — secret API key (recommended)

```go
package main

import (
    "github.com/globalpayments/go-sdk/api"
    "github.com/globalpayments/go-sdk/api/entities/enums/environment"
    "github.com/globalpayments/go-sdk/api/serviceconfigs"
)

func configure() error {
    config := serviceconfigs.NewPorticoConfig()
    config.SecretApiKey = "skapi_cert_YOUR_KEY" // skapi_prod_... in production
    config.Environment = environment.TEST        // environment.PRODUCTION for live
    config.EnableLogging = true

    return api.ConfigureService(config, "default")
}
```

### Portico — 5-point legacy credentials

Mutually exclusive with `SecretApiKey` — `PorticoConfig.Validate()` (`api/serviceconfigs/PorticoConfig.go`) rejects a config that sets both.

```go
config := serviceconfigs.NewPorticoConfig()
config.SiteId    = "SITE_ID"
config.LicenseId = "LICENSE_ID"
config.DeviceId  = "DEVICE_ID"
config.Username  = "USERNAME"
config.Password  = "PASSWORD"
config.Environment = environment.TEST

if err := api.ConfigureService(config, "default"); err != nil {
    // handle configuration error — validate() requires all five fields
    // present together, or none of them
    return err
}
```

`PorticoConfig` also exposes `VersionNumber`, `DeveloperId`, `SafDataSupported` (bool, store-and-forward), `Timeout` (via embedded `Configuration`), and `ServiceUrl` (auto-set to the Portico test/production endpoint if left blank). Confirmed fields: `api/serviceconfigs/PorticoConfig.go`.

### GP API / GP Ecom

**Not available.** `api/serviceconfigs/` contains only `Configuration.go`, `GatewayConfig.go`, `PorticoConfig.go` — there is no `GpApiConfig` or `GpEcomConfig` type anywhere in the repo tree (confirmed by path search, 2026-08-06). Use the PHP, Java, .NET, Node.js or Python SDK for GP API or GP Ecom integrations.

---

## Payment Methods

Confirmed types in `api/paymentmethods/`: `Credit`/`CreditCardData`, `Debit`/`DebitTrackData`, `EBT`/`EBTCardData`/`EBTTrackData`, `GiftCard`. **There is no `ECheck`/ACH type** — zero `echeck`/`ach` path hits in the tree.

### Credit Card (manual entry)

`CreditCardData` keeps `number`, `cvn`, and `expYear` as unexported fields reached only through setters; `ExpMonth` is exported but still a pointer (`*int`), matching `expYear`'s shape.

```go
import "github.com/globalpayments/go-sdk/api/paymentmethods"

card := paymentmethods.NewCreditCardData()
card.SetNumber("CARD_NUMBER") // see Test Cards below
card.SetCvn("CVV")

month := 12
year := 2026
card.SetExpMonth(&month)
card.SetExpYear(&year)
card.SetCardHolderName("Jane Smith")
```

### Credit Card (token)

```go
card := paymentmethods.NewCreditCardDataWithToken("TOKEN_VALUE")
```

### Gift Card

```go
gift := paymentmethods.NewGiftCard()
gift.SetNumber("GIFT_CARD_NUMBER")
```

### Debit (track data — card present)

```go
track := paymentmethods.NewDebitTrackData()
track.SetValue("TRACK_DATA_STRING")
```

---

## Core Transactions

Every gateway builder is executed with the package-level generic function `api.ExecuteGateway[T](ctx, builder)` — there is no `.Execute()` you call directly on `CreditCardData`; charge/authorize/etc. return an `*builders.AuthorizationBuilder`, which is then passed to `ExecuteGateway`. Confirmed pattern: `tests/integration/gateways/portico/PorticoCredit_test.go`.

### Charge (sale — auth + capture)

```go
import (
    "context"
    "github.com/globalpayments/go-sdk/api"
    "github.com/globalpayments/go-sdk/api/entities/transactions"
    "github.com/globalpayments/go-sdk/api/utils/stringutils"
)

ctx := context.Background()

amount, err := stringutils.ToDecimalAmount("29.99")
if err != nil {
    return err
}

charge := card.ChargeWithAmount(amount)
charge.WithCurrency("USD")
charge.WithAllowDuplicates(true)

response, err := api.ExecuteGateway[transactions.Transaction](ctx, charge)
if err != nil {
    return err
}

transactionId := response.GetTransactionId()
responseCode := response.GetResponseCode() // "00" == approved
```

### Authorize (hold, capture later)

```go
amount, err := stringutils.ToDecimalAmount("29.99")
if err != nil {
    return err
}

auth := card.AuthorizeWithAmount(amount, false) // isEstimated=false
auth.WithCurrency("USD")

response, err := api.ExecuteGateway[transactions.Transaction](ctx, auth)
if err != nil {
    return err
}
```

### Capture

Follow-on operations hang off the `*transactions.Transaction` you got back from the authorize call, not off the card.

```go
captureAmount, err := stringutils.ToDecimalAmount("29.99")
if err != nil {
    return err
}

capture := response.CaptureWithAmount(captureAmount)
captureResponse, err := api.ExecuteGateway[transactions.Transaction](ctx, capture)
if err != nil {
    return err
}
```

### Void

```go
voidBuilder := response.Void(nil, false) // amount nil, force=false
voidResponse, err := api.ExecuteGateway[transactions.Transaction](ctx, voidBuilder)
if err != nil {
    return err
}
```

If you only have a transaction ID and no live `Transaction` object (e.g. it came from storage), reconstruct one first:

```go
import (
    "github.com/globalpayments/go-sdk/api/builders/rebuilders"
    "github.com/globalpayments/go-sdk/api/entities/enums/paymentmethodtype"
)

txn := rebuilders.FromId(storedTransactionId, paymentmethodtype.Credit)
voidResponse, err := api.ExecuteGateway[transactions.Transaction](ctx, txn.Void(nil, false))
if err != nil {
    return err
}
```

### Refund / Reverse

`Refund()` settles a standalone credit; `Reverse()` reverses an unsettled authorization or sale. Both exist as methods on `*transactions.Transaction` (`response.RefundWithAmount(...)`, `response.ReverseWithAmount(...)`). `CreditCardData` itself only overrides `ReverseWithAmount(amount)` for a standalone reversal not tied to a prior transaction — confirmed in `api/paymentmethods/CreditCardData.go`. There is no card-level `Refund`/`RefundWithAmount` override: `CreditCardData` embeds `Credit`, whose `RefundWithAmount(amount *decimal.Decimal, pm abstractions2.IPaymentMethod)` takes a second payment-method argument (`api/paymentmethods/Credit.go`), so a single-argument `card.RefundWithAmount(amount)` will not compile. Issue a standalone refund through `response.RefundWithAmount(...)` on a prior transaction instead.

```go
refundAmount, err := stringutils.ToDecimalAmount("10.00")
if err != nil {
    return err
}

// Refund a settled transaction
refund := response.RefundWithAmount(refundAmount)
refundResponse, err := api.ExecuteGateway[transactions.Transaction](ctx, refund)
if err != nil {
    return err
}

// Reverse a card-level standalone transaction (not tied to a prior response)
reversal := card.ReverseWithAmount(refundAmount)
reversal.WithCurrency("USD")
reversalResponse, err := api.ExecuteGateway[transactions.Transaction](ctx, reversal)
if err != nil {
    return err
}
```

### Verify

```go
verify := card.Verify()
verify.WithAllowDuplicates(true)

response, err := api.ExecuteGateway[transactions.Transaction](ctx, verify)
if err != nil {
    return err
}
```

---

## Address Verification (AVS)

`base.Address` fields (confirmed `api/entities/base/Address.go`): `StreetAddr1`, `StreetAddr2`, `StreetAddr3`, `City`, `Province` (state — reached via `GetState()`/`SetState()`, there is no `State` field name), `PostalCode`, `Country`, `CountryCode`, `Type` (`addresstype.AddressType`). There is no `StreetAddress1` spelling.

```go
import "github.com/globalpayments/go-sdk/api/entities/base"

address := base.NewAddressWithStreet("30301", "1 Main Street")
address.City = "Atlanta"
address.SetState("GA")
address.Country = "US"

amount, err := stringutils.ToDecimalAmount("100.00")
if err != nil {
    return err
}
charge := card.ChargeWithAmount(amount)
charge.WithCurrency("USD")
charge.WithAddress(address)

response, err := api.ExecuteGateway[transactions.Transaction](ctx, charge)
if err != nil {
    return err
}

avsCode := response.GetAvsResponseCode()
avsMessage := response.GetAvsResponseMessage()
cvnCode := response.GetCvnResponseCode()
cvnMessage := response.GetCvnResponseMessage()
```

---

## Hosted Fields

**Not applicable to this SDK.** This SDK has no GP API connector and no equivalent access-token service — there is nothing to generate a browser-safe hosted-fields token with. For a web-facing card-collection flow, use the PHP, Java, .NET, Node.js, or Python SDK on the server side.

---

## Tokenization

Portico supports a multi-use token flow through `Verify()` + `WithRequestMultiUseToken(true)`, confirmed in `tests/integration/gateways/portico/PorticoTokenManagement_test.go`.

### Store a card as a multi-use token

```go
verify := card.Verify()
verify.WithRequestMultiUseToken(true)

response, err := api.ExecuteGateway[transactions.Transaction](ctx, verify)
if err != nil {
    return err
}

token := response.GetToken()
```

### Charge a stored token

```go
tokenCard := paymentmethods.NewCreditCardDataWithToken(token)

amount, err := stringutils.ToDecimalAmount("50.00")
if err != nil {
    return err
}
charge := tokenCard.ChargeWithAmount(amount)
charge.WithCurrency("USD")

response, err := api.ExecuteGateway[transactions.Transaction](ctx, charge)
if err != nil {
    return err
}
```

### Update token expiry / delete a token

These are methods on `Credit`/`CreditCardData` that take a `context.Context` and a live gateway (not a builder passed to `ExecuteGateway`):

```go
gateway, err := api.LoadGateway()
if err != nil {
    return err
}

tokenCard := paymentmethods.NewCreditCardDataWithToken(token)
newMonth, newYear := 1, 2027
tokenCard.SetExpMonth(&newMonth)
tokenCard.SetExpYear(&newYear)

ok, err := tokenCard.UpdateToken(ctx, gateway)
if err != nil {
    return err
}
if !ok {
    return errors.New("token expiry update failed")
}

// Or delete it entirely:
deleted, err := tokenCard.DeleteToken(ctx, gateway)
```

---

## Recurring Billing

**Effectively unusable as shipped — flag this rather than generating a flow that will silently fail.** `api/entities/recurring/Customer.go` and `RecurringEntity.go` exist with `Create()`/`SaveChanges()`/`Delete()`/`ForceDelete()` on the `abstractions.IRecurringEntity` interface. But `PorticoConfig.ConfigureContainer` (`api/serviceconfigs/PorticoConfig.go`) never calls `services.SetRecurringConnector(...)` — the PayPlan wiring is present only as commented-out source:

```go
// from api/serviceconfigs/PorticoConfig.go, ConfigureContainer() — commented out in source:
//payplan := &PayPlanConnector{}
//payplan.SetSecretApiKey(gc.SecretApiKey)....
//services.SetRecurringConnector(payplan)
```

No `PayPlanConnector` type exists anywhere in the repo tree (confirmed by path search). A `Customer` built with this SDK has no configured recurring connector to call through — `Create()` has nothing to reach. Do not generate a working recurring-billing integration for this SDK. Point the user at the PHP, Java, .NET, or Node.js SDK for working recurring billing.

---

## 3D Secure 2

**Not supported.** `api/entities/ThreeDSecure.go` exists as a plain data entity (embedded on `Credit` as `ThreeDSecure *entities.ThreeDSecure`, confirmed in `api/paymentmethods/Credit.go`), and `api/entities/enums/securethreedversion/Secure3dVersion.go` is an enum used to tag legacy MPI data on a Portico request. But there is **no `Secure3dService`** anywhere in the tree — no `checkEnrollment`, `initiateAuthentication`, or `getAuthenticationData` orchestration exists (confirmed: zero `Secure3dService` path hits, 2026-08-06). Never emit a 3DS2 enrollment/authentication flow for this SDK — there is no service to call. Use the PHP, Java, .NET, Node.js, or Python SDK for 3DS2.

---

## Reporting

`reportingservice` (`api/services/reportingservice/ReportingService.go`) returns a `*builders.TransactionReportBuilder`, executed the same way as a payment builder — through `api.ExecuteGateway[T]`, but with `transactionsummary.ActivityReport` as the type parameter instead of `transactions.Transaction`.

```go
import (
    "time"
    "github.com/globalpayments/go-sdk/api/entities/transactionsummary"
    "github.com/globalpayments/go-sdk/api/services/reportingservice"
    "github.com/globalpayments/go-sdk/api/utils/stringutils"
)

startDate := stringutils.ToStandardDateString(time.Now().AddDate(0, 0, -7))
endDate := stringutils.ToStandardDateString(time.Now())

activity := reportingservice.Activity().
    WithStartDate(startDate).
    WithEndDate(endDate)

report, err := api.ExecuteGateway[transactionsummary.ActivityReport](ctx, activity)
if err != nil {
    return err
}

for _, txn := range report.TransactionSummaries {
    _ = txn.TransactionId
    _ = txn.GatewayResponseCode
}

// Detail for a specific transaction
detail := reportingservice.FindTransactionsWithID(report.TransactionSummaries[0].TransactionId)
detailReport, err := api.ExecuteGateway[transactionsummary.ActivityReport](ctx, detail)
if err != nil {
    return err
}
```

### Batch close

```go
import "github.com/globalpayments/go-sdk/api/services/batchservice"

batchClose := batchservice.CloseBatch()
batchResponse, err := api.ExecuteGateway[transactions.Transaction](ctx, batchClose)
if err != nil {
    return err
}
```

---

## Error Handling

This SDK has **no exception hierarchy** — it uses Go's idiom throughout: every fallible call returns `(result, err)`, and `err` is a plain `error` interface value that is one of several unrelated concrete types. There is nothing to `catch`; check `err != nil` and, if you need to branch on the failure kind, use a type switch or `errors.As`.

```go
import (
    "context"
    "errors"
    "github.com/globalpayments/go-sdk/api"
    "github.com/globalpayments/go-sdk/api/entities/exceptions"
    "github.com/globalpayments/go-sdk/api/entities/transactions"
    "github.com/globalpayments/go-sdk/api/gateways"
)

ctx := context.Background()

response, err := api.ExecuteGateway[transactions.Transaction](ctx, charge)
if err != nil {
    var builderErr *exceptions.BuilderException
    var configErr *exceptions.ConfigurationException
    var unsupportedErr *exceptions.UnsupportedTransactionException
    var gatewayErr *gateways.GatewayResponseError

    switch {
    case errors.As(err, &builderErr):
        // missing/invalid required builder field, e.g. no currency
    case errors.As(err, &configErr):
        // bad or conflicting PorticoConfig — e.g. both SecretApiKey and legacy fields set
    case errors.As(err, &unsupportedErr):
        // Portico doesn't support this operation
    case errors.As(err, &gatewayErr):
        // gateway-level decline/error — carries an error code
        code := gatewayErr.GetErrorCode()
        _ = code
    default:
        // network error, context cancellation, or *exceptions.ApiException / MessageException
    }
    return err
}

if response.GetResponseCode() != "00" {
    // approved-but-not-"00": inspect response.GetResponseMessage()
}
```

Real exported error types, confirmed by source read: `api/entities/exceptions/{ApiException,BuilderException,ConfigurationException,MessageException,UnsupportedTransactionException}.go` (each a flat struct with `message`/`innerException`, no shared base type beyond the `error` interface) and `api/gateways/GatewayResponse.go`'s `GatewayResponseError` (message + `errorCode`). There is no `GatewayException` and no `ValidationException` name in this SDK.

---

## Terminal Operations

Semi-integrated control of a physical UPA (Unified Payments Application) terminal over TCP/IP or HTTP. Confirmed source: `api/terminals/`, `api/services/deviceservice/DeviceService.go`, `api/TerminalExecutor.go`, `tests/integration/gateways/terminals/upa/`.

Terminal support is the largest part of this SDK relative to its size. It supports **UPA only** — 62 terminal files under `api/terminals/` (confirmed by path search, 2026-08-06), with no PAX, HPA, Genius, or Diamond connector. If you need one of those device families, use the PHP, .NET or Java SDK.

`DeviceService` creates an `IDeviceInterface` from a `ConnectionConfig`, and device methods return terminal builders.

### Connect to a terminal

```go
import (
    "github.com/globalpayments/go-sdk/api/entities/enums/connectionmodes"
    "github.com/globalpayments/go-sdk/api/entities/enums/devicetype"
    "github.com/globalpayments/go-sdk/api/services/deviceservice"
    "github.com/globalpayments/go-sdk/api/terminals"
    "github.com/globalpayments/go-sdk/api/terminals/abstractions"
)

config := terminals.NewConnectionConfig()
config.IpAddress = "192.168.1.100"
config.Port = 8081
config.Timeout = 45000 // milliseconds
config.DeviceType = devicetype.UPA_DEVICE
config.ConnectionMode = connectionmodes.TCP_IP

var device abstractions.IDeviceInterface
device, err := deviceservice.DeviceServiceCreate(config)
if err != nil {
    return err
}
```

`ConnectionConfig` (`api/terminals/ConnectionConfig.go`) also exposes `BaudRate`, `Parity`, `StopBits`, `DataBits` (for serial connections) and `RequestIdProvider` (an `abstractions.IRequestIdProvider` you can supply for deterministic request IDs in tests). `Validate()` requires `IpAddress` and a non-zero `Port` when `ConnectionMode` is `TCP_IP` or `HTTP`.

### Run a sale on the terminal

`IDeviceInterface` (`api/terminals/abstractions/IDeviceInterface.go`) exposes `CreditSale`, `CreditAuth`, `CreditRefund`, `CreditVoid`, `CreditCapture`, `DebitSale`, `DebitRefund`, `DebitVoid`, `GiftAddValue`, `TipAdjust`, `EndOfDay`, `Ping`, `Reboot`, and more — each returns a `*builders.TerminalAuthBuilder` (or `*builders.TerminalManageBuilder` for capture/tip-adjust) plus an `error`, which is then run through `api.ExecuteTerminal`.

```go
import (
    "github.com/globalpayments/go-sdk/api"
    "github.com/globalpayments/go-sdk/api/utils/stringutils"
)

amount, err := stringutils.ToDecimalAmount("12.01")
if err != nil {
    return err
}

terminalAuth, err := device.CreditSale(amount)
if err != nil {
    return err // setup error — device unreachable, etc.
}

response, err := api.ExecuteTerminal(terminalAuth)
if err != nil {
    return err // transaction-level error
}

status := response.GetStatus()               // e.g. "Success" / "Failed"
terminalRefNumber := response.GetTerminalRefNumber()
```

### Cancel with context (long-running terminal operations)

```go
import (
    "context"
    "time"
)

ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

response, err := api.ExecuteTerminalWithContext(ctx, terminalAuth)
if err != nil {
    // err wraps "context canceled" or "context deadline exceeded" if the
    // customer walks away from the terminal before completing the tap/dip
    return err
}
```

### Void a terminal transaction

Terminal void uses the response's `TerminalRefNumber`, not a gateway transaction ID:

```go
voidBuilder, err := device.CreditVoid()
if err != nil {
    return err
}

voidResponse, err := api.ExecuteTerminal(voidBuilder.WithTerminalRefNumber(response.GetTerminalRefNumber()))
if err != nil {
    return err
}
```

### `TerminalAuthBuilder` (sale/auth/refund shape)

Confirmed fields/methods (`api/terminals/builders/TerminalAuthBuilder.go`): `WithAmount`, `WithCurrency`, `WithAddress`, `WithGratuity`, `WithCashBack`, `WithAllowDuplicates`, `WithSignatureCapture`, `WithInvoiceNumber`, `WithPoNumber`, `WithTaxAmount`, `WithTaxType`, `WithRequestMultiUseToken`, `WithCardBrandStorage`. All builder methods return `*TerminalAuthBuilder` for chaining, then run through `api.ExecuteTerminal` (or `ExecuteWithName`/`ExecuteTerminalWithContext` for a named config or explicit context).

### `TerminalManageBuilder` (capture/tip-adjust shape)

Confirmed fields/methods (`api/terminals/builders/TerminalManageBuilder.go`): `WithAmount`, `WithCurrency`, `WithGratuity`, `WithTerminalRefNumber`, `WithTransactionId`. Returned by `device.CreditCapture(amount)`, `device.TipAdjust(amount)`, and `device.CreditVoid()`/`device.DebitVoid()`.

```go
capture, err := device.CreditCapture(amount)
if err != nil {
    return err
}
captureResponse, err := api.ExecuteTerminal(capture.WithTerminalRefNumber(response.GetTerminalRefNumber()))
if err != nil {
    return err
}
```

### End of day / batch close on the terminal

```go
eodResponse, err := device.EndOfDay()
if err != nil {
    return err
}
```

---

## Test Cards

**Do not hardcode real card numbers in generated integration code.** Use placeholders and point users to https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md. The table below is published directly in the SDK's own `README.md` for its integration tests — sandbox test data, not cardholder data.

| Brand | Number | Exp Month | Exp Year | CVN |
|---|---|---|---|---|
| Visa | `4263970000005262` | 12 | 2025 | 123 |
| MasterCard | `2223000010005780` | 12 | 2019 | 900 |
| MasterCard | `5425230000004415` | 12 | 2025 | 123 |
| Discover | `6011000000000087` | 12 | 2025 | 123 |
| Amex | `374101000000608` | 12 | 2025 | 1234 |
| JCB | `3566000000000000` | 12 | 2025 | 123 |
| Diners Club | `36256000000725` | 12 | 2025 | 123 |

Source: `README.md`, `globalpayments/go-sdk` @ `main` (2026-08-06). Some of these expiry years are already in the past relative to the plan date — sandbox environments generally accept expired test-card dates for non-production certification traffic, but confirm current behavior against the portal testing page before relying on an exact date.
