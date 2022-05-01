"""
    1 | Registation of a user 0 tokens
    2 | Registration of a user
    3 | Each user gets 10 tokens
    4 | Store a sentance on our database for 1 token
    5 | Retrieve his stored sentance on out database for 1 token

"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app) # restful API

client = MongoClient("mongodb://db:27017")
db = client.sentancesDatabase # database
users = db["users"] # collection


class Register(Resource):
    """
        Sign up form
    """
    def post(self):
        # 1 | get posted data
        posted_data = request.get_json()

        # 2 | get data
        username = posted_data["username"]
        password = posted_data["password"]

        # 3 | hashing
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # 4 | store username and password into the db
        users.insert_one({
            "username": username,
            "password": hashed_pw,
            "sentance": "",
            "tokens": 6
        })

        return_json = {
            "status": 200,
            "msg": "You successfully signed up for the API" 
        }
        return jsonify(return_json)


def verify_pw(username, password):
    hashed_pw = users.find({
        "username": username
    })[0]["password"]

    if bcrypt.hashpw(password.encode("utf-8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False


def count_tokens(username):
    tokens = users.find({
        "username": username
    })[0]["tokens"]
    return tokens


class Store(Resource):
    def post(self):
        # 1 | get posted data
        posted_data = request.get_json()

        # 2 | extract posted data
        username = posted_data["username"]
        password = posted_data["password"]
        sentance = posted_data["sentance"]

        # 3 | verify the username and password
        correct_pw = verify_pw(username, password)
        if not correct_pw:
            return_json = {
                "status": 302
            }
            return jsonify(return_json)

        # 4 | verify that user has enough tokens
        num_tokens = count_tokens(username)
        if num_tokens <= 0:
            return_json = {
                "status": 301
            }
            return jsonify(return_json)

        # 5 | store the sentance, take 1 token away and return 200 OK
        users.update_one({
            "username": username
        },{
            "$set": {
                "sentance": sentance,
                "tokens": num_tokens -1
                }
        })

        return_json = {
                "status": 200,
                "msg": "sentance saved successfully"
            }
        return jsonify(return_json)


class Get(Resource):
    def post(self):
        # 1 | get posted data
        posted_data = request.get_json()

        # 2 | extract posted data
        username = posted_data["username"]
        password = posted_data["password"]

        # 3 | verify the username and password
        correct_pw = verify_pw(username, password)
        if not correct_pw:
            return_json = {
                "status": 302
            }
            return jsonify(return_json)

        # 4 | verify that user has enough tokens
        num_tokens = count_tokens(username)
        if num_tokens <= 0:
            return_json = {
                "status": 301
            }
            return jsonify(return_json)

        # 5 | make the user pay
        users.update_one({
            "username": username
        },{
            "$set": {
                "tokens": num_tokens -1
                }
        })

        # 6 | find user with username
        sentance = users.find({
            "username": username
         })[0]["sentance"]

        # 7 | return user's sentance
        return_json = {
                "status": 200,
                "sentance": sentance
            }
        return jsonify(return_json)
         


# create endpoints
api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")


if __name__ == '__main__':
    app.run(host='0.0.0.0')













"""
    Hashing:
    hashed=bcrypt.hashpw("123xyz".encode("utf-8"), bcrypt.gensalt())
    bcrypt.hashpw("123xyz".encode("utf-8"), hashed)==hashed
"""



"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")  # same name in docker compose
db = client.site_db
num_users = db['UserNum']

num_users.insert_one(
    {
        'num_of_users': 0
    }
)


class Visit(Resource):
    def get(self):
        views_num = num_users.find({})[0]['num_of_users'] + 1
        num_users.update_one({}, {"$set": {"num_of_users": views_num}})
        return str(f"Hello user {views_num}")


@app.route('/')
def hello_word():
    return 'Hello Word'


def get_data():
    try:
        post_data = request.get_json()

        x = float(post_data['x'])
        y = float(post_data['y'])
    except Exception as e:
        print(e)
        return None, None, 301, str(e)

    return x, y, 200, ''


class Add(Resource):
    def post(self):
        # if i'm here, the resource add was requested using the method POST

        # Step 1: get the json data and manage errors
        x, y, status_code, error_message = get_data()

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        # Step 3: do the calculation
        result = x + y

        # step 4: Create Json response and send
        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


class Subtract(Resource):
    def post(self):
        x, y, status_code, error_message = get_data()

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        result = x - y

        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


class Multiply(Resource):
    def post(self):
        x, y, status_code, error_message = get_data()

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        result = x * y

        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


class Divide(Resource):
    def post(self):
        x, y, status_code, error_message = get_data()

        if y == 0:
            status_code = 302
            error_message = 'y is equal to zero, you cannot divide a number by 0'

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        result = x / y

        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")
api.add_resource(Visit, "/visit")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""