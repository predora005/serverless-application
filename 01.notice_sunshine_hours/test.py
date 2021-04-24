# coding: utf-8

import scrape
import datetime
import numpy as np
import pandas as pd

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
        print(date, sunshine_hour)
        
        # リストに追加
        date_list.append(date)
        sunshine_hour_list.append(sunshine_hour)
    
    # DataFrameを作成
    df = pd.DataFrame({'日付': date_list, '日照時間(h)': sunshine_hour_list})
    
    return df
    
##################################################
# メイン
##################################################
if __name__ == '__main__':
    
    # 水戸市の都道府県番号と観測所番号
    prec_no = 40
    block_no = 47629
    
    # 開始日付と終了日付
    end_date =  datetime.date.today() + datetime.timedelta(days=-1)
    start_date = end_date + datetime.timedelta(days=-1)
    
    df = get_sunshine_hours(prec_no, block_no, start_date, end_date)
    print(df)
    