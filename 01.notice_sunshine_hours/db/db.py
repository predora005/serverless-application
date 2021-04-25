# coding: utf-8

import boto3
from boto3.dynamodb.conditions import Key
import decimal
import pandas as pd

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
    