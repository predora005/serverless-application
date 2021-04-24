# coding: utf-8

import scrape
import datetime
import numpy as np
import time
import pandas as pd
import boto3
import decimal
from boto3.dynamodb.conditions import Key
import slackweb
import json

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
# DynamoDBに書き込み
##################################################
def put_db(point_name, df):
    
    # テーブルを指定
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('sunshine-hours')
    
    for index, row in df.iterrows():
        
        date_str = row['日付'].strftime('%Y-%m-%d')
        shunshine_hours = decimal.Decimal(row['日照時間'])
        shunshine_hours = shunshine_hours.quantize(decimal.Decimal('0.1'))
        
        table.put_item(Item={
            'point_name': point_name,
            'date': date_str,
            'sunshine_hours': shunshine_hours
        })
    
##################################################
# DynamoDBから読み込み
##################################################
def get_db(point_name, start_date, end_date):
    
    # テーブルを指定
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('sunshine-hours')
    
    # 日付を文字列化
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    option = {
        'KeyConditionExpression':
            Key('point_name').eq(point_name) & \
            Key('date').between(start_date_str, end_date_str)
    }
    
    response = table.query(**option)
    df = pd.json_normalize(response['Items'])
    return df
    
    
##################################################
# Slackに投稿する
##################################################
def post_to_slack(df):
    
    # 過去1週間の日照時間を合計し、メッセージを作成
    one_week_hours = df['sunshine_hours'].sum()
    pretext = f"{df['point_name'][0]} 過去1週間の日照時間は{one_week_hours} hoursです。"
    pretext += f"平年の{4}月平均は{41} hoursです。"
    
    # 日毎の日照時間をfieldsにセットする
    fields = []
    for index, row in df.iterrows():
        # ex) title='2021-04-18', value = '11.9 hours'
        title = row['date']
        value = f"{row['sunshine_hours']} hours"
        
        field= {'title': title, 'value': value}
        fields.append(field)
    
    # Slackに送るメッセージをセット
    color = '#f49d00'
    attachments = []
    attachments.append({
        'pretext': pretext, 'fields': fields, 'color': color})
    
    url = ''
    slack = slackweb.Slack(url=url)
    slack.notify(attachments=attachments)

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
    put_db('水戸市', df)
    
    # DynamoDBから過去1週間分の日照時間を読み込み
    end_date =  datetime.date.today() + datetime.timedelta(days=-1)
    start_date = end_date + datetime.timedelta(days=-6)
    df = get_db('水戸市', start_date, end_date)
    
    # Slackに投稿する
    post_to_slack(df)
    