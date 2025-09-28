# AVAILABLE ENDPOINTS

This document provides an overview of all available API endpoints, their methods, permissions, and descriptions.  
For detailed examples, see the Postman documentation or the hosted Swagger UI.

---

## Users

| HTTP Method | Path                         | Functionality                       | Permissions     | Extra Notes                                   |
| ----------- | ---------------------------- | ----------------------------------- | --------------- | --------------------------------------------- |
| GET         | /api/users/                  | List all users                      | Authenticated   | Admin/staff only in production                |
| POST        | /api/users/                  | Register a new user                 | AllowAny        | Returns created user data                     |
| GET         | /api/users/{user_id}/        | Retrieve user details               | Authenticated   | User can only view their own profile          |
| PUT         | /api/users/{user_id}/        | Fully update a user                 | Authenticated   | Can only update their own account             |
| PATCH       | /api/users/{user_id}/        | Partially update a user             | Authenticated   | e.g. `first_name`, `last_name`, `email`       |
| DELETE      | /api/users/{user_id}/        | Delete a user account               | Authenticated   | User can delete their own account             |
| GET         | /api/users/me/               | Get the authenticated user’s profile| IsUser          | Profile endpoint scoped to the current user   |
| PUT         | /api/users/me/               | Update the authenticated user       | IsUser          | Replace all profile fields                    |
| PATCH       | /api/users/me/               | Partially update user profile       | IsUser          | Update address, phone, avatar, etc.           |
| POST        | /api/users/password_change/  | Change password                     | Authenticated   | Email/notification integration optional       |
| POST        | /api/users/password_reset/   | Reset password                      | AllowAny        | Email/notification integration optional       |

---

## Products

| HTTP Method | Path                         | Functionality                       | Permissions     | Extra Notes                                   |
| ----------- | ---------------------------- | ----------------------------------- | --------------- | --------------------------------------------- |
| GET         | /api/products/               | List all products                   | AllowAny        | Supports filtering, sorting, pagination       |
| GET         | /api/products/{product_id}/  | Get product details                 | AllowAny        | Public, cached                                |
| GET         | /api/products/search/?q=term | Search products by name/description | AllowAny        | Requires query parameter `q`                  |

---

## Categories

| HTTP Method | Path                         | Functionality                       | Permissions     | Extra Notes                                   |
| ----------- | ---------------------------- | ----------------------------------- | --------------- | --------------------------------------------- |
| GET         | /api/categories/             | List all categories                 | AllowAny        | Useful for filters and navigation             |

---

## Cart

| HTTP Method | Path                         | Functionality                       | Permissions     | Extra Notes                                   |
| ----------- | ---------------------------- | ----------------------------------- | --------------- | --------------------------------------------- |
| GET         | /api/cart/                   | Retrieve current user’s cart        | Authenticated   | Includes products, quantities, totals         |
| POST        | /api/cart/                   | Add product to cart                 | Authenticated   | Requires `product_id` and `quantity`          |
| PATCH       | /api/cart/{item_id}/         | Update cart item quantity           | Authenticated   | Adjust quantity of a cart item                |
| DELETE      | /api/cart/{item_id}/         | Remove product from cart            | Authenticated   | Returns `204 No Content`                      |

---

## Orders

| HTTP Method | Path                         | Functionality                       | Permissions     | Extra Notes                                   |
| ----------- | ---------------------------- | ----------------------------------- | --------------- | --------------------------------------------- |
| GET         | /api/orders/                 | List all orders for user            | Authenticated   | Paginated                                     |
| POST        | /api/orders/                 | Create new order                    | Authenticated   | Requires products, payment, shipping info     |
| GET         | /api/orders/{order_id}/      | Retrieve order details              | Authenticated   | Only order owner or admin can access          |
| PATCH       | /api/orders/{order_id}/      | Update order (e.g. status)          | Admin Only      | For managing fulfillment                      |

---

## Authentication

| HTTP Method | Path                         | Functionality                       | Permissions     | Extra Notes                                   |
| ----------- | ---------------------------- | ----------------------------------- | --------------- | --------------------------------------------- |
| POST        | /api/token/                  | Obtain JWT access and refresh tokens| AllowAny        | Requires email & password                     |
| POST        | /api/token/refresh/          | Refresh an expired access token     | AllowAny        | Requires valid refresh token                  |

---

## Notes

- All protected endpoints require `Authorization: Bearer <token>` in the request header.  
- Errors follow standard HTTP status codes (`401 Unauthorized`, `403 Forbidden`, etc.).  
- For interactive exploration, visit the Swagger UI at `/swagger/`.  
