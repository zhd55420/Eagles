import os
import subprocess
import logging
import datetime
import json
from influxdb import InfluxDBClient
import requests
from pytz import UTC

logger = logging.getLogger('streamstatus')

def all_stream_task():
    try:
        # 这里放置 All_stream.py 的逻辑代码
        bk_url = "http://3.15.111.189:2082/api/rapidStreamStatus/query/v1"
        HEADERS = {
            "Content-Type": "application/json ;charset=utf-8 "
        }
        data_request = {
            "streamRequest": {
                "source": ""
            },
            "gooseStreamRequest": {
                "source": ""
            }
        }
        json_data = json.dumps(data_request)
        res = requests.post(bk_url, data=json_data, headers=HEADERS)
        now_time = datetime.datetime.utcnow()
        points = []
        for e in json.loads(res.text)['data']:
            masterStreamStatus = "null"
            transcodeStreamStatus = "null"
            channelReceiverStreamStatus = "null"
            bandWidth = 0
            if e['streamStatus']['masterStreamStatus'] == None:
                masterStreamStatus = False
                bandWidth = 0
            else:
                masterStreamStatus = True
                bandWidth = e['streamStatus']['masterStreamStatus']['bw']
            if e['streamStatus']['transcodeStreamStatus'] == None:
                transcodeStreamStatus = False
            else:
                transcodeStreamStatus = True
            if e['streamStatus']['channelReceiverStreamStatus'] == None:
                channelReceiverStreamStatus = False
            else:
                channelReceiverStreamStatus = True
            point = {
                "measurement": "rapid_stream_status",
                "tags": {
                    "stream_id": e['streamResponse']['streamId'],
                    "source": e['streamResponse']['source'],
                    "signalType": e['streamResponse']['signalType']
                },
                "time": now_time,
                "fields": {
                    "stream": e['streamResponse']['streamId'],
                    "masterStatus": masterStreamStatus,
                    "master_server_id": e['streamResponse']['masterServer']['serverId'],
                    "transcodeStatus": transcodeStreamStatus,
                    "forward_server_id": e['streamResponse']['forwardServer']['serverId'],
                    "receiverStatus": channelReceiverStreamStatus,
                    "bandWidth": bandWidth
                }
            }
            points.append(point)
        print(points)
        client = InfluxDBClient(host='15.204.133.239', port=8086, database='rapid_stream', username='uploader',
                                password='bja!d7BB')
        client.write_points(points, database='rapid_stream')
        client.close()
        logger.info("Running All Stream Task")
    except Exception as e:
        logger.error(f"Error in All Stream Task: {str(e)}")


def all_goose_stream_task():
    try:
        # 这里放置 All_goose_stream.py 的逻辑代码
        bk_url = "http://54.237.33.107:2082/api/rapidStreamStatus/query/v1"
        HEADERS = {
            "Content-Type": "application/json ;charset=utf-8 "
        }
        data_request = {
            "streamRequest": {
                "source": ""
            },
            "gooseStreamRequest": {
                "source": ""
            }
        }
        json_data = json.dumps(data_request)
        res = requests.post(bk_url, data=json_data, headers=HEADERS)
        now_time = datetime.datetime.utcnow()
        points = []
        for e in json.loads(res.text)['data']:
            masterStreamStatus = "null"
            transcodeStreamStatus = "null"
            channelReceiverStreamStatus = "null"
            bandWidth = 0
            if e['streamStatus']['masterStreamStatus'] == None:
                masterStreamStatus = False
                bandWidth = 0
            else:
                masterStreamStatus = True
                bandWidth = e['streamStatus']['masterStreamStatus']['bw']
            if e['streamStatus']['transcodeStreamStatus'] == None:
                transcodeStreamStatus = False
            else:
                transcodeStreamStatus = True
            if e['streamStatus']['channelReceiverStreamStatus'] == None:
                channelReceiverStreamStatus = False
            else:
                channelReceiverStreamStatus = True
            point = {
                "measurement": "goose_rapid_stream_status",
                "tags": {
                    "stream_id": e['streamResponse']['streamId'],
                    "source": e['streamResponse']['source'],
                    "signalType": e['streamResponse']['signalType']
                },
                "time": now_time,
                "fields": {
                    "stream": e['streamResponse']['streamId'],
                    "masterStatus": masterStreamStatus,
                    "master_server_id": e['streamResponse']['masterServer']['serverId'],
                    "transcodeStatus": transcodeStreamStatus,
                    "forward_server_id": e['streamResponse']['forwardServer']['serverId'],
                    "receiverStatus": channelReceiverStreamStatus,
                    "bandWidth": bandWidth
                }
            }
            points.append(point)
        print(points)
        client = InfluxDBClient(host='15.204.133.239', port=8086, database='rapid_stream', username='uploader',
                                password='bja!d7BB')
        client.write_points(points, database='rapid_stream')
        client.close()
        logger.info("Running All Goose Stream Task")
    except Exception as e:
        logger.error(f"Error in All Goose Stream Task: {str(e)}")
