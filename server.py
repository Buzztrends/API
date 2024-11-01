import argparse
#------------- SERVER IMPORTS-------------
import os

import logging
from logger.UserLogger import UserLogger

user_logger =  UserLogger().getLogger()
user_logger.info("Logger Intialized")

root= logging.root
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s","%B %d, %Y %H:%M:%S %Z",)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("./logs/root.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
root.addHandler(file_handler,)
root.addHandler(console_handler)
root.setLevel(logging.DEBUG)
root.log(10,"Root Initialized")

if not os.path.exists("./config/.env"):
    # os.mkdir("./config/.env")
    with open("./config/.env","w") as f:
        f.write("")

# environment setup
with open("./config/.key", "r") as key_file:
    keys = list(key_file)

for item in keys:
    variable, value = item.split("=")[0], "=".join(item.split("=")[1:])
    os.environ[variable] = value.replace("\n", "")

from functools import wraps
import jwt
import json
import base64
import bcrypt
from flask import Flask, request, make_response, jsonify,session
from datetime import datetime, timedelta
from security.auth import hash_password,verify_password
from rsa import newkeys, decrypt, encrypt,PrivateKey,PublicKey
from flask_pymongo import MongoClient
from flask_cors import CORS, cross_origin
from utils.utils import run_simple_query
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

#===========Models=========================

from models import APIModel,User

#==========================================
print("Loading Guidelines...")
with open("./utils/guidelines.json") as f:
    guidelines = json.load(f)
print("Guidelines Loaded")
#==============App Setup==================
app = Flask("BuzztrendsAPI")
app.config["SECRET_KEY"]=os.environ["SECRET_KEY"]
cors = CORS(app)

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
        if db_resp is None:
            return json.dumps(dict(message="Invalid User Provided",status_code=401))
        else:
            if db_resp["role"]!= "admin":
                return json.dumps(dict(message="User is not admin",status_code=401))
        return func()
    return decor 

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print("Token Captured:",token)
        # return 401 if token is not passed
        if not token:
            return json.dumps({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user = db["users"]["user-data"].find_one({"username":data["username"]})
        except Exception as e:
            print(e)
            return json.dumps({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        session['ctx'] = current_user['username']
        return  f(current_user,*args,**kwargs)
  
    return decorated

def auth_api_key(func):
    @wraps(func)
    def decor(*args,**kwargs):
        global db
        key= None
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
            print(userId)
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
@app.route("/api/promote_user",methods=["POST"])
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
    return json.dumps({"response": "BuzzTrends API, you found the correct link :D"})

#=================== USER ==========================

@app.route("/user/register_user",methods=["POST"])

@auth_api_key
def register_user():
    data = request.get_json() if request.content_length != 0 else {}
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    try:
        if  is_user_valid(data["username"]):
            return json.dumps(
                dict(message="User already Exists",status_code=401)
            )
    except KeyError:
        user_logger.error("No Username found in request")
        return json.dumps(
            dict(message="Username Not provided",status_code=406),406
        )
    try:
        passw = data["password"]
    except KeyError:
        user_logger.error("No password found in request")
        return json.dumps(
            dict(message="Password Not provided",status_code=406),406
        )
    user_logger.info("Encrypting password")
    enc_password = hash_password(passw)
    user_logger.info("Encryption Successfull")

    data["password"] = enc_password
    data["role"] = "non_admin"
    user_model = User(**data)
    db["users"]["user-data"].insert_one(user_model.model_dump())
    user_logger.info("DB Transaction Success")
    return json.dumps(dict(message="User Registered Successfully",user=data["username"]))

@app.route("/user/authenticate",methods=["POST"])
@auth_api_key
def login_user():

    global user_logger
    data = request.get_json() if request.content_length != 0 else {}
    print(user_logger.name)
    root.info("==================================================")
    user_logger.log(30,"Inside Login user")
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")

    try:
        if not is_user_valid(data["username"]):
            user_logger.error("User Does not Exists")
            return json.dumps(
                dict(message="User Does not Exists",status_code=401)
            )
    except KeyError:
        user_logger.error("No Username found in request")

        return json.dumps(
            dict(message="Username Not provided",status_code=401),401
        )
    try:
        passw = data["password"]
    except KeyError:
        user_logger.error("No password found in request")
        return json.dumps(
            dict(message="Password Not provided",status_code=406),406
        )

    passw = data["password"]
    hashed_password = db["users"]["user-data"].find_one({"username":data["username"].lower()})["password"]

    if verify_password(passw,hashed_password):
        user_logger.info("Password Verified! successfully")
        token = jwt.encode({
            'username': data["username"].lower(),
            'exp' : datetime.utcnow() + timedelta(minutes = 300)
        }, app.config['SECRET_KEY'])

        user_logger.info("User Authenticated Successfully!")

        response = jsonify(dict(message="User Authenticated Successfully",username=data["username"],company_name=db["users"]["user-data"].find_one({"username":data["username"].lower()})["company_name"],company_id=db["users"]["user-data"].find_one({"username":data["username"].lower()})["company_id"],token=token,status_code=200))

        
    else:
        response = json.dumps(dict(message="User authentication Failed",status_code=401))

    # response.headers.add('Access-Control-Allow-Origin', '*')
    user_logger.info(f"Response:\n\t{response}")

    return response


@app.route("/user/data",methods=["POST"])
@auth_api_key
@token_required
def get_user(data):
    """
    Args:
        data- Userdata Model
        returns - user data
    
    Request Body- {}
    """
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{data['username']}")
    # # print(request.json())
    # # data = request.get_json()
    # user = find_company(data["company_id"])
    # if user == None:
    #     return json.dumps(
    #         dict(message="User Does not Exists",status_code=401)
    #     )
    return json.dumps(data,default=str)

@app.route("/user/update_user",methods=["POST"])
@auth_api_key
@token_required
def update_user(user):
    """
    params: parameter_to_update
            old_value
            new_value
    """

    data = request.get_json() if request.content_length != 0 else {}
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{user['username']}")
    
    try:
        username = data["username"]
    except KeyError:
        user_logger.error("No Username found in request")
        return json.dumps(
            dict(message="Username Not provided",status_code=401),401
        )
    try:
        parameter_to_update = data["parameter_to_update"]
    except KeyError:
        user_logger.error("No Parameter to update found in request")
        return json.dumps(
            dict(message="parameter_to_update Not provided",status_code=406),406
        )
    old_value = data.get("old_value",None)
    try:
        new_value = data["new_value"]
    except KeyError:
        user_logger.error("No New Value found in request")
        return json.dumps(
            dict(message="new_value Not provided",status_code=406),406
        )

    if is_user_valid(username):
    
        if parameter_to_update == "password":
            user_logger.info("Updating Password...")
            if old_value is None or old_value == "":
                user_logger.error("Invalid New Password Provided!")
                return json.dumps(
                    dict(message="Old Password Cannot be None or empty",status_code=401)
                )
            else:
                old_password = db["users"]["user-data"].find_one({"username":username})["password"]
                verify = verify_password(old_value,old_password)
                user_logger.info("Verify Status:",verify)
                if verify:
                    db["users"]["user-data"].update_one(filter={"username":username},update={"$set":{f"{parameter_to_update}":hash_password(new_value)}})
                    user_logger.info("Values updated Successfully!")
                else:
                    user_logger.error("Incorrect Old Password Provided")
                    return json.dumps(
                        dict(message="Incorrect Old Password Provided",status_code=401)
                    )
                
        else:
            db["users"]["user-data"].update_one(filter={"username":username},update={"$set":{f"{parameter_to_update}":(new_value)}})
            user_logger.info("Values updated Successfully!")

    else:
        user_logger.error("Invalid User Found!")
        return json.dumps(
                        dict(message="Invalid User Provided",status_code=401)
                    )
    return json.dumps(
        dict(message="User data updated Successfully",status_code=200)
    )

@app.route("/user/delete_user",methods=["POST"])
@token_required
def delete_user(data):
    body_data = request.get_json() if request.content_length !=0 else {}
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{data['username']}")
    username = data["username"]
    
    if not is_user_valid(username):
        user_logger.error("Invalid User Encountered")
        return json.dumps(
            dict(message="Invalid User Encountered",status_code=401)
        )
    else:
        db["users"]["user-data"].delete_one({"username":username})
        user_logger.warning(f"User: {username} Deleted")
        return json.dumps(
            dict(message="User Deleted Successfully",status_code=200)
        )
    
#=========== SAVE POST =============================
@app.route("/user/save_post",methods=["POST"])
@auth_api_key
@token_required
def save_post(user):
    data = request.get_json() if request.content_length !=0 else {}
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{user['username']}")
    try:
        state = data["state"]
        post = data['post']
    except Exception as e:
        return json.dumps(dict(message="Invalid parameters found!",error=e,status="Failure",status_code=401)),401
    user['saved_posts'][state].append(post)
    print("="*15,"\n",user['saved_posts'])
    db["users"]['user-data'].find_one_and_update({"company_id":user['company_id']},update={"$set":{f"saved_posts.{state}":user['saved_posts'][state]}})
    ans = db["users"]['user-data'].find_one({"company_id":user['company_id']})['saved_posts']
    print("="*15,"\n",ans)
    return json.dumps({f"saved_posts":ans,"status_code":200,"status":"Success"})

@app.route("/user/get_save_post",methods=["GET"])
@auth_api_key
@token_required
def get_save_post(user):
    data = request.get_json() if request.content_length !=0 else {}
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{user['username']}")
    return json.dumps(dict(save_posts=user['saved_post'],username=user['username']))
#============= Save Topics==========================
@app.route("/user/get_save_topic",methods=["GET"])
@auth_api_key
@token_required
def get_save_topic(user):
    data = request.get_json() if request.content_length !=0 else {}
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{user['username']}")
    return json.dumps(dict(save_topics=user['saved_topics'],username=user['username']))

@app.route("/user/save_topic",methods=["POST"])
@auth_api_key
@token_required
def save_topic(user):
    data = request.get_json() if request.content_length !=0 else {}

    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{user['username']}")
    try:
        post = data['moment']
    except Exception as e:
        return json.dumps(dict(message="Invalid parameters found!",error=e,status="Failure",status_code=401)),401
    try:
        user['saved_topics'].append(post)
    except KeyError:
        user["saved_topics"] = [post]
    print("="*15,"\n",user['saved_topics'])
    db["users"]['user-data'].find_one_and_update({"company_id":user['company_id']},update={"$set":{f"saved_topics":user['saved_topics']}})
    ans = db["users"]['user-data'].find_one({"company_id":user['company_id']})['saved_topics']
    print("="*15,"\n",ans)
    return json.dumps({f"saved_topics":ans,"status_code":200,"status":"Success"})
#===================================================
#           Image Generation Roufte

@app.route("/image_generation/edenai", methods=["POST"])
@auth_api_key
def generate_image():
    # write the driver code here
    global db
    data = request.get_json() if request.content_length !=0 else {}
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    if session.get("ctx",-1)==-1:
        username = "No username found"
    else:
        username = session['ctx']
    user_logger.info(f"Request Raise by User:{username}")
    root.info(f"{request.access_route} hit with the body \nBody:{data}")
    try: 
        extras = data["extras"]
    except ValueError:
        root.error("Extras not provided")
        json.dumps(
            dict(message="Extras not available",status_code=401)
        )
    else:
        output = run_simple_query(extras, """What is the text suggested for images only. Write your answer as text seperated by ||, eg <text 1>||<text 2>. Remove the 'images' title, I only want to retain the content""")
        image_queries = output.split("||")
        if not len(image_queries) > 1: 
            image_queries = output.split(".")
        print(image_queries)
        images = []
        for i, item in enumerate(image_queries[:4]):
            images.append(generate_image_edenai_2(item, provider="stabilityai",model="stable-diffusion-xl-1024-v1-0"))
        return json.dumps(
            dict(
            images = images,
            status_code = 200)
        )
        

#           Text Generation Route - Simple Generation

@auth_api_key
@token_required
def create_prompt():

    pass
@auth_api_key
@app.route("/text_generation/simple_generation",methods=["POST"])
def generate_post():
    global db
    global guidelines
    data = request.get_json()
    root.info(f"{request.access_route} hit with the body \nBody:{data}")
    if data.get("company_id",-1) == -1:
        return json.dumps(dict(message="Provide the compant ID",status_code=403)),403
    if data.get("moment",-1) == -1:
        data["moment"]="Write about the company and its product."
    if data.get("content_type",-1) == -1:
        data["content_type"]=""
    if data.get("tone",-1) == -1:
        data["tone"]=guidelines[data["content_type"]]["tone"]
    if data.get("objective",-1) == -1:
        data["objective"]=""
    if data.get("structure",-1) == -1:
        data["structure"]=guidelines[data["content_type"]]["structure"]
    if data.get("location",-1) == -1:
        data["location"]=" for general people from anywhere"
    if data.get("audience",-1) == -1:
        data["audience"]=" for everyone across the world"
    if data.get("custom_moment",-1) == -1:
        data["custom_moment"]=1
    moment = data["moment"].split(" | ")[0]
    company_data = db["users"]["user-data"].find_one(filter={"company_id":data["company_id"]})
    if not company_data:
        root.error("Invalid Company ID found")
        return json.dumps(
            dict(message="Invalid Company ID")
        )
    user_logger.info(f"{request.access_route} hit with the body:\
                     \n{data}")
    user_logger.info(f"Request Raise by User:{company_data['username']}")
    root.info("Company Generation Info:",company_data.get("generation_available"))
    if company_data.get("generation_available") is None:
        company_data =db["users"]["user-data"].update_one({"company_id":data["company_id"]},update={"$set":{'generation_available':20}})
    elif company_data["generation_available"] == 0:
        return json.dumps(
            dict(message="You have exhausted your generation credits!",status_code=403)
        ),403
    root.info("Capturing Moments ...")
    moment_context_sitetexts = get_sitetexts(get_related_links(moment.replace("Title: ", "") + f" {company_data['content_category']}", country=company_data["country_code"], num_results=5))
    moment_vectorstore, moment_retriver, _, _ = build_vectorstore(moment_context_sitetexts)

    moment_memory = VectorStoreRetrieverMemory(
            retriever=moment_retriver,
            input_key="moment_query"
                            )
    
    root.info("Initializing Content Generation...")
    if data.get("product",-1)=="" or data.get("product",-1)==-1 or company_data.get("product",-1)=={}:
        generation_guidelines = guidelines[data["content_type"]]["extras"]
        if data["content_type"]==["blog post"]:
            generation_guidelines+="Write the blog in such a manner that its not Robot detectable."
        if data.get("similar_content",-1) ==-1 or data.get("similar_content",-1) =='':
            out = generate_content_2(
                company_name=company_data["company_name"],
                moment=data["moment"],
                content_type=data["content_type"],
                tone=data["tone"],
                objective=data["objective"],
                structure=data["structure"],
                location=data["location"],
                audience=data["audience"],
                company_info=company_data["company_description"],
                moment_retriver=moment_retriver,
                model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure",
                extras_guidelines = generation_guidelines
            )
        else:
            root.info("Similar Content Triggered")
            out = generate_similar_content(
                company_name=company_data["company_name"],
                moment=data["moment"],
                content_type=data["content_type"],
                objective=data["objective"],
                location=data["location"],
                audience=data["audience"],
                ref_post=data["similar_content"],
                company_info=company_data["company_description"],
                moment_retriver=moment_retriver,
                model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure",
                extras_guidelines = guidelines[data["content_type"]]["extras"]
            )
    else:
        root.info("Product Content Triggered")
        out = generate_post_with_prod(
            company_name=company_data["company_name"],
            moment=data["moment"],
            content_type=data["content_type"],
            tone=data["tone"],
            objective=data["objective"],
            structure=data["structure"],
            location=data["location"],
            audience=data["audience"],
            company_info=company_data["company_description"],
            moment_retriver=moment_retriver,
            product_name=data["product"],
            products = company_data["products"],
            ref_post = data.get("similar_content",None),

            extras_guidelines=guidelines[data["content_type"]]["extras"],
            model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure"

        )
    root.info("Content Successfully Generated!")
    generation_available = company_data["generation_available"]
    root.info("Updating User Credits...")
    db["users"]["user-data"].find_one_and_update(filter={"company_id":data["company_id"]},update={"$set":{"generation_available":generation_available-1}})
    out["remaining_generation"]=generation_available-1
    root.info("User Credits Updated!")
    root.info(f"Response Provided:{out}")
    return json.dumps(out),201

#           Text Generation Route - Reference Post Generation

@auth_api_key
@app.route("/text_generation/reference_post_generation",methods=["POST"])
def generate_reference_post():
    global db
    data = request.get_json()
    if data.get("company_id",-1) == -1:
        return json.dumps(dict(message="Provide the compant ID",status_code=403)),403
    if data.get("moment",-1) == -1:
        data["moment"]=""
    if data.get("content_type",-1) == -1:
        data["content_type"]=""
    if data.get("tone",-1) == -1:
        data["tone"]=""
    if data.get("objective",-1) == -1:
        data["objective"]=""
    if data.get("structure",-1) == -1:
        data["structure"]=""
    if data.get("location",-1) == -1:
        data["location"]=""
    if data.get("audience",-1) == -1:
        data["audience"]=""
    if data.get("custom_moment",-1) == -1:
        data["custom_moment"]=1
    root.info(data)
    moment = data["moment"].split(" | ")[0]
    company_data = db["users"]["user-data"].find_one(filter={"company_id":data["company_id"]})
    if company_data["generation_available"] == 0:
        return json.dumps(
            dict(message="You have exhausted your generation credits!")
        )

    moment_context_sitetexts = get_sitetexts(get_related_links(moment.replace("Title: ", "") + f" {company_data['content_category']}", country=company_data["country_code"], num_results=5))

    moment_vectorstore, moment_retriver, _, _ = build_vectorstore(moment_context_sitetexts)

    
    if not company_data:
        return json.dumps(
            dict(message="Invalid Company ID")
        )

    if data["custom_moment"] ==1:
        out = generate_similar_content(
            company_name=company_data["company_name"],
            moment=data["moment"],
            content_type=data["content_type"],
            objective=data["objective"],
            location=data["location"],
            audience=data["audience"],
            ref_post=data["reference_post"],
            company_info=company_data["company_description"],
            moment_retriver=moment_retriver,
            model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure"
        )
    else:
        out = generate_similar_content(
            company_name=company_data["company_name"],
            moment=data["moment"],
            content_type=data["content_type"],
            objective=data["objective"],
            location=data["location"],
            audience=data["audience"],
            ref_post=data["reference_post"],
            company_info=company_data["company_description"],
            moment_retriver=moment_retriver,
            model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure"
        )
    generation_available = company_data["generation_available"]
    db["users"]["user-data"].find_one_and_update(filter={"company_id":data["company_id"]},update={"$set":{"generation_available":generation_available-1}})
    out["remaining_generation"]=generation_available-1
    root.info(f"Response Provided:{out}")
    return json.dumps(out)

#           Text Generation Route - Catelogue Generation

@auth_api_key 
@app.route("/text_generation/catelogue_generation",methods=["POST"])
def generate_post_from_catalogue():
    data = request.get_json()
    moment = data["moment"].split(" | ")[0]
    company_data = db["users"]["user-data"].find_one(filter={"company_id":data["company_id"]})
    if company_data["generation_available"] == 0:
        return json.dumps(
            dict(message="You have exhausted your generation credits!")
        )
    moment_context_sitetexts = get_sitetexts(get_related_links(moment.replace("Title: ", "") + f" {company_data['content_category']}", country=company_data["country_code"], num_results=5))


    moment_vectorstore, moment_retriver, _, _ = build_vectorstore(moment_context_sitetexts)

    
    if not company_data:
        return json.dumps(
            dict(message="Invalid Company ID")
        )

    if data["custom_moment"] ==1:
        out = generate_post_with_prod(
            company_name=company_data["company_name"],
            moment=data["moment"],
            content_type=data["content_type"],
            tone=data["tone"],
            objective=data["objective"],
            structure=data["structure"],
            location=data["location"],
            audience=data["audience"],
            company_info=company_data["company_description"],
            moment_retriver=moment_retriver,
            products = company_data["products"],
            product_names_col = data["product_names_col"],
            product_name = data["product_name"],
            ref_post = data["reference_post"],
            model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure"
        )
    else:
        out = generate_post_with_prod(
            company_name=company_data["company_name"],
            moment=data["moment"],
            content_type=data["content_type"],
            tone=data["tone"],
            objective=data["objective"],
            structure=data["structure"],
            location=data["location"],
            audience=data["audience"],
            company_info=company_data["company_description"],
            moment_retriver=moment_retriver,
            products = pd.read_csv(data["products"]),
            product_name = data["product_name"],
            ref_post = data["reference_post"],
            model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure"
        )
    generation_available = company_data["generation_available"]
    db["users"]["user-data"].find_one_and_update(filter={"company_id":data["company_id"]},update={"generation_available":generation_available-1})
    out["remaining_generation"]=generation_available-1
    root.info(f"Response Provided:{out}")
    return json.dumps(out)

@app.route("/user/get_products",methods=["GET","POST"])
@auth_api_key
@token_required
def get_products(user)->json :
    if user.get("products",-1)==-1:
        return json.dumps(
            dict(products={},status_code=200)
        )
    else:
        return json.dumps(dict(products=list(user["products"].keys()),status_code=200))

@app.route("/get_test",methods=["GET"])
def get_test():
    print(request)
    print("Hey there")
    return json.dumps(dict(message="You did it!"))

@app.route("/")
def index():
    return "Buzztrends Index"

if __name__ == "__main__":
   

    parser = argparse.ArgumentParser(description='find env settings',prog='server.py')
    parser.add_argument('--env',dest='ENV_SETTINGS',default='PROD',help="Setup the enviroment",choices=["DEV","PROD"])

    arg = (parser.parse_args())
    env_settings = (arg.ENV_SETTINGS)
    if os.environ.get("ENV_SETTINGS",-1) ==-1:
        os.environ['ENV_SETTINGS']=env_settings
    print("Booting the server in ",os.environ['ENV_SETTINGS']," settings")
    app.run(
            host="0.0.0.0",
            port=5000,
            # ssl_context=(os.environ["SSL_CERT"], os.environ["SSL_KEY"])
    )