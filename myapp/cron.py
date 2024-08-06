import os
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import pytz

# 配置 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Eagles.settings')

import django

django.setup()

from myapp.Utils.send_to_lark import send_message_to_optlark, send_message_to_spclark,send_message_to_streamlark,send_message_to_Vodlark
from myapp.Utils.query_bandwidth import query_and_log_bandwidth,query_and_log_tracker_users,query_and_log_resource_groups,query_and_log_vod  # 确保函数被正确导入
from myapp.Utils.send_to_zabbix import query_vod_bw_users_send_to_zabbix,query_bw_users_send_to_zabbix

# 获取日志记录器
logger = logging.getLogger('bandwidth_logger')


def configure_logging():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'bandwidth.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(logging.DEBUG)

    logger = logging.getLogger('bandwidth_logger')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


configure_logging()


def run_opt_job_users_and_bw():
    query_and_log_bandwidth("opt", send_message_to_optlark)


def run_spc_job_users_and_bw():
    query_and_log_bandwidth("spc", send_message_to_spclark)

def run_spc_tracker_job_users():
    query_and_log_tracker_users("spc", send_message_to_spclark)

def run_resource_group_job():
    query_and_log_resource_groups(send_message_to_streamlark)

def run_vod_job_users_and_bw():
    query_and_log_vod(send_message_to_Vodlark)

def send_data_to_live_zabbix():
    query_bw_users_send_to_zabbix('opt')
    query_bw_users_send_to_zabbix('spc')

def send_data_to_vod_zabbix():
    query_vod_bw_users_send_to_zabbix()



