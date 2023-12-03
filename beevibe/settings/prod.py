import os
import dj_database_url
from .common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['beevibe-prod.herokuapp.com','beevibe-prod-7815d8f510b2.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config()
}