import io
from flask import Flask, render_template, request, redirect, session, send_file
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"
bcrypt = Bcrypt(app)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]
users = db["users"]
products = db["products"]
carts = db["carts"]
orders = db["orders"]


@app.route('/')
def initial():
    return render_template('home.html')


@app.route('/auth')
def auth():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(
            request.form['password']).decode('utf-8')
        role = request.form['role']
        users.insert_one(
            {'username': username, 'password': password, 'role': role})
        return redirect('/auth')
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = users.find_one({'username': username})
    if user and bcrypt.check_password_hash(user['password'], password):
        session['username'] = username
        session['role'] = user['role']
        return redirect('/dashboard')
    return render_template('login.html', error="Invalid username or password.")


@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect('/')
    username = session['username']
    if session['role'] == 'admin':
        return redirect('/admin/dashboard')
    products_list = list(products.find())
    user_orders = list(orders.find({'username': username}))
    return render_template('user_dashboard.html', products=products_list, orders=user_orders)


@app.route('/add_product', methods=['POST'])
def add_product():
    if session.get('role') != 'admin':
        return redirect('/')

    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    description = request.form['description']
    image_data = None

    # Handle file upload
    if 'image_file' in request.files:
        image = request.files['image_file']
        if image and image.filename != '':
            image_data = image.read()

    # Handle image URL
    if not image_data and 'image_url' in request.form:
        image_url = request.form['image_url']
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = response.content
        except:
            pass

    # If no image data, display message
    if not image_data:
        print("No image data available.")

    products.insert_one({
        'name': name,
        'price': price,
        'description': description,
        'quantity': quantity,
        'image': image_data
    })
    return redirect('/dashboard')


@app.route('/product_image/<product_id>')
def get_product_image(product_id):
    product = products.find_one({'_id': ObjectId(product_id)})
    if product and 'image' in product and product['image']:
        return send_file(BytesIO(product['image']), mimetype='image/jpeg')
    return '', 404


@app.route('/add_to_cart/<product_id>')
def add_to_cart(product_id):
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    product = products.find_one({'_id': ObjectId(product_id)})
    if not product or int(product['quantity']) <= 0:
        return """
        <div style="max-width: 500px; margin: 40px auto; padding: 20px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 8px; font-family: sans-serif; text-align: center;">
        <strong>Product not available.</strong>
        <div style="margin-top: 15px;">
            <a href="/dashboard" style="color: #0056b3; text-decoration: none; font-weight: bold;">Back to Home</a>
        </div>
        </div>
        """


    existing_item = carts.find_one(
        {'username': username, 'product_id': ObjectId(product_id)})
    if existing_item:
        carts.update_one({'_id': existing_item['_id']}, {
                         '$inc': {'quantity': 1}})
    else:
        carts.insert_one({
            'username': username,
            'product_id': product['_id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': 1
        })
    return redirect('/dashboard')


@app.route('/cart')
def view_cart():
    if 'username' not in session:
        return redirect('/')
    user_cart = list(carts.find({'username': session['username']}))
    for item in user_cart:
        product = products.find_one({'_id': item['product_id']})
        if not product or int(product['quantity']) <= 0:
            carts.delete_one({'_id': item['_id']})
    user_cart = list(carts.find({'username': session['username']}))
    total = sum(item['price'] * item['quantity'] for item in user_cart)
    return render_template('cart.html', cart=user_cart, total=total)


@app.route('/checkout')
def checkout():
    if 'username' not in session:
        return redirect('/')
    username = session['username']
    user_cart = list(carts.find({'username': username}))
    if not user_cart:
        return """
        <div style="max-width: 500px; margin: 40px auto; padding: 20px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 8px; font-family: sans-serif; text-align: center;">
        <strong>Cart is empty...</strong>
        <div style="margin-top: 15px;">
            <a href="/dashboard" style="color: #0056b3; text-decoration: none; font-weight: bold;">Back to Dashboard</a>
        </div>
        </div>
        """

    
    orders.insert_one({
        'username': username,
        'items': user_cart,
        'status': 'pending'
    })
    carts.delete_many({'username': username})
    return render_template('user_order_placed.html')


@app.route('/edit_cart/<cart_id>', methods=['GET', 'POST'])
def edit_cart(cart_id):
    if 'username' not in session:
        return redirect('/')
    cart_item = carts.find_one({'_id': ObjectId(cart_id)})
    if request.method == 'POST':
        new_quantity = int(request.form['quantity'])
        if new_quantity <= 0:
            carts.delete_one({'_id': ObjectId(cart_id)})
        else:
            carts.update_one({'_id': ObjectId(cart_id)}, {
                             '$set': {'quantity': new_quantity}})
        return redirect('/cart')
    return render_template('edit_cart.html', cart_item=cart_item)


@app.route('/delete_cart_item/<cart_id>')
def delete_cart_item(cart_id):
    if 'username' not in session:
        return redirect('/')
    carts.delete_one({'_id': ObjectId(cart_id)})
    return redirect('/cart')


@app.route('/order_status')
def order_status():
    if 'username' not in session:
        return redirect('/')
    
    orders_list = list(orders.find({'username': session['username']}))

    for order in orders_list:
        for item in order.get('items', []):
            prod = products.find_one({'_id': item['product_id']})
            item['is_missing'] = prod is None  # Add flag if product is gone

    return render_template('order_status.html', orders=orders_list)



@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')
    products_list = list(products.find())
    orders_list = list(orders.find())
    num_orders = len(orders_list)
    num_products = len(products_list)
    return render_template('admin_dashboard.html', products=products_list, orders=orders_list, num_orders=num_orders , num_products=num_products)


@app.route('/admin/orders')
def admin_orders():
    if session.get('role') != 'admin':
        return redirect('/')
    orders_list = list(orders.find())
    return render_template('admin_check_orders.html', orders=orders_list)


@app.route('/admin/add/products')
def admin_add_products():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('admin_add_products.html', )


@app.route('/admin/update_status/<order_id>', methods=['POST'])
def update_status(order_id):
    if session.get('role') != 'admin':
        return redirect('/')

    order = orders.find_one({'_id': ObjectId(order_id)})
    if not order:
        return redirect('/admin/dashboard')

    # Check if any product in the order no longer exists
    missing_products = []
    for item in order.get('items', []):
        if not products.find_one({'_id': item['product_id']}):
            missing_products.append(item['name'])

    if missing_products:
        # You can choose between "refund" or "delayed" depending on your logic
        orders.update_one({'_id': ObjectId(order_id)}, {
            '$set': {'status': 'refund'}
        })

        return f"""
        <div style="max-width: 600px; margin: 40px auto; padding: 20px; background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; border-radius: 8px; font-family: sans-serif;">
            <strong>Order status updated to 'refund'.</strong><br>
            The following product(s) are no longer available: {', '.join(missing_products)}
            <div style="margin-top: 15px;">
                <a href="/admin/dashboard" style="text-decoration: none; color: #004085; font-weight: bold;">Return to Dashboard</a>
            </div>
        </div>
        """

    # If all products exist, update to selected status
    status = request.form['status']
    orders.update_one({'_id': ObjectId(order_id)}, {
        '$set': {'status': status}
    })

    return redirect('/admin/dashboard')


@app.route('/admin/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    if session.get('role') != 'admin':
        return redirect('/')

    # Check if product is in any non-final orders
    active_orders_count = orders.count_documents({
        'status': {'$in': ['pending', 'approved', 'shipping']},
        'items': {'$elemMatch': {'product_id': ObjectId(product_id)}}
    })
    if active_orders_count > 0:
        # Optional: Store this as flash message or render template with warning
        return """
        <div style="max-width: 600px; margin: 40px auto; padding: 20px; background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; border-radius: 8px; font-family: sans-serif;">
            <strong>Warning:</strong> This product is currently in use in active orders. You cannot delete it until those orders are completed or canceled.
            <div style="margin-top: 15px;">
                <a href="/admin/dashboard" style="text-decoration: none; color: #004085; font-weight: bold;">Return to Dashboard</a>
            </div>
        </div>
        """

    # Proceed to delete the product
    products.delete_one({'_id': ObjectId(product_id)})
    return redirect('/admin/dashboard')



@app.route('/admin/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('role') != 'admin':
        return redirect('/')

    # Fetch the existing product from the database
    product = products.find_one({'_id': ObjectId(product_id)})
    if not product:
        return redirect('/admin/dashboard')  # If product is not found

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        description = request.form['description']

        # Default to current image if no new image is uploaded
        image_data = product.get('image')

        # Handle file upload (if a new file is provided)
        if 'image_file' in request.files:
            image = request.files['image_file']
            if image and image.filename != '':
                image_data = image.read()  # Read and save the image data

        # Handle image URL (if a new URL is provided)
        if not image_data and 'image_url' in request.form:
            image_url = request.form['image_url']
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = response.content  # Store image data from URL
            except:
                pass

        # If no image data is provided, print a message
        if not image_data:
            # You can also raise an error or set a default image
            print("No image data available.")

        # Update the product with new information
        products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {
                'name': name,
                'price': price,
                'quantity': quantity,
                'description': description,
                'image': image_data  # Update image if changed
            }}
        )
        return redirect('/admin/dashboard')

    return render_template('admin_edit_product.html', product=product)


@app.route('/cancel_order/<order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'username' not in session:
        return redirect('/')
    order = orders.find_one({'_id': ObjectId(order_id)})
    if order and order['username'] == session['username']:
        orders.update_one({'_id': ObjectId(order_id)}, {
                          '$set': {'status': 'canceled'}})
    return redirect('/order_status')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
