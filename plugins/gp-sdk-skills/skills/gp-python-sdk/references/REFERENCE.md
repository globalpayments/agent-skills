# GP Python SDK — Code Reference

Quick-copy Python snippets for the `globalpayments/python-sdk`. All class names, method chains, and field names are verified against the SDK source at https://github.com/globalpayments/python-sdk (default branch `master`).

---

## Installation

```bash
pip install GlobalPayments.Api
```

PyPI normalizes distribution names, so `pip install globalpayments-api` resolves to the same package. Confirmed: `pyproject.toml` declares `name = "GlobalPayments.Api"`, `version = "2.0.7"`, `python = "^3.11"` (PyPI's own metadata reports `requires_python: ">=3.11,<4.0"`). Requirements (from `pyproject.toml`): `xmltodict`, `jsonpickle`, `urllib3`, `certifi`, `pyopenssl`, `idna`, `dateparser`, `requests` — all installed automatically as dependencies.

Import root:
```python
import globalpayments.api
```

---

## Gateway Configuration

### GP API

```python
from globalpayments.api import GpApiConfig, ServicesContainer
from globalpayments.api.entities.enums import Environment, CardChannel

config = GpApiConfig()
config.app_id = "YOUR_APP_ID"
config.app_key = "YOUR_APP_KEY"
config.environment = Environment.Test              # Environment.Production for live
config.country = "US"
config.channel = CardChannel.CARD_NOT_PRESENT       # CardChannel.CARD_PRESENT for in-person

ServicesContainer.configure(config)
```

Optional GP API fields (confirmed, `globalpayments/api/__init__.py`):
```python
config.merchant_id               = "MER_xxx"
config.merchant_contact_url      = "https://yoursite.com/about"   # required for 3DS
config.method_notification_url   = "https://yoursite.com/3ds/method"
config.challenge_notification_url = "https://yoursite.com/3ds/challenge"
config.seconds_to_expire         = 3600
config.interval_to_expire        = 5
config.permissions               = ["TRN_POST_Authorize"]
config.dynamic_headers           = {"x-gp-platform": "your-platform;version=1.0"}
```

> **Real divergence — `CardChannel`, not `Channel`.** `GpApiConfig.channel` is typed `Optional[CardChannel]` with `SCREAMING_SNAKE_CASE` members: `CardChannel.CARD_NOT_PRESENT = "CNP"`, `CardChannel.CARD_PRESENT = "CP"` (`entities/enums.py`). A second, unrelated `Channel` enum also exists in the same file (`Channel.CardNotPresent = "CNP"`) but is not the type `GpApiConfig.channel` expects — don't use it here.

> **No `DataResidency` enum exists in this SDK**, confirmed absent from `entities/enums.py` (grepped the full 1240-line file) — there is no `config.data_residency` field on `GpApiConfig`.

> **No terminal / POS device support in this SDK.** Confirmed absent by full-tree path search (2026-08-06): zero paths match `/terminals/`, `DeviceService`, `ConnectionConfig` or any device controller. There is no semi-integrated device code path here at all — for POS terminal control, use the PHP, .NET, Java, Node.js or Go SDK.

### Portico (Heartland) — secret API key

```python
from globalpayments.api import PorticoConfig, ServicesContainer
from globalpayments.api.entities.enums import Environment

config = PorticoConfig()
config.secret_api_key = "skapi_cert_YOUR_KEY"
config.service_url    = "https://cert.api2.heartlandportico.com"

ServicesContainer.configure(config)
```

### Portico — 5-point legacy credentials

```python
config = PorticoConfig()
config.site_id    = "SITE_ID"
config.license_id = "LICENSE_ID"
config.device_id  = "DEVICE_ID"
config.username   = "USERNAME"
config.password   = "PASSWORD"

ServicesContainer.configure(config)
```

`PorticoConfig.validate()` (`globalpayments/api/__init__.py`) raises `ConfigurationException` if `secret_api_key` and any of the 5-point fields are both set, and raises if only *some* of the 5-point fields are set — all five or none.

### GP Ecom — no dedicated config class; reuse `PorticoConfig`

**Real, confirmed finding: this SDK has no `GpEcomConfig` class anywhere in its source tree.** GP Ecom is internally still named "Realex" (`RealexConnector` in `globalpayments/api/gateways/__init__.py`). You reach it by setting `merchant_id` and `shared_secret` on a **`PorticoConfig`** instance instead of the Portico-specific fields:

```python
from globalpayments.api import PorticoConfig, ServicesContainer

config = PorticoConfig()
config.merchant_id   = "YOUR_MERCHANT_ID"
config.account_id    = "internet"
config.shared_secret = "YOUR_SECRET"

ServicesContainer.configure(config, "gp_ecom")   # named config, e.g. "gp_ecom" or "realex"
```

This is confirmed both in the config-resolution logic and in a real, active SDK test:
- `ServicesContainer.configure()` (`globalpayments/api/__init__.py`, lines 271–297): when `isinstance(config, PorticoConfig)` and `config.merchant_id is not None`, it builds a `RealexConnector()` instead of a `PorticoConnector()`, wiring `account_id`, `channel`, `merchant_id`, `rebate_password`, `refund_password`, `shared_secret` onto it.
- `tests/integration/gateways/realex_connector/test_credit.py`: `PorticoConfig()` with `merchant_id = "heartlandgpsandbox"`, `account_id = "api"`, `shared_secret = "secret"`, then `ServicesContainer.configure(config, "realex")`.

A `GatewayProvider.GpEcom = "GP_ECOM"` enum value does exist (`entities/enums.py`), but the `PorticoConfig`-with-`merchant_id` branch in `ServicesContainer.configure()` does **not** set it — `config.gateway_provider` stays `GatewayProvider.Portico` regardless of which connector is actually wired up. Don't rely on inspecting `config.gateway_provider` to tell GP Ecom and Portico apart in this SDK; the connector selection itself (visible only inside `ServicesContainer`) is the real signal.

This SDK's config shape is genuinely different from a dedicated-class pattern — not an omission in this document.

---

## Payment Methods

### Credit Card (manual entry)

```python
from globalpayments.api.payment_methods import CreditCardData

card = CreditCardData()
card.number = "CARD_NUMBER"   # see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
card.exp_month = "MM"
card.exp_year = "YYYY"
card.cvn = "CVV"
card.card_holder_name = "Jane Smith"
```

### Credit Card (token)

```python
card = CreditCardData()
card.token = "PMT_TOKEN"
```

### Track Data (card present)

```python
from globalpayments.api.payment_methods import CreditTrackData
from globalpayments.api.entities.enums import EntryMethod

track = CreditTrackData()
track.value = "TRACK_DATA_STRING"   # see sandbox track data: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
track.entry_method = EntryMethod.Swipe
```

### eCheck / ACH

```python
from globalpayments.api.payment_methods import ECheck
from globalpayments.api.entities.enums import AccountType, CheckType, SecCode

echeck = ECheck()
echeck.account_number = "ACCOUNT_NUMBER"
echeck.routing_number = "ROUTING_NUMBER"
echeck.account_type = AccountType.Checking
echeck.check_type = CheckType.Personal
echeck.sec_code = SecCode.PPD
echeck.check_holder_name = "Jane Smith"
```

> **Real, narrower method set: `ECheck` supports only `.charge()`.** Confirmed by reading the complete 72-line `payment_methods/echeck.py` — no `.authorize()`, `.refund()`, `.reverse()`, or `.verify()` are defined on this class.

### Gift Card

```python
from globalpayments.api.payment_methods import GiftCard

gift = GiftCard()
gift.number = "GIFT_CARD_NUMBER"
```

> Confirmed absent: there is no `Cash` payment-method class. `globalpayments/api/payment_methods/cash.py` exists in the repo tree but is a literal empty file (0 bytes, no class defined) — confirmed by fetching it directly.

---

## Core Transactions
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/online/api-guide.md

### Charge (sale — auth + capture)

```python
response = card.charge(29.99) \
    .with_currency("USD") \
    .with_description("Order #1234") \
    .execute()

transaction_id = response.transaction_id
status = response.response_message   # "CAPTURED" or "SUCCESS"
auth_code = response.authorization_code
```

### Authorize (hold, capture later)
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/capture-guide.md

```python
response = card.authorize(29.99) \
    .with_currency("USD") \
    .execute()

transaction_id = response.transaction_id
```

### Capture

```python
from globalpayments.api.entities import Transaction

transaction = Transaction.from_id(transaction_id)
response = transaction.capture(29.99).execute()
```

### Void / Reverse
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/reverse-guide.md

**Gateway differences (confirmed against `builders/request_builder/GpApi/GpApiManagementRequestBuilder.py` and `gateways/__init__.py`):**
- **GP API** — use `.reverse()`. `GpApiManagementRequestBuilder.build_request()` has no branch for `TransactionType.Void`; calling `.void()` against GP API silently falls through to a malformed empty-endpoint POST request rather than raising a typed exception. There is a `TransactionType.Reversal` branch.
- **Portico** — use `.void()`. `PorticoConnector` maps `Void` to `CreditVoid`/`CheckVoid`/`GiftCardVoid` distinctly from `Reversal`'s `CreditReversal`/`DebitReversal`/`GiftCardReversal`.
- **GP Ecom** — use `.void()`. `RealexConnector` maps *both* `TransactionType.Void` and `TransactionType.Reversal` to the same `"void"` gateway operation.

```python
from globalpayments.api.entities import Transaction

# GP API — reverse a transaction
transaction = Transaction.from_id(transaction_id)
response = transaction.reverse().execute()

# Portico / GP Ecom — void a transaction
transaction = Transaction.from_id(transaction_id)
response = transaction.void().execute()
```

### Refund
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/refund-guide.md

```python
# Refund a settled transaction by ID
transaction = Transaction.from_id(transaction_id)
response = transaction.refund(10.00) \
    .with_currency("USD") \
    .execute()

# Standalone credit (refund directly to a payment method)
response = card.refund(10.00) \
    .with_currency("USD") \
    .execute()
```

### Verify
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/verify-guide.md

```python
response = card.verify() \
    .with_currency("USD") \
    .execute()
```

---

## Address Verification (AVS)

```python
from globalpayments.api.entities import Address

address = Address()
address.street_address1 = "1 Main Street"
address.city = "Atlanta"
address.state = "GA"              # property proxy onto `province`
address.postal_code = "30301"
address.country = "US"

response = card.charge(100.00) \
    .with_currency("USD") \
    .with_address(address) \
    .execute()

avs_result = response.avs_response_code
cvn_result = response.cvn_response_code
```

`Address.state` is a get/set property proxying `province`, and `Address.country`/`.country_code` are properties that cross-populate each other via `CountryUtils` when only one is set (`entities/address.py`) — confirmed by reading the property implementations.

---

## Hosted Fields (PCI-Compliant Card Collection)

**No dedicated token-generation service class was found for this SDK** for minting a restricted, browser-safe access token for GlobalPayments.js hosted fields. Searching this SDK's full 187-file tree and `globalpayments/api/services/__init__.py` (which exports only `BatchService`, `RecurringService`, `ReportingService`) turns up no equivalent class — the closest thing is `GpApiConnector.get_access_token()`, an instance method on the connector object returned only after `ServicesContainer.configure()`, not a standalone public service. This is a **not found**, not a confirmed absence across every possible code path — if you need this flow, check https://github.com/globalpayments/python-sdk directly for anything added since this was last verified, and consider generating the restricted access token via a direct GP API REST call per the portal's hosted-fields guide instead of assuming an SDK helper exists.

**PCI guidance still applies:** for server-to-server integrations (CLI scripts, backend test suites) passing `CreditCardData` with a raw card number is acceptable. For any web-facing integration, prefer GlobalPayments.js hosted fields so card data is collected inside GP-hosted iframes and your server only ever sees a `PMT_` payment reference token — even without a confirmed SDK-native token helper, the browser-side and token-charge halves of the pattern below are still valid.

### Step 1 — Mount hosted card iframes (JavaScript, browser-side)

```html
<!-- Load GlobalPayments.js -->
<!-- Read latest version of JS library from this file in its source repository:
     https://github.com/globalpayments/globalpayments-js/blob/master/packages/globalpayments-js/src/lib/version.ts -->
<script src="https://js.globalpay.com/5.1.0/globalpayments.js"></script>

<div id="credit-card-form"></div>

<script>
GlobalPayments.configure({
    accessToken: ACCESS_TOKEN_FROM_YOUR_BACKEND,
    env: 'sandbox',          // 'production' for live
    apiVersion: '2021-03-22',
});

const cardForm = GlobalPayments.creditCard.form('#credit-card-form', {
    style: 'gp-default',
    amount: '19.99',
});

cardForm.on('token-success', async (resp) => {
    // resp.paymentReference is a PMT_ token — no raw card data here
    await fetch('/api/charge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ payment_token: resp.paymentReference }),
    });
});

cardForm.on('token-error', (resp) => { console.error(resp); });
</script>
```

### Step 2 — Charge the token (Python, server-side)

```python
from flask import request
from globalpayments.api.payment_methods import CreditCardData

card = CreditCardData()
card.token = request.form["payment_token"]   # PMT_ reference from GlobalPayments.js

response = card.charge(19.99) \
    .with_currency("USD") \
    .execute()

transaction_id = response.transaction_id
status = response.response_message
```

---

## Tokenization
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/tokenization/card-storage-guide.md

### Store a card

```python
response = card.tokenize().execute()
token = response.token   # starts with "PMT_"
```

`Credit.tokenize(verify=True)` (`payment_methods/credit.py`) verifies the card with the issuer by default before tokenizing — pass `card.tokenize(verify=False)` to skip verification.

### Charge a stored token

```python
token_card = CreditCardData()
token_card.token = token

response = token_card.charge(50.00) \
    .with_currency("USD") \
    .execute()
```

### Update token expiry

```python
token_card = CreditCardData()
token_card.token = existing_token
token_card.exp_month = "MM"
token_card.exp_year = "YYYY"

token_card.update_token_expiry()
```

### Delete a token

```python
token_card.delete_token()
```

---

## Recurring Billing
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/recurring/recurring-payments-guide.md

```python
from globalpayments.api.entities import Customer, RecurringPaymentMethod

# Create customer and store a payment method
customer = Customer()
customer.id = "cust-001"
customer.first_name = "Jane"
customer.last_name = "Smith"
customer.email = "jane@example.com"
customer.create()

recurring_method = customer.add_payment_method("pm-001", card)
recurring_method.create()

# Charge the stored method
response = recurring_method.charge(19.99) \
    .with_currency("USD") \
    .execute()
```

> **`Customer.add_payment_method()` only builds a local `RecurringPaymentMethod` object — it does not call the gateway.** Confirmed: `entities/__init__.py`, `Customer.add_payment_method()` constructs and returns the object with no service call. A separate `.create()` (inherited from `RecurringEntity`, which delegates to `RecurringService.create()`) is required to persist it — skipping it is a common source of silently-unpersisted payment methods.

> **Real divergence — `RecurringPaymentMethod` lives in `globalpayments/api/entities/__init__.py`, not `payment_methods/`.** Its constructor is overloaded: `RecurringPaymentMethod(payment_method_or_customer, payment_id=None)` — pass a string as the first argument to build by `customer_key`/`payment_id` directly, or let `Customer.add_payment_method()` build it from a payment-method object.

---

## 3D Secure 2
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/risk-management/3D-secure/browser-authentication-guide.md
> Reference: `tests/integration/gateways/GpApi_connector/gpapi_test_3DSecure.py` (active test file, targets **GP API**)

**A real finding on the sample repo:** the only `globalpayments-samples` repo carrying the "3ds2" topic with a `python/` directory is `gpecom-3ds2`, but its `python/server.py` is generic, uncustomized Flask boilerplate — it does not call `check_enrollment`/`initiate_authentication`/`get_authentication_data` at all (confirmed by reading the complete 147-line file). The chain below is grounded instead in the SDK's own active integration test, which targets **GP API**, not GP Ecom. `gpapi-3ds2` (the GP API-flavored sample repo) has no `python/` directory at all (confirmed 404).

**Regional default:** 3DS is required by default in most regions outside the US. Implement the full 3DS2 flow for non-US merchants.

### Config Requirements for 3DS

```python
from globalpayments.api import GpApiConfig, ServicesContainer
from globalpayments.api.entities.enums import Environment, CardChannel

config = GpApiConfig()
config.app_id = "YOUR_APP_ID"
config.app_key = "YOUR_APP_KEY"
config.environment = Environment.Test
config.country = "GB"                    # non-US → 3DS is required
config.channel = CardChannel.CARD_NOT_PRESENT

# Required for 3DS
config.merchant_contact_url = "https://yoursite.com/about"
config.method_notification_url = "https://yoursite.com/3ds-method-notification"
config.challenge_notification_url = "https://yoursite.com/3ds-challenge-notification"

ServicesContainer.configure(config)
```

### Imports

```python
from globalpayments.api.services.secure_3d_service import Secure3dService
from globalpayments.api.entities import Address, ThreeDSecure
from globalpayments.api.entities.browser_data import BrowserData
from globalpayments.api.entities.enums import (
    AddressType,
    AuthenticationSource,
    ColorDepth,
    ChallengeWindowSize,
    MethodUrlCompletion,
)
```

### Step 1 — Check Enrollment

```python
secure_ecom = Secure3dService.check_enrollment(card) \
    .with_currency("GBP") \
    .with_amount(10.00) \
    .execute()

enrolled = secure_ecom.enrolled                    # "ENROLLED" (Secure3dStatus.ENROLLED.value)
server_transaction_id = secure_ecom.server_transaction_id
issuer_acs_url = secure_ecom.issuer_acs_url
payer_authentication_request = secure_ecom.payer_authentication_request
```

### Step 2 — Initiate Authentication

```python
browser_data = BrowserData()
browser_data.accept_header = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
browser_data.color_depth = ColorDepth.TWENTY_FOUR_BITS
browser_data.ip_address = "127.0.0.1"
browser_data.java_enabled = False
browser_data.java_script_enabled = True
browser_data.language = "en-GB"
browser_data.screen_height = 1080
browser_data.screen_width = 1920
browser_data.challenge_window_size = ChallengeWindowSize.WINDOWED_600X400
browser_data.time_zone = "0"
browser_data.user_agent = "Mozilla/5.0"

shipping_address = Address()
shipping_address.street_address1 = "1 Test Street"
shipping_address.city = "London"
shipping_address.postal_code = "SW1A 1AA"
shipping_address.country_code = "826"   # ISO 3166-1 numeric

formatted_date = "2026-08-06 12:00:00"   # order_create_date takes a formatted string, not a datetime

init_auth = Secure3dService.initiate_authentication(card, secure_ecom) \
    .with_amount(10.00) \
    .with_currency("GBP") \
    .with_authentication_source(AuthenticationSource.Browser) \
    .with_method_url_completion(MethodUrlCompletion.Yes) \
    .with_order_create_date(formatted_date) \
    .with_address(shipping_address, AddressType.Shipping) \
    .with_browser_data(browser_data) \
    .execute()

status = init_auth.status              # "CHALLENGE_REQUIRED" | "SUCCESS_AUTHENTICATED" | etc.
acs_transaction_id = init_auth.acs_transaction_id
challenge_request = init_auth.payer_authentication_request   # base64-encoded CReq, present on challenge
```

### Step 3 — Handle Challenge (when `status == "CHALLENGE_REQUIRED"`)

```python
if init_auth.status == "CHALLENGE_REQUIRED":
    challenge_request_url = init_auth.issuer_acs_url
    encoded_challenge_request = init_auth.payer_authentication_request
    # Build and POST the CReq form to the ACS URL.
    # Your challenge_notification_url receives the CRes when the user completes the challenge.
```

### Step 4 — Get Authentication Result

```python
final_secure_ecom = Secure3dService.get_authentication_data() \
    .with_server_transaction_id(secure_ecom.server_transaction_id) \
    .with_amount(10.00) \
    .execute()

final_status = final_secure_ecom.status
liability_shift = final_secure_ecom.liability_shift   # "YES" on success
```

### Step 5 — Charge with 3DS Data Attached

```python
card.three_d_secure = final_secure_ecom

transaction = card.charge(10.00) \
    .with_currency("GBP") \
    .execute()

transaction_id = transaction.transaction_id
status = transaction.response_message   # "CAPTURED"
```

### 3DS Test Cards

Source: `tests/data/Gpapi_3ds_test_cards.py`, confirmed by real assertions in `gpapi_test_3DSecure.py`. Use a future expiry and any CVV.

| Card number | Expected result |
|---|---|
| `4263970000005262` | Frictionless success (v2.1) |
| `4222000006285344` | Frictionless success (v2.2) |
| `4012001038488884` | Challenge required (v2.1) |
| `4222000001227408` | Challenge required (v2.2) |
| `4012001037461114` | Not authenticated (v2.1) |
| `4012001038443335` | Issuer rejected (v2.1) |

For the full test card list, see: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

---

## Reporting
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/reporting/real-time-reporting-guide.md

```python
from globalpayments.api.services import ReportingService
from globalpayments.api.entities.enums import TransactionSortProperty, SortDirection, SearchCriteria

# Single transaction detail
detail = ReportingService.transaction_detail(transaction_id).execute()

# Paged transaction search
summary = ReportingService.find_transactions_paged(1, 10) \
    .order_by(TransactionSortProperty.TIME_CREATED, SortDirection.DESC) \
    .where(SearchCriteria.StartDate, start_date) \
    .and_with(SearchCriteria.EndDate, end_date) \
    .execute()

for txn in summary:
    print(txn.transaction_id, txn.transaction_status)
```

`.where(criteria, value)` returns the underlying `SearchCriteriaBuilder`; chain further filters with `.and_with(criteria, value)`. The `.where(...).and_with(...).execute()` portion is attested verbatim in `tests/integration/gateways/GpApi_connector/gpapi_test_reporting_transactions.py`. The leading `.order_by(...)` is **not** — it is commented out in that test. It is nonetheless valid: `order_by` returns `self` on `TransactionReportBuilder`, so the combined chain type-checks. Treat the ordering clause as source-verified by signature, not by a passing test.

### Deposits and disputes — no `ReportingService` facade

`ReportingService` exposes only `.activity()`, `.transaction_detail()`, `.find_transactions_paged()`, `.find_transactions()` (confirmed, complete 48-line `services/reporting_service.py`). To run a deposits or disputes report, build the report builder directly:

```python
from globalpayments.api.builders import TransactionReportBuilder
from globalpayments.api.entities.enums import ReportType

deposits = TransactionReportBuilder(ReportType.FindDepositsPaged) \
    .with_paging(1, 10) \
    .execute()

disputes = TransactionReportBuilder(ReportType.FindDisputesPaged) \
    .with_paging(1, 10) \
    .execute()
```

---

## Error Handling
> Always catch from most specific to least specific.

```python
from globalpayments.api.entities.exceptions import (
    ApiException,
    ArgumentException,
    BuilderException,
    ConfigurationException,
    GatewayException,
    MessageException,
    UnsupportedTransactionException,
)

try:
    response = card.charge(100.00) \
        .with_currency("USD") \
        .execute()

    if response.response_code == "00" or response.response_message == "SUCCESS":
        pass  # approved

except BuilderException as e:
    # Missing required builder field (e.g. no currency)
    print(f"Builder error: {e.message}")
except ConfigurationException as e:
    # Bad or incomplete config
    print(f"Config error: {e.message}")
except GatewayException as e:
    # Gateway declined or returned an error
    print(f"Gateway error [{e.response_code}]: {e.message}")
except UnsupportedTransactionException as e:
    # Gateway doesn't support this operation
    print(f"Unsupported: {e.message}")
except MessageException as e:
    # Device message error
    print(f"Message error: {e.message}")
except ApiException as e:
    # Catch-all for everything else in the ApiException hierarchy
    print(f"API error: {e.message}")
except ArgumentException as e:
    # NOT a subclass of ApiException — must be caught separately
    print(f"Argument error: {e}")
```
