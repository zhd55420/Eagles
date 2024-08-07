import os
from logging.handlers import TimedRotatingFileHandler

from django.shortcuts import render
from django.http import HttpResponse
import requests
import paramiko

import logging
from .forms import HostnameUpdateForm

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

ZABBIX_API_URL = 'http://135.148.52.229:8080/api_jsonrpc.php'
ZABBIX_API_USER = 'valor'
ZABBIX_API_PASSWORD = 'optnet!c47dff'

def update_hostname(request):
    if request.method == 'POST':
        form = HostnameUpdateForm(request.POST)
        if form.is_valid():
            single_ip_address = form.cleaned_data['single_ip_address']
            single_new_hostname = form.cleaned_data['single_new_hostname']
            bulk_input = form.cleaned_data['bulk_input']

            messages = []

            # 处理单个IP和主机名更新
            if single_ip_address and single_new_hostname:
                result = update_zabbix_host(single_ip_address, single_new_hostname)
                if result:
                    update_telegraf_host(single_ip_address, single_new_hostname)
                    message = f"Successfully updated hostname for {single_ip_address} to {single_new_hostname}."
                    logger.info(message)
                else:
                    message = f"Failed to update hostname for {single_ip_address}."
                    logger.error(message)
                messages.append(message)

            # 处理批量IP和主机名更新
            if bulk_input:
                bulk_lines = bulk_input.splitlines()
                for line in bulk_lines:
                    try:
                        ip_address, new_hostname = map(str.strip, line.split(','))
                        result = update_zabbix_host(ip_address, new_hostname)
                        if result:
                            update_telegraf_host(ip_address, new_hostname)
                            message = f"Successfully updated hostname for {ip_address} to {new_hostname}."
                            logger.info(message)
                        else:
                            message = f"Failed to update hostname for {ip_address}."
                            logger.error(message)
                    except Exception as e:
                        message = f"Error processing line '{line}': {str(e)}"
                        logger.error(message)
                    messages.append(message)

            return HttpResponse("<br>".join(messages))
    else:
        form = HostnameUpdateForm()

    return render(request, 'hostname_updater/update_hostname.html', {'form': form})

def update_zabbix_host(ip_address, new_hostname):
    host_id = get_zabbix_host_id(ip_address)
    if host_id:
        payload = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": host_id,
                "host": new_hostname,
                "name": new_hostname
            },
            "auth": get_zabbix_auth_token(),
            "id": 1
        }
        response = requests.post(ZABBIX_API_URL, json=payload)
        return response.json()
    return None

def get_zabbix_host_id(ip_address):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid"],
            "filter": {
                "ip": ip_address
            }
        },
        "auth": get_zabbix_auth_token(),
        "id": 1
    }
    response = requests.post(ZABBIX_API_URL, json=payload)
    result = response.json().get('result', [])
    return result[0]['hostid'] if result else None

def get_zabbix_auth_token():
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": ZABBIX_API_USER,
            "password": ZABBIX_API_PASSWORD
        },
        "id": 1
    }
    response = requests.post(ZABBIX_API_URL, json=payload)
    return response.json().get('result')


def update_telegraf_host(ip_address, new_hostname):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 尝试使用默认端口22连接
        try:
            ssh.connect(ip_address, port=22, username='optuser', password='MvRun1XrIve1MgFqs#gaxcoDdJ8FNj6jmY8p%Igg', timeout=30)
            logger.info(f"Connected to {ip_address} on port 22")
        except Exception as e:
            logger.warning(f"Failed to connect to {ip_address} on port 22: {str(e)}. Trying port 28822...")
            # 尝试使用备用端口28822连接
            ssh.connect(ip_address, port=28822, username='optuser', password='MvRun1XrIve1MgFqs#gaxcoDdJ8FNj6jmY8p%Igg', timeout=30)
            logger.info(f"Connected to {ip_address} on port 28822")

        # 更新 Telegraf 配置
        update_telegraf_command = f'sudo sed -i \'s/^  hostname = .*/  hostname = "{new_hostname}"/\' /etc/telegraf/telegraf.conf'
        stdin, stdout, stderr = ssh.exec_command(update_telegraf_command)
        stdout_text = stdout.read().decode()
        stderr_text = stderr.read().decode()

        if stderr_text:
            raise Exception(f"Error modifying Telegraf config: {stderr_text}")

        # 重启 Telegraf 服务
        stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart telegraf')
        stdout_text = stdout.read().decode()
        stderr_text = stderr.read().decode()

        if stderr_text:
            raise Exception(f"Error restarting Telegraf: {stderr_text}")

        # 更新 Zabbix Agent 配置
#        update_zabbix_command = f'sudo sed -i "s/^Hostname=.*/Hostname={new_hostname}/" /etc/zabbix/zabbix_agentd.conf'
        update_zabbix_command = f'sudo sed -i \'s/^Hostname=.*/Hostname={new_hostname}/\' /etc/zabbix/zabbix_agentd.conf'
        stdin, stdout, stderr = ssh.exec_command(update_zabbix_command)
        stdout_text = stdout.read().decode()
        stderr_text = stderr.read().decode()

        if stderr_text:
            raise Exception(f"Error modifying Zabbix Agent config: {stderr_text}")

        # 重启 Zabbix Agent 服务
        stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart zabbix-agent')
        stdout_text = stdout.read().decode()
        stderr_text = stderr.read().decode()

        if stderr_text:
            raise Exception(f"Error restarting Zabbix Agent: {stderr_text}")

        ssh.close()
        logger.info(f"Successfully updated Telegraf and Zabbix Agent hostname for {ip_address} to {new_hostname}.")
    except paramiko.AuthenticationException:
        logger.error(f"Authentication failed when connecting to {ip_address}")
    except paramiko.SSHException as sshException:
        logger.error(f"Unable to establish SSH connection to {ip_address}: {str(sshException)}")
    except paramiko.BadHostKeyException as badHostKeyException:
        logger.error(f"Unable to verify server's host key for {ip_address}: {str(badHostKeyException)}")
    except Exception as e:
        logger.error(
            f"Failed to update Telegraf and Zabbix Agent hostname for {ip_address} to {new_hostname}. Error: {str(e)}",
            exc_info=True)

