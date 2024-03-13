import streamlit as st
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components
import re


# Initialize SQLite database
conn = sqlite3.connect('ecommerce.db')
c = conn.cursor()

# Create tables if not exists
c.execute('''
          CREATE TABLE IF NOT EXISTS users (
              user_id INTEGER PRIMARY KEY,
              username TEXT,
              email TEXT,
              password TEXT
          )
          ''')

c.execute('''
          CREATE TABLE IF NOT EXISTS orders (
              order_id INTEGER PRIMARY KEY,
              user_id INTEGER,
              product_name TEXT,
              quantity INTEGER,
              order_date TEXT,
              FOREIGN KEY (user_id) REFERENCES users (user_id)
          )
          ''')

# Add robots table
c.execute('''
          CREATE TABLE IF NOT EXISTS robots (
              robot_id INTEGER PRIMARY KEY,
              name TEXT,
              qty INTEGER,
              price REAL,
              color TEXT,
              description TEXT
          )
          ''')

# Populate robots table with placeholder data
robot_data = []

c.executemany('INSERT OR IGNORE INTO robots (name, qty, price, color, description) VALUES (?, ?, ?, ?, ?)', robot_data)
conn.commit()

# Function to validate email format using regex
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to fetch orders
@st.cache_data
def fetch_orders(user_id):
    return c.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,)).fetchall()

# Function to send email
@st.cache_data
def send_email(to_email, subject, body):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'your_email@example.com'
    smtp_password = 'your_email_password'

    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, msg.as_string())
        st.success(f"Email sent successfully to {to_email}")
    except smtplib.SMTPConnectError as e:
        st.error(f"SMTP connection failed: {e}")
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"SMTP authentication failed: {e}")
    except smtplib.SMTPException as e:
        st.error(f"SMTP error occurred: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


    
# Function to fetch user details
@st.cache_data
def fetch_user(user_id):
    return c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()

# Function to register a new user
@st.cache_data
def register_user(username, email, password):
    c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
    conn.commit()

# Function to log in a user
# Function to log in a user
@st.cache_data
def login_user(email, password):
    user = c.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
    if user:
        st.session_state.user_id = user[0]
        return user
    else:
        return None

    
# Function to process payment
@st.cache_data
def process_payment(total_amount):
    if 'user_id' not in st.session_state:
        st.error('Please log in to proceed with payment.')
        return
    
    user_id = st.session_state.user_id
    # Add your payment processing logic here
    # For example, you can update the order status in the database
    # This is a placeholder function, replace it with your actual payment processing logic
    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if 'user_id' in st.session_state:
        user_id = st.session_state.user_id
        c.execute('INSERT INTO orders (user_id, product_name, quantity, order_date) VALUES (?, ?, ?, ?)',
              (user_id, 'Online Payment', 1, order_date))
        conn.commit()
        st.success("Payment successful! It will take 3 working days to process your payment.")
    else:
        st.error("Please log in to proceed with payment.")



# Streamlit app
# Streamlit app
def main():
    # Display buttons side by side on top
    col1, col2, col3, col4, col5 = st.columns(5)  # Use col5 for the new button


    # Initialize session_state
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 'home'

    # Set background image for the whole page
    st.markdown(
        """
        <style>
            .stApp {
                background-image: url('https://images.unsplash.com/photo-1555255707-c07966088b7b?q=80&w=1932&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
                background-size: cover;
            }
            /* Change font color to white */
             .stTextInput, .stText {
                color: white !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Container for each section
    container_home = st.container()
    container_shop = st.container()
    container_account = st.container()
    container_cart = st.container()

    # Cart
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    # Home
    with col1:
        if st.button('Home') or st.session_state.current_section == 'home':
            st.session_state.current_section = 'home'
            container_shop.empty()  # Clear other sections
            container_account.empty()
            container_cart.empty()
            container_home.empty()  # Add this line to clear the home section
            container_home.header('Robotics E-commerce Website')
            container_home.write("Created by Law Yi Yang.")

    # Shop
    with col2:
        if st.button('Shop') or st.session_state.current_section == 'shop':
            st.session_state.current_section = 'shop'
            container_home.empty()  # Clear other sections
            container_account.empty()
            container_cart.empty()
            container_shop.header('Shop')

            # Fetch and display robot products
            robots = c.execute('SELECT * FROM robots').fetchall()
            if robots:
                container_shop.header('Robot Products')
                row_num = 0
                for robot in robots:
                    if row_num % 4 == 0:
                        row = container_shop.columns(4)
                    with row[row_num % 4]:
                        product_id, name, qty, price, color, description = robot
                        product_image_path = f'product{product_id}.jpg'

                        # Provide a unique key for each button by appending product_id
                        if st.button(f"{name}\n\nPrice: ${price:.2f}", key=f"button_{product_id}"):
                            # Update selected_product in the session state
                            st.session_state.selected_product = {
                                'id': product_id,
                                'name': name,
                                'qty': qty,
                                'price': price,
                                'color': color,
                                'description': description
                            }

                        st.image(product_image_path, use_column_width=True, caption=f"{name}\nPrice: ${price:.2f}")

                    row_num += 1
            else:
                container_shop.warning('No robot products found.')

    # Cart
    with col3:
        if st.button('Cart') or st.session_state.current_section == 'cart':
            st.session_state.current_section = 'cart'
            container_home.empty()  # Clear other sections
            container_shop.empty()  # Clear Shop section
            container_account.empty()
            container_cart.header('Shopping Cart')

            if not st.session_state.cart:
                container_cart.warning('Your cart is empty.')
            else:
                total_amount = sum(item['price'] for item in st.session_state.cart)
                container_cart.write('### Cart Items:')
                for item in st.session_state.cart:
                    container_cart.write(f"- {item['name']} (${item['price']:.2f})")

                container_cart.write(f'### Total Amount: ${total_amount:.2f}')

                # Check if the user is logged in before displaying the payment button
                if 'user_id' in st.session_state:
                    # Add a button to proceed with payment
                    if st.button('Proceed to Payment'):
                        # Process payment and display a message
                        st.image('Payment.png', use_column_width=True)
                        process_payment(st.session_state.user_id, total_amount)
                        container_cart.success(f"Payment successful! It will take 3 working days to process your payment.")
                else:
                    container_cart.warning('Please log in to proceed with payment.')

    # Account
    with col4:
        if st.button('Account') or st.session_state.current_section == 'account':
            st.session_state.current_section = 'account'
            container_home.empty()  # Clear other sections
            container_shop.empty()
            container_cart.empty()

            # Check if the user is logged in
            if 'user_id' in st.session_state:
                # If the user is logged in, show account details and order history
                user_id = st.session_state.user_id
                user = fetch_user(user_id)
                container_account.subheader(f'Hello, {user[1]}!')

                # Display account details
                container_account.write('### Account Details:')
                container_account.write(f'- Username: {user[1]}')
                container_account.write(f'- Email: {user[2]}')

                # Display order history
                orders = fetch_orders(user_id)
                if orders:
                    container_account.write('### Order History:')
                    for order in orders:
                        container_account.write(
                            f"- Order ID: {order[0]}, Product: {order[2]}, Quantity: {order[3]}, Order Date: {order[4]}")
                else:
                    container_account.warning('No order history.')
            else:
                # If the user is not logged in, show the login/registration form

                # Registration form
                username = st.text_input('Username:')
                email_register = st.text_input('Email (Register):', key='email_register')  # Unique key for registration form
                password_register = st.text_input('Password (Register):', type='password')

                if st.button('Register'):
                    # Perform basic validation
                    if not username or not email_register or not password_register:
                        st.error('Please fill in all fields.')
                    elif not validate_email(email_register):
                        st.error('Please enter a valid email address.')
                    else:
                        # Check if the email is already registered
                        existing_user = c.execute('SELECT * FROM users WHERE email = ?', (email_register,)).fetchone()
                        if existing_user:
                            st.error('Email is already registered. Please use a different email.')
                        else:
                            # Register the new user
                            register_user(username, email_register, password_register)
                            st.success('Registration successful! You can now log in.')

                # Login form
                email_login = st.text_input('Email (Login):', key='email_login')  # Unique key for login form
                password_login = st.text_input('Password (Login):', type='password')

                if st.button('Log In'):
                    # Perform login
                    user = login_user(email_login, password_login)
                    if user:
                        st.session_state.user_id = user[0]
                        st.success(f"Welcome back, {user[1]}!")
                    else:
                        st.error('Invalid email or password. Please try again.')
                    
    
    with col5:  # Use col5 for the new button
        if st.button('About Us'):
            st.header('About Us')
            st.image('logo.png', use_column_width=False)
            st.write("Welcome to our e-commerce website! We strive to provide the best shopping experience for our customers.")
            st.write("Feel free to visit [https://github.com/yiyanglaw](https://github.com/yiyanglaw) for more IT projects.")

    
    
    
    # Display selected product
    if 'selected_product' in st.session_state:
        selected_product = st.session_state.selected_product
        show_product_page(selected_product['id'], selected_product['name'], selected_product['qty'],
                          selected_product['price'], selected_product['color'], selected_product['description'])

def show_product_page(product_id, name, qty, price, color, description):
    # Clear the current page
    st.empty()

    # Set background image
    st.markdown(
        """
        <style>
            .stApp {
                background-image: url('https://browsecat.art/sites/default/files/a-road-5k-wallpapers-41105-2616-8136744.png');
                background-size: cover;
            }
            .stTextInput, .stText {
                color: white !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create a new subheader/page for the product details
    st.subheader(f'{name} - Product Page')
    product_image_path = f'product{product_id}.jpg'
    st.image(product_image_path, use_column_width=True, caption=f"{name}\nPrice: ${price:.2f}")
    st.write(f"Quantity: {qty}")
    st.write(f"Color: {color}")
    st.write(f"Description: {description}")

    # Add to Cart button
    if st.button('Add to Cart'):
        st.session_state.cart.append({'product_id': product_id, 'name': name, 'price': price})
        st.success(f"{name} added to the cart!")

    # Button to return to the previous page
    if st.button('Back to Shop'):
        st.session_state.current_section = 'shop'
        st.session_state.pop('selected_product', None)  # Clear selected_product
        st.experimental_rerun()

if __name__ == '__main__':
    main()
