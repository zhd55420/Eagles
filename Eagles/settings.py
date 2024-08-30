"""
Django settings for Eagles project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from myapp.Utils.send_to_lark import send_message_to_optlark, send_message_to_spclark

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gavpr0hkm(i$0zxl$*ze^+a%jh*u$b*kvf-+!iugdt*8!$3rv1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'myapp',
    'hostname_updater',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = '/static/'

# 静态文件目录
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 设置 STATIC_ROOT 用于 collectstatic 命令
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


# settings.py 文件中添加新的定时任务
CRONJOBS = [
    ('*/30 * * * *', 'myapp.cron.run_opt_job_users_and_bw'),
    ('*/30 0-11 * * *', 'myapp.cron.run_spc_job_users_and_bw'),
    ('*/30 0-11 * * *', 'myapp.cron.run_resource_group_job'),
    ('*/30 0-11 * * *', 'myapp.cron.run_vod_job_users_and_bw'),
    ('*/2 * * * *', 'myapp.cron.send_data_to_live_zabbix'),
    ('*/2 * * * *', 'myapp.cron.send_data_to_vod_zabbix'),
    ('*/1 * * * *', 'myapp.cron.send_stream_status_influxdb'),
]
# 日志文件夹路径
# 定义你的日志目录
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 定义需要创建的子目录（即各个 app 的日志目录）
log_subdirs = ['hostname_updater', 'myapp']


# 确保日志目录和子目录存在
def ensure_log_dirs():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    for subdir in log_subdirs:
        subdir_path = os.path.join(LOG_DIR, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)


# 调用函数创建日志目录结构
ensure_log_dirs()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'django': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'app.log'),
            'when': 'midnight',
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'hostname_updater': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR,  'hostname_updater','webrequest.log'),
            'when': 'midnight',
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'streamstatus': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'myapp', 'streamstatus.log'),
            'when': 'midnight',
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'influxdb_query': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'myapp', 'influxdb_query_error.log'),
            'when': 'midnight',
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'bw_user': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'myapp','bw_user_logger.log'),
            'when': 'midnight',
            'backupCount': 7,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
    },
    'root': {
        'handlers': ['django'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['django'],
            'level': 'DEBUG',
            'propagate': False,  # 阻止向上传播到root logger
        },
        'influxdb_query_error': {
            'handlers': ['influxdb_query'],
            'level': 'DEBUG',
            'propagate': False,  # 阻止向上传播到root logger
        },
        'bandwidth_logger': {
            'handlers': ['bw_user'],
            'level': 'DEBUG',
            'propagate': False,  # 阻止向上传播到root logger
        },
        'hostname_updater': {
            'handlers': ['hostname_updater'],
            'level': 'DEBUG',
            'propagate': False,  # 阻止向上传播到root logger
        },
        'streamstatus': {
            'handlers': ['streamstatus'],
            'level': 'DEBUG',
            'propagate': False,  # 阻止向上传播到root logger
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'Eagles.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'Eagles.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# LIVE InfluxDB configurations
LIVE_INFLUXDB_CONFIG = {
    'HOST': '15.204.133.239',
    'PORT': 8086,
    'DATABASE': 'livetv',
    'USERNAME': 'reader',  # 如果需要s
    'PASSWORD': 'By@Zs7XK',  # 如果需要
}
# VOD InfluxDB configurations
VOD_INFLUXDB_CONFIG = {
    'HOST': '15.204.133.239',
    'PORT': 8086,
    'DATABASE': 'mdb',
    'USERNAME': 'reader',  # 如果需要s
    'PASSWORD': 'By@Zs7XK',  # 如果需要
}

# Zabbix configurations
ZABBIX_CONFIG = {
    'livetv_01': {
        'IP': '135.148.52.229',
        'PORT': 10051,
        'API_URL': 'http://135.148.52.229:8080/api_jsonrpc.php',
        'API_USER': 'valor',
        'API_PASSWORD': 'optnet!c47dff'
    },
    'livetv_02': {
        'IP': '51.81.49.118',
        'PORT': 10051,
        'API_URL': 'http://51.81.49.118:8080/api_jsonrpc.php',
        'API_USER': 'valor',
        'API_PASSWORD': 'optnet!c47dff'
    },
    'vod_01': {
        'IP': '135.148.53.180',
        'PORT': 10051,
        'API_URL': 'http://135.148.53.180:8080/api_jsonrpc.php',
        'API_USER': 'valor',
        'API_PASSWORD': 'optnet!c47dff'
    },
    'vod_02': {
        'IP': '51.81.49.196',
        'PORT': 10051,
        'API_URL': 'http://51.81.49.196:8080/api_jsonrpc.php',
        'API_USER': 'valor',
        'API_PASSWORD': 'optnet!c47dff'
    },
    'goose_01': {
        'IP': '51.81.49.196',
        'PORT': 10051,
        'API_URL': 'http://15.204.208.231/zabbix/api_jsonrpc.php',
        'API_USER': 'valor',
        'API_PASSWORD': '#A1H$eIvN2G9,0+9'
    },
}


opt_LARK_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/96c73090-2a31-4a6c-9721-c5c291c7777c'
spc_LARK_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/9b4a8d03-8db4-4e2a-903d-459de038b814'
stream_LARK_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/ae5e8462-4127-408e-a16e-49d0b709a192'
VOD_LARK_WEBHOOK_URL = 'https://open.larksuite.com/open-apis/bot/v2/hook/9c105fac-287b-44cd-96d6-9d41b3c8cb15'

