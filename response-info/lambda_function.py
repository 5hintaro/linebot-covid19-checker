import boto3
import os, sys

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

bucket = 'BUCKET_NAME'
filename = 'FILE_NAME'

japan_list = ['北海道','青森県','岩手県','宮城県','秋田県','山形県','福島県','茨城県',
              '栃木県','群馬県','埼玉県','千葉県','東京都','神奈川県','新潟県','富山県',
              '石川県','福井県','山梨県','長野県','岐阜県','静岡県','愛知県','三重県',
              '滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県','鳥取県','島根県',
              '岡山県','広島県','山口県','徳島県','香川県','愛媛県','高知県','福岡県',
              '佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県']

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def lambda_handler(event, context):
    signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        # Create data
        area = line_event.message.text
        if area in japan_list:
            csvfile = boto3.resource('s3').Object(bucket, filename).get()['Body'].read().decode('utf-8')
            lines = csvfile.split()
            data = [line for line in lines if area in line]
            output = data[-1].strip('[]').strip("''").split(',')
            text_result = '患者数：' + output[4] + '\n' + '現在は入院等：' + output[5] + '\n' + '退院者：' + output[6] + '\n'  + '死亡者：' + output[7]
        else:
            text_result = '都道府県名を入力してください'
    
        line_bot_api.reply_message(line_event.reply_token, [TextSendMessage(text=text_result)])

    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json
