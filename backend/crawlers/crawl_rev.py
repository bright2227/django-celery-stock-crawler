import datetime
import requests
import pandas as pd
from io import StringIO
from core.models import save_db, engine, MonthRevenueSii, MonthRevenueOtc
from celery import shared_task
from crawlers.request_proxy import get_api_rotate
from bs4 import BeautifulSoup
import csv
import os


@shared_task  #get method
def request_month_revenue(year, month, stock_type):
    date = f"{year}-{month}-15"

    year = year - 1911
    month = (month+10)%12+1
    if month == 12:
        year -= 1    

    url = f'https://mops.twse.com.tw/nas/t21/{stock_type}/t21sc03_{year}_{month}.html'

    res = get_api_rotate(url)

    # bs = BeautifulSoup(res,'html.parser')

    # companys = bs.find_all('tr', attrs={'align':'right'})
    # industries = bs.find_all('th', attrs={'align':'left'})
    # industries = list(map(lambda x: x.string[4:].split('（',1)[0], industries))

    # columns2 = ['date', 'industry', 'company_id', 'company_name', 'rev_cm', 'rev_pm', 'rev_lm', 'rev_mom', 'rev_yoy', 'acu_rev_m' , 'acu_rev_l', 'acu_rev_qoq', 'remark']

    # def string_formate(x):
    #     x = x.string
    #     i = 0
    #     while i < len(x):
    #         if x[i] != ' ':
    #             break
    #         i+=1
    #     x = x[i:]
        
    #     if x in ('\xa0', '不適用'):
    #         return None
    #     else:
    #         return x.replace(',','').replace('*','')

    # i=0
    # obj_list=[]
    # for company in companys[:-1]:
    #     company = company.find_all('td')
        
    #     if len(company) != 11:
    #         i+=1
    #         continue
            
    #     company = list(map(string_formate, company))  # regex  # need regex
    #     company = [date, industries[i]] + company
    #     obj = {k:v for k,v in zip(columns2, company)}
    #     obj_list.append(obj)

    columns2 = ['date', 'industry', 'company_id', 'company_name', 'rev_cm', 'rev_pm', 'rev_lm', 'rev_mom', 'rev_yoy', 'acu_rev_m' , 'acu_rev_l', 'acu_rev_qoq', 'remark']

    dfs = pd.read_html(res)

    obj_list = []

    for df in dfs:
        
        check_ind = str(df.columns[0]).split('產業別：')
        
        if check_ind[0] == '0':
            continue
        
        if len(check_ind) == 2:
            ind = check_ind[1].replace("')", '').split('（')[0]
            continue
        
        for i in range(len(df)-1):
            obj = [date, ind] + list(map(lambda x : str(x), df.iloc[i].to_list())) + ['-']
            obj = {k:v for k,v in zip(columns2, obj)}
            obj_list.append(obj)

    if stock_type  == 'sii':
        save_db(obj_list, MonthRevenueSii, engine)
    elif stock_type  == 'otc':
        save_db(obj_list, MonthRevenueOtc, engine) 
    return

# @shared_task   #post method
# def request_month_revenue(year, month, stock_type):
#     # insert dispatcher by date
#     filename = f'MonthRevenue_{year}_{month}_{stock_type}.csv'
#     date = f"{year}-{month}-15"

#     year = year - 1911
#     month = (month+10)%12+1
#     if month == 12:
#         year -= 1

#     url = "https://mops.twse.com.tw/server-java/FileDownLoad"

#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
#             'Host': 'mops.twse.com.tw', 
#             'Referer': f'https://mops.twse.com.tw/nas/t21/{stock_type}/t21sc03_{year}_{month}.html',
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
#             "Content-Type": "application/x-www-form-urlencoded"
#             }

#     data = {'step': 9,
#             'functionName': 'show_file',
#             'filePath': f"/home/html/nas/t21/{stock_type}/",
#             'fileName': f"t21sc03_{year}_{month}.csv"}

#     res = request_post(url, headers, data)  
#     res.encoding = 'utf-8-sig'  #直接省略 csv中開頭\ufeff

#     res = StringIO(res.text)
#     with open(f'files/{filename}', 'w', newline='', encoding='utf-8-sig') as csvfile:
#         writer = csv.writer(csvfile)

#         check_columns = res.readline()    
#         l = check_columns.split(',')
        
#         if check_columns.split(',') != ['出表日期', '資料年月', '公司代號', '公司名稱', \
#                                         '產業別', '營業收入-當月營收', '營業收入-上月營收', \
#                                         '營業收入-去年當月營收', '營業收入-上月比較增減(%)', \
#                                         '營業收入-去年同月增減(%)', '累計營業收入-當月累計營收', \
#                                         '累計營業收入-去年累計營收', '累計營業收入-前期比較增減(%)', '備註\r\n']:
#             for line in res.readlines():
#                 print(line)
            
#             csvfile.close()
#             os.remove(f'files/{filename}')
#             raise Exception(f'columns formate of {filename} is changed') 

#         writer.writerow(['', '日期', '公司代號', '公司名稱', '產業別', '營業收入_當月營收', '營業收入_上月營收', \
#                         '營業收入_去年當月營收', '營業收入_上月比較增減百分比', '營業收入_去年同月增減百分比', \
#                         '累計營業收入_當月累計營收', '累計營業收入_去年累計營收', '累計營業收入_前期比較增減百分比', '備註'])
#         i = 0
#         for line in res.readlines():
#             line = line[1:-2].split('","')[2:]  # 備註有 ',' 妨礙copy_from
#             line = [i, date] + line[:-1] + [line[-1][:-1].replace(',','')]
#             writer.writerow(line)
#             i+=1

#     return 
