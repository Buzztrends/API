# API


## File/Call sturcture

```
Root
|
|Moments
|
|Text Generation
|---|Simple generation
|---|Reference post generation
|---|Catelogue generation
|
|Image generation
|---|edenai
|
|vectorstores <not revealed>
|---|Interface
|
|Data sources <not revealed>
|---|validation (best-hashtags, google trends)
|---|news/content sources (google news, buzzfeed)
|
|Utilities (all extra stuff, scraping, google search, ) <not revealed>
|
|
```

# Payload Structure

## 1. Moments

* URL
```
https://<url>/text_generation/moments
```

* Params
```
{
    "key": <key>,
    "company_UID": <>,
    "moment": <>,
    "content_type": <>,
}
```

* Return
```
{
    "general_news": [{
        "title": <>,
        "url":<>,
        "source": <>,
        "topic": <>,
        "validation": <string or None>
    }, ... ],
    "industry_news": [{
        "title": <>,
        "url":<>,
        "source": <>,
        "topic": <>,
        "validation": <string or None>    
    }, ... ]
    "current_events": [{
        "event_name": <>,
        "topic": <>,
        "reason": <>,
        "validation": <string or None>
    }, ... ],
    "social_media_trends": [{
        "title": <>,
        "reason": <>,
        "hashtags": [<list of strings>],
        "validation": <string or None>
    }]
}
```

<hr>

## 2. TEXT GENERATION

### Text generation - simple generation

* URL
```
https://<url>/text_generation/simple_generation
```

* Params
```
{
    "key": <key>,
    "company_name": <>,
    "moment": <>,
    "custom_moment": <0 or 1>,
    "content_type": <>,
    "tone": <>,
    "objective": <>,
    "structure": <>,
    "location": <>,
    "audience": <>,
    "company_info": <>
}
```

3. Text generation - Reference post generation

* URL
```
https://<url>/text_generation/reference_post_generation
```

* Params
```
{
    "key": <key>,
    "company_name": <>,
    "moment": <>,
    "custom_moment": <0 or 1>,
    "content_type": <>,
    "objective": <>,
    "location": <>,
    "audience": <>,
    "company_info": <>,
    "reference_post": <text from the url>
}
```

4. Text generation - catelogue generation

* URL
```
https://<url>/text_generation/catelogue_generation
```

* Params
```
{
    "key": <key>,
    "company_name": <>,
    "moment": <>,
    "custom_moment": <0 or 1>,
    "content_type": <>,
    "objective": <>,
    "location": <>,
    "audience": <>,
    "company_info": <>,
    "list_of_product": [<list of strings>]
}
```

### TEXT GENERATION OUTPUT

```
{
    "posts": <string>,
    "extras": <string>
}
```

<hr>

## Image generation

* params
```
{
    "key": <key>
    "extras": <extras generated in text generation>
}
```

* return
```
{"urls": [<list of strings>]}
```

<hr>

