from channels import Channel
import json


def ws_connect(message):
    global rc
    rc = message.reply_channel.name
    print(rc)
    message.reply_channel.send({
        'text': json.dumps({
            'msg': u"websocket connection established.",
            'action': 'connect'
        })
    })


def push_message(message):
    print('Triggered by push request ' + str(message['pushkey']) + '.')
    print('Sending message on ' + rc + '.')
    Channel(rc).send({
        'text': json.dumps({
            'msg': u"websocket message sent.",
            'action': 'push_qrcode'
        })
    })
    print('Message sent on ' + rc + '.')
