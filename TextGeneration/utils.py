from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
def get_llm(name, temperature=0):
    return {
        "gpt_3_5_chat":ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=temperature),
        "gpt_3_5_high_temp":ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.7),
        "gpt_4_chat":ChatOpenAI(model_name="gpt-4", temperature=temperature),
        "gpt_3_5":OpenAI(model_name="gpt-3.5-turbo-16k", temperature=temperature),
        "gpt_4":OpenAI(model_name="gpt-4", temperature=temperature),
        "gpt_4_high_temp":OpenAI(model_name="gpt-4", temperature=0.7)
        }[name]
