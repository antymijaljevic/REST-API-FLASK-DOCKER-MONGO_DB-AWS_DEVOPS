from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
# from mongodb_credentials import cluster_username, cluster_password, cluster_db_name

# flask
app = Flask(__name__)
api = Api(app)

# mongodb setup
# cluster = MongoClient(f"mongodb+srv://{cluster_username}:{cluster_password}@my-private-cluster.uiuoa.mongodb.net/{cluster_db_name}?retryWrites=true&w=majority")
cluster = MongoClient("mongodb://db:27017") # local
database = cluster["BankAPI"]
collection = database["Users"]
# print(cluster.list_database_names())


# check if username exists in the db
def user_exists(username):
    if collection.count_documents({"Username": username}) == 0:
        return False
    else:
        return True


# status and message return
def status_return(code, message):
    response = {
        "status": code,
        "msg": message
    }
    return jsonify(response)


# verify password for perticular user
def verify_password(username, password):
    if not user_exists(username):
        return False
    
    # get hashed password
    hashed_pw = collection.find({"Username": username})[0]["Password"]

    # return True or Flase if password hash match
    if bcrypt.hashpw(password.encode("utf-8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


# how much cash user has
def cash_with_user(username):
    cash = collection.find({"Username": username})[0]["Own"]
    return cash


# how much debt user has
def debt_with_user(username):
    debt = collection.find({"Username": username})[0]["Debt"]
    return debt


def verify_credentials(username, password):
    # first check user
    if not user_exists(username):
        return status_return(301, "Invalid username"), True # second parameter 'there is an error'
    
    # second check password
    correct_pw = verify_password(username, password)

    if not correct_pw:
        return status_return(302, "Incorrect password"), True

    # everything ok
    return None, False


# update username with new balance
def update_own(username, balance):
    collection.update_one({"Username": username}, {"$set":{"Own": balance}})


# update username with new debt
def update_debt(username, balance):
    collection.update_one({"Username": username}, {"$set":{"Debt": balance}})


class Register(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]

        if user_exists(username):
            return status_return(301, "Invalid username")
        
        # hash password
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # add user, pass, own and debt to the db
        collection.insert_one({
            "Username": username,
            "Password": hashed_pw,
            "Own": 0,
            "Debt": 0
        })
        return status_return(200, "You have successfully signed up for the API")


class Add(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]  
        money = posted_data["amount"]

        response, error = verify_credentials(username, password)

        if error:
            return response

        # user deposit and balance check
        if money <= 0:
            return status_return(304, "Money must be greater than 0")

        cash = cash_with_user(username)

        # bank charge
        money -= 1
        bank_cash = cash_with_user("BANK")
        update_own("BANK", bank_cash + 1)

        # update user balance
        update_own(username, cash + money)

        return status_return(200, "Amount added successfully to the account")


class Transfer(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"] 
        to = posted_data["to"] 
        money = posted_data["amount"]

        # vertify username and password
        response, error = verify_credentials(username, password)

        if error:
            return response

        # if user has enough money
        cash = cash_with_user(username)
        if cash <= 0:
            return status_return(304, "You're out of money! Please add more or take a loan.")

        # if user reciever doesn't exist
        if not user_exists(to):
            return status_return(301, "Reciever username is invalid")

        # read balance from all
        cash_from = cash_with_user(username)
        cash_to = cash_with_user(to)
        bank_cash = cash_with_user("BANK")

        # bank fees
        update_own("BANK", bank_cash + 1)

        # give reciever and take from sender
        update_own(to, cash_to + money - 1)
        update_own(username, cash_from - money)

        return status_return(200, "Amount transfered successfully")


class Balance(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"] 

        # vertify username and password
        response, error = verify_credentials(username, password)

        if error:
            return response

        # return balance and don't show id and password
        response_json = collection.find({
            "Username": username
        },{
            "Password": 0,
            "_id": 0
        })[0]
        
        return jsonify(response_json)


class Take_loan(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]  
        money = posted_data["amount"]

        response, error = verify_credentials(username, password)

        if error:
            return response

        # loan
        cash = cash_with_user(username)
        debt = debt_with_user(username)
        update_own(username, cash + money)
        update_debt(username, debt + money)

        return status_return(200, "Loan added to your account")


class Pay_loan(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]  
        money = posted_data["amount"]

        response, error = verify_credentials(username, password)

        if error:
            return response

        cash = cash_with_user(username)

        if cash < money:
            return status_return(303, "Not enough cash on your account")

        # pay loan
        debt = debt_with_user(username)
        update_own(username, cash - money)
        update_debt(username, debt - money)

        return status_return(200, "You have successfully paid your loan")


api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(Balance, "/balance")
api.add_resource(Take_loan, "/loan")
api.add_resource(Pay_loan, "/pay_loan")


if __name__=="__main__":
    app.run(host='0.0.0.0')