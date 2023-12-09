import argparse
import logging

#------------- SERVER IMPORTS-------------
import os

from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            }
        },
        
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },"root_file":{
                "class": "logging.FileHandler",
                "filename":"./logs/root.log",
                "formatter": "default",
            },"out_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "./logs/out_request.log",
                "formatter": "default",
                "maxBytes": 1000000,
                "backupCount": 5,
            },"in_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "./logs/in_request.log",
                "formatter": "default",
                "maxBytes": 1000000,
                "backupCount": 5,
            }
        },"root": {
            "level": "DEBUG", "handlers": ["console","root_file"]
        },"loggers": {
            "incoming_req": {
                "level": "INFO",
                "handlers": ["in_file"],
                "propagate": False,
            },
            "outgoing_req": {
                "level": "INFO",
                "handlers": ["out_file"],
                "propagate": False,
            }
        },
        
    }
)

extra = logging.getLogger("incoming_req")
out = logging.getLogger("outgoing_req")

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
        print(db_resp,"\n================\n")
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
        session["ctx"] = current_user["username"]
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
    data = request.get_json()
    if  is_user_valid(data["username"]):
        return json.dumps(
            dict(message="User already Exists",status_code=401)
        )
    passw = data["password"]
    enc_password = hash_password(passw)
    data["password"] = enc_password
    data["role"] = "non_admin"
    user_model = User(**data)
    db["users"]["user-data"].insert_one(user_model.model_dump())
    print("Transaction Success")
    return json.dumps(dict(message="User Registered Successfully",user=data["username"]))

@app.route("/user/authenticate",methods=["POST","OPTIONS"])
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
        token = jwt.encode({
            'username': data["username"],
            'exp' : datetime.utcnow() + timedelta(minutes = 300)
        }, app.config['SECRET_KEY'])

        response = jsonify(dict(message="User Authenticated Successfully",username=data["username"],company_name=db["users"]["user-data"].find_one({"username":data["username"]})["company_name"],company_id=db["users"]["user-data"].find_one({"username":data["username"]})["company_id"],token=token,status_code=200))
        
    else:
        response = json.dumps(dict(message="User authentication Failed",status_code=401))

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', ["POST", "GET", "OPTIONS", "PUT", "DELETE"])
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')


    return response


@app.route("/user/data",methods=["POST"])
@auth_api_key
@token_required
def get_user(data):
    # print(request.json())
    # data = request.get_json()
    user = find_company(data["company_id"])
    if user == None:
        return json.dumps(
            dict(message="User Does not Exists",status_code=401)
        )
    print("Returning user data")
    print(user)
    return json.dumps(user)

@app.route("/user/update_user",methods=["POST"])
@auth_api_key
@token_required
def update_user(user):
    """
    params: parameter_to_update
            old_value
            new_value
    """
    data = request.get_json()
    username = data["username"]
    parameter_to_update = data["parameter_to_update"]
    old_value = data["old_value"]
    new_value = data["new_value"]

    if is_user_valid(username):
    
        if parameter_to_update == "password":
            if old_value is None or old_value == "":
                return json.dumps(
                    dict(message="Old Password Cannot be None or empty",status_code=401)
                )
            else:
                old_password = db["users"]["user-data"].find_one({"username":username})["password"]
                print(old_password)
                verify = verify_password(old_value,old_password)
                print("Verify Status:",verify)
                if verify:
                    db["users"]["user-data"].update_one(filter={"username":username},update={"$set":{f"{parameter_to_update}":hash_password(new_value)}})
                else:
                    return json.dumps(
                        dict(message="Incorrect Old Password Provided",status_code=401)
                    )
                
        else:
            db["users"]["user-data"].update_one(filter={"username":username},update={"$set":{f"{parameter_to_update}":(new_value)}})
    else:
        return json.dumps(
                        dict(message="Invalid User Provided",status_code=401)
                    )
    return json.dumps(
        dict(message="User data updated Successfully",status_code=200)
    )

@app.route("/user/delete_user",methods=["POST"])
@token_required
def delete_user(data):
    # data = request.get_json()
    username = data["username"]
    
    if not is_user_valid(username):
        return json.dumps(
            dict(message="Invalid User Encountered",status_code=401)
        )
    else:
        db["users"]["user-data"].delete_one({"username":username})
        return json.dumps(
            dict(message="User Deleted Successfully",status_code=200)
        )
    
#=========== SAVE POST =============================
@app.route("/user/save_post",methods=["POST"])
@auth_api_key
@token_required
def save_post(user):
    data = request.get_json()
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
    return json.dumps(dict(save_posts=user['saved_post'],username=user['username']))
#============= Save Topics==========================
@app.route("/user/get_save_topic",methods=["GET"])
@auth_api_key
@token_required
def get_save_topic(user):
    return json.dumps(dict(save_topics=user['saved_topics'],username=user['username']))

@app.route("/user/save_topic",methods=["POST"])
@auth_api_key
@token_required
def save_topic(user):
    data = request.get_json()
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
    data = request.get_json()
    try: 
        extras = data["extras"]
    except ValueError:
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
            images.append(generate_image_edenai_2(item, provider="stabilityai"))
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
        return json.dumps(
            dict(message="Invalid Company ID")
        )
    print("Company Generation Info:",company_data.get("generation_available"))
    if company_data.get("generation_available") is None:
        company_data =db["users"]["user-data"].update_one({"company_id":data["company_id"]},update={"$set":{'generation_available':20}})
    elif company_data["generation_available"] == 0:
        return json.dumps(
            dict(message="You have exhausted your generation credits!",status_code=403)
        ),403
    print("Capturing Moments ...")
    moment_context_sitetexts = get_sitetexts(get_related_links(moment.replace("Title: ", "") + f" {company_data['content_category']}", country=company_data["country_code"], num_results=5))
    moment_vectorstore, moment_retriver, _, _ = build_vectorstore(moment_context_sitetexts)

    moment_memory = VectorStoreRetrieverMemory(
            retriever=moment_retriver,
            input_key="moment_query"
                            )
    
    print("Initializing Content Generation...")
    if data.get("product",-1)=="" or data.get("product",-1)==-1 or company_data.get("product",-1)=={}:
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
                extras_guidelines = guidelines[data["content_type"]]["extras"]
            )
        else:
            print("Similar Content Triggered")
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
        print("Product Content Triggered")
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
            model="gpt_4_high_temp" if os.environ['ENV_SETTINGS'] =="PROD" else "gpt_3_5_chat_azure"
        )
    print("Content Successfully Generated!")
    generation_available = company_data["generation_available"]
    print("Updating User Credits...")
    db["users"]["user-data"].find_one_and_update(filter={"company_id":data["company_id"]},update={"$set":{"generation_available":generation_available-1}})
    out["remaining_generation"]=generation_available-1
    print("User Credits Updated!")
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
    print(data)
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

@app.after_request
def logAfterRequest(response):
    if request.method!="OPTIONS":
        if session.get("ctx"==-1):
            session["ctx"] = "No User name provided"
        ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        out.info(
            "(IP: %s) | path: %s | method: %s | status: %s | size: %s >>> | user: %s \nResponse: %s",
            ip_addr,
            request.path,
            request.method,
            response.status,
            response.content_length,
            session["ctx"],
            response.get_data()
        )

    return response

@app.before_request
def logBeforeRequest():
    if request.method != "OPTIONS":  
        ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if request.content_length !=0:
            json_data = request.get_json()
            session["ctx"] = json_data["username"]
        else:
            session["ctx"] = "No username provided"
            json_data = {}
        print("before Request\nsession['ctx']:",session['ctx'])
        extra.info(
            "Incoming Request from:(IP: %s) | path: %s | method: %s | size: %s | >>> user: %s | payload: %s",
            ip_addr,
            request.path,
            request.method,
            request.content_length,
            session["ctx"],
            json_data
        )

    return 

if __name__ == "__main__":
   

    parser = argparse.ArgumentParser(description='find env settings',prog='server.py')
    parser.add_argument('--env',dest='ENV_SETTINGS',default='DEV',help="Setup the enviroment",choices=["DEV","PROD"])

    arg = (parser.parse_args())
    env_settings = (arg.ENV_SETTINGS)
    print("Booting the server in ",env_settings," settings")
    os.environ['ENV_SETTINGS']=env_settings
    app.run(
            host="0.0.0.0",
            port=443,
            debug=True,
            ssl_context=(os.environ["SSL_CERT"], os.environ["SSL_KEY"])
    )