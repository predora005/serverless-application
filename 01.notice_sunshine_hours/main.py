# coding: utf-8

import scrape, db, slack
import datetime
import numpy as np
import time
import pandas as pd
import decimal
#import slackweb

##################################################
# 日毎の日照時間を抽出
##################################################
def get_sunshine_hours(prec_no, block_no, start_date, end_date):
    
    date_list= []
    sunshine_hour_list = []
    
    days = (end_date - start_date).days + 1
    for i in range(days):
        
        # 指定日付の気象データを取得
        date = start_date + datetime.timedelta(i)
        year, month, day = date.year, date.month, date.day
        df = scrape.get_weather(prec_no, block_no, year, month, day)
        
        # 日照時間の合計を取得
        sunshine_hours = df[('日照時間(h)','日照時間(h)')]
        sunshine_hours = sunshine_hours.str.strip().replace('', np.nan)
        sunshine_hour = sunshine_hours.astype('float32').sum()
        
        # リストに追加
        date_list.append(date)
        sunshine_hour_list.append(sunshine_hour)
        
        # 1秒スリープ
        time.sleep(1)
    
    # DataFrameを作成
    df = pd.DataFrame({'日付': date_list, '日照時間': sunshine_hour_list})
    
    return df
    
##################################################
# メイン
##################################################
if __name__ == '__main__':
    
    # 水戸市の都道府県番号と観測所番号
    prec_no = 40
    block_no = 47629
    point_name = '水戸市'
    
    # 前日の日照時間を取得する。
    end_date =  datetime.date.today() + datetime.timedelta(days=-1)
    start_date = end_date
    df = get_sunshine_hours(prec_no, block_no, start_date, end_date)
    
    # DynamoDBに前日の日照時間を書き込み
    db.put_db('水戸市', df)
    
    # DynamoDBから過去1週間分の日照時間を読み込み
    end_date =  datetime.date.today() + datetime.timedelta(days=-1)
    start_date = end_date + datetime.timedelta(days=-6)
    df = db.get_db('水戸市', start_date, end_date)
    
    # Slackに投稿する
    slack.post(df)
    