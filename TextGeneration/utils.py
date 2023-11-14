from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

import pandas as pd


def  prepare_prods(df:pd.DataFrame):
    df = df.fillna("")
    ans = ""
    for i in range(df.shape[0]):
        item_info = ""
        for col in df.columns:
            if df.loc[i,col] != "" :
                print(df.loc[i,col])
                item_info += f"{col}:{df.loc[i,col]} || "
        item_info +="\n"
        ans+=item_info
    return ans