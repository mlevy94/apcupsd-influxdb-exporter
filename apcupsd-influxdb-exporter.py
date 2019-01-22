#!/usr/bin/python
import os
import time

from apcaccess import status as apc
from influxdb import InfluxDBClient

HOSTNAME = os.getenv('HOSTNAME', 'apcupsd-influxdb-exporter')
dbname = os.getenv('INFLUXDB_DATABASE', 'apcupsd')
user = os.getenv('INFLUXDB_USER', '')
password = os.getenv('INFLUXDB_PASSWORD', '')
port = os.getenv('INFLUXDB_PORT', 8086)
host = os.getenv('INFLUXDB_HOST', 'localhost')
client = InfluxDBClient(host, port, user, password, dbname)

client.create_database(dbname)

while True:
    ups = apc.parse(apc.get(host=os.getenv('APCUPSD_HOST', 'localhost')), strip_units=True)

    if os.environ['WATTS']:
        ups['NOMPOWER'] = os.environ['WATTS']

    watts = float(float(ups['NOMPOWER']) * float(0.01 * float(ups['LOADPCT'])))
    json_body = [
        {
            'measurement': 'APC-NEW',
            'fields': {
                'WATTS': float(watts),
                'LOADPCT': float(ups['LOADPCT']),
                'BCHARGE': float(ups['BCHARGE']),
                'TONBATT': float(ups['TONBATT']),
                'TIMELEFT': float(ups['TIMELEFT']),
                'NOMPOWER': float(ups['NOMPOWER']),
                'CUMONBATT': float(ups['CUMONBATT']),
                'BATTV': float(ups['BATTV']),
                'OUTPUTV': float(ups['OUTPUTV']),
                'ITEMP': float(ups['ITEMP'])
            },
            'tags': {
                'host': HOSTNAME
            }
        }
    ]
    print json_body
    print client.write_points(json_body)
    time.sleep(5)
