from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

import pandas as pd


def  prepare_prods(products:dict[str,dict[str,str]],prod):
    print("Inside prepare Prod")
    print("this is what i got \n",products)
    ans = ""
    temp = ""
    for feature in products.keys():
        temp+=f"{feature}:{products[feature]}\t\t"
    ans+=f" [{prod}:{temp}]\n"

    return ans