"""
    REST is a type of API. Not all APIs are REST, but all REST services are APIs.
    API is a very broad term. Generally it's how one piece of code talks to another. In web development API often refers to the way in which we retrieve information from an online service. The API documentation will give you a list of URLs, query parameters and other information on how to make a request from the API, and inform you what sort of response will be given for each query.
    REST is a set of rules/standards/guidelines for how to build a web API. Since there are many ways to do so, having an agreed upon system of structuring an API saves time in making decisions when building one, and saves time in understanding how to use one.
    Other popular API paradigms include SOAP and GraphQL.
"""
"""
    pip3 install flask
    pip3 install flask-restful
"""

# import necessary libraries
from flask import Flask, jsonify, request
from flask_restful import Api, Resource


# set flask and restfull api
app = Flask(__name__)
api = Api(app)


def check_posted_data(posted_data, function_name):
    if (function_name == "add" or function_name == "subtract" or function_name == "multiply"):
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        else:
            return 200
    elif (function_name == "divide"):
        if "x" not in posted_data or "y" not in posted_data:
            return 301
        if posted_data["x"] == 0 or posted_data["y"] == 0:
            return 302
        else:
            return 200



class Add(Resource):
    def post(self):
        # get posted data
        posted_data = request.get_json()

        # check posted data
        status_code = check_posted_data(posted_data, "add")

        # return bad status code if not successful
        if (status_code != 200):
            retJson = {
                "Message":"An error has happened",
                "Status Code": status_code
            }
            return jsonify(retJson)

        # manipulate data (if status code is successful)
        x = posted_data["x"]
        y = posted_data["y"]
        x = int(x)
        y = int(y)
        ret = x + y
        
        # return result in json
        retMap = {
            "Message": ret,
            "Status Code": 200
        }
        return jsonify(retMap)


class Subtract(Resource):
    def post(self):
        # 1
        posted_data = request.get_json()

        # 2
        status_code = check_posted_data(posted_data, "subtract")

        # 3
        if (status_code != 200):
            response = {
                "Message": "An error has happened",
                "Status Code": status_code
            }
            return jsonify(response)

        # 4
        x = posted_data["x"]; x = int(x)
        y = posted_data["y"]; y = int(y)
        z = x - y

        #5
        retMap = {
            "Message": z,
            "Status Code": status_code
        }
        return jsonify(retMap)


class Multiply(Resource):
    def post(self):
        # 1
        posted_data = request.get_json()

        # 2
        status_code = check_posted_data(posted_data, "multiply")

        # 3
        if (status_code != 200):
            response = {
                "Message": "An error has happened",
                "Status Code": status_code
            }
            return jsonify(response)

        # 4
        x = posted_data["x"]; x = int(x)
        y = posted_data["y"]; y = int(y)
        z = x * y

        #5
        retMap = {
            "Message": z,
            "Status Code": status_code
        }
        return jsonify(retMap)


class Divide(Resource):
    def post(self):
        # 1
        posted_data = request.get_json()

        # 2
        status_code = check_posted_data(posted_data, "divide")

        # 3
        if (status_code != 200):
            response = {
                "Message": "An error has happened",
                "Status Code": status_code
            }
            return jsonify(response)

        # 4
        x = posted_data["x"]; x = int(x)
        y = posted_data["y"]; y = int(y)
        z = x / y

        #5
        retMap = {
            "Message": z,
            "Status Code": status_code
        }
        return jsonify(retMap)



# make routes
api.add_resource(Add, "/add")
# 6
api.add_resource(Subtract, "/subtract")

api.add_resource(Multiply, "/multiply")

api.add_resource(Divide, "/divide")



@app.route("/")
def hello_world():
    return "Hello World"


# run flask
if __name__ == "main":
    app.run(debug=True)