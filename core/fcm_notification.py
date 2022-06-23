import json

import requests

from core.enums import ENotificationChannel
from core.enums import EPostType

URL = "https://fcm.googleapis.com/fcm/send"
TOPIC = '/topics/post'
CHANNEL_ID = 'post_channel'
LEGACY_SERVER_KEY = 'key=AAAAHlsVPwQ:APA91bGrKvS9rAXhg5BqbLrfTlXxZ5fq1drWW4QxV_12IAoPhzf67tXksgOoTP6zI' \
                    '-DNGE63jlT98PGCRlRwGgWhyomUimh-PZvODVPwT8qFkW7LmXMpl5qsP2jtH0RAh_YY2JHDsuQi'
PRIORITY = 'high'

headers = {
    'Authorization': LEGACY_SERVER_KEY,
    'Content-Type': 'application/json'
}


def send_notification(title: str, body: str, notification_for: id, channel: ENotificationChannel,
                      post_type: EPostType | None, post_id: str | None):
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
