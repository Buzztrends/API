from .indexes import index
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

from utils.utils import get_llm
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
    from langchain.chat_models import ChatOpenAI
    gpt_3_5 = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.9)
    moment_data = moment_chain({"moment_query":moment})
    print("Provided Prompt==>")
    print(moment_data["moment_info"])
    post_prompt = index.query(f"""write prompt to make GPT generate prompt to write a social media post with the following details. Just write the prompt, no extra information. Format should be 
Prompt: <Prompt>
User: Information 
"company_description": "Zomato is a popular online platform that provides a comprehensive range of services related to dining and food. Originally founded in India, Zomato has expanded globally and is now a prominent player in the food technology industry. The platform allows users to explore and discover restaurants, cafes, and eateries in their vicinity, offering detailed information such as menus, reviews, ratings, and photos.\n\nZomato's user-friendly interface enables individuals to browse through a diverse range of cuisines, make reservations, and order food for delivery or takeaway. The platform has become a go-to resource for food enthusiasts seeking recommendations, as it aggregates user-generated reviews to help people make informed decisions about where to dine.\n\nIn addition to its consumer-facing services, Zomato has also ventured into food delivery, connecting users with a wide network of restaurants and delivery partners. The platform's commitment to enhancing the overall dining experience has made it a popular choice for both food lovers and businesses in the food industry.",
"company_name": "Zomato",
"content_category": "Indian Food",
"content_type":"linkedIn post",
"topic":"sesonal foods",
"objective":"persuade",
"location":"india",
"audience":"young teenagers",
"tone":"informal",
"structure":"Title and body".
"moment":{moment}
"moment_info":{moment_data["moment_info"]}
""",llm = gpt_3_5)
    print(post_prompt)
    post_prompt = PromptTemplate(input_variables=[],template=post_prompt)
    post_chain = LLMChain(llm=llm, prompt=post_prompt, output_key="post")

    generator_template = """Given this post text for a {content_type}: {post}

    Tell me what other things can be put in the post. Include description of images, videos, audio, hashtags, etc. as lists, only include elements that are relevant to a {content_type}"""
    generator_prompt = PromptTemplate(input_variables=["post", "content_type"], template=generator_template)
    generator_chain = LLMChain(llm=llm, prompt=generator_prompt, output_key="extras")

    final_chain = SequentialChain(
        chains=[post_chain, generator_chain],
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


# def generate_content(
#     company_name: str,
#     moment: str,
#     content_type: str,
#     tone: str,
#     objective: str,
#     structure: str,
#     location: str,
#     audience: str,
#     company_info,
#     moment_memory,
#     model="gpt_3_5_chat"
# ): 
#     if location == "":
#         location = "No specific target location."
    
#     if audience == "":
#         audience = "No specific target audience. Make it appeal to everyone."
    
#     # llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.5)
#     print("using ", model)
#     llm = get_llm(model, 0.5)

#     moment_query_template = "Tell me about {moment_query}. How is it relevant, significant, and important?"
#     moment_prompt = PromptTemplate(input_variables=["moment_query"], template=moment_query_template)
#     moment_chain = LLMChain(llm=llm, prompt=moment_prompt, memory=moment_memory, output_key="moment_info")


#     post_template = """Imagine that you are in charge of creating a {content_type}. 

# You are to write a {content_type} about {moment_query}. You must relate it with {company_name}.

# The content should be targetted towards:
# Location: {location}
# Target audience: {audience}.

# Be creative with the language.

# Create a title if a {content_type} requires a title

# IMPORTANT INSTRUCTIONS:

# Tone of {content_type}: {tone}
# Objective of {content_type}: {objective}
# Structuring of {content_type}: {structure}

# CONTEXT ON {company_name} and {moment_query} follows: 

# Information about {company_name}:
# {company_info}

# Information about {moment_query}:
# {moment_info}
# """
#     post_prompt = PromptTemplate(input_variables=["company_name", "location", "audience", "moment_query", "company_info", "moment_info", "tone", "objective", "content_type", "structure"], template=post_template)
#     post_chain = LLMChain(llm=llm, prompt=post_prompt, output_key="post")

#     generator_template = """Given this post text for a {content_type}: {post}

#     Tell me what other things can be put in the post. Include description of images, videos, audio, hashtags, etc. as lists, only include elements that are relevant to a {content_type}"""
#     generator_prompt = PromptTemplate(input_variables=["post", "content_type"], template=generator_template)
#     generator_chain = LLMChain(llm=llm, prompt=generator_prompt, output_key="extras")

#     final_chain = SequentialChain(
#         chains=[moment_chain, post_chain, generator_chain],
#         input_variables=["company_name", "company_info", "location", "audience", "moment_query", "tone", "objective", "content_type", "structure"],
#         output_variables=["post", "extras"],
#         verbose=True
#     )

#     return final_chain({
#         "company_name": company_name,
#         "company_info": company_info,
#         "moment_query": moment,
#         "tone": tone,
#         "objective": objective,
#         "structure": structure,
#         "location": location,
#         "audience": audience,
#         "content_type": content_type
#     })

if __name__ == '__main__':
    pass