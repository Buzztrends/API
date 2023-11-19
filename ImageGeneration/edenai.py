import os
import requests
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import OpenAIEmbeddings

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

print(os.path.abspath(os.path.curdir)+"/ImageGeneration/")
print("Creating Indexes from Handbook...")
pdf = PyPDFLoader(file_path=os.path.abspath(os.path.curdir)+"/ImageGeneration/"+r"prompt_book.pdf")
index = VectorstoreIndexCreator().from_loaders([pdf])
gpt_3_5 = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.7)
print("Indexes created Successfully")

def generate_image_edenai(prompt, provider="openai", dims="512x512"):
    url = "https://api.edenai.run/v2/image/generation"

    payload = {
        "response_as_dict": True,
        "attributes_as_list": False,
        "show_original_response": False,
        "resolution": dims,
        "num_images": 1,
        "providers": provider,
        "text": prompt
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {os.environ['EDENAI_BEARER_TOKEN']}"
    }

    response = requests.post(url, json=payload, headers=headers).json()
    print(response.keys())
    try:
        print(response[provider].keys())
        img_url = response[provider]['items'][0]['image_resource_url']
    except Exception as e:
        print(e,"\n")
        print(response[provider]['error'])
        return ""
    return img_url

def generate_image_edenai_2(prompt, provider="openai", dims="512x512"):
    global index
    global gpt_3_5
    url = "https://api.edenai.run/v2/image/generation"
    image_gen_prompt = """
    [System]: You're an AI that narrate the scence to click the marketing picture for the given requirements, keep the prompt limited to 300 characters. If The information discuss about humans or living beings, always make 2D digital arts. Do not use any textual data to write on image.
    [User]: Write in detail about the scence to click a picture for the given picture.
    {picture_info}
"""
    image_gen_prompt_template = PromptTemplate(input_variables=["picture_info"],template=image_gen_prompt)
    content_gen_chain = LLMChain(llm=gpt_3_5, prompt=image_gen_prompt_template, output_key="scence detail")
    chain_out  = content_gen_chain({"picture_info":prompt})["scence detail"]
    print(chain_out)
    opt_prompt = index.query(f"Write a prompt in 250 characters to create an illustration for the current scene.{chain_out}",llm=gpt_3_5)
    print(opt_prompt)
    payload = {
        "response_as_dict": True,
        "attributes_as_list": False,
        "show_original_response": False,
        "resolution": dims,
        "num_images": 1,
        "providers": provider,
        "text": opt_prompt
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {os.environ['EDENAI_BEARER_TOKEN']}"
    }

    response = requests.post(url, json=payload, headers=headers).json()
    print(response.keys())
    try:
        print(response[provider].keys())
        img_url = response[provider]['items'][0]['image_resource_url']
    except Exception as e:
        print(e,"\n")
        print(response[provider]['error'])
        return ""
    return img_url