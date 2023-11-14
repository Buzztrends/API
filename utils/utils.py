import requests
from bs4 import BeautifulSoup
import os

from googleapiclient.discovery import build

def extract_text_from(url):
    print("Getting text:", url)
    html = requests.get(url, headers={"user-agent": "something"}).text
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    return '\n'.join(line for line in lines if line)


def get_sitetexts(sitelinks):
    """extract text from a list of given sites"""
    sitetexts = []
    for url in sitelinks:
        try:
            text = extract_text_from(url)

            text = " ".join(text.split(" ")[:1000])

            sitetexts.append({
                "source": url,
                "text": text
            })
        except:
            pass

    return sitetexts


def googleSearch(query:str,n:int=10):
    """
    Fetches top 'n' links for the corresponding links  and 'query'

    Dependencies: pygoogle

    ! MUST HAVE "GOOGLE API KEY and SEARCH ENGINE KEY" as ENVIRONMENT VARIABLE
    Args:
        - query: string, the query to search on the internet
        - n    : int, number of links to return
    Returns:
        - List[Str]: List of string containing the URL of websites
    """
    #define key
    api_key = os.environ['GOOGLE_API_KEY']          # enviroment variable with API key
    cse_key = os.environ['SEARCH_ENGINE_KEY']       # enviroment variable with Search Engine Key
    
    results = []
    nextPage = 0

    # build the service
    resource = build("customsearch", 'v1', developerKey=api_key).cse()
    
    # search the required number of URLs
    for i in range(n//10):
        resp= resource.list(q=query, cx=cse_key,num=10,start=nextPage).execute()
        nextPage = resp['queries']['nextPage'][0]['startIndex']
        links = [i['link'] for i in resp['items']]
        results.extend(links)
    resp = resource.list(q=query, cx=cse_key,num=n%10).execute()
    nextPage = resp['queries']['nextPage'][0]['startIndex']
    links = [i['link'] for i in resp['items']]
    results.extend(links[:n%10])
    
    # return the URLs
    return results

def get_related_links(query, num_results=10, initial="", kind="", country="IN"):
    """lookup google for related content"""
    results = googleSearch(f'{initial} {query} {kind}', num_results=num_results, country=country)

    return results
