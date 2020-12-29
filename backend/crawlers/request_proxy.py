from celery import shared_task
import requests


def request_post_proxy(url, headers, data):
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
                "api_key": "MPOONOA92WORPC99R2NDG6ZHNZCPGEZIMPCF0NEPFG22DMYJWDFARW0UJUAFII37NQMP7D2LP4WXKM6F",
                "forward_headers": "true",
            },
            headers=bee_headers,
            data=data,
            timeout=(connect_timeout, read_timeout),
        )
    except requests.exceptions.RequestException as e:
        print(e)        
    return res


def request_post(url, headers, data):
    connect_timeout, read_timeout = 10.0, 30.0
    try:
        res = requests.post(url, headers=headers, data=data, timeout=(connect_timeout, read_timeout))
    except requests.exceptions.RequestException as e:
        print(e)
    return res


post_proxy_methods = {'bee':request_post_proxy, 'non':request_post}
