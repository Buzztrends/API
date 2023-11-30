from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

import pandas as pd


def  prepare_prods(products:dict[str,dict[str,str]]):
    ans = ""
    for prod in products.keys():
        temp = ""
        for feature in products[prod].keys():
            temp+=f"{feature}:{products[prod][feature]}\t\t"
        ans+=f" [{prod}:{temp}]\n"

    return ans