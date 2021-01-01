from celery import shared_task
from crawlers import api_keys
import requests
import json
from crawl.celery import re
from crawlers import api_keys


@shared_task
def request_proxy_ips_proxypage():

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


# def request_post_proxy(url, headers, data):
#     # Post
#     # POST https://app.scrapingbee.com/api/v1
#     # bee request can't work with celery, it shows "message max concurrency 1"
#     connect_timeout, read_timeout = 10.0, 30.0

#     bee_headers = {}
#     for k,v in headers.items():
#         bee_headers['Spb-'+k] = v

#     try:
#         res = requests.post(
#             url="https://app.scrapingbee.com/api/v1",
#             params={
#                 "url": url,
#                 "api_key": api_keys.BEE,
#                 "forward_headers": "true",
#             },
#             headers=bee_headers,
#             data=data,
#             timeout=(connect_timeout, read_timeout),
#         )
#     except requests.exceptions.RequestException as e:
#         print(e)        
#     return res


def request_post(url, headers, data,):
    
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