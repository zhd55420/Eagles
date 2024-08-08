import os
from logging.handlers import TimedRotatingFileHandler

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import logging
from .forms import HostnameUpdateForm
from .utils.utils import update_zabbix_hostname, update_telegraf_host

logger = logging.getLogger('hostname_updater')

def configure_logging():
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'hostname_updater.log'),
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(logging.DEBUG)

    logger = logging.getLogger('hostname_updater')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


configure_logging()

def update_hostname(request):
    success_messages = []
    error_messages = []
    zabbix_servers = [(key, f"{key.replace('_', ' ').title()} Server") for key in settings.ZABBIX_CONFIG.keys()]

    if request.method == 'POST':
        form = HostnameUpdateForm(request.POST)
        form.fields['zabbix_server'].choices = zabbix_servers
        if form.is_valid():
            single_ip_address = form.cleaned_data['single_ip_address']
            single_new_hostname = form.cleaned_data['single_new_hostname']
            bulk_input = form.cleaned_data['bulk_input']
            zabbix_server = form.cleaned_data['zabbix_server']


            # 处理单个IP和主机名更新
            if single_ip_address and single_new_hostname:
                result = update_zabbix_hostname(single_ip_address, single_new_hostname, zabbix_server)
                if result:
                    update_telegraf_host(single_ip_address, single_new_hostname)
                    message = f"Successfully updated hostname for {single_ip_address} to {single_new_hostname}."
                    success_messages.append(message)
                    logger.info(message)
                else:
                    message = f"Failed to update hostname for {single_ip_address}."
                    error_messages.append(message)
                    logger.error(message)

            # 处理批量IP和主机名更新
            if bulk_input:
                bulk_lines = bulk_input.splitlines()
                for line in bulk_lines:
                    try:
                        ip_address, new_hostname = map(str.strip, line.split(','))
                        result = update_zabbix_hostname(ip_address, new_hostname, zabbix_server)
                        if result:
                            update_telegraf_host(ip_address, new_hostname)
                            message = f"Successfully updated hostname for {ip_address} to {new_hostname}."
                            success_messages.append(message)
                            logger.info(message)
                        else:
                            message = f"Failed to update hostname for {ip_address}."
                            error_messages.append(message)
                            logger.error(message)
                    except Exception as e:
                        message = f"Error processing line '{line}': {str(e)}"
                        error_messages.append(message)
                        logger.error(message)

    else:
        form = HostnameUpdateForm()
        form.fields['zabbix_server'].choices = zabbix_servers

    context = {
        'form': form,
        'success_messages': success_messages,
        'error_messages': error_messages,
        'zabbix_servers': zabbix_servers,
    }

    return render(request, 'hostname_updater/update_hostname.html', context)
