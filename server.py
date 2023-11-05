#------------- SERVER IMPORTS-------------
import os
import json
import uuid
import base64
from functools import wraps
from hmac import compare_digest
from flask import Flask, request,make_response
from rsa import newkeys, decrypt, encrypt,PrivateKey
#------------- MODULES IMMPORTS-----------

# Image Generation Module
from ImageGeneration.edenai import *

# Text Generation Module
from TextGeneration.SimpleGeneration import *
from TextGeneration.CatelogueGeneration import *
from TextGeneration.ReferencePostGeneration import *

# Moments Module
from Moments.Moments import *
    

#==================================================================================================
app = Flask("BuzztrendsAPI")

#=========== Models ========================
class Users:
    def __init__(self,user:str,role:str) -> None:
        self.id = str(uuid.uuid4())
        self.user = user
        self.role = role
        self.public_key = None
    
    def from_dict(self,userData:dict):
        self.id = userData.keys()[0]
        self.user = userData[self.id]["user"]
        self.role = userData[self.id]["role"]

    def to_dict(self):
        return {self.id:{"user":self.user,"role":self.role}}

    def set_public_key(self,key):
        self.public_key = key

def admin_action(f):
    @wraps(f)
    def decor(*args,**kwargs):
        key = None
        if "x-api-key" in request.headers:
            key = eval(request.headers["x-api-key"])
            print("Key Captured",key)
        if not key:
            return json.dumps({"message":"Admin Action Triggered! No admin Key found."})
        with open("./config/.env","r") as f:
            data = eval(f.read())
            if "admin_id" not in data or data["admin_id"] == "":
                return json.dumps({"message":"No admin Registered Create an admin first","status_code":401})
            private_key = data["PRIVATE_KEY"]
            private_key = PrivateKey.load_pkcs1(private_key)
        try:
            decode_key = base64.b64decode(key.encode("utf-8"))    
            userId = decrypt(decode_key,priv_key=private_key).decode()
        except Exception as e:
            print(e)
            return json.dumps({"message":"Invalid ID detected","status_code":401})
        with open("./config/users","r") as f:
            users = eval(f.read())
            if userId not in users:
                return json.dumps(dict(message="Invalid User Provided",status_code=401))
            else:
                if userId[userId]["role"]!= "admin":
                    return json.dumps(dict(message="User is not admin",status_code=401))
        return f()
    return decor 



@app.route("/register")
@admin_action
def register():
    return json.dumps(dict(message="Registration Successful"))

@app.route("/test/users")
def list_users():
    pass
@app.route("/",methods=["GET"])
def index_():
    return "BuzzTrends API"

#           Image Generation Route
@app.route("/image_generation")
def generate_image():
    # write the driver code here


    urls = ["tempurl.url"]
    return json.dumps(
        dict(urls=urls)
    )

#           Text Generation Route - Simple Generation
@app.route("/text_generation/simple_generation")
def generate_post():
    # write the driver code here

    post = "example post"
    extras = ["example extras"]
    return json.dumps(
        dict(post=post,extras=extras)
    )

#           Text Generation Route - Reference Post Generation
@app.route("/text_generation/reference_post_generation")
def generate_reference_post():
    # write the driver code here

    post = "example post"
    extras = ["example extras"]
    return json.dumps(
        dict(post=post,extras=extras)
    )

#           Text Generation Route - Catelogue Generation
@app.route("/text_generation/catelogue_generation")
def generate_post_from_catalogue():
    # write the driver code here

    post = "example post"
    extras = ["example extras"]
    return json.dumps(
        dict(post=post,extras=extras)
    )

if __name__ == "__main__":
    app.run(
        host="localhost",
        port=8001,
        debug=True
    )