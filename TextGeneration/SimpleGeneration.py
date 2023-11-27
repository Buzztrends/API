from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.vectorstores.base import VectorStoreRetriever


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
    company_info: str,
    moment_retriver: VectorStoreRetriever,
    model="gpt_3_5_chat"
): 
    if location == "":
        location = "No specific target location."
    
    if audience == "":
        audience = "No specific target audience. Make it appeal to everyone."
    
    # llm = OpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.5)
    print("using ", model)
    llm = get_llm(model, 0.5)
    
    # =================== MOMENT EXTRACTOR CHAIN ==========
    moment_query = f"Tell me in detail about {moment}"
    relevant_docs = moment_retriver.get_relevant_documents(moment_query)
    moment_context = "\n".join([item.page_content.replace("\n", " ") for item in relevant_docs])
    moment_query_template = """Given the following context, i want you to answer this query: {moment_query}

    {moment_context}
    """
    moment_prompt = PromptTemplate(input_variables=["moment_query", "moment_context"], template=moment_query_template)
    moment_chain = LLMChain(llm=get_llm("gpt_3_5_chat"), prompt=moment_prompt, output_key="moment_info")

    # OLD STUFF
    # moment_query_template = "Tell me about {moment_query}. How is it relevant, significant, and important?"
    # moment_prompt = PromptTemplate(input_variables=["moment_query"], template=moment_query_template)
    # moment_chain = LLMChain(llm=llm, prompt=moment_prompt, memory=moment_memory, output_key="moment_info")


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
        input_variables=["company_name", "company_info", "location", "audience", "moment_query", "moment_context", "tone", "objective", "content_type", "structure"],
        output_variables=["post", "extras"],
        verbose=True
    )

    return final_chain({
        "company_name": company_name,
        "company_info": company_info,
        "moment_query": moment,
        "moment_context": moment_context,
        "tone": tone,
        "objective": objective,
        "structure": structure,
        "location": location,
        "audience": audience,
        "content_type": content_type
    })
