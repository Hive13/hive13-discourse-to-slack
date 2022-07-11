from flask import Flask, request
import requests as r
import logging
import json

# set up logging
logging.basicConfig(filename='hive13-dts.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

# slack url
config = json.load(open('config.json', 'r'))
url = config['slack_url']

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

# see slack block kit to understand the shape of this request body:
# https://app.slack.com/block-kit-builder/

categories_to_ignore = ["leadership", "wardens"]

def we_ignore_this_one(category_slug):
    if category_slug in categories_to_ignore:
        return True
    return False

@app.route('/', methods=['POST'])
def home_route_post():
    logging.debug("POST on /")
    incoming_request = request.get_json()
    logging.debug(incoming_request)
    if we_ignore_this_one(incoming_request['post']['category_slug']):
        return

    data = {
        "text": "New message on Discourse!",
        "blocks": [
            {
                "type": "header",
                "text": {
                        "type": "plain_text",
                        "text": incoming_request['post']['topic_title'],

                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                        {
                            "type": "plain_text",
                            "text": incoming_request['post']['username'],

                        },
                    {
                            "type": "plain_text",
                            "text": incoming_request['post']['category_slug'],

                        }
                ]
            },
            {
                "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": incoming_request['post']['raw'],
                        },
                "accessory": {
                            "type": "button",
                            "text": {
                                    "type": "plain_text",
                                    "text": "Go to Topic"
                            },
                            "value": "click_me_123",
                            "url": f"https://discourse.hive13.org/t/{incoming_request['post']['topic_id']}",
                            "action_id": "button"
                        }
            }
        ]
    }
    res = r.post(url, json=data)

    if res.status_code != 200:
        logging.error('Error posting message', json.dumps(incoming_request))
        return 'Error'
    else:
        logging.debug(json.dumps(incoming_request))
        return 'Success'


@app.route('/', methods=['GET'])
def home_route_get():
    return 'you meant to make a post request huh'


if __name__ == '__main__':

    # set host equal to machine IP, and specify a port
    app.run(host='0.0.0.0', port=42069)
