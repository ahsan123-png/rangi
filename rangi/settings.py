import os
from dotenv import load_dotenv
from pathlib import Path
SITE_ID = 1
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-*9l4#897#vrk3j+_%ti)(z@)008nz*##p@)+2!(pwj=v%e^tla'
DEBUG = True #True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'customer',
    'serviceProvider',
    'adminsView',
    'userEx',
    'payments',
    'corsheaders',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',



]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    
]
ROOT_URLCONF = 'rangi.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = (
    BASE_DIR / "rangi" / "static",
)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5*10485760

MEDIA_ROOT =  BASE_DIR / 'media'
MEDIA_URL = '/media/'
WSGI_APPLICATION = 'rangi.wsgi.application'

#Local database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# production database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '3306',  # Default MySQL port
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://thefixit4u.com", 
    "http://thefixit4u.com",
    "https://51.20.63.119",
]
CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'x-csrftoken',
    'accept',
    'origin',
    'user-agent',
]
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']

#Email varifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'gtxm1306.siteground.biz'
EMAIL_PORT = 465 
EMAIL_USE_SSL = True 
EMAIL_HOST_USER = 'support@api.thefixit4u.com' 
EMAIL_HOST_PASSWORD = '3N@e@nB5@1'
DEFAULT_FROM_EMAIL = 'support@api.thefixit4u.com'  


ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'

DEFAULT_FROM_EMAIL = 'support@api.thefixit4u.com'
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[TheFixIt4U] '
FRONTEND_URL = 'https://thefixit4u.com'
STRIPE_SECRET_KEY="sk_test_51QDoJ4Akxpr7eq0awwN9ciyCPgPjVA1KVTlgRzjmI1ywii5IfrCO85nKprZH6gqUFmtK0aMo7nmMk8HZILHsPsRV00SEYPfLtl"
STRIPE_PUBLIC_KEY="pk_test_51QDoJ4Akxpr7eq0aRNIdRJGByHFSTELl57c58EVMHHSFTbgbvHijuO8VDfpP5V1dFqq6PWFb2iAmlhqAmjUlgas500D0X5o2s0"