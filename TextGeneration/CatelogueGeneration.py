from .SimpleGeneration import generate_content
from .ReferencePostGeneration import generate_similar_content
from .utils import prepare_prods
from typing import Union
import pandas as pd

def generate_post_with_prod(company_name: str,
    moment: str,
    content_type: str,
    objective: str,
    location: str,
    audience: str,
    company_info,
    moment_retriver,
    products:pd.DataFrame,
    product_names_col:str,
    product_name:str,
    ref_post:Union[str,None] = None,
    tone:Union[str,None] = None,
    structure:Union[str,None] = None,
    model="gpt_3_5_chat",
    )-> dict[str,str]:
    prod = prepare_prods(products.loc[products[product_names_col].isin(product_name)].reset_index())
    company_info += "Following are some of the products sell by {company_name}. Talk about the following products in the post: \n"+ prod

    if ref_post is None:
        return generate_content(
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
                        model="gpt_4_high_temp"
                    )
    else:
        return generate_similar_content(company_name,
                moment,
                content_type,
                objective,
                location,
                audience,
                company_info,
                moment_retriver,
                ref_post,
                model="gpt_4_high_temp"
            )