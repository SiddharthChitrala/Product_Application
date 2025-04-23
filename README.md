# E-commerce QuickCart Website with Flask

This is a fully functional e-commerce website built using **Flask**, **MongoDB**, and **Flask-Bcrypt** for password hashing. It offers features like user registration, login, product management, shopping cart, checkout, and order management. Admins can manage products and orders from a dedicated dashboard.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Routes](#routes)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication**: 
  - Register and log in with hashed passwords.
  - Session-based authentication with user roles (admin, user).
  
- **Admin Panel**: 
  - Admin users can manage products, view all orders, and modify order statuses.
  - Admins can add, edit, and delete products (including product images via file upload or URL).
  
- **Product Management**: 
  - Display products with descriptions, prices, and images.
  
- **Shopping Cart**: 
  - Users can add products to their cart and manage the quantity of items.
  - Cart persistence across sessions.
  
- **Order Management**: 
  - Users can place orders from their cart.
  - Admins can update order status (pending, approved, shipping, canceled, etc.).

- **Responsive Design**: 
  - Works well on desktop and mobile devices for a seamless experience.

## Technologies Used

- **Flask**: Web framework for Python to handle routing, views, and templates.
- **MongoDB**: NoSQL database for storing user, product, and order data.
- **Flask-Bcrypt**: Used for password hashing and security.
- **Werkzeug**: For secure file handling (uploads).
- **Requests**: To handle external image URLs.
- **HTML5/CSS3**: For front-end development (templates).
- **Bootstrap**: For responsive and modern UI components.

## Installation

### Prerequisites

- **Python 3.6+**: You need Python installed on your machine.
- **MongoDB**: Local MongoDB instance or a cloud-based MongoDB service (like Atlas).

### Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/ecommerce-flask.git
   cd ecommerce-flask
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**:
   - You can use a local MongoDB installation or a cloud service like [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
   - Create a database called `ecommerce` and ensure the following collections are available: `users`, `products`, `carts`, `orders`.

5. **Run the Flask application**:

   ```bash
   python app.py
   ```

   The application will be accessible at [http://localhost:5000](http://localhost:5000).

## Usage

### Home Page

Upon visiting the site, users can:

- View a list of products.
- Register for a new account or log in if they are already registered.

### User Registration & Login

- Users can create an account by providing a username, password, and role.
- Registered users can log in with their credentials to access their dashboard, view products, add them to the cart, and place orders.

### Admin Panel

- Admins can access a dedicated dashboard at `/admin/dashboard`.
- Admins have the ability to add, edit, and delete products, as well as manage the status of orders.

### Shopping Cart & Checkout

- Users can view their cart, update quantities, remove items, and proceed to checkout.
- After placing an order, the cart is cleared, and the order status is marked as "pending" by default.

### Order Status

- Users can view their order status, which will be updated based on actions taken by the admin (e.g., shipped, canceled).
- Admins can modify the order status as required.

## Routes

| Route                          | Description                                   |
|--------------------------------|-----------------------------------------------|
| `/`                            | Home page, view products                      |
| `/auth`                        | Authentication page (Login/Signup)            |
| `/register`                    | User registration page                        |
| `/login`                       | User login action (POST)                      |
| `/dashboard`                   | User dashboard, product list, order history   |
| `/add_product`                 | Add new product (Admin only)                  |
| `/product_image/<product_id>`  | Get product image                             |
| `/add_to_cart/<product_id>`    | Add product to cart                           |
| `/cart`                        | View and edit cart                            |
| `/checkout`                    | Checkout and place an order                   |
| `/order_status`                | View order status                             |
| `/admin/dashboard`             | Admin dashboard with product and order stats  |
| `/admin/orders`                | Admin panel to manage orders                  |
| `/admin/add/products`          | Admin panel to add new products               |
| `/admin/update_status/<order_id>`| Admin updates order status                   |
| `/admin/delete_product/<product_id>`| Admin deletes a product                   |
| `/logout`                      | Log out and clear session                     |

## Screenshots

**Home Page (Products View)**

![Home Page](assets/screenshots/home_page.png)

**User Dashboard**

![User Dashboard](assets/screenshots/user_dashboard.png)

**Admin Dashboard**

![Admin Dashboard](assets/screenshots/admin_dashboard.png)

**Cart Page**

![Cart Page](assets/screenshots/cart_page.png)

## Contributing

We welcome contributions to improve the project! Feel free to fork the repository, make improvements, and submit pull requests.

### How to contribute:

1. Fork the repository.
2. Create a new branch for your feature/fix (`git checkout -b feature-name`).
3. Make changes and commit them (`git commit -am 'Add feature-name'`).
4. Push to the branch (`git push origin feature-name`).
5. Submit a pull request to the `main` branch.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README provides an organized overview of the project, setup instructions, and helpful details for both developers and users. Feel free to customize it further based on your preferences and additional features you want to highlight!
