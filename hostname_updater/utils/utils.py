# utils.py
from pyzabbix import ZabbixAPI
from django.conf import settings
import paramiko
import logging

logger = logging.getLogger('hostname_updater')

def get_zabbix_connection(server_name):
    server_config = settings.ZABBIX_CONFIG.get(server_name)
    if not server_config:
        raise ValueError(f"Unknown Zabbix server: {server_name}")

    zapi = ZabbixAPI(url=server_config['API_URL'],user=server_config['API_USER'],password=server_config['API_PASSWORD'])
    return zapi

def update_zabbix_hostname(ip_address, new_hostname, server_name):
    zapi = get_zabbix_connection(server_name)
    host_id = get_zabbix_host_id(ip_address, zapi)
    if host_id:
        zapi.host.update(
            hostid=host_id,
            host=new_hostname,
            name=new_hostname
        )
        return True
    return False

def get_zabbix_host_id(ip_address, zapi):
    result = zapi.host.get(filter={"ip": ip_address}, output=['hostid'])
    return result[0]['hostid'] if result else None

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
        stderr_text = stderr.read().decode()

        if stderr_text:
            raise Exception(f"Error modifying Telegraf config: {stderr_text}")

        # 重启 Telegraf 服务
        stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart telegraf')
        stderr_text = stderr.read().decode()

        if stderr_text:
            raise Exception(f"Error restarting Telegraf: {stderr_text}")

        # 更新 Zabbix Agent 配置
        update_zabbix_command = f'sudo sed -i \'s/^Hostname=.*/Hostname={new_hostname}/\' /etc/zabbix/zabbix_agentd.conf'
        stdin, stdout, stderr = ssh.exec_command(update_zabbix_command)
        stderr_text = stderr.read().decode()

        if stderr_text:
            raise Exception(f"Error modifying Zabbix Agent config: {stderr_text}")

        # 重启 Zabbix Agent 服务
        stdin, stdout, stderr = ssh.exec_command('sudo systemctl restart zabbix-agent')
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

def get_zabbix_host_id(zapi, ip_address):
    result = zapi.host.get(filter={"ip": ip_address})
    return result[0]['hostid'] if result else None
