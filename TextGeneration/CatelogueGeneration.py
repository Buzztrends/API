from .SimpleGeneration import generate_content,generate_content_2
from .ReferencePostGeneration import generate_similar_content
from .utils import prepare_prods
from typing import Union
import pandas as pd
from logger.contentGenLogger import ContentGenLogger

logger = ContentGenLogger().getLogger()
logger.info("Module Imported!")

def generate_post_with_prod(company_name: str,
    moment: str,
    content_type: str,
    objective: str,
    location: str,
    audience: str,
    company_info,
    moment_retriver,
    product_name:str,
    products:dict,
    extras_guidelines:str,
    ref_post:Union[str,None] = None,
    tone:Union[str,None] = None,
    structure:Union[str,None] = None,
    model="gpt_3_5_chat_azure",
    )-> dict[str,str]:
    prod = prepare_prods(products[product_name],product_name)
    company_info += "Following are some of the products sell by {company_name}. Talk about the following products in the post: \n"+ prod
    logger.info(f"{__name__} Called Called:\n- Parameters:\
                 \n\tCompany Name:{company_name}\
                 \n\t-Moment:{moment}\
                 \n\t-Content Type:{content_type}\
                 \n\t-Tone:{tone}\
                 \n\t-Objective:{objective}\
                 \n\t-Structure:{structure}\
                 \n\t-Location:{location}\
                 \n\t-Audience:{audience}\
                 \n\t-Company Info:{company_info}\
                 \n\t-Extras Guidelines:{extras_guidelines}")
    if ref_post is None:
        logger.info("Hitting the generate_content_2 method")
        return generate_content_2(
                        company_name,
                        moment,
                        content_type,
                        tone,
                        objective,
                        structure,
                        location,
                        audience,
                        company_info,
                        moment_retriver,
                        extras_guidelines,
                        model="gpt_4_high_temp",
                    )
    else:
        logger.info("Hitting the generate_similar_content method")
        return generate_similar_content(company_name,
                moment,
                content_type,
                objective,
                location,
                audience,
                company_info,
                moment_retriver,
                ref_post,
                model="gpt_4_high_temp",
                extras_guidelines=extras_guidelines,
            )