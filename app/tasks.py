'''
    Should contain only Task methods.
    avoid having any utility functions inside this file.
    Please do not corrupt/pollute this file with unncessary imports, or functions
'''

from .views import *
from distutils.log import error
from .models import *
from .serializers import *
from celery.utils.log import get_task_logger
from celery import Celery

logger = get_task_logger(__name__)
app = Celery()