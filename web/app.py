from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.similarityDB
users = db["users"]

def user_exist(username):
    return users.find({
        "username":username
    }).count() != 0

class Register(Resource):
    def post(self):
        posted_data = request.get_json()
        username = posted_data["username"]
        password = posted_data["password"]
        
        ret_json = {}

        if user_exist(username):
            ret_json = {
                "status":301,
                "msg":"Invalid Username"
            }
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())
            
            users.insert({
                "username":username,
                "password":hashed_pw,
                "tokens":6
            })

            ret_json = {
                "status":200,
                "msg":"You've successfully signed up to the API"
            }
        return jsonify(ret_json)
