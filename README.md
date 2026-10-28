# Bazarak (بازارک)

**English** | [فارسی](README.fa.md)

A multi-vendor online marketplace built with Django 5.2.

> **Educational project.** It extends a single-store course project (the
> ["shop" project](https://github.com/rogolsanamlo/django-online-store), written while
> following the lessons of my instructor, Mehdi Abbasi) into a marketplace where every store sells the
> same catalog products at its own price.

## How it works

- Anyone can browse and search the whole catalog.
- A user must register (a `UserProfile` is created automatically) and log in to order.
- A user can own **one** store (`Store` has a one-to-one relation with the user). New stores are
  inactive until an admin approves them.
- The admin defines catalog **products** (e.g. "cooking oil"). A seller adds a product to their
  store with **their own price** (`StoreProduct`), and manages stock from the seller panel.
- One order contains products from **one store only**.

## Features

- Home page with a banner, popular groups and "newest" / "cheapest" products with a tab per main group
- Product groups (main groups + sub-groups), brands, features and filtering (price range, brand, store), sorting, search
- Product comparison, favorites, ratings, comments (admin approval)
- Session shopping cart, checkout, discount baskets and coupons
- Online payment with ZarinPal; registration and password recovery with SMS codes (Kavenegar)
- **Seller panel:** store profile, products and prices, orders, stock, sales analytics (charts, Excel export)
- Persian admin panel ([admin guide](docs/ADMIN_GUIDE.md))
- REST API (Django REST framework + JWT)

## Screenshots

The interface is in Persian (right-to-left). Screenshots were taken with the demo data.

### Storefront

<table>
<tr><td width="50%"><img src="docs/screenshots/01-home.png" alt="Home page: header, search and banner"><br><sub>Home page: header, search and banner</sub></td><td width="50%"><img src="docs/screenshots/02-home-category-tabs.png" alt="Home page: the &quot;cheapest&quot; block filtered by a category tab (&quot;newest&quot; works the same way)"><br><sub>Home page: the "cheapest" block filtered by a category tab ("newest" works the same way)</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/03-category-menu.png" alt="Category menu with main groups and sub-groups"><br><sub>Category menu with main groups and sub-groups</sub></td><td width="50%"><img src="docs/screenshots/04-group-page.png" alt="Products of a group, with sorting and page size"><br><sub>Products of a group, with sorting and page size</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/05-filters-price-brand.png" alt="Filters: price range, brand and store"><br><sub>Filters: price range, brand and store</sub></td><td width="50%"><img src="docs/screenshots/06-product-page.png" alt="Product page with price, rating, tabs and add to cart"><br><sub>Product page with price, rating, tabs and add to cart</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/07-payment-sandbox.png" alt="ZarinPal sandbox payment page (demo card, no real money)"><br><sub>ZarinPal sandbox payment page (demo card, no real money)</sub></td><td width="50%"></td></tr>
</table>

### Accounts, favorites and orders

<table>
<tr><td width="50%"><img src="docs/screenshots/17-login.png" alt="Login page"><br><sub>Login page</sub></td><td width="50%"><img src="docs/screenshots/18-password-recovery.png" alt="Password recovery, step 1: enter the mobile number"><br><sub>Password recovery, step 1: enter the mobile number</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/19-verify-code.png" alt="Password recovery, step 2: enter the code sent by SMS"><br><sub>Password recovery, step 2: enter the code sent by SMS</sub></td><td width="50%"><img src="docs/screenshots/20-change-password.png" alt="Password recovery, step 3: choose a new password"><br><sub>Password recovery, step 3: choose a new password</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/21-favorites.png" alt="Favorites list with stock status and an add-to-cart button"><br><sub>Favorites list with stock status and an add-to-cart button</sub></td><td width="50%"><img src="docs/screenshots/22-my-orders.png" alt="User panel: latest orders"><br><sub>User panel: latest orders</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/23-my-payments.png" alt="User panel: payments"><br><sub>User panel: payments</sub></td><td width="50%"></td></tr>
</table>

### Seller panel

<table>
<tr><td width="50%"><img src="docs/screenshots/08-seller-dashboard.png" alt="Seller dashboard: best-selling products"><br><sub>Seller dashboard: best-selling products</sub></td><td width="50%"><img src="docs/screenshots/09-seller-last-7-days.png" alt="Seller dashboard: sales of the last 7 days"><br><sub>Seller dashboard: sales of the last 7 days</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/10-seller-sales-by-group.png" alt="Seller dashboard: sales by product group"><br><sub>Seller dashboard: sales by product group</sub></td><td width="50%"><img src="docs/screenshots/11-seller-abc-analysis.png" alt="Reports: ABC analysis of products"><br><sub>Reports: ABC analysis of products</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/12-seller-pivot-table.png" alt="Reports: monthly sales pivot table"><br><sub>Reports: monthly sales pivot table</sub></td><td width="50%"><img src="docs/screenshots/13-seller-stock.png" alt="Stock page: current stock per product"><br><sub>Stock page: current stock per product</sub></td></tr>
<tr><td width="50%"><img src="docs/screenshots/14-seller-stock-history.png" alt="Stock page: latest changes (output rows are added automatically after a successful payment)"><br><sub>Stock page: latest changes (output rows are added automatically after a successful payment)</sub></td><td width="50%"><img src="docs/screenshots/15-seller-products.png" alt="Store products with price, status and stock"><br><sub>Store products with price, status and stock</sub></td></tr>
</table>

### Admin panel

<table>
<tr><td width="50%"><img src="docs/screenshots/16-admin-warehouse.png" alt="Admin: stock entries per store product (input / output)"><br><sub>Admin: stock entries per store product (input / output)</sub></td><td width="50%"></td></tr>
</table>

## Setup

Developed with Python 3.12 (the pinned `numpy` and `pandas` need Python 3.11 or newer). Unless you use
SQLite (see below), you also need a MySQL server.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env  (then edit the values)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

For a zero-setup demo set `DB_ENGINE=sqlite` in `.env`. With an empty `KAVENEGAR_API_KEY`,
SMS verification codes are printed to the console. Payments use the ZarinPal **sandbox** by
default (`ZARINPAL_SANDBOX=True`), which accepts any 36-character merchant id and needs an internet
connection; use a real merchant id and `ZARINPAL_SANDBOX=False` in production. While `DEBUG` is on,
the technical reason of a gateway error is shown on the payment result page.

Run the tests (the MySQL user needs permission to create a test database):

```bash
python manage.py test
```

## Payment

Payments use ZarinPal's **sandbox**, the gateway's test environment: the page shows a demo card and no
real money moves, which is the normal setup for a portfolio project. To accept real payments you
need your own approved ZarinPal merchant account and a public domain, then set in `.env`:

```
ZARINPAL_MERCHANT_ID=<your real 36-character merchant id>
ZARINPAL_SANDBOX=False
ZARINPAL_CALLBACK_URL=https://your-domain/payments/verify/
```

`ZARINPAL_ACCESS_TOKEN` is optional; it is only needed for ZarinPal's reporting API.

## Stock

Stock is a ledger, not a stored number. Every change is a row in `Warehouse` (an **input** or an
**output** entry for one `StoreProduct`), and the quantity in stock is the sum of the inputs minus
the sum of the outputs (`StoreProduct.get_number_in_warehouse()`).

- A seller adds entries from the stock page of the seller panel. The price entered on an input
  entry is the purchase price: the profit report is *sales minus purchase cost*, so enter it to get
  meaningful profit figures.
- When a ZarinPal payment is verified, the order is marked as final and **one output entry per
  order line is created automatically**. This happens only the first time the order becomes final,
  so a repeated gateway callback (for example a refresh of the result page) never decreases stock
  twice. These entries are recorded under the buyer's account and appear in the admin and in the
  seller's stock history as "خروج از انبار".
- Stock is not checked when an item is added to the cart or an order is created (see
  [Known limitations](#known-limitations)).

## Demo data

To get a populated site without typing data by hand (development only):

```bash
python manage.py seed_demo
```

It creates 3 groups with 6 sub-groups, 4 brands, 12 products with generated pictures and two
demo stores that list them at different prices, with stock. It can be run again safely. Log in
as a demo seller to try the seller panel:

| Store | Mobile | Password |
|---|---|---|
| فروشگاه نمونه آلفا | `09120000001` | `demo12345` |
| فروشگاه نمونه بتا | `09120000002` | `demo12345` |

The command refuses to run when `DEBUG` is off (unless `--force` is given), because the demo
accounts have a well-known password.

## First steps after installing

1. Log in to `/admin/` and follow the [admin guide](docs/ADMIN_GUIDE.md): create a group and a
   sub-group, a brand and a product.
2. Register a user on the site, create a store, then activate it in the admin.
3. In the seller panel add the product to the store with a price.

## Project layout

| App | Responsibility |
|---|---|
| `main` | Home, about and contact pages, the `seed_demo` command |
| `accounts` | Custom user, profile, store, registration / login, seller panel pages |
| `products` | Brands, groups, products, `StoreProduct`, filtering, comparison |
| `orders` | Session shopping cart, orders, checkout, coupons |
| `payments` | ZarinPal payment request and verification |
| `discounts` | Discount baskets and coupons |
| `warehouses` | Stock entries per store product |
| `comment_scoring_favorites` | Comments, scores, favorites |
| `search` | Product search |
| `analytics` | Seller reports (pandas, Chart.js) |
| `api` | REST API (DRF + JWT) |

## Design note

`Store` lives in the `accounts` app because, in the current business rules, every store belongs to
exactly one user. If stores ever need to exist without a user, or a user needs several stores, move
`Store` to its own `stores` app and change the relation to a `ForeignKey`. `Product` is linked to
stores only through `StoreProduct`, so it stays untouched.

## Known limitations

- The mobile layout of the header is not implemented (the desktop header is hidden on small screens).
- Stock is decreased when a payment is verified, but it is not checked when an item is added to the
  cart or an order is created, so concurrent buyers can push a product's stock below zero.
- PDF export of the reports is disabled (the buttons only show a notice): it needs WeasyPrint and its native
  system libraries, which are not part of `requirements.txt`. Excel export works.
- The seller charts need Chart.js. It is loaded from `static/vendor/chartjs/chart.umd.js` if that file
  exists (see the README.txt next to it), otherwise from a CDN, so they need internet access
  unless you add the local copy.
- Uploaded files are stored on the local disk (`MEDIA_ROOT`). For production, configure Django's `STORAGES`
  setting (for example with `django-storages`) to keep them elsewhere.
- The `media/` folder is not part of the repository, so uploaded images are not included: `seed_demo`
  generates sample pictures, or upload your own through the admin panel.

## Acknowledgments

Built as a course project, following the tutorials of my instructor, **Mehdi Abbasi**: I wrote the
original single-store "shop" project while following his lessons, then extended it and built Bazarak on
top of it, with the help of AI tools (Claude by Anthropic).

## License

The project's own source code (everything except the third-party material listed below) is released
under the [MIT License](LICENSE) (Copyright (c) 2026 Roghayeh Golsanamlo).

Third-party material is **not** covered by that license and keeps its own terms:

- **Front-end theme.** The HTML structure, `static/css/style.css`, `static/js/main.js` and the icon font in
  `static/fonts/stroyka1/` come from a theme that the course instructor (Mehdi Abbasi) supplied for coursework. Its license
  terms are not known to the author, so check them before redistributing or reusing it.
- **Persian fonts.** The fonts in `static/fonts/farsi-fonts/` (the site uses IRANYekan) have their own licenses.
- **Libraries.** The libraries in `static/vendor/` (Bootstrap, jQuery, Owl Carousel, Font Awesome) and Chart.js
  keep their own open-source licenses.
