#------------- SERVER IMPORTS-------------
from flask import Flask
import json

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