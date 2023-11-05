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