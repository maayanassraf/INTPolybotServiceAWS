import flask
from flask import request
import os
import boto3
import json
from bot import ObjectDetectionBot

app = flask.Flask(__name__)


# TODO load TELEGRAM_TOKEN value from Secret Manager
secretsmanager = boto3.client('secretsmanager')
response = secretsmanager.get_secret_value(SecretId='telegram_bot_token')
secret = json.loads(response['SecretString'])

TELEGRAM_TOKEN = secret["telegram_bot_token"]

TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


@app.route(f'/results', methods=['POST'])
def results():
    prediction_id = request.args.get('predictionId')

    # TODO use the prediction_id to retrieve results from DynamoDB and send to the end-user
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('maayana-aws-project-predictions')

    response = table.get_item(
        Key={
            'prediction_id': prediction_id
        }
    )
    prediction = response['Item']

    chat_id = prediction['chat_id']
    labels = prediction['labels']
    objects = []
    for label in labels:
        objects.append(label['class'])

    counter = dict.fromkeys(objects, 0)
    for val in objects:
        counter[val] += 1

    text_results = f'Detected Objects: \n{counter}'

    bot.send_text(chat_id, text_results)
    return 'Ok'


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
