import datetime
import requests
import pandas as pd
from io import StringIO
from celery import shared_task
from crawlers.request_proxy import post_proxy_methods
import csv
import os


@shared_task
def request_month_revenue(year, month, stock_type, proxy):
    # insert dispatcher by date
    filename = f'MonthRevenue_{year}_{month}_{stock_type}.csv'
    date = f"{year}-{month}-15"

    year = year - 1911
    month = (month+10)%12+1
    if month == 12:
        year -= 1

    url = "https://mops.twse.com.tw/server-java/FileDownLoad"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Host': 'mops.twse.com.tw', # 404 error
            'Referer': f'https://mops.twse.com.tw/nas/t21/{stock_type}/t21sc03_{year}_{month}.html',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
            "Content-Type": "application/x-www-form-urlencoded"
            }

    data = {'step': 9,
            'functionName': 'show_file',
            'filePath': f"/home/html/nas/t21/{stock_type}/",
            'fileName': f"t21sc03_{year}_{month}.csv"}

    request_post = post_proxy_methods[proxy]
    res = request_post(url, headers, data)  
    res.encoding = 'utf-8-sig'  #直接省略 csv中開頭\ufeff

    res = StringIO(res.text)
    with open(f'files/{filename}', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)

        check_columns = res.readline()    
        l = check_columns.split(',')
        
        if check_columns.split(',') != ['出表日期', '資料年月', '公司代號', '公司名稱', \
                                        '產業別', '營業收入-當月營收', '營業收入-上月營收', \
                                        '營業收入-去年當月營收', '營業收入-上月比較增減(%)', \
                                        '營業收入-去年同月增減(%)', '累計營業收入-當月累計營收', \
                                        '累計營業收入-去年累計營收', '累計營業收入-前期比較增減(%)', '備註\r\n']:
            for line in res.readlines():
                print(line)
            
            csvfile.close()
            os.remove(f'files/{filename}')
            raise Exception(f'columns formate of {filename} is changed') 

        writer.writerow(['', '日期', '公司代號', '公司名稱', '產業別', '營業收入_當月營收', '營業收入_上月營收', \
                        '營業收入_去年當月營收', '營業收入_上月比較增減百分比', '營業收入_去年同月增減百分比', \
                        '累計營業收入_當月累計營收', '累計營業收入_去年累計營收', '累計營業收入_前期比較增減百分比', '備註'])
        i = 0
        for line in res.readlines():
            line = line[1:-2].split('","')[2:]  # 備註有 ',' 妨礙copy_from
            line = [i, date] + line[:-1] + [line[-1][:-1].replace(',','')]
            writer.writerow(line)
            i+=1

    return 
