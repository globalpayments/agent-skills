# GP PHP SDK — Code Reference

Quick-copy PHP snippets for the `globalpayments/php-sdk`. All class names and method chains are verified against the SDK source at https://github.com/globalpayments/php-sdk.

---

## Installation

```bash
composer require globalpayments/php-sdk
```

Requirements: PHP 8.0+, ext-curl, ext-dom, ext-openssl, ext-json, ext-zlib, ext-intl, ext-mbstring, ext-fileinfo.

---

## Gateway Configuration

### GP API
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/integration-options/sdk/php.md

```php
use GlobalPayments\Api\ServiceConfigs\Gateways\GpApiConfig;
use GlobalPayments\Api\ServicesContainer;
use GlobalPayments\Api\Entities\Enums\Environment;
use GlobalPayments\Api\Entities\Enums\Channel;

$config = new GpApiConfig();
$config->appId       = 'YOUR_APP_ID';
$config->appKey      = 'YOUR_APP_KEY';
$config->environment = Environment::TEST;        // Environment::PRODUCTION for live
$config->country     = 'US';
$config->channel     = Channel::CardNotPresent;  // Channel::CardPresent for in-person

ServicesContainer::configureService($config);
```

Optional GP API fields:
```php
use GlobalPayments\Api\Entities\Enums\IntervalToExpire;
use GlobalPayments\Api\Entities\Enums\DataResidency;

$config->merchantId               = 'MER_xxx';
$config->merchantContactUrl       = 'https://yoursite.com/about'; // required for 3DS
$config->methodNotificationUrl    = 'https://yoursite.com/3ds/method';
$config->challengeNotificationUrl = 'https://yoursite.com/3ds/challenge';
$config->secondsToExpire          = 3600;
$config->intervalToExpire         = IntervalToExpire::WEEK;
$config->dataResidency            = DataResidency::EU; // EU data residency
```

### GP Ecom (Realex)

```php
use GlobalPayments\Api\ServiceConfigs\Gateways\GpEcomConfig;

$config = new GpEcomConfig();
$config->merchantId   = 'YOUR_MERCHANT_ID';
$config->accountId    = 'internet';
$config->sharedSecret = 'YOUR_SECRET';
$config->environment  = Environment::TEST;

ServicesContainer::configureService($config);
```

### Portico (Heartland) — secret API key

```php
use GlobalPayments\Api\ServiceConfigs\Gateways\PorticoConfig;

$config = new PorticoConfig();
$config->secretApiKey = 'skapi_cert_YOUR_KEY';
$config->environment  = Environment::TEST;

ServicesContainer::configureService($config);
```

### Portico — 5-point credentials (via GpApiConfig)

```php
$config = new GpApiConfig();
$config->deviceId    = 'DEVICE_ID';
$config->siteId      = 'SITE_ID';
$config->licenseId   = 'LICENSE_ID';
$config->username    = 'USERNAME';
$config->password    = 'PASSWORD';
$config->environment = Environment::TEST;

ServicesContainer::configureService($config);
```

---

## Payment Methods

### Credit Card (manual entry)

```php
use GlobalPayments\Api\PaymentMethods\CreditCardData;

$card = new CreditCardData();
$card->number         = 'CARD_NUMBER'; // see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
$card->expMonth       = 'MM';
$card->expYear        = 'YYYY';
$card->cvn            = 'CVV';
$card->cardHolderName = 'Jane Smith';
```

### Credit Card (token)

```php
$card = new CreditCardData();
$card->token = 'PMT_TOKEN';
```

### Track Data (card present)

```php
use GlobalPayments\Api\PaymentMethods\CreditTrackData;
use GlobalPayments\Api\Entities\Enums\EntryMethod;

$track = new CreditTrackData();
$track->value       = 'TRACK_DATA_STRING'; // see sandbox track data: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
$track->entryMethod = EntryMethod::SWIPE;
```

### eCheck / ACH

```php
use GlobalPayments\Api\PaymentMethods\ECheck;
use GlobalPayments\Api\Entities\Enums\{AccountType, CheckType, SecCode};

$eCheck = new ECheck();
$eCheck->accountNumber   = 'ACCOUNT_NUMBER';
$eCheck->routingNumber   = 'ROUTING_NUMBER';
$eCheck->accountType     = AccountType::CHECKING;
$eCheck->checkType       = CheckType::PERSONAL;
$eCheck->secCode         = SecCode::PPD;
$eCheck->checkHolderName = 'Jane Smith';
```

### Gift Card

```php
use GlobalPayments\Api\PaymentMethods\GiftCard;

$gift = new GiftCard();
$gift->number = 'GIFT_CARD_NUMBER';
```

---

## Core Transactions
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/online/api-guide.md

### Charge (sale — auth + capture)

```php
$response = $card->charge(29.99)
    ->withCurrency('USD')
    ->withDescription('Order #1234')
    ->execute();

$transactionId = $response->transactionId;
$status        = $response->responseMessage; // 'CAPTURED' or 'SUCCESS'
$authCode      = $response->authorizationCode;
```

### Authorize (hold, capture later)
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/capture-guide.md

```php
$response = $card->authorize(29.99)
    ->withCurrency('USD')
    ->execute();

$transactionId = $response->transactionId;
```

### Capture

```php
use GlobalPayments\Api\Entities\Transaction;

$transaction = Transaction::fromId($transactionId);
$response    = $transaction->capture(29.99)->execute();
```

### Void / Reverse
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/reverse-guide.md

**Gateway differences:**
- **GP API** — use `->reverse()`. The `->void()` method maps to `TransactionType::VOID` which is not handled by the GP API connector and will throw a `TypeError`.
- **Portico / GP Ecom** — use `->void()`.

```php
use GlobalPayments\Api\Entities\Transaction;

// GP API — reverse a transaction
$transaction = Transaction::fromId($transactionId);
$response    = $transaction->reverse()->execute();

// Portico / GP Ecom — void a transaction
$transaction = Transaction::fromId($transactionId);
$response    = $transaction->void()->execute();
```

### Refund
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/refund-guide.md

```php
// Refund a settled transaction by ID
$transaction = Transaction::fromId($transactionId);
$response    = $transaction->refund(10.00)
    ->withCurrency('USD')
    ->execute();

// Standalone credit (refund directly to a payment method)
$response = $card->refund(10.00)
    ->withCurrency('USD')
    ->execute();
```

### Verify
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/manage-payments/verify-guide.md

```php
$response = $card->verify()
    ->withCurrency('USD')
    ->execute();
```

---

## Address Verification (AVS)

```php
use GlobalPayments\Api\Entities\Address;

$address = new Address();
$address->streetAddress1 = '1 Main Street';
$address->city           = 'Atlanta';
$address->state          = 'GA';
$address->postalCode     = '30301';
$address->country        = 'US';

$response = $card->charge(100.00)
    ->withCurrency('USD')
    ->withAddress($address)
    ->execute();

$avsResult = $response->avsResponseCode;
$cvnResult = $response->cvnResponseCode;
```

---

## Hosted Fields (PCI-Compliant Card Collection)
> GlobalPayments.js hosted fields — raw card numbers never flow through the merchant server.

**PCI guidance:** For server-to-server integrations (like CLI scripts or backend test suites) passing `CreditCardData` with a raw card number is acceptable. For any web-facing integration, use hosted fields so card data is collected inside GP-hosted iframes and your server only ever sees a `PMT_` payment reference token.

### Step 1 — Generate a restricted access token (PHP, server-side)

```php
use GlobalPayments\Api\ServiceConfigs\Gateways\GpApiConfig;
use GlobalPayments\Api\Services\GpApiService;
use GlobalPayments\Api\Entities\Enums\Environment;
use GlobalPayments\Api\Entities\Enums\Channel;

$config = new GpApiConfig();
$config->appId       = 'YOUR_APP_ID';
$config->appKey      = 'YOUR_APP_KEY';
$config->environment = Environment::TEST;
$config->channel     = Channel::CardNotPresent;
$config->country     = 'US';
$config->permissions = ['PMT_POST_Create_Single']; // restrict to single-use tokenisation only

$tokenInfo   = GpApiService::generateTransactionKey($config);
$accessToken = $tokenInfo->accessToken; // short-lived token — safe to expose to the browser
```

Return `$accessToken` as JSON to the browser. **Never expose your `appKey` or a full-permission token to client-side code.**

### Step 2 — Mount hosted card iframes (JavaScript, browser-side)

```html
<!-- Load GlobalPayments.js -->
<!-- Read latest version of JS library from this file in its source repository:
     https://github.com/globalpayments/globalpayments-js/blob/master/packages/globalpayments-js/src/lib/version.ts -->
<script src="https://js.globalpay.com/5.1.0/globalpayments.js"></script>

<!-- Single container div. GlobalPayments.js renders card number, expiry,
     CVV, and a submit button as iframes inside here.
     Do NOT add separate input fields or a submit button. -->
<div id="credit-card-form"></div>

<script>
GlobalPayments.configure({
    accessToken: ACCESS_TOKEN_FROM_YOUR_BACKEND,
    env: 'sandbox',          // 'production' for live
    apiVersion: '2021-03-22',
});

// Single container — GlobalPayments.js renders card number, expiry, CVV,
// and a submit button as iframes inside this div. No separate button needed.
// style: 'gp-default' includes the submit button automatically.
// amount is the display amount; PHP SDK handles numeric conversion server-side.
const cardForm = GlobalPayments.creditCard.form('#credit-card-form', {
    style: 'gp-default',
    amount: '19.99',
});

// token-success fires after the user clicks the built-in submit button
// and GP tokenises the card. No cardForm.submit() call needed.
cardForm.on('token-success', async (resp) => {
    // resp.paymentReference is a PMT_ token — no raw card data here
    await fetch('/api/charge.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ payment_token: resp.paymentReference }),
    });
});

cardForm.on('token-error', (resp) => { console.error(resp); });
</script>
```

### Step 3 — Charge the token (PHP, server-side)

```php
use GlobalPayments\Api\PaymentMethods\CreditCardData;

$card        = new CreditCardData();
$card->token = $_POST['payment_token']; // PMT_ reference from GlobalPayments.js

$response = $card->charge(19.99)
    ->withCurrency('USD')
    ->execute();

$transactionId = $response->transactionId;  // TRN_...
$status        = $response->responseMessage; // CAPTURED
$authCode      = $response->authorizationCode;
```

---

## Tokenization
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/tokenization/card-storage-guide.md

### Store a card

```php
$response = $card->tokenize()->execute();
$token    = $response->token; // starts with 'PMT_'
```

### Charge a stored token

```php
$tokenCard        = new CreditCardData();
$tokenCard->token = $token;

$response = $tokenCard->charge(50.00)
    ->withCurrency('USD')
    ->execute();
```

### Update token expiry

```php
$tokenCard          = new CreditCardData();
$tokenCard->token   = $existingToken;
$tokenCard->expMonth = 'MM';
$tokenCard->expYear  = 'YYYY';

$tokenCard->updateTokenExpiry();
```

---

## Recurring Billing
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/recurring/recurring-payments-guide.md

```php
use GlobalPayments\Api\Entities\Customer;
use GlobalPayments\Api\PaymentMethods\RecurringPaymentMethod;

// Create customer and store a payment method
$customer            = new Customer();
$customer->id        = 'cust-001';
$customer->firstName = 'Jane';
$customer->lastName  = 'Smith';
$customer->email     = 'jane@example.com';
$customer->create();

// addPaymentMethod() only builds a local RecurringPaymentMethod; ->create() persists it.
// There is no ->execute() on RecurringPaymentMethod (src/PaymentMethods/RecurringPaymentMethod.php).
$storedMethod = $customer->addPaymentMethod('pm-001', $card)->create();

// Charge the stored method
$rpm      = new RecurringPaymentMethod('cust-001', 'pm-001');
$response = $rpm->charge(19.99)
    ->withCurrency('USD')
    ->execute();
```

---

## 3D Secure 2
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/risk-management/3D-secure/browser-authentication-guide.md
> Reference implementation: https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/php

**Regional default:** 3DS is **required by default in all regions except the United States**. Always implement the full 3DS2 flow for non-US merchants. US merchants may opt in.

### Config Requirements for 3DS

Three additional fields are required on `GpApiConfig` for any 3DS flow:

```php
use GlobalPayments\Api\ServiceConfigs\Gateways\GpApiConfig;
use GlobalPayments\Api\Entities\Enums\Environment;
use GlobalPayments\Api\Entities\Enums\Channel;
use GlobalPayments\Api\ServicesContainer;

$config = new GpApiConfig();
$config->appId       = 'YOUR_APP_ID';
$config->appKey      = 'YOUR_APP_KEY';
$config->environment = Environment::TEST;
$config->country     = 'GB';                 // non-US → 3DS is required
$config->channel     = Channel::CardNotPresent;

// Required for 3DS — HTTPS URLs
$config->merchantContactUrl        = 'https://yoursite.com/about';         // shown in ACS UI
$config->methodNotificationUrl     = 'https://yoursite.com/3ds-method-notification';
$config->challengeNotificationUrl  = 'https://yoursite.com/3ds-challenge-notification'; // must be HTTPS

ServicesContainer::configureService($config, 'my-config');
```

### Imports

```php
use GlobalPayments\Api\Services\Secure3dService;
use GlobalPayments\Api\Entities\ThreeDSecure;
use GlobalPayments\Api\Entities\Address;
use GlobalPayments\Api\Entities\BrowserData;
use GlobalPayments\Api\Entities\Enums\AddressType;
use GlobalPayments\Api\Entities\Enums\AuthenticationSource;
use GlobalPayments\Api\Entities\Enums\ChallengeWindowSize;
use GlobalPayments\Api\Entities\Enums\ColorDepth;
use GlobalPayments\Api\Entities\Enums\MethodUrlCompletion;
```

### Step 1 — Check Enrollment

Call this before rendering the payment form. The response tells you whether the card is enrolled in 3DS and provides the `serverTransactionId` that ties all subsequent steps together.

```php
$secure = Secure3dService::checkEnrollment($card)
    ->withAmount('10.00')
    ->withCurrency('GBP')
    ->execute('my-config');

// Map response fields
$serverTransId  = $secure->serverTransactionId;
$enrolled       = $secure->enrolled;           // 'ENROLLED' | 'NOT_ENROLLED' | 'ERROR'
$messageVersion = $secure->messageVersion ?? $secure->getVersion();
$methodUrl      = $secure->issuerAcsUrl ?? null;      // present when ACS method is available
$methodData     = $secure->payerAuthenticationRequest ?? null;
```

### Step 2 — Initiate Authentication

Send browser fingerprint data collected from the user's browser. This may resolve frictionlessly (no user interaction) or return `CHALLENGE_REQUIRED`.

```php
// Collect from browser via JS (navigator / screen properties)
$browserData = new BrowserData();
$browserData->acceptHeader       = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8';
$browserData->colorDepth         = ColorDepth::TWENTY_FOUR_BITS;
$browserData->ipAddress          = '127.0.0.1';
$browserData->javaEnabled        = false;
$browserData->javaScriptEnabled  = true;
$browserData->language           = 'en-GB';
$browserData->screenHeight       = '1080';
$browserData->screenWidth        = '1920';
$browserData->challengWindowSize = ChallengeWindowSize::FULL_SCREEN;
$browserData->timeZone           = '0';
$browserData->userAgent          = $_SERVER['HTTP_USER_AGENT'] ?? 'Mozilla/5.0';

// Shipping address (required for initiate-auth)
$shippingAddress = new Address();
$shippingAddress->streetAddress1 = '1 Test Street';
$shippingAddress->city           = 'London';
$shippingAddress->postalCode     = 'SW1A 1AA';
$shippingAddress->countryCode    = '826'; // ISO 3166-1 numeric

// Seed object carrying the server transaction ID from step 1
$seed = new ThreeDSecure();
$seed->serverTransactionId = $serverTransId;

$secure = Secure3dService::initiateAuthentication($card, $seed)
    ->withAmount('10.00')
    ->withCurrency('GBP')
    ->withOrderCreateDate(date('Y-m-d H:i:s'))
    ->withAddress($shippingAddress, AddressType::SHIPPING)
    ->withAuthenticationSource(AuthenticationSource::BROWSER)
    ->withBrowserData($browserData)
    ->withMethodUrlCompletion(MethodUrlCompletion::UNAVAILABLE) // YES | NO | UNAVAILABLE
    ->execute('my-config');

$status            = $secure->status;                     // 'SUCCESS_AUTHENTICATED' | 'CHALLENGE_REQUIRED' | 'FAILED' | etc.
$acsTransId        = $secure->acsTransactionId ?? null;
$acsChallengeUrl   = $secure->issuerAcsUrl ?? null;
$eci               = $secure->eci ?? null;
$authValue         = $secure->authenticationValue ?? null;
```

### Step 3 — Handle Challenge (when `status === 'CHALLENGE_REQUIRED'`)

When a challenge is required, redirect the browser to the ACS. On return, call `getAuthenticationData` (Step 3b) to retrieve the final result.

```php
if ($secure->status === 'CHALLENGE_REQUIRED') {
    // Retrieve challenge details
    $challengeRequestUrl     = $secure->issuerAcsUrl;
    $encodedChallengeRequest = $secure->payerAuthenticationRequest; // base64-encoded CReq
    $messageType             = $secure->messageType ?: 'creq';

    // Build and POST the CReq form to the ACS URL
    // Your challengeNotificationUrl receives the CRes when the user completes the challenge
}
```

### Step 3b — Get Authentication Result

Call this after the ACS posts back to your `challengeNotificationUrl` (or immediately after a frictionless `SUCCESS_AUTHENTICATED` to confirm final state):

```php
$secure = Secure3dService::getAuthenticationData()
    ->withServerTransactionId($serverTransId)
    ->withAmount('10.00')
    ->execute('my-config');

$finalStatus   = $secure->status;                          // 'SUCCESS_AUTHENTICATED' | 'FAILED' | etc.
$eci           = $secure->eci;
$authValue     = $secure->authenticationValue;
$dsTransRef    = $secure->directoryServerTransactionId;
```

### Step 4 — Charge with 3DS Data Attached

```php
use GlobalPayments\Api\PaymentMethods\CreditCardData;

$card = new CreditCardData();
$card->token = 'PMT_TOKEN'; // from hosted fields tokenisation

// Attach the completed ThreeDSecure object before charging
$card->threeDSecure = $secure;

$transaction = $card->charge('10.00')
    ->withCurrency('GBP')
    ->execute('my-config');

$transactionId = $transaction->transactionId;
$status        = $transaction->responseMessage; // 'CAPTURED'
$resultCode    = $transaction->responseCode;
```

### Full Hosted Fields + 3DS Combined Flow

The recommended pattern for web integrations combines Hosted Fields tokenisation with the 3DS flow. Raw card numbers never touch your server.

**Server exposes these endpoints:**

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/tokenization-config` | Returns short-lived `PMT_POST_Create_Single` token for Hosted Fields |
| POST | `/api/check-enrollment` | Step 1 — 3DS enrollment check |
| POST | `/api/initiate-auth` | Step 2 — Initiate authentication with browser data |
| POST | `/api/get-auth-result` | Step 3b — Retrieve final auth result |
| POST | `/api/authorize-payment` | Step 4 — Charge the tokenised card |

**Request shape for `/api/check-enrollment`:**
```json
{
  "payment_method_id": "PMT_...",
  "amount": "10.00",
  "currency": "GBP"
}
```

**Request shape for `/api/initiate-auth`:**
```json
{
  "payment_method_id": "PMT_...",
  "amount": "10.00",
  "currency": "GBP",
  "server_trans_id": "...",
  "method_url_completion": "UNAVAILABLE",
  "browser_data": {
    "accept_header": "...",
    "color_depth": 24,
    "ip": "127.0.0.1",
    "java_enabled": false,
    "javascript_enabled": true,
    "language": "en-GB",
    "screen_height": 1080,
    "screen_width": 1920,
    "challenge_window_size": "FULL_SCREEN",
    "timezone": "0",
    "user_agent": "..."
  }
}
```

**Request shape for `/api/authorize-payment`:**
```json
{
  "payment_method_id": "PMT_...",
  "amount": "10.00",
  "currency": "GBP",
  "authentication_id": "<server_trans_ref from initiate-auth response>"
}
```

### 3DS Test Cards

Use expiry `12/2026` and CVV `123`. Source: https://github.com/globalpayments-samples/gpapi-3ds2/tree/main/php

| Card number | Expected result | ECI |
|---|---|---|
| `4263970000005262` | Frictionless success | `05` |
| `5425230000004415` | Frictionless success | `02` |
| `4012001037141112` | Challenge required | — |
| `5114610000004778` | Challenge or issuer decline path | — |
| `4012001036853337` | Not enrolled / auth failed | `07` |
| `4012001036273338` | Not enrolled / unavailable | `07` |

For the full test card list, see: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md

---

## Reporting
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/reporting/real-time-reporting-guide.md

```php
use GlobalPayments\Api\Services\ReportingService;
use GlobalPayments\Api\Entities\Enums\TransactionSortProperty;
use GlobalPayments\Api\Entities\Enums\SortDirection;
use GlobalPayments\Api\Entities\Reporting\SearchCriteria;

// Single transaction detail
$detail = ReportingService::transactionDetail($transactionId)->execute();

// Paged transaction search
$summary = ReportingService::findTransactionsPaged(1, 10)
    ->orderBy(TransactionSortProperty::TIME_CREATED, SortDirection::DESC)
    ->where(SearchCriteria::START_DATE, new DateTime('2025-01-01'))
    ->andWith(SearchCriteria::END_DATE, new DateTime('2025-12-31'))
    ->execute();

foreach ($summary->result as $txn) {
    echo $txn->transactionId . ' ' . $txn->transactionStatus . PHP_EOL;
}

// Deposits (paged)
$deposits = ReportingService::findDepositsPaged(1, 10)->execute();

// Disputes (paged)
$disputes = ReportingService::findDisputesPaged(1, 10)->execute();
```

---

## Error Handling
> Always catch from most specific to least specific.

```php
use GlobalPayments\Api\Entities\Exceptions\{
    ApiException,
    BuilderException,
    ConfigurationException,
    GatewayException,
    UnsupportedTransactionException
};

try {
    $response = $card->charge(100.00)
        ->withCurrency('USD')
        ->execute();

    if ($response->responseCode === '00' || $response->responseMessage === 'SUCCESS') {
        // approved
    }

} catch (BuilderException $e) {
    // Missing required builder field (e.g., no currency)
    error_log('Builder error: ' . $e->getMessage());
} catch (ConfigurationException $e) {
    // Bad or incomplete config
    error_log('Config error: ' . $e->getMessage());
} catch (GatewayException $e) {
    // Gateway declined or returned an error
    error_log('Gateway error [' . $e->responseCode . ']: ' . $e->getMessage());
} catch (UnsupportedTransactionException $e) {
    // Gateway doesn't support this operation
    error_log('Unsupported: ' . $e->getMessage());
} catch (ApiException $e) {
    // Catch-all
    error_log('API error: ' . $e->getMessage());
}
```

---

## Terminal Operations
> Semi-integrated, card-present device support (PAX, UPA, HPA, Genius, Diamond terminals). This is a **separate code path** from every gateway operation above — read "Gateway vs. Terminal" before mixing patterns.
> Portal: https://developer.globalpayments.com/gh-assets/markdown/docs/payments/in-store/semi-integration.md — a conceptual overview of semi-integration and UPA-based standalone terminals. It does not document the PHP SDK's classes; the PHP terminal tree (`src/Terminals/`, 223 files) also covers PAX, HPA, Genius, and Diamond device families in addition to UPA. Verify every class/method below against source, not the portal page.

### Gateway vs. Terminal: two distinct code paths

Terminal transactions do **not** go through `ServicesContainer::configureService($config)` + a payment-method `->execute()` the way gateway charges do. They go through a parallel registration and execution path:

- **Gateway path:** `ServicesContainer::configureService($gatewayConfig)` registers a `gatewayConnector` on `ConfiguredServices`; `AuthorizationBuilder::execute()` calls `ServicesContainer::instance()->getClient($configName)->processAuthorization($this)` (`src/Builders/AuthorizationBuilder.php`).
- **Terminal path:** `DeviceService::create($connectionConfig)` calls `ServicesContainer::configureService($config, $configName)`, which (via `ConnectionConfig::configureContainer()`) registers a `DeviceController` on `ConfiguredServices` (`$services->setDeviceController(...)`, `src/ConfiguredServices.php`). `TerminalAuthBuilder::execute()` and `TerminalManageBuilder::execute()` call `ServicesContainer::instance()->getDeviceController($configName)->processTransaction($this)` / `->manageTransaction($this)` (`src/Terminals/Builders/TerminalAuthBuilder.php`, `src/Terminals/Builders/TerminalManageBuilder.php`) — never `getClient()`.

Both builder families end in `->execute()` and both extend the same `TransactionBuilder` → `BaseBuilder` ancestry (`src/Terminals/Builders/TerminalBuilder.php` extends `src/Builders/TransactionBuilder.php`), so the call shape looks identical. What differs is which registry entry `execute()` reaches into — `deviceController`, not `gatewayConnector`. Do not call `ServicesContainer::configureService()` directly with a `ConnectionConfig` and expect a payment-method object's `->charge()` to work against a terminal; use the `IDeviceInterface` returned by `DeviceService::create()` instead.

### Creating a Device

```php
use GlobalPayments\Api\Services\DeviceService;
use GlobalPayments\Api\Terminals\ConnectionConfig;
use GlobalPayments\Api\Terminals\Enums\{ConnectionModes, DeviceType};

$config = new ConnectionConfig();
$config->deviceType      = DeviceType::PAX_DEVICE;
$config->connectionMode  = ConnectionModes::TCP_IP;
$config->ipAddress       = '192.168.0.5';
$config->port            = '10009';
$config->timeout         = 10; // seconds; Configuration::$timeout defaults to 65000 (src/ServiceConfigs/Configuration.php)

$device = DeviceService::create($config);
```

`DeviceService::create(ConnectionConfig $config, string $configName = "default"): IDeviceInterface` (`src/Services/DeviceService.php`) registers the config under `$configName` and, if `$config->gatewayConfig` is set, registers that gateway config too — then returns the `IDeviceInterface` for the device.

### `ConnectionConfig`
> `src/Terminals/ConnectionConfig.php` — extends `Configuration` (`src/ServiceConfigs/Configuration.php`), implements `ITerminalConfiguration`.

| Field | Type | Notes |
|---|---|---|
| `deviceType` | `DeviceType` | Required. Selects which controller `configureContainer()` wires up — see Device Families below. |
| `connectionMode` | `ConnectionModes` | `SERIAL`, `TCP_IP`, `SSL_TCP`, `HTTP`, `HTTPS`, `MEET_IN_THE_CLOUD`, `DIAMOND_CLOUD` (`src/Terminals/Enums/ConnectionModes.php`). |
| `ipAddress`, `port` | `?string` | Required by `validate()` when `connectionMode` is `TCP_IP` or `HTTP`. |
| `baudRate`, `parity`, `stopBits`, `dataBits` | enums | Serial connection settings. |
| `requestIdProvider` | `IRequestIdProvider` | Required by `validate()` when `deviceType === DeviceType::HPA_ISC250`; optional otherwise. Interface: `src/Terminals/Abstractions/IRequestIdProvider.php` — one method, `getRequestId()`. |
| `logManagementProvider` | mixed | e.g. `TerminalLogManagement` (`src/Utils/Logging/TerminalLogManagement.php`). |
| `gatewayConfig` | `GatewayConfig` | Set when the device needs an underlying gateway config registered alongside it (e.g. Meet-in-the-Cloud). |
| `meetInTheCloudConfig` | `Genius\ServiceConfigs\MitcConfig` | Required (or `gatewayConfig`) when `connectionMode === ConnectionModes::MEET_IN_THE_CLOUD`. |
| `timeout` | `int` | Inherited from `Configuration`; default `65000`. |

`validate()` (in `ConnectionConfig`) throws `ConfigurationException` when: `MEET_IN_THE_CLOUD` mode is set without `meetInTheCloudConfig` or `gatewayConfig`; `TCP_IP`/`HTTP` mode is set without both `ipAddress` and `port`; `deviceType === HPA_ISC250` without `requestIdProvider`; or `DIAMOND_CLOUD` mode is set without `isvID`/`secretKey`.

**Diamond Cloud is a separate config class.** `isvID` and `secretKey` are not fields on `ConnectionConfig` itself — they're declared on `DiamondCloudConfig extends ConnectionConfig` (`src/Terminals/DiamondCloudConfig.php`), which also adds `region`, `posID`, and `statusUrl`. Use `DiamondCloudConfig`, not a plain `ConnectionConfig`, when `connectionMode` is `DIAMOND_CLOUD`.

### Device Families

All routing below is read directly from `ConnectionConfig::configureContainer()`'s `switch ($this->deviceType)` statement.

| Family | `DeviceType` constants | Controller |
|---|---|---|
| PAX | `PAX_DEVICE`, `PAX_S300`, `PAX_D200`, `PAX_D210`, `PAX_PX5`, `PAX_PX7` | `src/Terminals/PAX/PaxController.php` |
| HPA | `HPA_ISC250` | `src/Terminals/HPA/HpaController.php` |
| UPA | `UPA_DEVICE`, `UPA_SATURN_1000`, `UPA_VERIFONE_T650P`, `UPA_VERIFONE_T650C`, `UPA_VERIFONE_T660` | `src/Terminals/UPA/UpaController.php` |
| Diamond | `PAX_ARIES8`, `PAX_A80`, `PAX_A35`, `PAX_A920`, `PAX_A77`, `NEXGO_N5` | `src/Terminals/Diamond/DiamondController.php` |
| Genius | `GENIUS_VERIFONE_P400` | `src/Terminals/Genius/GeniusController.php` |

Two things to watch:
- **Diamond devices use `PAX_*`-named constants.** `PAX_ARIES8`, `PAX_A80`, `PAX_A35`, `PAX_A920`, and `PAX_A77` route to `DiamondController`, not `PaxController` — the constant name is not a reliable guide to which controller handles it. Always check the `configureContainer()` switch, not the enum member's name.
- **`HPA_IPP350` is declared but unrouted.** `DeviceType::HPA_IPP350` exists as a constant (`src/Terminals/Enums/DeviceType.php`), but `configureContainer()`'s switch has no `case` for it — only `HPA_ISC250` is handled; an unmatched `deviceType` falls through to `default: break;` and no controller is registered. Confirmed by reading `src/Terminals/ConnectionConfig.php` directly; do not set `deviceType = DeviceType::HPA_IPP350` expecting a working controller.

### `IDeviceInterface` Operations
> `src/Terminals/Abstractions/IDeviceInterface.php`. The base `DeviceInterface` implementation (`src/Terminals/DeviceInterface.php`) throws `UnsupportedTransactionException` for any method a given device family doesn't override — expect that exception, not a fatal error, when calling an operation a device doesn't support.

**Sales / auth (return `TerminalAuthBuilder`):**
`sale()`, `authorize()`, `verify()`, `refund()`, `addValue()`, `balance()`, `withdrawal()`, `tokenize()`, `startTransaction()`, `continueTransaction()`, `completeTransaction()`, `processTransaction()`.

**Management (return `TerminalManageBuilder`):**
`void()`, `capture()`, `tipAdjust()`, `deletePreAuth()`, `increasePreAuth()`, `reverse()`, `updateTaxInfo()`, `updateLodgingDetails()`.

**Batch / reporting:**
`batchClose(): IBatchCloseResponse`, `endOfDay()`, `getLastEOD(): IBatchCloseResponse`, `getSAFReport(): TerminalReportBuilder`, `getBatchReport(): TerminalReportBuilder`, `getBatchDetails(...)`, `findBatches(): TerminalReportBuilder`, `getOpenTabDetails(): TerminalReportBuilder`, `sendSaf()`, `sendStoreAndForward(): ISAFResponse`.

**Device / connectivity admin:**
`ping()`, `reboot()`, `reset()`, `initialize()`, `communicationCheck()`, `logon()`, `closeLane()`, `openLane()`, `getAppInfo()`, `getBatteryPercentage()`, `getEncryptionType()`, `setTimeZone()`, `getParam()`, `getDeviceConfig()`, `setDebugLevel()`, `getDebugLevel()`, `getDebugInfo()`, `returnToIdle()`.

**Card / signature / UI:**
`startCard()`, `removeCard()`, `cancel()`, `getSignatureFile(): ISignatureResponse`, `promptForSignature()`, `enterPIN()`, `lineItem()`, `displayMessage()`, `prompt()`, `print()`, `scan()`, `returnDefaultScreen()`, `getGenericEntry()`, plus user-defined-screen commands `loadUDData()`, `removeUDData()`, `executeUDData()`, `injectUDData()` (each returns `IDeviceScreen`).

### Worked Example: PAX Credit Sale
> Traced to `test/Integration/Gateways/Terminals/PAX/PaxCreditTests.php` — the SDK's own working pattern for this device family.

```php
use GlobalPayments\Api\PaymentMethods\CreditCardData;
use GlobalPayments\Api\Services\DeviceService;
use GlobalPayments\Api\Terminals\Abstractions\IRequestIdProvider;
use GlobalPayments\Api\Terminals\ConnectionConfig;
use GlobalPayments\Api\Terminals\Enums\{ConnectionModes, DeviceType};

// A minimal IRequestIdProvider — only required when deviceType is HPA_ISC250,
// but harmless to supply for any device.
class SimpleRequestIdProvider implements IRequestIdProvider
{
    public function getRequestId()
    {
        return random_int(10000, 99999);
    }
}

$config = new ConnectionConfig();
$config->ipAddress        = '192.168.0.5';
$config->port              = '10009';
$config->deviceType         = DeviceType::PAX_DEVICE;
$config->connectionMode     = ConnectionModes::TCP_IP;
$config->timeout            = 10;
$config->requestIdProvider  = new SimpleRequestIdProvider();

$device = DeviceService::create($config);

// Card-present: the terminal itself prompts for and reads the card.
// No CreditCardData object is needed — the device is the entry point.
$response = $device->sale(10)
    ->withAllowDuplicates(1)
    ->execute();

$transactionId = $response->transactionId;
$responseCode  = $response->responseCode; // '00' on approval

// Manual/keyed entry on the same device: attach a CreditCardData explicitly.
$card = new CreditCardData();
$card->number         = 'CARD_NUMBER'; // see test cards: https://developer.globalpayments.com/gh-assets/markdown/docs/getting-started/testing.md
$card->expMonth       = 12;
$card->expYear        = 2026;
$card->cvn            = '123';
$card->cardHolderName = 'Jane Smith';

$response = $device->sale(10)
    ->withPaymentMethod($card)
    ->withAllowDuplicates(1)
    ->execute();
```

`TerminalAuthBuilder::execute(string $configName = "default"): TerminalResponse` and `TerminalManageBuilder::execute($configName = "default"): TerminalResponse` are the terminal builders' own overrides of `BaseBuilder::execute()` — same method name as gateway builders, different implementation (see "Gateway vs. Terminal" above).
