from celery import shared_task
from crawlers import api_keys
import requests
import json
import http.client
import time
from crawl.celery import re
from crawlers import api_keys
from scraper_api import ScraperAPIClient


@shared_task
def get_proxyips_proxypage():

    url = "https://proxypage1.p.rapidapi.com/v1/tier2"

    querystring = {"ssl":"True","limit":"100","country":"US","type":"HTTP"}

    headers = {
        'x-rapidapi-host': "proxypage1.p.rapidapi.com",
        'x-rapidapi-key': api_keys.PROXYPAGE
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    proxy_list = json.loads(response.text)

    for proxy in proxy_list:
        re.lpush('proxy_set', f"{proxy['ip']}:{proxy['port']}")
    
    return


def post_proxy(url, headers, data,):
    proxy = re.lpop("proxy_set")  
    ## 20 proxys may run out, wait some time for them
    i = 0
    while proxy is None:
        if i > 5:
            raise Exception("Can't get proxy from redis")        
        i += 1
        time.sleep(5)
        proxy = re.lpop("proxy_set")

    proxies = {
     "http": f"http://{proxy}",
     "https": f"https://{proxy}",
    }

    for _ in range(3):
        try:
            res = requests.request("POST", url, headers=headers, data=data, proxies=proxies)
            re.lpush("proxy_set", proxy)
            return res
        except requests.exceptions.RequestException as e:
            print(e, proxy)
            err = e

    ## proxys may broke
    if 'ProxyError' in str(err):
        re.rpush("proxy_set", proxy)
        return request_post(url, headers, data,)


def post_proxy_bee(url, headers, data):
    # Post
    # POST https://app.scrapingbee.com/api/v1
    # bee request can't work with celery, it shows "message max concurrency 1"
    connect_timeout, read_timeout = 10.0, 30.0

    bee_headers = {}
    for k,v in headers.items():
        bee_headers['Spb-'+k] = v

    try:
        res = requests.post(
            url="https://app.scrapingbee.com/api/v1",
            params={
                "url": url,
                "api_key": api_keys.BEE,
                "forward_headers": "true",
            },
            headers=bee_headers,
            data=data,
            timeout=(connect_timeout, read_timeout),
        )
    except requests.exceptions.RequestException as e:
        print(e)        
    return res


def get_proxy_bee(url):
    # GET https://app.scrapingbee.com/api/v1
    # bee request can't work with celery, it shows "message max concurrency 1"
    res = requests.get(
        url="https://app.scrapingbee.com/api/v1",
        params={
            "url": url,
            "api_key": api_keys.BEE,
        },
    )
    # only return string
    return res.text 


def get_proxy_scraper(url):
    # 5 concurrent 
    client = ScraperAPIClient(api_keys.SCRAPER)
    res = client.get(url = url).text
    return res


def get_proxy_ant(url):
    conn = http.client.HTTPSConnection("api.scrapingant.com")
    headers = {
        'x-api-key': api_keys.ANT
    }
    #  url[8:] to remove 'https://'+
    conn.request("GET", "/v1/general?url=https%3A%2F%2F"+ url[8:], headers=headers)

    res = conn.getresponse()
    data = res.read()
    res = json.loads(data.decode("utf-8"))['content']
    res = res.replace('<tbody>',"").replace("</tbody>", "")
    return res


def get_no_proxy(url):
    # GET https://app.scrapingbee.com/api/v1
    # bee request can't work with celery, it shows "message max concurrency 1"
    res = requests.get(
        url=url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'},
    )
    res.encoding = 'big5hkscs'
    time.sleep(5)
    # only return string
    return res.text 


api_mehtods = {
    'bee': get_proxy_bee,
    'scraper': get_proxy_scraper,
    'ant': get_proxy_ant,
    'non': get_no_proxy,
}


def get_api_rotate(url):
    key, api = re.blpop("api_list", timeout=600)
    get_api_method = api_mehtods[api]
    re.rpush("api_list", api)
    res = get_proxy_ant(url)
    return res



