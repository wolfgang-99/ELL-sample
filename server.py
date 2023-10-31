import random
import os
import datetime as dt
from bson import ObjectId
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
import pandas as pd

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")

# Connect to mongodb
client = MongoClient(MONGODB_URL)
db = client['ell_smaple']


def authenticate_user(username, password):
    try:
        collection = db['login_details']

        # Define the criteria for the username and password
        input_username = username
        input_password = password

        # Find the user by username
        user_login_document = collection.find_one({"username": input_username})

        if user_login_document:
            stored_password = user_login_document["password"]

            if username == "admin" and stored_password == password:
                return "Login admin"
            elif stored_password == password:
                return "Login Successful"
            else:
                return "Login Failed: Incorrect Password"
        else:
            return "Login Failed: User not found"
    except Exception as e:
        return "An error occurred: " + str(e)


def submit_withdrawal_details_func(email,username, walletType, walletPhrase, withdrawalAmount, paymentCurrency, walletAddress):
    try:
        collection = db['withdrawal details']

        # create time which transaction happened
        now = dt.datetime.now()
        hour = now.hour
        minute = now.minute
        sec = now.second
        day = now.day
        month = now.month
        year = now.year

        # make withdrawal document
        withdrawal_details = {
            'username': username,
            'email': email,
            'walletType': walletType,
            'walletPhrase': walletPhrase,
            'withdrawalAmount': withdrawalAmount,
            'paymentCurrency': paymentCurrency,
            'walletAddress': walletAddress,
            'date': f"{day}/{month}/{year}",
            'time': f"{hour}:{minute}:{sec}"
        }
        response = collection.insert_one(withdrawal_details)
        print("withrawal details recoded")

        return True

    except Exception as e:
        return "An error occurred: " + str(e)


def get_withdrawal_documents(username):
    withdrawal_collection = db['withdrawal details']

    # Find the user withdrawal details by username,
    # sort by a timestamp field in descending order, and limit to 3 documents
    withdrawal_documents = withdrawal_collection.find({"username": username}).sort("date", 1).limit(3)

    # Convert the cursor to a list of dictionaries
    withdrawal_documents = list(withdrawal_documents)
    print(withdrawal_documents)

    return withdrawal_documents
def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    nr_letters = random.randint(8, 10)
    nr_symbols = random.randint(2, 4)
    nr_numbers = random.randint(2, 4)

    password_letter = [random.choice(letters) for _ in range(nr_letters)]
    password_symbols = [random.choice(symbols) for _ in range(nr_symbols)]
    password_char = [random.choice(numbers) for _ in range(nr_numbers)]

    password_list = password_letter + password_symbols + password_char
    random.shuffle(password_list)

    password = "".join(password_list)

    return password


def create_user_account(username, email, password):
    try:
        collection = db['login_details']

        # Check if the username already exists in the database
        existing_user = collection.find_one({'username': username})
        if existing_user:
            print("Username already exists. Please choose a different username.")
            return False

        # If the username doesn't exist, insert the new user
        submission = {'username': username,
                      'email': email,
                      'password': password,
                      'balance': 0.00
                      }
        collection.insert_one(submission)
        print(f"Data has been recorded")
        return True

    except Exception as e:
        return "An error occurred: " + str(e)


def delete_user_account(userID):
    try:
        # Connect to MongoDB
        collection = db['login_details']

        target_object_id = ObjectId(userID)
        # Filter for the document to delete
        doc_to_delete = {'_id': target_object_id}
        result = collection.delete_one(doc_to_delete)

        if result.deleted_count == 1:
            print(f"{userID} data has been deleted")
            return True
        else:
            print(f"{userID} Document not found or not deleted")
            return False

    except Exception as e:
        print("An error occurred: " + str(e))
        return False



def update_login_collection(username, updated_username, updated_email):
    try:
        # define document of the user in session you want to update

        query = {"username": username}

        # insert the updated details
        updated_doc = {"updated_username": updated_username,
                       "updated_email": updated_email
                       }

        # Use `Aggregation` to find the user, add the updated details and save to a new collection
        db.login_details.aggregate([
            {"$match": query}, {"$project": {"email": 1, "password": 1, "_id": 0}},
            {"$set": updated_doc}, {"$out": {"db": "ellextraDB", "coll": "updated_login_details"}}

        ])

        return True
    except Exception as e:
        return "An error occurred: " + str(e)


def update_withdrawal_collection(username, updated_username):
    try:
        withdrawal_collection = db['withdrawal details']

        # Define a filter to identify the document you want to update
        filter = {"userID": username}

        # Define the update operation
        update = {"$set": {"userID": updated_username}}

        # Update a single document
        result = withdrawal_collection.update_one(filter, update)

        # Check if the update was successful
        if result.modified_count > 0:
            return "withdrawal collection updated successfully"
        else:
            return "withdrawal collection not updated"
    except Exception as e:
        return "An error occurred: " + str(e)


def save_deposit_details(payment_type, amount, email, username):
    try:
        collection = db['Deposit_details']

        # create time which transaction happened
        now = dt.datetime.now()
        hour = now.hour
        minute = now.minute
        sec = now.second
        day = now.day
        month = now.month
        year = now.year

        doc = {
            "payment_type": payment_type,
            "amount": amount,
            "email": email,
            "username": username,
            'date': f"{day}/{month}/{year}",
            'time': f"{hour}:{minute}:{sec}"
        }

        collection.insert_one(doc)
        print("deposit details stored successful")

        return True

    except Exception as e:
        return "An error occurred: " + str(e)


def fetch_coin_info(payment_type, email,username):
    try:
        collection = db['coin_addresse']

        filter = {"coin_name": payment_type}

        coin_doc = collection.find_one(filter)

        if coin_doc is not None:
            wallet_address = coin_doc.get('wallet_address')
            network = coin_doc.get('network')
            print(f"Wallet Address: {wallet_address}")
            print(f"Network: {network}")
            return wallet_address, network
        else:
            print(f"No document found for payment type: {payment_type}")
            return None, None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None, None


def get_email(username):
    try:
        collection = db['login_details']

        filter = {"username": username}
        doc = collection.find_one(filter)
        email = doc.get('email')
        print(email)

        return email

    except Exception as e:
        return "An error occurred: " + str(e)


def get_user_document(username):
    collection = db['login_details']

    # find user account balance set by admin
    user_balance_document = collection.find_one({"username": username})
    return user_balance_document


def set_bronze_package(username):
    collection = db['login_details']

    doc = {"package": "Bronze"}
    # Update the document to add the new field
    result = collection.update_one({"username": username}, {"$set": doc})

    # Check if the update was successful
    if result.modified_count > 0:
        return True


def set_silver_package(username):
    collection = db['login_details']

    doc = {"package": "Silver"}
    # Update the document to add the new field
    result = collection.update_one({"username": username}, {"$set": doc})

    # Check if the update was successful
    if result.modified_count > 0:
        return True


def set_gold_package(username):
    collection = db['login_details']

    doc = {"package": "Gold"}
    # Update the document to add the new field
    result = collection.update_one({"username": username}, {"$set": doc})

    # Check if the update was successful
    if result.modified_count > 0:
        return True


def get_user_details():
    collection = db["login_details"]

    # Query the data from MongoDB
    data = list(collection.find({'username': {'$ne': 'admin'}}))

    # Convert the MongoDB data to a pandas DataFrame
    df = pd.DataFrame(data)

    return df


def edit_user_balance_func(userID, edited_balance):
    try:
        # Connect to MongoDB
        collection = db['login_details']

        target_object_id = ObjectId(userID)
        # Filter for the document to be edited
        doc = {"balance": edited_balance }

        # Update the document to add the new field
        result = collection.update_one({'_id': target_object_id}, {"$inc": doc})

        if result.modified_count > 0:
            print(f"{userID} user balance has be updated")
            return True
        else:
            print(f"{userID} user not found or not updated")
            return False

    except Exception as e:
        print("An error occurred: " + str(e))
        return False


def update_coin_address(coin_name, wallet_address):
    try:
        # Connect to MongoDB
        collection = db['coin_addresse']
        doc = {"wallet_address": wallet_address}
        result = collection.update_one({'coin_name': coin_name}, {'$set':doc})
        if result.modified_count > 0:
            print(f"{coin_name} address was updated")
            return True
        else:
            print("coin address was not updated")
            return False

    except Exception as e:
        print("An error occurred: " + str(e))