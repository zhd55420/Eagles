import os
from logging.handlers import TimedRotatingFileHandler
import yaml
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse,HttpResponseRedirect
import logging
from .forms import HostnameUpdateForm,ResourceGroupForm, PRTForm, TrackerForm,ZabbixDeleteForm
from .utils.utils import update_zabbix_hostname, update_telegraf_host, get_zabbix_connection, get_zabbix_host_id
from django.contrib import messages
# 配置 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Eagles.settings')

logger = logging.getLogger('hostname_updater')

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
                        print(result)
                        if result:
                            telegraf_result = update_telegraf_host(ip_address, new_hostname)
                            message = f"Successfully updated hostname for {ip_address} to {new_hostname}."
                            success_messages.append(message)
                            success_messages.append(telegraf_result['message']) if telegraf_result[
                                'success'] else error_messages.append(telegraf_result['message'])
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


# 获取项目根目录
BASE_DIR = settings.BASE_DIR

# 拼接出 resource_groups.yaml 的路径
RESOURCE_GROUPS_YAML_PATH = os.path.join(BASE_DIR, 'myapp', 'Configs', 'resource_groups.yaml')

def load_resource_groups():
    with open(RESOURCE_GROUPS_YAML_PATH, 'r') as file:
        data = yaml.safe_load(file)
        return data.get('resource_groups', {})

def save_resource_groups(data):
    with open(RESOURCE_GROUPS_YAML_PATH, 'w') as file:
        yaml.safe_dump({'resource_groups': data}, file)


def manage_resources(request):
    messages = []
    resource_groups = load_resource_groups()
    selected_group = None
    prts = []
    trackers = []

    if request.method == 'POST':
        if 'select_group' in request.POST:
            selected_group = request.POST.get('group_name')
            if selected_group:
                prts = resource_groups[selected_group]['prt']
                trackers = resource_groups[selected_group]['trackers']

        elif 'submit_group' in request.POST:
            group_form = ResourceGroupForm(request.POST)
            if group_form.is_valid():
                action = group_form.cleaned_data['action']
                group_name = group_form.cleaned_data['group_name']
                if action == 'add':
                    if group_name in resource_groups:
                        messages.append(f"⚠️ Resource group '{group_name}' already exists.")

                    else:
                        resource_groups[group_name] = {'prt': [], 'tracker': []}
                        messages.append(f"✅ Resource group '{group_name}' added.")
                elif action == 'delete':
                    if group_name in resource_groups:
                        del resource_groups[group_name]
                        messages.append(f"❌ Resource group '{group_name}' deleted.")
                    else:
                        messages.append(f"⚠️ Resource group '{group_name}' does not exist.")
                save_resource_groups(resource_groups)

        elif 'submit_prt' in request.POST:
            prt_form = PRTForm(request.POST, resource_groups=resource_groups.keys())
            if prt_form.is_valid():
                action = prt_form.cleaned_data['action']
                group_name = prt_form.cleaned_data['group_name']
                prt_value = prt_form.cleaned_data['prt_value']
                if action == 'add':
                    if prt_value in resource_groups[group_name]['prt']:
                        messages.append(f"⚠️ PRT '{prt_value}' already exists in '{group_name}'.")
                        logger.error(messages)
                    else:
                        resource_groups[group_name]['prt'].append(prt_value)
                        messages.append(f"✅ PRT '{prt_value}' added to '{group_name}'.")
                        logger.error(messages)
                elif action == 'delete':
                    if prt_value in resource_groups[group_name]['prt']:
                        resource_groups[group_name]['prt'].remove(prt_value)
                        messages.append(f"❌ PRT '{prt_value}' deleted from '{group_name}'.")
                        logger.error(messages)
                    else:
                        messages.append(f"⚠️ PRT '{prt_value}' does not exist in '{group_name}'.")
                        logger.error(messages)
                save_resource_groups(resource_groups)
            else:
                print(prt_form.errors)

        elif 'submit_tracker' in request.POST:
            tracker_form = TrackerForm(request.POST, resource_groups=resource_groups.keys())
            if tracker_form.is_valid():
                action = tracker_form.cleaned_data['action']
                group_name = tracker_form.cleaned_data['group_name']
                tracker_value = tracker_form.cleaned_data['tracker_value']
                if action == 'add':
                    if tracker_value in resource_groups[group_name]['trackers']:
                        messages.append(f"⚠️ Tracker '{tracker_value}' already exists in '{group_name}'.")
                        logger.error(messages)
                    else:
                        resource_groups[group_name]['trackers'].append(tracker_value)
                        messages.append(f"✅ Tracker '{tracker_value}' added to '{group_name}'.")
                        logger.error(messages)
                elif action == 'delete':
                    if tracker_value in resource_groups[group_name]['trackers']:
                        resource_groups[group_name]['trackers'].remove(tracker_value)
                        messages.append(f"❌ Tracker '{tracker_value}' deleted from '{group_name}'.")
                        logger.error(messages)
                    else:
                        messages.append(f"⚠️ Tracker '{tracker_value}' does not exist in '{group_name}'.")
                        logger.error(messages)
                save_resource_groups(resource_groups)

    group_form = ResourceGroupForm()
    prt_form = PRTForm(resource_groups=resource_groups.keys())
    tracker_form = TrackerForm(resource_groups=resource_groups.keys())

    return render(request, 'hostname_updater/manage_resources.html', {
        'group_form': group_form,
        'prt_form': prt_form,
        'tracker_form': tracker_form,
        'messages': messages,
        'resource_groups': resource_groups,
        'selected_group': selected_group,
        'prts': prts,
        'trackers': trackers,
    })


def zabbix_delete(request):
    success_messages = []
    error_messages = []
    zabbix_servers = [(key, f"{key.replace('_', ' ').title()} Server") for key in settings.ZABBIX_CONFIG.keys()]

    if request.method == 'POST':
        form = ZabbixDeleteForm(request.POST)
        form.fields['zabbix_server'].choices = zabbix_servers

        if form.is_valid():
            server_name = form.cleaned_data['zabbix_server']
            ip_addresses = form.cleaned_data['ip_addresses'].splitlines()

            for ip_address in ip_addresses:
                ip_address = ip_address.strip()
                if not ip_address:
                    continue

                try:
                    zapi = get_zabbix_connection(server_name)
                    host_id = get_zabbix_host_id(zapi, ip_address)

                    if host_id:
                        zapi.host.delete(host_id)  # 确保传递的 `host_id` 是一个列表
                        message = f"Successfully deleted monitoring for IP: {ip_address} on {server_name}"
                        messages.success(request, message)
                        success_messages.append(message)
                    else:
                        message = f"No monitoring found for IP: {ip_address} on {server_name}"
                        messages.warning(request, message)
                        error_messages.append(message)

                except Exception as e:
                    message = f"Failed to delete monitoring for IP: {ip_address} on {server_name}. Error: {str(e)}"
                    messages.error(request, message)
                    error_messages.append(message)


    else:
        form = ZabbixDeleteForm()
        form.fields['zabbix_server'].choices = zabbix_servers

    context = {
        'form': form,
        'success_messages': success_messages,
        'error_messages': error_messages,
        'zabbix_servers': zabbix_servers,
    }

    return render(request, 'hostname_updater/zabbix_delete.html', context)

