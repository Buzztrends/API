from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain

from utils.utils import get_llm

def generate_similar_content(company_name: str,
    moment: str,
    content_type: str,
    objective: str,
    location: str,
    audience: str,
    company_info,
    moment_memory,
    ref_post:str,
    model="gpt_3_5_chat"):
    llm = get_llm(model, 0.2)
    print("Reference Post\n","="*20,ref_post)

    if location == "":
        location = "across the globe"
    
    if audience == "":
        audience = "to everyone"
    # =================== MOMENT EXTRACTOR CHAIN ==========
    moment_query_template = "Tell me about {moment_query}. How is it relevant, significant, and important?"
    moment_prompt = PromptTemplate(input_variables=["moment_query"], template=moment_query_template)
    moment_chain = LLMChain(llm=llm, prompt=moment_prompt, memory=moment_memory, output_key="moment_info")
    
    # =================== TONALITY CHAIN ==================
    # tonality_post_prompt = """
    # [System]: Write the Tonality ["formal", "casual", "informative", "persuasive"] in One Word only
    # [System]: DO NOT write any extra information
    # [User]: Given the post, find the tonality
    # Post:{post}
    # """
    # tonality_post_prompt_template = PromptTemplate(input_variables=["post"], template=tonality_post_prompt)
    # tonality_post_chain = LLMChain(llm=gpt_4, prompt=tonality_post_prompt_template, output_key="tonality")
    
    # ============= CONTENT GEN CHAIN ======================
    content_gen_prompt = """
    [System]: Assume you're a model that generates social media post for the organisation {company_name} with the following company information {company_info}. You're supposed to talk about the organisation very smartly in every post. Mention {company_name} where it is good to have mention at least once. Make the post a combination of marketing campaign. 
    [System]: You are supposed to write {content_type} post about the {moment_query} with the provided info {moment_info}.
    [System]: Tone of the post must be same as the provided post the possible tones are ["formal", "casual", "informative", "persuasive"] and target the {audience} audience.
    [System]: Keep it specific to {location}.
    [System]: DO NOT PROVIDE ANY EXTRA INFORMATION.
    [User]: Write a post similar to the post {ref_post} about the {moment_query} that is relevant to my company. You are allowed to use this post to find a relevant structure.Structure the post with the reference post. You are not allowed to use the exact words from the post. No Plagerism allowed.
    """
    content_gen_prompt_template = PromptTemplate(input_variables=["company_name","company_info","content_type","moment_query","audience","location","ref_post","moment_info"],template=content_gen_prompt)
    content_gen_chain = LLMChain(llm=llm, prompt=content_gen_prompt_template, output_key="post")

    extras_gen_prompt = """Given this post text for a {content_type}: {post}
    Tell me what other things can be put in the post. Include description of images, videos, audio, hashtags, etc. as lists, only include elements that are relevant to a {content_type}"""
    extras_gen_prompt_template = PromptTemplate(input_variables = ["content_type","post"],template=extras_gen_prompt)
    extras_gen_chain = LLMChain(llm=llm, prompt=extras_gen_prompt_template, output_key="extras")

    final_chain = SequentialChain(
        # chains=[moment_chain, tonality_post_chain, content_gen_chain],
        chains=[moment_chain, content_gen_chain,extras_gen_chain],
        input_variables=["company_name", "company_info", "location", "audience", "moment_query", "objective", "content_type","ref_post"],
        output_variables=["post","extras"],
        verbose=True
    )
    return final_chain({
        "company_name": company_name,
        "company_info": company_info,
        "moment_query": moment,
        "objective": objective,
        "location": location,
        "audience": audience,
        "content_type": content_type,
        "ref_post": ref_post
    })