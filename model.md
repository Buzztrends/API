# User Data Model:

## JSON Scheme
```
{'BaseMoment': {'properties': {'_id': {'title': ' Id',
                                                 'type': 'string'},
                                         'hashtags': {'anyOf': [{'items': {'type': 'string'},
                                                                 'type': 'array'},
                                                                {'type': 'null'}],
                                                      'title': 'Hashtags'},
                                         'source': {'anyOf': [{'type': 'string'},
                                                              {'type': 'null'}],
                                                    'title': 'Source'},
                                         'title': {'title': 'Title',
                                                   'type': 'string'},
                                         'topic': {'anyOf': [{'type': 'string'},
                                                             {'type': 'null'}],
                                                   'title': 'Topic'},
                                         'url': {'title': 'Url',
                                                 'type': 'string'},
                                         'validation': {'anyOf': [{'type': 'string'},
                                                                  {'type': 'null'}],
                                                        'title': 'Validation'}},
                          'required': ['title',
                                       'url',
                                       'source',
                                       'topic',
                                       'validation',
                                       'hashtags'],
                          'title': 'BaseMoment',
                          'type': 'object'},
           'Moments': {'properties': {'_id': {'title': ' Id', 'type': 'string'},
                                      'current_events': {'default': [],
                                                         'items': {'$ref': '#/$defs/BaseMoment'},
                                                         'title': 'Current '
                                                                  'Events',
                                                         'type': 'array'},
                                      'general_news': {'default': [],
                                                       'items': {'$ref': '#/$defs/BaseMoment'},
                                                       'title': 'General News',
                                                       'type': 'array'},
                                      'industry_news': {'default': [],
                                                        'items': {'$ref': '#/$defs/BaseMoment'},
                                                        'title': 'Industry '
                                                                 'News',
                                                        'type': 'array'},
                                      'social_media': {'default': [],
                                                       'items': {'$ref': '#/$defs/BaseMoment'},
                                                       'title': 'Social Media',
                                                       'type': 'array'},
                                      'vector_store_id': {'title': 'Vector '
                                                                   'Store Id',
                                                          'type': 'string'}},
                       'required': ['vector_store_id'],
                       'title': 'Moments',
                       'type': 'object'}}
```
## Example JSON
```
 'examples':{'company_description': 'Company Description',
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
                                               'validation': 'Test Validation '
                                                             '3'},
                                              {'hashtags': ['h1', 'h2', 'h3'],
                                               'id': 'e9db6435-b92c-4143-9cad-3bff073aea41',
                                               'source': 'test_source 4',
                                               'title': 'Test Title 4',
                                               'topic': 'Test Topic 4',
                                               'url': 'www.example.com',
                                               'validation': 'Test Validation '
                                                             '4'}],
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
                                             'validation': 'Test Validation '
                                                           '2'}],
                           'id': '9003e9a5-9c3d-4129-ac53-e028f8070704',
                           'industry_news': [{'hashtags': ['h1', 'h2', 'h3'],
                                              'id': '0478ceec-00f5-4830-8260-b0b4a523b430',
                                              'source': 'test_source 7',
                                              'title': 'Test Title 7',
                                              'topic': 'Test Topic 7',
                                              'url': 'www.example.com',
                                              'validation': 'Test Validation '
                                                            '7'},
                                             {'hashtags': ['h1', 'h2', 'h3'],
                                              'id': '3d8876fd-26a9-4bad-a78e-28e4438c79d2',
                                              'source': 'test_source 8',
                                              'title': 'Test Title 8',
                                              'topic': 'Test Topic 8',
                                              'url': 'www.example.com',
                                              'validation': 'Test Validation '
                                                            '8'}],
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
                                             'validation': 'Test Validation '
                                                           '6'}],
                           'vector_store_id': 'vec_1'},
               'password': 'password',
               'saved_items': [],
               'username': 'user_1'},
```
## Properties
```
 'properties': {'_id': {'title': ' Id', 'type': 'string'},
                'company_description': {'title': 'Company Description',
                                        'type': 'string'},
                'company_name': {'title': 'Company Name', 'type': 'string'},
                'content_category': {'title': 'Content Category',
                                     'type': 'string'},
                'last_5_generations': {'anyOf': [{'items': {'type': 'string'},
                                                  'type': 'array'},
                                                 {'items': {}, 'type': 'array'},
                                                 {'type': 'null'}],
                                       'default': [],
                                       'title': 'Last 5 Generations'},
                'moments': {'anyOf': [{'$ref': '#/$defs/Moments'},
                                      {'type': 'null'}],
                            'default': None},
                'password': {'title': 'Password', 'type': 'string'},
                'saved_items': {'anyOf': [{'items': {'type': 'string'},
                                           'type': 'array'},
                                          {'items': {}, 'type': 'array'},
                                          {'type': 'null'}],
                                'default': [],
                                'title': 'Saved Items'},
                'username': {'title': 'Username', 'type': 'string'}},
```
## Required Fields
```
 'required': ['company_name',
              'username',
              'password',
              'company_description',
              'content_category'],
 'title': 'Main',
 'type': 'object'
```