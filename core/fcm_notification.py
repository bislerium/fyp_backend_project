import json

import requests

from core.enums import ENotificationChannel
from core.enums import EPostType

URL = "https://fcm.googleapis.com/fcm/send"
TOPIC = '/topics/post'
CHANNEL_ID = 'post_channel'
LEGACY_SERVER_KEY = 'key=AAAA6-pcyjI:APA91bHWpegtlR-Ysp5if62ftl8tuL4GUoZ8' \
                    '-3x3NK__ssXSY8BuLBYGruYJIywLgAADv_4X0eB5tXHxSC15hJ2l4wn7gujbLM' \
                    '-aW9KP7iAiECPV2LA4xMOHqGtMnmog_JH1y8RhTeNG '
PRIORITY = 'high'

headers = {
    'Authorization': LEGACY_SERVER_KEY,
    'Content-Type': 'application/json'
}


def send_notification(title: str, body: str, notification_for: id, channel: ENotificationChannel,
                      post_type: EPostType | None, post_id: str | None):
    print('wowowwo')
    payload = json.dumps({
        "to": TOPIC,
        "notification": {
            "title": title,
            "body": body,
            "android_channel_id": CHANNEL_ID
        },
        "priority": PRIORITY,
        "data": {
            "account_id": notification_for,
            "channel": channel.name,
            "post_type": None if post_type is None else post_type.name.lower(),
            "post_id": post_id
        },
    })

    response = requests.request("POST", URL, headers=headers, data=payload, timeout=5)
    print('Notification sent status =>', response.status_code)
