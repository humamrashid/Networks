# Humam Rashid
# CISC 7334X, Prof. Chen.

# "Hello, World" program using python with flask

from flask import Flask

app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, World!"

# EOF.
