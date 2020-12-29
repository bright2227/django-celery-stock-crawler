import os 
import time
import psycopg2
from os.path import isfile, join
from sqlalchemy.ext.declarative import declarative_base, AbstractConcreteBase
from sqlalchemy import Column, Integer, String,  create_engine, BigInteger, DateTime, Text, Float
from sqlalchemy.orm import scoped_session, sessionmaker
from crawl.settings import db_url, db_param
from celery import shared_task
import pandas as pd
from io import StringIO
import sys

Base = declarative_base()
engine = create_engine(db_url, pool_recycle=3600, pool_size=10 )


class MonthRevenue(AbstractConcreteBase, Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column("日期", DateTime)
    company_id = Column('公司代號', Integer)
    company_name = Column("公司名稱", String(12))
    industry = Column("產業別", String(12))
    rev_cm = Column("營業收入_當月營收", BigInteger) #Current month
    rev_pm = Column("營業收入_上月營收", BigInteger) #Previous month
    rev_lm = Column("營業收入_去年當月營收", BigInteger) #Last year month
    rev_mom = Column("營業收入_上月比較增減百分比", Float) #Month on month
    rev_yoy = Column("營業收入_去年同月增減百分比", Float) #Year on year
    acu_rev_m = Column('累計營業收入_當月累計營收', BigInteger) # accumulate
    acu_rev_l = Column('累計營業收入_去年累計營收', BigInteger) 
    acu_rev_qoq = Column('累計營業收入_前期比較增減百分比', Float) # 
    remark = Column('備註', Text) # 
    __table_args__ = {
        "mysql_charset" : "utf8"
    }


class MonthRevenueSii(MonthRevenue):
    __tablename__ = 'MonthRevenueSii'


class MonthRevenueOtc(MonthRevenue):
    __tablename__ = 'MonthRevenueOtc'


def copy_from_stringio(conn, df, tablename):
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    cursor = conn.cursor()  
    cursor.copy_from(buffer, tablename, sep=",", null="", columns=df.columns)
    conn.commit()

    cursor.close()
    return


@shared_task
def save_files(files_n, times):

    mypath = 'files/'
    for i in range(times):
        time.sleep(3)
        onlyfiles = sorted([f for f in os.listdir(mypath) if isfile(join(mypath, f))])
        if files_n is None:
            break
        elif files_n != len(onlyfiles):
            print('some files are not downloaded, sleep for 3 secondes')
            if i == 2:
                raise Exception('some files are not downloaded, please check.')
        elif files_n == len(onlyfiles):
            break


    conn = psycopg2.connect(**db_param)

    for filename in onlyfiles:
        table, year, month, stock_type = filename.split('_')
        tablename = '"' + table + stock_type[0].upper() + stock_type[1:3] + '"'

        df = pd.read_csv(mypath+filename, index_col=0)
        copy_from_stringio(conn, df, tablename)
        os.remove(mypath+filename)

    conn.close()
    return 

if __name__ == '__main__':
    # create tables docker exec -it crawl_app_web_1 python3 -m core.models create
    if len(sys.argv) == 2:

        if sys.argv[1] == 'create':
            print('create tables, Old table remain uneffected')
            DBSession = scoped_session(sessionmaker())
            DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
            Base.metadata.create_all(engine)

        elif sys.argv[1] == 'drop':
            print('drop all tables data')
            DBSession = scoped_session(sessionmaker())
            DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
            Base.metadata.drop_all(engine)

