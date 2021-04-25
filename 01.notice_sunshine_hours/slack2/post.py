# coding: utf-8

from slack_sdk.webhook import WebhookClient

##################################################
# Slackに投稿する
##################################################
def post(df):
    
    header = __make_header(df)
    main_messages = __make_main_messages(df)
    divider = __make_divider(df)
    fields = __make_fields(df)
    
    # Slackに送るメッセージをセット
    blocks = []
    blocks.append(header)
    blocks.extend(main_messages)
    blocks.extend([divider, fields])
    
    url = ''
    webhook = WebhookClient(url)
    response = webhook.send(blocks=blocks)
    print(response.status_code)
    print(response.body)
    
##################################################
# headerを作成
##################################################
def __make_header(df):
    
    start_date = df['date'].head(1).iloc[-1]
    end_date = df['date'].tail(1).iloc[-1]
    
    header = {}
    header['type'] = 'header'
    header['text'] = {}
    header['text']['type'] = 'plain_text'
    header['text']['text'] = f"{start_date}〜{end_date}の日照時間"
    
    return header
    
##################################################
# メインメッセージを作成
##################################################
def __make_main_messages(df):
    
    # 平年の平均日照時間、平均からズレを許容する範囲
    average_hours = 37
    range = 5
    
    # 過去1週間の日照時間を合計し、メッセージを作成
    one_week_hours = df['sunshine_hours'].sum()
    text1 = f"{df['point_name'][0]} 過去1週間の日照時間は *{one_week_hours}* hoursです。"
    text1 += f"平年の平均日照時間は約 *{average_hours}* hoursです。"
    
    # 平年の日照時間と過去1週間とを比較して、メッセージ作成
    if one_week_hours < (average_hours - range):
        text2 = ':exclamation: 今週は日照時間が少ないので、意識して日光を浴びましょう。'
    elif one_week_hours > (average_hours + range):
        text2 = ':sunny: 今週は日照時間が多い１週間です。'
    else:
        text2 = ':information_source: 今週の日照時間は平年並みです。'
    
    message1 = {}
    message1['type'] = 'section'
    message1['text'] = {}
    message1['text']['type'] = 'mrkdwn'
    message1['text']['text'] = text1
    
    message2 = {}
    message2['type'] = 'section'
    message2['text'] = {}
    message2['text']['type'] = 'mrkdwn'
    message2['text']['text'] = text2
    
    return (message1, message2)
    
##################################################
# divider
##################################################
def __make_divider(df):
    
    divider = {}
    divider['type'] = 'divider'
    
    return divider
    
##################################################
# fieldsを作成
##################################################
def __make_fields(df):
    
    # 日毎の日照時間をfieldsにセットする
    fields = []
    for index, row in df.iterrows():
        
        date = row['date']
        value = row['sunshine_hours']
        
        field = {}
        field['type'] = 'plain_text'
        field['text'] = f"{date}:  {value} hours"
        
        fields.append(field)
    
    text_fields = {}
    text_fields['type'] = 'section'
    text_fields['fields'] = fields
    
    return text_fields
    