from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017") # default mongodb port
db = client.SimilarityDB # new db
users = db["Users"] # new collection


# check if user exists
def user_exists(username):
    if users.find({"username": username}).count() == 0:
        return False
    else:
        return True

# verify username and pass
def verify_pw(username, password):
    if not user_exists(username):
        return False
    
    hashed_pw = users.find({
        "username": username
    })[0]["password"]

    if bcrypt.hashpw(password.encode("utf-8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


# token counter
def count_tokens(username):
    tokens = users.find({
        "username": username
    })[0]["tokens"]
    return tokens


class Register(Resource):
    def post(self):
        # get data from user
        posted_data = request.get_json()

        # extract data
        username = posted_data["username"]
        password = posted_data["password"]

        # if user already exists
        if user_exists(username):
            return_json = {
                "status": 301,
                "msg": "Invalid username"
            }
            
            return jsonify(return_json)

        # hash password
        hashed_pass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # input into db
        users.insert_one({
            "username": username,
            "password": hashed_pass,
            "tokens": 6 # each user gets 6 tokens
        })

        # return 200 status
        return_json = {
            "status": 200,
            "msg": "You've successfully signed up to the API"
        }

        return jsonify(return_json)


class Detect(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        # get posted text documents
        text_1 =  posted_data["text_1"]
        text_2 =  posted_data["text_2"]

        # if user doesn't exists
        if not user_exists(username):
            return_json = {
                "status": 301,
                "msg": "Invalid username"
            }
            
            return jsonify(return_json)

        # verify username and pass
        correct_pw = verify_pw(username, password)

        # if password incorrect
        if not correct_pw:
            return_json = {
                "status": 302,
                "msg": "Invalid password"
            }

            return jsonify(return_json)

        # if user doesn't have enough tokens
        num_tokens = count_tokens(username)

        if num_tokens <=0:
            return_json = {
                "status": 303,
                "msg": "Out of tokens, please refill!"
            }
            
            return jsonify(return_json)

        # calculate the edit distance
        nlp = spacy.load("en_core_web_sm")

        text_1 =  nlp(text_1)
        text_2 =  nlp(text_2)

        ratio = text_1.similarity(text_2)

        return_json = {
            "status": 200,
            "similarity": ratio,
            "msg": "Similarity score calculated successfully"
        }
        
        # take one token from user for service
        current_tokens = count_tokens(username)

        users.update({
            "username": username,
        },{
            "$set": {
                "tokens": current_tokens - 1
            }
        })

        return jsonify(return_json)


class Refill(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["admin_pw"]
        refill_amount = posted_data["refill"]


        if not user_exists(username):
            return_json = {
                "status": 301,
                "msg": "Invalid username"
            }

            return jsonify(return_json)

        # admin password should be stored encrypted in db as well
        correct_pw = "abc123"
        if not password == correct_pw:
            return_json = {
                "status": 304,
                "msg": "Invalid admin password!"
            }

            return jsonify(return_json)
        
        current_tokens = count_tokens(username)

        users.update({
            "username": username,
        },{
            "$set": {
                "tokens": refill_amount + current_tokens
            }
        })

        return_json = {
            "status": 200,
            "msg": "Refilled successfully!"
        }

        return jsonify(return_json)


api.add_resource(Register, "/register")
api.add_resource(Detect, "/detect")
api.add_resource(Refill, "/refill")


if __name__ == "__main__":
    app.run(host="0.0.0.0")