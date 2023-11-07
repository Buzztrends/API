from pydantic import BaseModel,Field,Json,ConfigDict
import uuid
from typing import List,Union
"""
user data model:
{
    "company_id": <int>,
    "company_name": <string>,
    "username": <string>,
    "password": <hashed string>,
    "company_description": <string>,
    "content_category": <string>,
    "moments": {
        "vectorstore_collection_id": <int>,
        "general_news": [<list of moments>],
        "industry_news": [<list of moments>],
        "current_events": [<list of moments>],
        "social_media": [<list of moments>]
    },
    "saved_items": [<list of moments>],
    "last_5_generations": [<list of posts>]
}
"""
"""
moment data model:
{
    "title": <string>,
    "url": <string>,
    "source": <string>,
    "topic": <string>,
    "validation": <string or None>,
    "hashtags": [<list of strings>] or None
}
"""
class BaseMoment(BaseModel):
    id        : str                   = Field(default_factory=uuid.uuid4, alias="_id")
    title     : str                   = Field(...)
    url       : str                   = Field(...)
    source    : Union[str,None]       = Field(...)
    topic     : Union[str,None]       = Field(...)
    validation: Union[str,None]       = Field(...)
    hashtags  : Union[List[str],None] = Field(...)

class Moments(BaseModel):
    
    id:str = Field(default_factory=uuid.uuid4, alias="_id")
    
    vector_store_id: str = Field(...)
    social_media   : List[BaseMoment]    = []
    general_news   : List[BaseMoment]    = []
    industry_news  : List[BaseMoment]    = []
    current_events : List[BaseMoment]    = []


class User(BaseModel):
    company_id         : str                        = Field(default_factory=uuid.uuid4, alias="_id")
    
    company_name       : str                        = Field(...)
    username           : str                        = Field(...)
    password           : str                        = Field(...)
    company_description: str                        = Field(...)
    content_category   : str                        = Field(...)
    moments            : Union[Moments,None]        = None
    saved_items        : Union[List[str],None,List] = []
    last_5_generations : Union[list[str],None,List] = []

    model_config = ConfigDict(title='Main')

import json
from pprint import pprint

if __name__ == "__main__":
    base_moment  = BaseMoment(title="Test Title",url="www.example.com",source="test_source",topic="Test Topic",validation="Test Validation",hashtags=["h1","h2","h3"])
    base_moment2 = BaseMoment(title="Test Title 2",url="www.example.com",source="test_source 2",topic="Test Topic 2",validation="Test Validation 2",hashtags=["h1","h2","h3"])
    base_moment3 = BaseMoment(title="Test Title 3",url="www.example.com",source="test_source 3",topic="Test Topic 3",validation="Test Validation 3",hashtags=["h1","h2","h3"])
    base_moment4 = BaseMoment(title="Test Title 4",url="www.example.com",source="test_source 4",topic="Test Topic 4",validation="Test Validation 4",hashtags=["h1","h2","h3"])
    base_moment5 = BaseMoment(title="Test Title 5",url="www.example.com",source="test_source 5",topic="Test Topic 5",validation="Test Validation 5",hashtags=["h1","h2","h3"])
    base_moment6 = BaseMoment(title="Test Title 6",url="www.example.com",source="test_source 6",topic="Test Topic 6",validation="Test Validation 6",hashtags=["h1","h2","h3"])
    base_moment7 = BaseMoment(title="Test Title 7",url="www.example.com",source="test_source 7",topic="Test Topic 7",validation="Test Validation 7",hashtags=["h1","h2","h3"])
    base_moment8 = BaseMoment(title="Test Title 8",url="www.example.com",source="test_source 8",topic="Test Topic 8",validation="Test Validation 8",hashtags=["h1","h2","h3"])

    moments = Moments(vector_store_id="vec_1")
    moments.general_news  .extend([base_moment,base_moment2])
    moments.current_events.extend([base_moment3,base_moment4])
    moments.social_media  .extend([base_moment5,base_moment6])
    moments.industry_news .extend([base_moment7,base_moment8])


    user = User(company_name="Company 1",username="user_1",password="password",company_description="Company Description",content_category="Category 1",moments=moments,saved_items=[],last_5_generations=[])
    pprint(json.loads (user.json()))