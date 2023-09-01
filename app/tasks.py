'''
    Should contain only Task methods.
    avoid having any utility functions inside this file.
    Please do not corrupt/pollute this file with unncessary imports, or functions
'''

import os
from .models import Notification, CustomToken, FoodEvent, STATUS
from celery import Celery, shared_task
from celery.utils.log import get_task_logger
from exponent_server_sdk import PushClient, PushMessage 
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
import logging

logger = get_task_logger(__name__)
app = Celery()

def send_push_message(user, title, message, notification_type):
    try:
        Notification.objects.create(user=user, title=title, message=message, notificationType=notification_type)
        
        if CustomToken.objects.filter(user=user).exists():
            custom_token = CustomToken.objects.get(user=user)

            try:
                PushClient().publish(
                    PushMessage(
                        to=custom_token.expoPushToken,
                        title=title,
                        body=message,
                    )
                )
            except Exception as e:
                print('==========>',str(e))
        else:
            print('Custom Token for user not exists') 
    except Exception as e:
        print('Cant Send MSG', str(e))

@shared_task(name='checking_event_status')
def event_status_check():
    try:
        today_date = timezone.now()
        active_food_events_list = FoodEvent.objects.filter(Q(eventStartDate__lte=today_date) & Q(eventEndDate__gte=today_date), active=False)
        for food_events in active_food_events_list:
            food_events.active = True
            food_events.save()
        expired_food_events_list = FoodEvent.objects.filter(Q(eventStartDate__gt=today_date) | Q(eventEndDate__lt=today_date), active=True)
        for food_events in expired_food_events_list:
            food_events.active = False
            food_events.save()
        return ({'success': True, 'message': 'Message is sent'})
    except Exception as e:
        return ({'success': False, 'message': str(e)})

@shared_task(name='pending_events_email')
def pending_events_reminder():
    try:
        pending_event_list = FoodEvent.objects.filter(status=STATUS[2][0]).order_by('-eventStartDate')[:5]
        detailslist = []
        for pending_events in pending_event_list:
            jobdetailscard = open(os.path.join(settings.PROJECT_DIR,'emailTemplates/EventDetailsCard.txt')).read()
            details = jobdetailscard.replace('{{event_name}}',str(pending_events.name)).replace('{{event_food}}',str(pending_events.additionalInfo)).replace('{{event_location}}', str(pending_events.address)).replace('{{event_date}}',str(pending_events.eventStartDate.date())).replace('{{event_time}}',str(pending_events.eventStartDate.time())).replace('{{event_organizer}}', str(pending_events.createdBy.name))
            detailslist.append(details) 
        emaildetailstext = open(os.path.join(settings.PROJECT_DIR,'emailTemplates/emaildetails.html'), mode = 'w')
        emaildetailstext.writelines(detailslist)
        emaildetailstext.close()            
        htmlstring = open(os.path.join(settings.PROJECT_DIR,'emailTemplates/emaildetails.html')).read()
        subject = f'Approval Pending for New Food Events'

        email_from = settings.DEFAULT_SENDER
        recipient_list = ['srao@climatehealers.org','climatehealers@climatehealers.org']

        finalhtmlcontent = open(os.path.join(settings.PROJECT_DIR,'emailTemplates/PendingEventsNotification.html')).read()
        email_text = finalhtmlcontent.replace('{{base_url}}', settings.PRODUCTION_URL).replace('{{details}}', htmlstring)
        try:
            msg = EmailMultiAlternatives(subject=subject, body=email_text, from_email=email_from, to=recipient_list)
            msg.attach_alternative(email_text, "text/html")
            msg.send()
            return ({'success': True, 'message': 'Message is sent'})
        except Exception as e:
            return ({'success': False,  'error': str(e)})

    except Exception as e:
        return ({'success': False, 'error': str(e)})
