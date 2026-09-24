# Kalki Starter App — Project Brain

> **Purpose**: This file documents the complete project structure, architecture, key files, and code patterns for the Kalki Fashion React Native app. Read this FIRST before making any changes — it saves full project re-reads.

---

## 1. Project Overview

- **App**: Kalki Fashion — luxury Indian fashion e-commerce mobile app
- **Framework**: React Native (Expo) with Appmaker SDK
- **Platform**: iOS & Android (+ Tablet support)
- **Package Manager**: Yarn (with Lerna monorepo)
- **Backend**: Shopify (Storefront API via `@appmaker-xyz/shopify`)
- **Analytics**: WebEngage + Firebase
- **Root**: `/Users/dd-mac-04/Desktop/kalki-starter-app`

---

## 2. Monorepo Structure

```
kalki-starter-app/
├── package.json               # Root — Expo scripts, all dependencies
├── app.config.ts              # Expo app config
├── lerna.json                 # Monorepo config
├── src/
│   ├── index.js               # App entry, imports initApp
│   └── initApp.js             # Initializes Appmaker SDK
├── packages/
│   ├── theme-kalki/           # ⭐ MAIN THEME PACKAGE (most work happens here)
│   ├── swish-wishlist-king/   # Wishlist plugin (Wishlist King integration)
│   ├── dd-custom-app-login-appmaker/  # Custom login/auth package
│   ├── lucent-simply-otp/     # OTP-based login flow
│   ├── plugin-webengage/      # WebEngage analytics events
│   └── plugin-tagalys/        # Tagalys product search/recommendation
```

---

## 3. Theme Kalki — Main Package (⭐ Most Important)

**Path**: `packages/theme-kalki/`
**Package name**: `@appmaker-packages/theme-kalki`
**Entry point**: `src/index.js`

### 3.1 Architecture Pattern

The app uses **Appmaker's plugin system**:
- **Blocks**: Reusable UI components registered via `blocks` object
- **Pages**: Full screen page definitions registered via `pages` object
- **Filters**: `appmaker.addFilter()` to modify data/behavior at hook points
- **Actions**: `appmaker.actions.registerAction()` for custom actions
- **Analytics**: `analytics.onTrack()` for tracking events
- **Theme Registration**: `registerTheme({ id, activate, blocks, pages })`

### 3.2 Key Entry — `src/index.js` (≈910 lines)

This is the **central file** that ties everything together:

| Section | Lines (approx) | Purpose |
|---------|----------------|---------|
| Imports | 1–31 | All dependencies |
| `StatusBarManager` | 34–74 | StatusBar utility object |
| `getUserData()` | 76–91 | Fetches user profile metafields (gender, DOB, anniversary) |
| `getUserDataForCart()` | 94–111 | Fetches user's `cart_id` metafield |
| `updateUserMetaData()` | 156–166 | Compares & updates cart metafield on server |
| `syncCart()` | 167–243 | Syncs cart from server `cart_id` metafield → local cart |
| `syncWebCart()` | 245–277 | Syncs cart from `cart_json` metafield (web cart) |
| `handleInitialCartSync()` | 279–286 | Calls `syncCart()` then `syncWebCart()` |
| Block definitions | 288–341 | Static block configs (HomeLogo, SearchBar, etc.) |
| `PAGE_CONFIGS` | 344–350 | Page category arrays for filters |
| WebEngage helpers | 356–375 | Login status tracking |
| `CUSTOM_LOGOUT` | 377–394 | Custom logout action |
| `activate()` | 396–597 | **Main activation function** — registers all filters, events, cart sync |
| `analytics.onTrack()` | 565–597 | Event tracking: cart_created, checkout_completed, user_login, user_logout |
| `analytics.onTrackSystemEvents()` | 599–611 | System events (initial_action → cart sync) |
| Filters | 614–790 | Page data, header/footer, product visibility, toast |
| `appmaker.addFilter('wrap-appmaker-app-component')` | 792–838 | App wrapper with ToastProvider, ScreenOrientation lock |
| `appmaker.addFilter('shopify-response-data')` | 840–868 | Filters out hidden products (custom_product_visibility = "no") |
| Toast filter | 872–889 | Custom toast messages |
| Tagalys filter | 892–898 | Stores tagalys subcategories |
| Theme export | 900–909 | `registerTheme(Kalki)` |

### 3.3 PAGE_CONFIGS

```js
const PAGE_CONFIGS = {
  HOME_PAGES: ['tabHome', 'home'],
  SPECIAL_PAGES: ['productList', 'luxe', 'recentlyViewed'],
  DRAWER_PAGES: ['DrawerMenu'],
  VISIBLE_PAGES: ['home'],
  PRODUCT_LIST_PAGES: ['productList'],
};
```

### 3.4 Cart Sync Flow

```
App Opens / User Login
    → handleInitialCartSync()
        → syncCart()           # Reads cart_id metafield → syncCartFromId() → UPDATE_CART_V2
        → syncWebCart()        # Reads cart_json metafield → manageCartHandler() → clearCartJson()

Cart Updated (add/remove items)
    → analytics.onTrack('cart_created'/'cart_updated')
        → updateUserMetaData(cartId)  # Saves cart_id to server metafield

Checkout Completed
    → analytics.onTrack('checkout_completed')
        → updateCartMetafield('')     # Clears cart_id metafield
        → clearCartJson()             # Clears cart_json metafield
        → handleAction('CLEAR_CART')  # Clears local cart

User Logout
    → handleAction('CLEAR_CART')      # Clears local cart only
```

---

## 4. Directory Structure — `theme-kalki/src/`

### 4.1 Components (`src/components/`)

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| **PDP/** | Product Detail Page | `ProductImage.js` (image gallery), `ProductData.js` (72KB — product info), `AddToCartButton.js` (51KB — ATC logic), `Variation.js` (88KB — size/color selection), `Description.js` |
| **PDP/components/** | PDP sub-components | `ImageSwiper.js`, `MultiVideoPlayer.js`, `SizeGuideModal.js`, `SubcategoryModal.js`, `CustomizeSizeModal.js`, `ExpressDeliveryComponent.js`, `SelectBlouseOption.js` |
| **PDP/helpers/** | PDP helper functions | `twiningCartHelpers.js` |
| **PLP/** | Product List Page | `ProductGridItem.js` (99KB — product card), `ProductListBanner.js`, `CustomProductList.js` (30KB), `Variation.js` (63KB — PLP variant picker), `VideoSwiper.js`, `SwiperImageAnimated.js` |
| **PLP/component/** | PLP sub-components | `CustomFadeHeader.js` |
| **CART/** | Cart page | `CartCard.js` (27KB — cart item), `CheckOutButton.js`, `PriceSummary.js`, `CouponBlock.js`, `ApplyCouponButton.js`, `StepperButton.js`, `EmptyCartBlock.js`, `CartOutOfStock.js` |
| **Home/** | Home page | `HomeLogo.js`, `HomePageNav.js` (14KB — navigation), `SearchBar.js`, `VerticalImageSwiper.js` (18KB), `VideoBlock.js`, `FloatingButton.js` |
| **Home/CategoryTabBar/** | Category navigation tabs | `CategoryTabBar.js` |
| **Home/Filter/** | Filter components | `ShopifyFilter.js` |
| **MENU/** | Navigation menu/drawer | `CoreMenu.js` (22KB), `MenuItem.js`, `SubMenuPage.js` |
| **SEARCH/** | Search | `SearchBlock.js`, `SearchSuggestions.js`, `SearchSuggestionWrapper.js`, `SearchDefaultCollection.js` |
| **Account/** | User account | `Profile.js`, `ProfileCard.js`, `ProfileSection.js`, `MenuItem.js`, `MyTryons.js`, `Lookbook.js`, `VideoShoppingBanner.js` |
| **Account/CMS/** | CMS content pages | `AboutUs.js`, `Blog.js`, `ContactUs.js`, `StoreLocator.js`, `StoreList.js`, `CustomStoreCollection.js`, `VideoSlider.js`, `Faqs.js`, etc. |
| **order/** | Order detail | `OrderDetailItemCard.js`, `OrderDetailHeader.js`, `ShippingAddress.js`, `OrderFooterDetails.js`, `TotalOrderSummaryCard.js`, `DeliveryStatusCard.js` |
| **bottomTab/** | Bottom navigation | `CustomBottomBar.js`, `BottomSpace.js` |
| **user/** | Auth/Address | Login, Register, ResetPassword, AddressList, AddressForm, AccountDetails |
| **Collection/** | Collection carousel | `CollectionCarousel.js` |
| **BookAppointment/** | Appointment booking | `AppointmentCalendar.js`, `BookLiveAppointment.js`, `HeaderBannerStore.js`, `StoreCalendar.js` |
| **toastNotification/** | Custom toast | `ToastNotification.js` |
| **ForceUpdate/** | Force update modal | `ForceUpdate.js` |
| **Select/** | Dropdown select | `Select.tsx` |
| **DropDown/** | Dropdown | `DropdownComponent.tsx` |
| **Popin/** | Popup/modal | Popin components |
| **RecentlyViewed/** | Recently viewed products | Recently viewed components |
| **Notifications/** | Notification center | Notification components |
| **WebViewPage/** | WebView pages | WebView components |
| **CheckBox/** | Checkbox input | Checkbox components |

### 4.2 Pages (`src/pages/`)

| File | Page ID | Purpose |
|------|---------|---------|
| `productDetail.js` | productDetail | PDP page layout |
| `productList.js` | productList | PLP page layout |
| `cartPage.js` | cart / cartPageCheckout | Cart page layout |
| `emptyCart.js` | emptyCart | Empty cart view |
| `SearchPage.js` | searchPage | Search page |
| `MyAccount.js` | MyAccount | Account page |
| `ProfilePage.js` | ProfilePage | Profile page |
| `DrawerMenu.js` | DrawerMenu | Side drawer menu |
| `LoginOptions.js` | LoginOptions | Login page |
| `RegisterPage.js` | RegisterPage | Registration |
| `orderDetail.js` | orderDetail | Order detail page |
| `luxe.js` | luxe | Luxe collection page |
| `recentlyViewed.js` | recentlyViewed | Recently viewed page |
| `AccountDetails.js` | AccountDetails | Account details |
| `Appointment.js` | — | Appointment page |
| `blogPage.js` | blogPage | Blog page |
| `myTryons.js` | myTryons | Virtual try-on page |

### 4.3 Blocks (`src/blocks/index.js`)

This file registers ALL UI blocks (≈592 lines). Each block maps a `name` string to a React component. Examples:
- `kalki/product-image` → `ProductImage`
- `kalki/product-data` → `ProductData`
- `kalki/add-cart-button` → `AddCartButton`
- `kalki/product-grid-item` → `ProductGridItem`
- `kalki/cart-card` → `CartCard`
- `kalki/home-logo` → `HomeLogo`
- `kalki/search-bar` → `SearchBar`
- `kalki/custom-bottom-block` → `CustomBottomBar`
- `kalki/category-tab-bar` → `CategoryTabBar`

### 4.4 API (`src/api/`)

| File | Purpose |
|------|---------|
| `updateCartMetafield.js` | POST to `apps.kalkifashion.com` — saves cart_id to customer metafield |
| `clearCartJson.js` | POST to `api.kalkifashion.com` — clears cart_json metafield |
| `vto.js` | Virtual Try-On API calls |

### 4.5 Hooks (`src/hooks/`)

| File | Purpose |
|------|---------|
| `useAutoSelectSize.js` / `V2` | Auto-selects product size |
| `useColorProducts.js` | Fetches color variant products |
| `useColorTabIndex.js` | Manages color tab selection |
| `useGenderTabIndex.js` | Manages gender tab selection |
| `usePredictiveSearch.ts` | Search suggestions API |
| `useRemoveOutOfStockProducts.js` | Filters out OOS items from cart |
| `useTwiningOptions.js` | Twinning product options |
| `useVirtualTryOn.js` | Virtual try-on camera logic |

### 4.6 Helpers (`src/helpers/`)

| File | Purpose |
|------|---------|
| `eventsHelper.js` | WebEngage event mapping (436 lines) — maps internal events to `App_*` events |
| `setUserAttributes.js` | Sets WebEngage user attributes (last purchase, etc.) |
| `registerToolBarIcons.js` | Registers custom toolbar/header icons |
| `helper.js` | General helper functions |
| `removeOutOfStock.js` | Removes OOS products |
| `useProductExtraData.js` | Fetches extra product data (highlights, style tips) |
| `useProductCollections.js` | Fetches product collections |
| `useTwiningProducts.js` | Fetches twinning/matching products |
| `themeEventEmitter.js` | Simple event emitter instance |

### 4.7 Utils (`src/utils/`)

| File | Purpose |
|------|---------|
| `constants.js` | App constants (7KB) |
| `function.js` | Utility functions (cart, formatting, etc.) |
| `ImagePath.js` | All image asset paths/requires |
| `AsyncStorage.js` | AsyncStorage wrapper utilities |
| `GetMetaObject.js` | GraphQL metaobject fetcher |
| `GetProductById.js` | Fetch product by ID (GraphQL) |
| `GetUserLastOrder.js` | Fetch user's latest order (14KB) |
| `deliveryUtils.js` | Delivery/pincode check utilities (11KB) |
| `checkLocationInventory.js` | Store inventory checker |
| `validators.js` | Input validation functions |
| `videoPlayer.js` | Video player utilities |
| `genrateRef.js` | Reference ID generator |
| `getMediaImage.js` | Media image URL helper |
| `vto.js` | VTO utility functions |

### 4.8 Styles (`src/styles/`)

| File | Purpose |
|------|---------|
| `index.js` | **Design tokens**: colors, spacing, fonts, font sizes |
| `PX.js` | Pixel scaling utility |

**Key Style Exports**:
```js
import { color, spacing, font, dimensions, isTab } from '../styles';
```

- **`isTab`**: `deviceRatio < 1.6` — tablet detection used globally
- **`font.family`**: Futura, Raleway, OpenSans, NewYork, Forum
- **`font.size`**: 9–55px (auto-scaled ×1.4 for tablets via `getFontSize()`)
- **`color`**: black, white, grey, redCC, etc.
- **`spacing`**: micro(2) → xxxl(72)

---

## 5. Other Packages

### 5.1 `swish-wishlist-king/`
- Wishlist integration with Wishlist King API
- **Entry**: `src/index.js`
- **Key**: `src/blocks/components/wishlist/WishlistHeader.js` — wishlist header UI
- Has its own API layer, blocks, and pages

### 5.2 `dd-custom-app-login-appmaker/`
- Custom login/registration flow
- **Entry**: `src/index.js`
- Has: actions, blocks, components, constants, pages, services, styles, utils

### 5.3 `lucent-simply-otp/`
- OTP-based authentication
- **Entry**: `src/index.js`
- **Key files**: `actions.js` (13KB — OTP send/verify), `filters.js` (8KB), `emailFilters.js`

### 5.4 `plugin-webengage/`
- WebEngage analytics integration
- **Entry**: `src/index.js`
- **Key**: `events.js` (22KB — maps all app events to WebEngage events)
- Handles: product_viewed, cart events, checkout, user events, etc.

### 5.5 `plugin-tagalys/`
- Tagalys product search/recommendation engine
- **Entry**: `src/index.js`
- Handles product search and filtering

---

## 6. Core SDK Dependencies

| Package | Purpose |
|---------|---------|
| `@appmaker-xyz/core` | Core framework: `appmaker`, `getUser`, `analytics`, `helpers`, `addFilter`, `appStorageApi` |
| `@appmaker-xyz/shopify` | Shopify integration: `fetchUser`, `syncCartFromId`, `shopifyIdHelper`, `fieldsHelper` |
| `@appmaker-xyz/shopify/actions/helper/manage-cart` | `manageCartHandler` for cart operations |
| `@appmaker-xyz/react-native` | `handleAction` for dispatching app actions |
| `@appmaker-xyz/ui` / `@appmaker-xyz/uikit` | UI components |

### Key Appmaker Patterns

```js
// Register a filter (modify data at hook points)
appmaker.addFilter('filter-name', 'namespace', (data, context) => modifiedData);

// Register an action
appmaker.actions.registerAction('ACTION_NAME', handlerFn);

// Dispatch an action
handleAction({ action: 'ACTION_NAME', params: {} });

// Track analytics
analytics.onTrack((event, params, context) => { ... }, 'namespace');

// Get current user
const user = getUser(); // sync, from cache
const user = await fetchUser({ metafields: [...] }); // async, with metafields

// App state
appStorageApi().setState({ key: value });
```

---

## 7. Tablet Detection Patterns

Multiple approaches used across the codebase:

```js
// Method 1: From styles (global)
import { isTab } from '../styles';
// isTab = (screenHeight / screenWidth) < 1.6

// Method 2: In component (local)
const { width, height } = useWindowDimensions();
const isTablet = width >= 768;

// Method 3: More precise
const ASPECT_RATIO = height / width;
const isTablet = Math.min(width, height) >= 600 && ASPECT_RATIO < 1.6;

// Method 4: From react-native-element-dropdown
const { isTablet, isIOS } = useDetectDevice;
```

---

## 8. Custom Shopify Metafields (via `function.js`)

Products have these custom metafields added via GraphQL:
- `custom.petticoat_option`, `custom.shapewear_option`, `custom.saree_stitching_option`
- `custom.similar_color_products`, `custom.primary_color`
- `custom.product_attribute`, `custom.style_tip`, `custom.product_highlights`
- `custom.gumlet_video_url`, `custom.custom_product_visibility`
- `custom.size_chart_collection`, `custom.size_type_settings`
- `custom.express_delivery`, `custom.try_on_sku`
- `custom.twining_products`, `custom.product_care`
- `seo.hidden`

Collections have:
- `custom.custom_breadcrumbs`, `custom.collection_banner`, `custom.collection_banner_mobile`
- `custom.collection_tc_content`

Customer metafields:
- `custom.cart_id` — Shopify cart ID for cross-device sync
- `custom.cart_json` — Web cart items for web→app sync
- `custom.gender1`, `custom.birth_date`
- `simply-otp-login.anniversary_date`, `simply-otp-login.date_of_birth`

---

## 9. External APIs

| Endpoint | Used In | Purpose |
|----------|---------|---------|
| `https://apps.kalkifashion.com/kalki-india-app/updateCartMetadata.php` | `updateCartMetafield.js` | Save cart_id to customer |
| `https://api.kalkifashion.com/kalki-india-app/updateCartMetadata.php` | `clearCartJson.js` | Clear cart_json metafield |

---

## 10. Event Names (Analytics)

### Internal → WebEngage Mapped Events (`eventsHelper.js`)
| Internal Event | WebEngage Event |
|---------------|-----------------|
| `Added To Cart` | `App_Added To Cart` |
| `Removed From Cart` | `App_Removed From Cart` |
| `Product Viewed` | `App_Product Viewed` |
| `Searched Product` | `App_Searched Product` |
| `Category Viewed` | `App_Category Viewed` |
| `Cart Viewed` | `App_Cart Viewed` |
| `Cart Updated` | `App_Cart Updated` |
| `Checkout Button Clicked` | `App_Checkout Button Clicked` |
| `Customer Registered` | `App_Customer Registered` |
| `Customer Login` | `App_Customer Login` |
| `Checkout Created` | `App_Checkout created` |
| `Order Completed` | `App_Order Completed` |

### System Events (`analytics.onTrack`)
| Event | Action |
|-------|--------|
| `cart_created` / `cart_updated` | Saves cart ID to customer metafield |
| `checkout_completed` | Clears cart metafield + cart_json + local cart |
| `user_login` | Triggers cart sync after 1s delay |
| `user_logout` | Clears local cart |
| `initial_action` | Triggers cart sync after 1s delay |

---

## 11. Key Actions

| Action | Purpose |
|--------|---------|
| `CLEAR_CART` | Clears the local cart |
| `UPDATE_CART_V2` | Updates local cart with line items |
| `LOGOUT` | Logs out user |
| `OPEN_URL` | Opens a URL |
| `CUSTOM_LOGOUT` | Custom logout (clears register popup + calls LOGOUT) |

---

## 12. Important Notes & Gotchas

1. **File sizes**: `ProductGridItem.js` (99KB), `Variation.js` (88KB), `ProductData.js` (72KB), `AddToCartButton.js` (51KB) — these are very large files, read specific sections only.
2. **Two Variation.js files**: One in `PDP/Variation.js` (88KB) and one in `PLP/Variation.js` (63KB) — different components!
3. **Font scaling**: All font sizes auto-scale ×1.4 on tablets via `getFontSize()` in `styles/index.js`.
4. **Screen orientation**: Locked to PORTRAIT via `expo-screen-orientation` in the app wrapper.
5. **Product visibility**: Products with `custom_product_visibility = "no"` are filtered from all lists via the `shopify-response-data` filter.
6. **Two cart metafield endpoints**: `apps.kalkifashion.com` for cart_id and `api.kalkifashion.com` for cart_json — different base URLs!
7. **Appmaker actions are async**: Always `await` them if you need to ensure completion.
8. **brain.md location**: This file is at `.agents/brain.md` — NOT inside theme-kalki. Do NOT commit to theme package.

---

## 13. DELIVERY_CALCULATION_CLEANUP

- **Core Calculator (`eddHelper.js`)**:
  - `calculateEDD`: Calculates EDD based on inventory (RTS vs MTO), stitching days, override days, and international shipping settings.
  - `getMetafieldFromProduct`: Reads metafields (`mto_rts_days`, `fast_shipping`, `stitching_days`, `days_override`) from product object or `product.metafields` array.
  - **Gift Cards**: If `productType`, `title`, or `sku` is `'Gift Card'`, returns `estimatedDeliveryDate: ''`.
- **PDP (`ProductData.js`)**:
  - **Gift Cards**: Omitted from cart line item customAttributes and hides Estimated delivery UI section.
  - **Twining Products**: `maxTwiningEDDResult` calculates EDD for both Female and Male products using `calculateEDD`, compares dates via `addBusinessDays`, and displays/passes the highest EDD.
- **Cart & Checkout (`CartCard.js`)**:
  - **Gift Cards**: Excluded from line item `Estimated delivery` attributes and hidden from Cart UI so EDD is hidden in Cart & Checkout.
  - **Twining Products**: Retains the highest EDD passed from PDP.
