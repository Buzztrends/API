import os
import requests
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import OpenAIEmbeddings

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

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
    url = "https://api.edenai.run/v2/image/generation"
    pdf = PyPDFLoader(file_path=r"prompt_book.pdf")
    index = VectorstoreIndexCreator().from_loaders([pdf])
    gen_prompt = lambda x: f"Create a detailed prompt to generate image with the following information {x}"
    opt_prompt = index.query(gen_prompt(prompt))
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