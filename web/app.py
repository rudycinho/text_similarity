from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

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

def verify_pw(username,password):
    if not user_exist(username):
        return False

    hashed_pw = username.find({
        "username":username
    })[0]["password"]

    return bcrypt.hashpw(password.encode('utf8'),hashed_pw)==hashed_pw

def count_tokens(username):
    tokens = users.find({
        "username":username
    })[0]["tokens"]
    return tokens

class Detect(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        text1 = posted_data["text1"]
        text1 = posted_data["text2"]

        if not user_exist(username):
            ret_json = {
                "status":"301",
                "msg":"Invalid Username"
            }
            return jsonify(ret_json)
        
        correct_pw = verify_pw(username,password)
        
        if not correct_pw:
            ret_json = {
                "status":"302",
                "msg":"Invalid password"
            }
            return jsonify(ret_json)
        
        num_tokens = count_tokens(username)

        if num_tokens <= 0:
            ret_json = {
                "status":"303",
                "msg":"You're out of tokens. please refill!"
            }
            return jsonify(ret_json)

        #Calculate the edit distance
        nlp = spacy.load('en_core_web_sm')

        text1 = nlp(text1)
        text2 = nlp(text2)

        #Ratio is a number between 0 and 1 the close to 1, 
        #the more similar text1 and text2 are

        ratio = text1.similarity(text2)

        ret_json = {
            "status":200,
            "similarity":ratio,
            "msg":"Similarity score calculated successfully"
        }

        current_tokens  = count_tokens(username)

        users.update({
            "username":username,
            
        },{
            "$set":{
                "tokens":current_tokens-1
            }
        })

        return jsonify(ret_json)