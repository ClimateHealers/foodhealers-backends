'''
    Should contain only Task methods.
    avoid having any utility functions inside this file.
    Please do not corrupt/pollute this file with unncessary imports, or functions
'''

from .models import *
from celery import Celery
from celery.utils.log import get_task_logger
from exponent_server_sdk import PushClient, PushMessage 

logger = get_task_logger(__name__)
app = Celery()

def send_push_message(user, title, message, notificationType):
    try:
        Notification.objects.create(user=user, title=title, message=message, notificationType=notificationType)
        
        if CustomToken.objects.filter(user=user).exists():
            customToken = CustomToken.objects.get(user=user)

            try:
                print(customToken.expoPushToken)
                response = PushClient().publish(
                    PushMessage(
                        to=customToken.expoPushToken,
                        title=title,
                        body=message,
                    )
                )
                print(response)
            except Exception as e:
                print('==========>',str(e))
        else:
            print('Custom Token for user not exists') 
    except Exception as e:
        print('Cant Send MSG', str(e))
    