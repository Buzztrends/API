from pydantic import BaseModel,Field,Json,ConfigDict
import uuid
from typing import List,Union
from pydantic_core import CoreSchema
from pydantic import BaseModel, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue


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
    # id        : str                   = Field(default_factory=uuid.uuid4, alias="_id")
    title     : str                   = Field(...)
    url       : str                   = Field(...)
    source    : Union[str,None]       = Field(...)
    topic     : Union[str,None]       = Field(...)
    validation: Union[str,None]       = Field(...)
    hashtags  : Union[List[str],None] = Field(...)

class Moments(BaseModel):
    
    # id:str = Field(default_factory=uuid.uuid4, alias="_id") 
    vector_store_id: str = Field(...)
    social_media   : List[BaseMoment]    = []
    general_news   : List[BaseMoment]    = []
    industry_news  : List[BaseMoment]    = []
    current_events : List[BaseMoment]    = []

class Post(BaseModel):
    pass

class User(BaseModel):
    company_id         : str                        = Field(default_factory=lambda :uuid.uuid4().int & (1<<32)-1)
    
    company_name       : str                        = Field(...)
    username           : str                        = Field(...)
    password           : str                        = Field(...)
    company_description: str                        = Field(...)
    content_category   : str                        = Field(...)
    country            : str                        = Field(...)
    country_code       : str                        = Field(...)
    generation_available:int                        = 99
    products           : dict                       = {} 
    moments            : Union[Moments,None]        = None
    saved_posts       : Union[dict[str,List],None] = {'under_review':[],'reviewed':[],'live':[]}
    last_5_generations : Union[list[Post],None,List] = []
    saved_topics        : Union[dict[str,List],None] = []
    model_config = ConfigDict(title='Main')
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['examples'] = [
            {'company_description': 'Company Description',
 'company_id': '2a2871b1-ad9c-4115-8264-c66dece955c6',
 'company_name': 'Company 1',
 'content_category': 'Category 1',
 'last_5_generations': [],
 'moments': {'current_events': [{'hashtags': ['h1', 'h2', 'h3'],
                                 'id': 'b18e724b-2183-489e-95db-ae040f658534',
                                 'source': 'test_source 3',
                                 'title': 'Test Title 3',
                                 'topic': 'Test Topic 3',
                                 'url': 'www.example.com',
                                 'validation': 'Test Validation 3'},
                                {'hashtags': ['h1', 'h2', 'h3'],
                                 'id': 'e9db6435-b92c-4143-9cad-3bff073aea41',
                                 'source': 'test_source 4',
                                 'title': 'Test Title 4',
                                 'topic': 'Test Topic 4',
                                 'url': 'www.example.com',
                                 'validation': 'Test Validation 4'}],
             'general_news': [{'hashtags': ['h1', 'h2', 'h3'],
                               'id': 'cd8ba55a-deb7-471a-a92a-33cd0717901e',
                               'source': 'test_source',
                               'title': 'Test Title',
                               'topic': 'Test Topic',
                               'url': 'www.example.com',
                               'validation': 'Test Validation'},
                              {'hashtags': ['h1', 'h2', 'h3'],
                               'id': '3282c29e-62b2-4c49-9b3d-530ea72a9dad',
                               'source': 'test_source 2',
                               'title': 'Test Title 2',
                               'topic': 'Test Topic 2',
                               'url': 'www.example.com',
                               'validation': 'Test Validation 2'}],
             'id': '9003e9a5-9c3d-4129-ac53-e028f8070704',
             'industry_news': [{'hashtags': ['h1', 'h2', 'h3'],
                                'id': '0478ceec-00f5-4830-8260-b0b4a523b430',
                                'source': 'test_source 7',
                                'title': 'Test Title 7',
                                'topic': 'Test Topic 7',
                                'url': 'www.example.com',
                                'validation': 'Test Validation 7'},
                               {'hashtags': ['h1', 'h2', 'h3'],
                                'id': '3d8876fd-26a9-4bad-a78e-28e4438c79d2',
                                'source': 'test_source 8',
                                'title': 'Test Title 8',
                                'topic': 'Test Topic 8',
                                'url': 'www.example.com',
                                'validation': 'Test Validation 8'}],
             'social_media': [{'hashtags': ['h1', 'h2', 'h3'],
                               'id': '2df63255-56a5-4178-80d0-204cbf323fa6',
                               'source': 'test_source 5',
                               'title': 'Test Title 5',
                               'topic': 'Test Topic 5',
                               'url': 'www.example.com',
                               'validation': 'Test Validation 6'},
                              {'hashtags': ['h1', 'h2', 'h3'],
                               'id': '756a8749-e061-4ce8-8249-14f0da4365a2',
                               'source': 'test_source 6',
                               'title': 'Test Title 6',
                               'topic': 'Test Topic 6',
                               'url': 'www.example.com',
                               'validation': 'Test Validation 6'}],
             'vector_store_id': 'vec_1'},
 'password': 'password',
 'saved_items': [],
 'username': 'user_1'}
        ]
        return json_schema


class APIModel:
    def __init__(self,user) -> None:
        self.uid:dict = uuid.uuid4().hex
        self.user = user
        self.role = "non_admin"

    def to_json(self) -> dict[str:str]:
        return {"uid":self.uid,"user":self.user,"role":self.role}

    def from_json(self,json_:dict) -> None:
        self.uid = json_.keys()[0]
        self.user = json_[self.uid]["user"]
        self.role = json_[self.uid]["role"]



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

    from server import db

    # db["users"]["user-data"].insert_one(user.dict())
    # db["api_subscribers"]["users"].insert_one({"bee621fc-5deb-4409-a428-932112d9a1a7": {
    #     "user": "test",
    #     "role": "non_admin"
    # }})
    # print(user.dict())
#     user.validate({
# 	"company_id" : 100,
# 	"company_name" : "Zomato",
# 	"username" : "zomato",
# 	"password" : "pass1",
# 	"company_description" : "https://www.zomato.com/about",
# 	"content_category" : "Indian Food",
# 	"country" : "India",
# 	"country_code" : "IN",
# 	"moments" : {
# 		"vectorstore_collection_id" : 100,
# 		"general_news" : [ ],
# 		"industry_news" : [ ],
# 		"current_events" : [ ],
# 		"social_media" : [ ]
# 	},
# 	"saved_items" : [ ],
# 	"last_5_generations" : [ ]
# })