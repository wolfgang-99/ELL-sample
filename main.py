import asyncio
import os
from datetime import timedelta
from dotenv import load_dotenv
from email_module import email_admin, email_user
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from server import authenticate_user, create_user_account, update_login_collection, \
    update_withdrawal_collection, delete_user_account, save_deposit_details, fetch_coin_info, get_withdrawal_documents, \
    get_user_document, set_bronze_package, set_silver_package, set_gold_package, get_user_details, \
    edit_user_balance_func, submit_withdrawal_details_func, update_coin_address

load_dotenv()
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(hours=3)
app.secret_key = os.getenv("secret_key")  # Set a secret key for sessions
MONGODB_URL = os.getenv("MONGODB_URL")


@app.route('/Home')
def Home():
    return render_template("index2.html")


async def send_email_notification_singup(email, username):
    # Put your email sending code here
    email_user(register_email=email, register_name=username, file_path='Email text/signup_Email_text.txt')


@app.route('/signup', methods=['POST'])
async def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('useremail')
        password = request.form.get('password')

        print(f"Received form data: username={username}, email={email}, password={password}")

        create_user = create_user_account(username, email, password)
        print(f"User creation result: {create_user}")

        if create_user:
            # Create a task to execute your email sending function
            email_task = asyncio.create_task(
                send_email_notification_singup(email, username))

            # Store data in the session
            session['username'] = username

            return redirect(url_for('dashboard'))
        else:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('Home'))


@app.route('/submit_login_details', methods=['POST'])
def submit_login_details():
    username = request.form.get('username')
    password = request.form.get('password')

    # call the authenticate function and use it
    auth_result = authenticate_user(username, password)

    if "Login admin" in auth_result:

        # Store data in the session
        session['username'] = username

        return redirect(url_for('admin'))
    elif "Login Successful" in auth_result:

        # Store data in the session
        session['username'] = username

        return redirect(url_for('dashboard'))
    elif "Login Failed: Incorrect Password" in auth_result:
        return redirect(url_for("login_failed_incorrect_password"))
    else:
        return redirect(url_for('login_failed_user_not_found'))


@app.route('/Login_Failed_Incorrect_Password')
def login_failed_incorrect_password():
    session.pop("username", None)
    flash('Login Failed: Incorrect_Password', 'danger')
    return redirect(url_for("Home"))


@app.route('/login_failed_user_not_found')
def login_failed_user_not_found():
    session.pop("username", None)
    flash('Login Failed: User not found', 'danger')
    return redirect(url_for("Home"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash('you have logged out', 'info')
    return redirect(url_for("Home", _rnd=request.args.get("_rnd", None)))



@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if "username" in session:  # check if username is in session
        username = session["username"]

        # find user account doc / details
        user_document = get_user_document(username)

        # call get_withdrawal_doc function
        withdrawal_documents = get_withdrawal_documents(username)

        if withdrawal_documents is not None:
            data = {
                "username": username,
                "account_balance": user_document.get("balance"),
                "user_email": user_document.get('email'),
                "account_package": user_document.get('package'),
                "withdrawal_documents": withdrawal_documents,  # Pass the withdrawal documents

            }
        else:
            get_user_document(username)

            data = {
                "username": username,
                "account_balance": user_document.get("balance"),
                "date": "No Transaction",
                "withdrawalAmount": "No Transaction",
                "paymentCurrency": "No Transaction",
            }
        return render_template("dashboard2.html", **data)  # Pass data to the template and render it
    else:
        flash('You need to login first.', 'warning')
        return redirect(url_for("Home"))


@app.route('/profile')
def profile():
    if "username" in session:

        # get username from session
        username = session["username"]
        # email = session["updated_email"]

        # find document of the user in session
        document = get_user_document(username)

        data = {
            "profile_name": username,
            "email": document.get("email"),
            "user_id": document.get("_id")
        }
        print("Reached the profile route")
        return render_template("profile.html", **data)
    else:
        flash('You need to login first.', 'warning')
        return redirect(url_for("Home"))


@app.route('/submit_withdraw_details', methods=['POST'])
def submit_withdraw_details():

    if 'username' in session:
        email = request.form.get('email')
        walletType = request.form.get('walletType')
        walletPhrase = request.form.get('walletPhrase')
        withdrawalAmount = request.form.get('withdrawalAmount')
        paymentCurrency = request.form.get('paymentCurrency')
        walletAddress = request.form.get('WalletAddress')

        if "username" in session:  # check if username is in session
            username = session["username"]
            submit_withdrawal_details_func(email, username, walletType, walletPhrase, withdrawalAmount, paymentCurrency, walletAddress)
        flash('transaction in processing', 'info')
        return redirect(url_for('dashboard'))

    else:
        flash("User not logged in", 'info')
        return redirect(url_for("Home"))


async def send_email_notification_deposit(email, username, amount, payment_type):
    # Put your email sending code here
    email_admin(register_email=email, register_name=username, admin_email="blazealex348@gmail.com",
                file_path="Email text/Admin_email_notification_deposite",
                deposit_amount=amount, wallet=payment_type)
    email_user(register_email=email, register_name=username, file_path='Email text/Deposite_Email_text.txt')


@app.route('/save_and_get_details', methods=['POST'])
async def save_and_get_details():
    if "username" in session:  # check if username is in session
        username = session["username"]
        try:
            payment_type = request.form.get('paymentType')
            amount = request.form.get('depositAmount')
            email = request.form.get('email')

            # Save deposit details
            saved = save_deposit_details(payment_type=payment_type, amount=amount, email=email, username=username)

            if saved:
                # Fetch coin data
                wallet_address, network = fetch_coin_info(payment_type, email, username)

                if wallet_address and network:

                    response = {
                        "success": True,
                        "wallet_address": wallet_address,
                        "network": network
                    }
                    # Create a task to execute your email sending function
                    email_task = asyncio.create_task(
                        send_email_notification_deposit(email, username, amount, payment_type))

                else:
                    response = {
                        "success": False,
                        "message": "Failed to fetch coin data"
                    }
            else:
                response = {"success": False, "message": "An error occurred while saving details"}

            return jsonify(response)

        except Exception as e:
            response = {"success": False, "message": "An error occurred: " + str(e)}
            return jsonify(response)

    else:
        flash("User not logged in", 'info')
        return redirect(url_for("Home"))


@app.route('/activate_package', methods=['Post'])
def activate_package():
    if "username" in session:  # check if username is in session
        username = session['username']

        depositAmount = float(request.form.get('depositAmount'))

        print(depositAmount)

        # find user account doc / details
        user_document = get_user_document(username)
        user_balance = float(user_document.get("balance"))

        # Validation logic
        # Initialize response with a default value
        response = {"success": False, "message": "Invalid Balance for Package"}

        # Validation logic
        if depositAmount >= 200 and depositAmount <= 1000:
            if user_balance >= depositAmount:
                # call bronze package
                set_package = set_bronze_package(username)
                if set_package:
                    print(f"added bronze package to user:{username} ")
                    response = {
                        "success": True
                    }

        elif depositAmount >= 1100 and depositAmount <= 10000:
            if user_balance >= depositAmount:

                # call sliver package
                set_package = set_silver_package(username)
                if set_package:
                    print(f"added sliver package to user:{username} ")
                    response = {
                        "success": True
                    }

        elif depositAmount >= 11000 and depositAmount <= 50000:
            if user_balance >= depositAmount:

                # call gold package
                set_package = set_gold_package(username)
                if set_package:
                    print(f"added gold package to user:{username} ")
                    response = {
                        "success": True
                    }

        return jsonify(response)

    else:
        flash("User not logged in", 'info')
        return redirect(url_for("Home"))


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if "username" in session:

        if request.method == 'POST':
            # get data admin want to create
            password = session['generated_admin_password']
            username = request.form.get('username')
            email = request.form.get('email')
            balance = request.form.get('balance')
            user_created = create_user_account(username=username, email=email, password=password)
            if user_created:
                flash(f"you have created {username} as a user", category='info')

                data = get_user_details()
                return render_template("admin.html", data=data)

        data = get_user_details()
        return render_template("admin2.html", data=data)
    else:
        flash('You need to login first.', 'warning')
        return redirect(url_for("Home"))


@app.route('/api/delete-user', methods=['POST'])
def delete_user():
    if 'username' in session:
        try:
            data = request.get_json()
            userID = data.get('userId')

            if userID is None:
                return jsonify({'error': 'User ID is missing'}), 400

            delete_user_result = delete_user_account(userID)

            if delete_user_result:
                flash(f'{userID} user has been deleted', 'info')
                return jsonify({'message': f'{userID} user has been deleted'}), 200
            else:
                flash(f'{userID} user had an issue during deletion', 'info')
                return jsonify({'message': f'{userID} user had an issue during deletion'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        flash("User not logged in", 'info')
        return redirect(url_for("Home"))


@app.route('/api/edit_user_balance', methods=['POST'])
def edit_user_balance():
    if 'username' in session:
        try:
            data = request.get_json()
            userID = data.get('userId')
            user_balance = int(data.get('userBalance'))

            if userID is None or user_balance is None:
                return jsonify({'error': 'User ID or balance is missing'}), 400

            user_result = edit_user_balance_func(userID=userID, edited_balance=user_balance)

            if user_result:
                flash(f'{userID} user balance have been updated', 'info')
                return jsonify({'message': f'{userID} user  balance have been updated'}), 200
            else:
                flash(f'{userID} user had an issue during deletion', 'info')
                return jsonify({'message': f'{userID} user had an issue during updating user balance'}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        flash("User not logged in", 'info')
        return redirect(url_for("Home"))

@app.route('/set_deposit_wallet', methods=['POST'])
def set_deposit_wallet():
    if 'username' in session:
        bitcoinAddress = request.form.get('bitcoinAddress')
        ethereumAddress = request.form.get('ethereumAddress')
        usdtAddress = request.form.get('usdtAddress')

        if bitcoinAddress or ethereumAddress or usdtAddress:

            if bitcoinAddress:
                update_coin_address(coin_name="Bitcoin", wallet_address=bitcoinAddress)
                print(f"Bitcoin Address: {bitcoinAddress}")
                flash('Bitcoin Address added', 'info')
                return redirect(url_for("admin"))

            if ethereumAddress:
                update_coin_address(coin_name="Ethereum", wallet_address=ethereumAddress)
                print(f"Ethereum Address: {ethereumAddress}")
                flash('Ethereum Address added', 'info')
                return redirect(url_for("admin"))

            if usdtAddress:
                update_coin_address(coin_name="USDT", wallet_address=usdtAddress)
                print(f"USDT Address: {usdtAddress}")
                flash('USDT Address added', 'info')
                return redirect(url_for("admin"))

        else:
            flash("No address data provided", 'info')
            return redirect(url_for("admin"))
    else:
        flash("User not logged in", 'info')
        return redirect(url_for("Home"))


@app.route('/')
def root():
    return redirect(url_for('Home'))


# Add a catch-all route for handling URL not found errors
@app.errorhandler(404)
def page_not_found(e):
    return "Page not found. Please check the URL.", 404


if __name__ == "__main__":
    app.run(debug=True)
