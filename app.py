from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import random
from datetime import datetime, timedelta
import csv, os
import pytz
from config import *

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Flask-Mail setup
app.config.update(
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_USE_TLS=MAIL_USE_TLS,
    MAIL_USE_SSL=MAIL_USE_SSL
)
mail = Mail(app)

# Dummy products
products = {
    "Moroccon Neela Powder": 1399,
    "XQM BB imported": 600,
    "Hydrating Face Cream": 1299
}

# --- CSV File Path ---
ORDERS_FILE = "orders.csv"

# --- CSV File Header (if not exists) ---
if not os.path.exists(ORDERS_FILE):
    with open(ORDERS_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "OrderID", "CustomerName", "Phone", "Email",
            "Address", "Description", "Items",
            "DeliveryFee", "Total", "Status", "Date"
        ])

# Pakistan Timezone
PKT = pytz.timezone("Asia/Karachi")

from flask import Flask, render_template, request, redirect, url_for, session
import csv





# ---- Login ----
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']

        # Admin login
        if role == 'admin' and email == "admin@gmail.com" and password == "admin123":
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        
        # Client login
        elif role == 'client':
            session['role'] = 'client'
            session['email'] = email
            return redirect(url_for('client_dashboard'))

    return render_template('login.html')

# ---- Admin Dashboard ----
@app.route('/admin')
def admin_dashboard():
    if session.get('role') == 'admin':
        orders = []
        with open("orders.csv", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                orders.append(row)
        return render_template('admin_dashboard.html', orders=orders)
    return redirect(url_for('login'))

# ---- Client Dashboard ----
@app.route('/client')
def client_dashboard():
    if session.get('role') == 'client':
        email = session['email']
        orders = []
        with open("orders.csv", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Email'] == email:
                    orders.append(row)
        return render_template('client_dashboard.html', orders=orders)
    return redirect(url_for('login'))




# ------------------- PAGES -------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cosmetics')
def cosmetics_page():
    return render_template('cosmetics.html')

@app.route('/health')
def health_page():
    return render_template('health.html')

@app.route('/laces')
def laces_page():
    return render_template('laces.html')

@app.route('/jewellery')
def jewellery_page():
    return render_template('jewellery.html')

@app.route('/shoes')
def shoes_page():
    return render_template('shoes.html')

@app.route('/clothes')
def clothes_page():
    return render_template('clothes.html')

@app.route('/cart')
def cart_page():
    return render_template('cart.html', products=products)

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

# ------------------- CHECKOUT -------------------

@app.route('/checkout', methods=['GET','POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        description = request.form.get('description', '')  # optional notes
        cart_data = request.form['cart_data']

        import json
        items = json.loads(cart_data)

        # Example delivery fee calculation
        delivery_fee = 100  
        total = delivery_fee
        for item in items:
            total += item['price'] * item['quantity']

        order_number = random.randint(100000, 999999)

        # Pakistan Time
        now = datetime.now(PKT)

        # Save order in session
        order = {
            'order_number': order_number,
            'name': name,
            'phone': phone,
            'email': email,
            'address': address,
            'description': description,
            'items': items,
            'delivery_fee': delivery_fee,
            'total': total,
            'timestamp': now.isoformat(),
            'status': 'confirmed'
        }
        session['order'] = order

        # ---------------- Save to CSV ----------------
        items_str = "; ".join([f"{i['name']} (x{i['quantity']})" for i in items])
        with open(ORDERS_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                order_number, name, phone, email,
                address, description, items_str,
                delivery_fee, total, "confirmed",
                now.strftime("%Y-%m-%d %H:%M:%S")
            ])

        # ---------------- Email to Customer ----------------
        cust_items_html = ""
        for item in items:
            cust_items_html += f"<tr><td>{item['name']}</td><td>{item['quantity']}</td><td>PKR {item['price']}</td><td>PKR {item['price']*item['quantity']}</td></tr>"

        cust_html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;">
          <h2>Order Confirmation - Kayiral Sellers</h2>
          <p>Hi {name},</p>
          <p>Thank you for your order! Your order number is <strong>#{order_number}</strong>.</p>
          <h3>Shipping Address</h3>
          <p>{address}</p>
          {"<h3>Additional Notes:</h3><p>"+description+"</p>" if description else ""}
          <h3>Order Items</h3>
          <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Product</th><th>Quantity</th><th>Price</th><th>Total</th></tr>
            {cust_items_html}
            <tr><td colspan="3"><strong>Delivery Fee</strong></td><td>PKR {delivery_fee}</td></tr>
            <tr><td colspan="3"><strong>Grand Total</strong></td><td>PKR {total}</td></tr>
          </table>
          <p>Your order will be delivered soon.</p>
          <p>For order-related discussion, contact us on WhatsApp: <strong>0349 9832172</strong></p>
          <p><a href="http://localhost:5000/track-order?order_id={order_number}" 
                style="display:inline-block;padding:10px 20px;background:#27ae60;color:#fff;text-decoration:none;border-radius:5px;">Track Your Order</a></p>
          <p><a href="http://localhost:5000/" style="display:inline-block;padding:10px 20px;background:#2a7ae2;color:#fff;text-decoration:none;border-radius:5px;">Back to Store</a></p>
        </body>
        </html>
        """

        msg_cust = Message(
            subject=f"Order Confirmation - Kayiral Sellers",
            sender=MAIL_USERNAME,
            recipients=[email]
        )
        msg_cust.html = cust_html
        mail.send(msg_cust)

        # ---------------- Email to Owner ----------------
        owner_items_html = ""
        for item in items:
            owner_items_html += f"<tr><td>{item['name']}</td><td>{item['quantity']}</td><td>PKR {item['price']}</td><td>PKR {item['price']*item['quantity']}</td></tr>"

        owner_html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;">
          <h2>New Order #{order_number}</h2>
          <p><strong>Customer:</strong> {name}</p>
          <p><strong>Phone:</strong> {phone}</p>
          <p><strong>Email:</strong> {email}</p>
          <p><strong>Address:</strong> {address}</p>
          {"<h3>Additional Notes:</h3><p>"+description+"</p>" if description else ""}
          <h3>Order Items</h3>
          <table border="1" cellpadding="5" cellspacing="0">
            <tr><th>Product</th><th>Quantity</th><th>Price</th><th>Total</th></tr>
            {owner_items_html}
            <tr><td colspan="3"><strong>Delivery Fee</strong></td><td>PKR {delivery_fee}</td></tr>
            <tr><td colspan="3"><strong>Grand Total</strong></td><td>PKR {total}</td></tr>
          </table>
          <p>Contact customer for further discussion: Phone: {phone}</p>
        </body>
        </html>
        """

        msg_owner = Message(
            subject=f"New Order #{order_number} from {name}",
            sender=MAIL_USERNAME,
            recipients=[MAIL_USERNAME]  # only seller
        )
        msg_owner.html = owner_html
        mail.send(msg_owner)

        return redirect(url_for('order_confirmation'))

    return render_template('checkout.html', products=products)

# ------------------- ORDER CONFIRMATION -------------------

@app.route('/order-confirmation')
def order_confirmation():
    order = session.get('order')
    if not order:
        return redirect(url_for('checkout'))

    order_time = datetime.fromisoformat(order['timestamp'])
    cancel_window = timedelta(minutes=30)
    can_cancel = datetime.now(PKT) - order_time <= cancel_window

    return render_template('order_confirmation.html',
                           order=order,
                           can_cancel=can_cancel,
                           clear_cart=True)

# ------------------- CANCEL ORDER -------------------
@app.route('/cancel-order')
def cancel_order():
    order = session.get('order')
    if not order:
        return redirect(url_for('checkout'))

    order_time = datetime.fromisoformat(order['timestamp'])
    cancel_window = timedelta(minutes=30)
    order_id = order['order_number']   # ✅ order_id define kiya

    if datetime.now(PKT) - order_time <= cancel_window:
        order['status'] = 'cancelled'
        session['order'] = order

        # Notify owner
        msg_owner = Message(
            subject=f"Order Cancelled - {order['name']}",
            sender=MAIL_USERNAME,
            recipients=[MAIL_USERNAME]
        )
        msg_owner.body = (
            f"Order #{order_id} cancelled by customer: {order['name']}\n"
            f"Items: {[i['name'] for i in order['items']]}\n"
            f"Total: PKR {order['total']}"
        )
        mail.send(msg_owner)

        # Notify customer
        msg_cust = Message(
            subject=f"Your Order #{order_id} Cancelled - Kayiral Sellers",
            sender=MAIL_USERNAME,
            recipients=[order['email']]
        )
        msg_cust.body = f"""Hi {order['name']},

🎉 Your order #{order_id} has been successfully cancelled! 🎉

We hope to serve you again soon!

Thank you for choosing Kayiral Sellers."""
        mail.send(msg_cust)

        # ✅ Update CSV order status to "cancelled"
        rows = []
        with open(ORDERS_FILE, mode="r") as file:
            reader = csv.DictReader(file)
            for r in reader:
                if r["OrderID"] == str(order_id):
                    r["Status"] = "cancelled"
                rows.append(r)

        with open(ORDERS_FILE, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        # Clear cart/session
        session.pop('order', None)

        return f"<h2 style='text-align:center;color:#e74c3c;'>🎉 Your order #{order_id} has been successfully cancelled! 🎉</h2>"

    return f"<h2 style='text-align:center;color:#e74c3c;'>❌ Sorry, you can no longer cancel order #{order_id}.</h2>"

# ------------------- TRACK ORDER -------------------

@app.route("/track-order", methods=["GET", "POST"])
def track_order():
    order = None
    searched = False
    if request.method == "POST":
        searched = True
        order_id = request.form["order_id"]
        with open("orders.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["OrderID"] == order_id:
                    order = row
                    break
    return render_template("track_order.html", order=order, searched=searched)

# ------------------- MARK ORDER AS DELIVERED -------------------
@app.route('/mark-delivered', methods=['POST'])
def mark_delivered():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    order_id = request.form['order_id']
    rows = []

    # Read CSV
    with open(ORDERS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['OrderID'] == order_id and r['Status'].lower() == 'confirmed':
                r['Status'] = 'delivered'

                # ---------------- Email to Client ----------------
                client_msg = Message(
                    subject=f"Your Order #{order_id} has been Delivered!",
                    sender=MAIL_USERNAME,
                    recipients=[r['Email']]
                )
                client_msg.html = f"""
                <p>Hi {r['CustomerName']},</p>
                <p>🎉 Your order <strong>#{order_id}</strong> has been delivered!</p>
                <p>Please give your feedback and continue shopping: <a href="http://localhost:5000/">Shop Again</a></p>
                """
                mail.send(client_msg)

                # ---------------- Email to Owner ----------------
                owner_msg = Message(
                    subject=f"Order #{order_id} Delivered",
                    sender=MAIL_USERNAME,
                    recipients=[MAIL_USERNAME]
                )
                owner_msg.body = f"Order #{order_id} for {r['CustomerName']} has been delivered."
                mail.send(owner_msg)

            rows.append(r)

    # Write back updated CSV
    with open(ORDERS_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    return redirect(url_for('admin_dashboard'))

# ---- Cancel order from client dashboard ----
@app.route('/cancel-order-client', methods=['POST'])
def cancel_order_client():
    order_id = request.form.get('order_id')
    if not order_id:
        return redirect(url_for('client_dashboard'))

    # Read orders from CSV
    rows = []
    order_to_cancel = None
    with open(ORDERS_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for r in reader:
            if r["OrderID"] == order_id and r["Email"] == session.get('email'):
                order_to_cancel = r
            rows.append(r)

    if not order_to_cancel:
        return "Order not found or not authorized", 403

    # Check 30-minute cancellation window
    order_time_naive = datetime.strptime(order_to_cancel['Date'], "%Y-%m-%d %H:%M:%S")
    order_time = PKT.localize(order_time_naive)  # timezone-aware
    now_time = datetime.now(PKT)

    if now_time - order_time <= timedelta(minutes=30):
        order_to_cancel['Status'] = 'cancelled'
        # Update CSV
        with open(ORDERS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            for r in rows:
                if r["OrderID"] == order_id:
                    writer.writerow(order_to_cancel)
                else:
                    writer.writerow(r)

        # Send email to customer
        msg_cust = Message(
            subject=f"Your Order Cancelled - Kayiral Sellers (#{order_id})",
            sender=MAIL_USERNAME,
            recipients=[order_to_cancel['Email']]
        )
        msg_cust.body = f"""Hi {order_to_cancel['CustomerName']},

❌ Your order #{order_id} has been successfully cancelled.

Thank you for choosing Kayiral Sellers.
"""
        mail.send(msg_cust)

        # Send email to owner (with order details)
        msg_owner = Message(
            subject=f"Order Cancelled - #{order_id}",
            sender=MAIL_USERNAME,
            recipients=[MAIL_USERNAME]
        )
        msg_owner.body = f"""Order #{order_id} cancelled by {order_to_cancel['CustomerName']} ({order_to_cancel['Email']})."""
        mail.send(msg_owner)

        return "<h2 style='text-align:center;color:#27ae60;'>🎉 Your order has been successfully cancelled! 🎉</h2>"

    else:
        # Cannot cancel message
        return "<h2 style='text-align:center;color:#e74c3c;'>❌ Sorry, you can no longer cancel this order.</h2>"





# ------------------- RUN APP -------------------

if __name__ == "__main__":
    app.run(debug=True)                 