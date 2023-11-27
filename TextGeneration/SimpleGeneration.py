from .indexes import index
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

from utils.utils import get_llm

import openai
def generate_content(
    company_name: str,
    moment: str,
    content_type: str,
    tone: str,
    objective: str,
    structure: str,
    location: str,
    audience: str,
    company_info,
    moment_memory,
    model="gpt_3_5_chat"
): 
    if location == "":
        location = "No specific target location."
    
    if audience == "":
        audience = "No specific target audience. Make it appeal to everyone."
    
    # llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.5)
    print("using ", model)
    llm = get_llm(model, 0.5)

    moment_query_template = "Tell me about {moment_query}. How is it relevant, significant, and important?"
    moment_prompt = PromptTemplate(input_variables=["moment_query"], template=moment_query_template)
    moment_chain = LLMChain(llm=llm, prompt=moment_prompt, memory=moment_memory, output_key="moment_info")


    post_template = """Imagine that you are in charge of creating a {content_type}. 

You are to write a {content_type} about {moment_query}. You must relate it with {company_name}.

The content should be targetted towards:
Location: {location}
Target audience: {audience}.

Be creative with the language.

Create a title if a {content_type} requires a title

IMPORTANT INSTRUCTIONS:

Tone of {content_type}: {tone}
Objective of {content_type}: {objective}
Structuring of {content_type}: {structure}

CONTEXT ON {company_name} and {moment_query} follows: 

Information about {company_name}:
{company_info}

Information about {moment_query}:
{moment_info}
"""
    post_prompt = PromptTemplate(input_variables=["company_name", "location", "audience", "moment_query", "company_info", "moment_info", "tone", "objective", "content_type", "structure"], template=post_template)
    post_chain = LLMChain(llm=llm, prompt=post_prompt, output_key="post")

    generator_template = """Given this post text for a {content_type}: {post}

    Tell me what other things can be put in the post. Include description of images, videos, audio, hashtags, etc. as lists, only include elements that are relevant to a {content_type}"""
    generator_prompt = PromptTemplate(input_variables=["post", "content_type"], template=generator_template)
    generator_chain = LLMChain(llm=llm, prompt=generator_prompt, output_key="extras")

    final_chain = SequentialChain(
        chains=[moment_chain, post_chain, generator_chain],
        input_variables=["company_name", "company_info", "location", "audience", "moment_query", "tone", "objective", "content_type", "structure"],
        output_variables=["post", "extras"],
        verbose=True
    )

    return final_chain({
        "company_name": company_name,
        "company_info": company_info,
        "moment_query": moment,
        "tone": tone,
        "objective": objective,
        "structure": structure,
        "location": location,
        "audience": audience,
        "content_type": content_type
    })

def generate_content_2(
    company_name: str,
    moment: str,
    content_type: str,
    tone: str,
    objective: str,
    structure: str,
    location: str,
    audience: str,
    company_info,
    moment_memory,
    model="gpt_3_5_chat"
): 
    llm = get_llm(model, 0.5)
    if location == "":
        location = "No specific target location."
    
    if audience == "":
        audience = "No specific target audience. Make it appeal to everyone."
    
    # llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.5)
    print("using ", model)
    # llm = AzureOpenAI(deployment_name="buzztrends-gpt35",model_name="gpt-35-turbo",openai_api_key=AZURE_OPENAI_KEY,openai_api_base=OPENAI_API_BASE,openai_api_version=OPENAI_API_VERSION,temperature=0.7,top_p=0.95)

    moment_query_template = "Tell me about {moment_query}. How is it relevant, significant, and important?"
    moment_prompt = PromptTemplate(input_variables=["moment_query"], template=moment_query_template)
    moment_chain = LLMChain(llm=llm, prompt=moment_prompt, memory=moment_memory, output_key="moment_info")
    moment_chain_out= moment_chain({"moment_query":moment})
    message_text = [
  {"role":"system","content":"You are an assistant that helps the master to create  the prompts that are further used to generate posts. You use words that carry much more information and good at finding interesting information that are good for marketing"},{"role":"user",
   "content":"""
           [User]:write a social media with the following information
           "Content Category": "Product Launch",
        "Objective": "Build anticipation",
        "Structure": "2-3 lines",
        "Tone": "Informal",
        "Topic/Theme": "Tech Enthusiasts",
        "Audience": "Tech enthusiasts'
        Use this following informations to talk about:
        Seasonal foods refer to the types of food that are traditionally grown and harvested during specific seasons in the year. This concept is closely linked to sustainable agriculture and local produce, as consuming seasonal foods reduces the energy needed for food production, storage, and transportation.
Seasonal foods are relevant because they are a key component of sustainable eating and agriculture. Consuming food in season promotes biodiversity by encouraging a varied diet and a diverse range of produce in agriculture.
Significance,Importance."
[Bot]:Generate a social media post discussing seasonal foods with the provided information. The post should focus on the "Product Launch" content category, aiming to build anticipation. Keep the tone informal, structure it in 2-3 lines, and target the audience of tech enthusiasts interested in sustainable eating and agriculture.
[User]:write a social media with the following information
           "Content Category": "Automobile",
        "Objective": "Retention",
        "Structure": "Title and body lines",
        "Tone": "Casual",
        "Topic/Theme": "Tech Enthusiasts",
        "Audience": "Adults'
        Use this following informations to talk about:
        Seasonal foods refer to the types of food that are traditionally grown and harvested during specific seasons in the year. This concept is closely linked to sustainable agriculture and local produce, as consuming seasonal foods reduces the energy needed for food production, storage, and transportation.
Seasonal foods are relevant because they are a key component of sustainable eating and agriculture. Consuming food in season promotes biodiversity by encouraging a varied diet and a diverse range of produce in agriculture.
Significance,Importance."
[Bot]:Write a social media post discussing seasonal foods with the provided information. The post should focus on the "automobile" content category,That helps to retain the customers. The tone of the post must be casual with a title and a body targeting adults of the globe interested in sustainable eating and agriculture.
[User]:Redefine the prompt to generate a good quality social media post with the following information.
"company name":{company_name},
"Company Info":{company_info},
"Moment" : {moment},
"tone" : {tone},
"objective":{objective},
"structure":{structure},
"location":{location},
"audience":{audience},
"conent type":{content_type},
"Moment Information:{moment_info}
Format the output as "Prompt":<Prompt>
[Bot]:""".format(company_name=company_name,company_info=company_info,moment=moment,tone=tone,
                 objective=objective,structure=structure,
                 location=location,audience=audience,
                 content_type=content_type,moment_info=moment_chain_out["moment_info"])}]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
  messages = message_text,
  temperature=0.6,
  max_tokens=800,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None,
)
    
    post_prompt = """[System]:You are an in charge of creating content for the {company_name} to create content for {content_type}
    [System]: Use the {company_info} as the context to create content.
    [User]:Generate a social media post for the given prompt {opt_prompt}"""
    post_template = PromptTemplate(input_variables=["company_name","content_type","company_info","opt_prompt"],template=post_prompt)
    post_chain = LLMChain(llm=llm,prompt=post_template,output_key="post")

    generator_template = """Given this post text for a {content_type}: {post}

    Tell me what other things can be put in the post. Include description of images, videos, audio, hashtags, etc. as lists, only include elements that are relevant to a {content_type}"""
    generator_prompt = PromptTemplate(input_variables=["post", "content_type"], template=generator_template)
    generator_chain = LLMChain(llm=llm, prompt=generator_prompt, output_key="extras")

    final_chain = SequentialChain(
        chains=[post_chain, generator_chain],
        input_variables=["opt_prompt","company_name", "company_info", "location", "audience", "moment_query", "tone", "objective", "content_type", "structure"],
        output_variables=["post", "extras"],
        verbose=True
    )

    return final_chain({
        "opt_prompt":completion.choices[0]["message"]["content"],
        "company_name": company_name,
        "company_info": company_info,
        "moment_query": moment,
        "tone": tone,
        "objective": objective,
        "structure": structure,
        "location": location,
        "audience": audience,
        "content_type": content_type,

    })

if __name__ == '__main__':
    pass