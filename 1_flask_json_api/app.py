from flask import Flask, jsonify, request
app = Flask(__name__)

# accept POST request
@app.route("/add_me", methods=["POST"])
def add_me():
    # get x, y from posted data
    dataDict = request.get_json()

    # return jsonify(dataDict)
    x = dataDict["x"]
    y = dataDict["y"]
    z = x * y

    resJson = {
        "z": z
    }

    return jsonify(resJson), 200


@app.route("/")
def hello_world():
    return "Hello World"


@app.route("/hithere")
def hi_there_everyone():
    return "I just hit /hithere"


@app.route("/bye")
def bye():
    c = 2*258
    s = str(c)
    # 3/0
    # return "bye"
    reJson = {
        "car": 22,
        "color": "red"
    }
    return jsonify(reJson)


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=80)
    # app.run(debug=True)
    app.run()


"""
  639  export FLASK_APP=app.py
  640  flask run
  install postman
"""

