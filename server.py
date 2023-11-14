#------------- SERVER IMPORTS-------------



import json
import base64
import bcrypt
from functools import wraps
from flask import Flask, request
from security.auth import hash_password,verify_password
from rsa import newkeys, decrypt, encrypt,PrivateKey,PublicKey
from flask_pymongo import MongoClient

from security.utlis import *
#------------- MODULES IMMPORTS-----------

# Image Generation Module
from ImageGeneration.edenai import *

# Text Generation Module
from TextGeneration.SimpleGeneration import *
from TextGeneration.CatelogueGeneration import *
from TextGeneration.ReferencePostGeneration import *

# Moments Module
from Moments.Moments import *
#===========Config Setup==================



if not os.path.exists("./config/.env"):
    os.mkdir("./config")
    with open("./config/.env","w") as f:
        f.write("")
import os
# environment setup
with open("./config/.env", "r") as key_file:
    keys = list(key_file)

for item in keys:
    variable, value = item.split("=")[0], "=".join(item.split("=")[1:])
    os.environ[variable] = value.replace("\n", "")
# if not os.path.exists("./config/users"):
#     os.mkdir("./config")
#     with open("./config/users","w") as f:
#         f.write("{}")

#==================================================================================================

#===========Models=========================

from models import APIModel,User

#==========================================

#==============App Setup==================
app = Flask("BuzztrendsAPI")
db = MongoClient(os.environ["MONGO_URI"])
#=========================================

#================ Authorization ==========
def api_admin_action(func):
    global db
    @wraps(func)
    def decor(*args,**kwargs):
        key = None
        try:
            print("\nHeader:",request.headers)
            print("\nJSON:",request.get_json())
        except Exception as e:
            print(e)

        if "api-key" in request.headers:
            key = (request.headers["api-key"])
            decode_key = base64.b64decode(key.encode("utf-8"))    
            print("Key Captured",key)
        if not key:
            print(request.get_json())
            return json.dumps({"message":"Admin Action Triggered! No admin Key found."})
        with open("./config/.env","r") as f:
            data = eval(f.read())
            if "PRIVATE_KEY" not in data:
                return json.dumps({"message":"No admin Registered Create an admin first","status_code":401})
            private_key_b64 = data["PRIVATE_KEY"]
            private_key = base64.b64decode(private_key_b64)
            private_key = PrivateKey.load_pkcs1(private_key)
        try:
            userId = decrypt(decode_key,priv_key=private_key).decode()
        except Exception as e:
            print(e)
            return json.dumps({"message":"Invalid ID detected","status_code":401})
        collection = db["users"]["api_subscribers"]
        print(userId)
        db_resp= collection.find_one({"uid":userId})
        print(db_resp,"\n================\n")
        if db_resp is None:
            return json.dumps(dict(message="Invalid User Provided",status_code=401))
        else:
            if db_resp["role"]!= "admin":
                return json.dumps(dict(message="User is not admin",status_code=401))
        return func()
    return decor 

def auth_api_key(func):
    @wraps(func)
    def decor(*args,**kwargs):
        global db

        if "api-key" in request.headers:
            key = (request.headers["api-key"])
            decode_key = base64.b64decode(key.encode("utf-8"))    
            print("Key Captured",key)

        if not key:
            print(request.get_json())
            return json.dumps({"message":"Admin Action Triggered! No admin Key found."})


        with open("./config/.env","r") as f:
            data = eval(f.read())
            if "PRIVATE_KEY" not in data:
                return json.dumps({"message":"No admin Registered Create an admin first","status_code":401})
            private_key_b64 = data["PRIVATE_KEY"]
            private_key = base64.b64decode(private_key_b64)
            private_key = PrivateKey.load_pkcs1(private_key)
        try:
            userId = decrypt(decode_key,priv_key=private_key).decode()
        except Exception as e:
            print(e)
            return json.dumps({"message":"Invalid ID detected","status_code":401})
        else:
            if db["users"]["api_subscribers"].find_one({"uid":userId}) is None:
                return json.dumps({"message":"Invalid ID detected","status_code":401})
            else:
                return func()
    return decor


@app.route("/api/create_api_admin")
def create_api_admin():


    user = APIModel("admin")
    user.role = "admin"
    pub, priv = newkeys(512)
    with open("./config/.env","r") as f:
        config = eval(f.read())
        if "PRIVATE_KEY" in config:
            return json.dumps(
        dict(
            message="Admin Already Exists",
            status_code=401
        )
    ) 
        priv_b64= base64.b64encode(priv.save_pkcs1()).decode("utf-8")
        pub_b64 = base64.b64encode(pub.save_pkcs1()).decode("utf-8")
        config["PRIVATE_KEY"]=priv_b64
        config["PUBLIC_KEY"] =pub_b64
    with open("./config/.env","w") as f:
        f.write(json.dumps(config))
    
    API_KEY = encrypt(user.uid.encode(),pub)
    API_KEY = base64.b64encode(API_KEY).decode("utf-8")
    print(user.to_json())
    db["users"]["api_subscribers"].insert_one((user.to_json()))
    return json.dumps(
        dict(
            message="Admin Created Successfully!",
            API_KEY=API_KEY,
            status_code=200
        )
    )

@app.route("/api/register_api_user",methods=["POST"])
@api_admin_action
def register_api():
    data= None
    try:
        data = request.get_json()
    except Exception as e:
        print(e)
        return json.dumps(dict(message="Registration Unsuccessful"))
    else:
        user = APIModel(data["user"])
        with open("./config/.env","r") as f:
            config = eval(f.read())
            pub_b64 = config["PUBLIC_KEY"]
        pub = base64.b64decode(pub_b64)
        pub = PublicKey.load_pkcs1(pub)
        API_KEY = encrypt(user.uid.encode(),pub)
        API_KEY = base64.b64encode(API_KEY).decode("utf-8")
        print(user.to_json())
        db["users"]["api_subscribers"].insert_one((user.to_json()))
        return json.dumps(
            dict(
                message="User Registered Successfully!",
                API_KEY=API_KEY,
                status_code=200
            )
        )  
@app.route("/api/delete_api_user",methods=["POST"])
@api_admin_action
def delete_api_user():
    global db
    user_data = request.get_json()
    print("="*20,"\n","User Data\n",user_data)
    resp = db["users"]["api_subscribers"].find_one_and_delete({"user":user_data["user"]})
    print("Response\n","="*20,"\n",resp)
    if resp is None:
        return json.dumps(
            dict(message="No User Found",status_code=401)
        )
    else:
        return json.dumps(
            dict(message="User Deleted Successfully",status_code=200)
        )

@api_admin_action
@app.route("/api/list_api_users",methods=["GET"])
def list_api_users():
    global db
    resp = db["api_subscribers"]["users"].find()
    json.dumps(
        dict(users=[x['user'] for x in resp],status_code=200)
    )
@app.route("/api/promote_user",methods=["GET"])
def promote_api_user():
    global db
    user_data = request.get_json()
    print("="*20,"\n","User Data\n",user_data)
    resp = db["users"]["api_subscribers"].find_one_and_update({"user":user_data["user"]},update={"role","admin"})
    print("Response\n","="*20,"\n",resp)
    if resp is None:
        return json.dumps(
            dict(message="No User Found",status_code=401)
        )
    else:
        return json.dumps(
            dict(message="User Promoted to Admin Successfully",status_code=200)
        )
@app.route("/",methods=["GET"])
def index_():
    return "BuzzTrends API"

#=================== USER ==========================

@app.route("/user/register_user",methods=["POST"])
@auth_api_key
def register_user():
    data = request.get_json()
    if  is_user_valid(data["username"]):
        return json.dumps(
            dict(message="User already Exists",status_code=401)
        )
    passw = data["password"]
    enc_password = hash_password(passw)
    data["password"] = enc_password
    user_model = User(**data)
    db["users"]["user-data"].insert_one(user_model.model_dump())
    print("Transaction Success")
    return json.dumps(dict(message="User Registered Successfully",user=data["username"]))

@app.route("/user/login_user",methods=["POST"])
@auth_api_key
def login_user():
    data = request.get_json()
    if not is_user_valid(data["username"]):
        return json.dumps(
            dict(message="User Does not Exists",status_code=401)
        )
    passw = data["password"]
    hashed_password = db["users"]["user-data"].find_one({"username":data["username"]})["password"]
    if verify_password(passw,hashed_password):
        return json.dumps(
            dict(message="User Authenticated Successfully",status_code=200)
        )
    return json.dumps(message="User authentication Failed",status_code=401)

@app.route("/user/data",methods=["GET"])
@auth_api_key
def get_user():
    # print(request.json())
    data = request.get_json()
    user = find_user(data["username"])
    if user == None:
        return json.dumps(
            dict(message="User Does not Exists",status_code=401)
        )

    user.pop("_id", None)
    return json.dumps(user)

#===================================================
#           Image Generation Route
@auth_api_key
@app.route("/image_generation")
def generate_image():
    # write the driver code here


    urls = ["tempurl.url"]
    return json.dumps(
        dict(urls=urls)
    )

#           Text Generation Route - Simple Generation
@auth_api_key
@app.route("/text_generation/simple_generation")
def generate_post():
    # write the driver code here

    post = "example post"
    extras = ["example extras"]
    return json.dumps(
        dict(post=post,extras=extras)
    )

#           Text Generation Route - Reference Post Generation
@auth_api_key
@app.route("/text_generation/reference_post_generation")
def generate_reference_post():
    # write the driver code here

    post = "example post"
    extras = ["example extras"]
    return json.dumps(
        dict(post=post,extras=extras)
    )

#           Text Generation Route - Catelogue Generation
@auth_api_key 
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