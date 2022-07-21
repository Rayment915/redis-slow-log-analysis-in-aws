import redis
import boto3
import os,sys
import json
import time
from datetime import datetime,timedelta
import pymysql
import socket
import struct


# get system environment
AWS_REGION=os.environ['AWS_REGION']
DB_HOST=os.environ['db_host']
DB_DataBase=os.environ['db_database']
DB_PW=os.environ['db_pw']
DB_USER=os.environ['db_user']
PORT=int(os.environ['port'])


# get current time from internet
# time.time() 方式的时间不准
def RequestTimefromNtp(addr='0.de.pool.ntp.org'):
    REF_TIME_1970 = 2208988800      # Reference time
    client = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    data = b'\x1b' + 47 * b'\0'
    client.sendto( data, (addr, 123))
    data, address = client.recvfrom( 1024 )
    if data:
        t = struct.unpack( '!12I', data )[10]
        t -= REF_TIME_1970
    return t


# get redis client
def aws_client():
    client = boto3.client(
        'elasticache',
        region_name=AWS_REGION,
    )
    return client


# get all redis cluster list
def get_redis_cluster_list(client):
    clusters_metas = client.describe_cache_clusters()['CacheClusters']
    clusters = []
    for item in clusters_metas:
        clusters.append(item['ReplicationGroupId'])
    cluster_list = set(clusters)
    return cluster_list


# get each redis cluster meta data
def get_redis_meta(client,groupid):
    info={}
    response=client.describe_replication_groups(
    ReplicationGroupId=groupid)
    NodeGroupMembers=response['ReplicationGroups'][0]['NodeGroups'][0]['NodeGroupMembers']
    for item in NodeGroupMembers:
        k = item['CacheClusterId']
        v = item['ReadEndpoint']['Address']
        info[k] = v
    return info


# get slow log every 1 min  
# 本次测试环境密码为空  
def get_slow_log_info(endpoint,nodeid,date,port='',pw=''):
    now=int(RequestTimefromNtp())
    last=int(now - 60)
    r=redis.Redis(host=endpoint)
    slow_data = r.slowlog_get()
    result=[]
    for item in slow_data:
        if (item['start_time']>= last and item['start_time']<= now ):
            try:
                command_type = str(item['command']).split('\'')[1].split()[0]
            except Exception as err:
                command_type = "null"


            try:
                command_key = str(item['command']).split('\'')[1].split()[1]
            except Exception as err:
                command_key = "null"


            try:
                duration = int(item['duration'])
            except Exception as err:
                duration = 0




            data = {
                'nodeid' : nodeid,
                'endpoint' : endpoint,
                'slowlog_time' : int(item['start_time']) , 
                'today' : str(date),
                'command' : command_type,
                'key' : command_key,
                'duration' : duration,
            }
            result.append(data)
    return result


# upload data to RDS
def upload_logs(result,DB_HOST,DB_USER,DB_PW,DB_DataBase,PORT):
    db = pymysql.connect(host=DB_HOST,
        user=DB_USER,
        password=DB_PW,
        database=DB_DataBase,
        port=PORT,
        cursorclass=pymysql.cursors.DictCursor)


    cur = db.cursor()
    for item in result:
        nodeid=item['nodeid']
        endpoint=item['endpoint']
        slowlog_time=item['slowlog_time']
        today=item['today']
        command=item['command']
        redis_key=item['key']
        duration=item['duration']


        SQL = "insert into slowlog.detail (nodeid,endpoint,slowlog_time,today,command,redis_key,duration) values('%s','%s',%d,'%s','%s','%s',%d)" % \
                (nodeid,endpoint,slowlog_time,today,command,redis_key,duration)
        cur.execute(SQL)
        db.commit()
    db.close()


def lambda_handler(event, context):
    date = datetime.now().strftime("%Y-%m-%d")
    client=aws_client()
    cluster_lists=get_redis_cluster_list(client)
    for item in cluster_lists:
        info = get_redis_meta(client,item)
        for k in info.keys():
            result=[]
            result=get_slow_log_info(info[k],k,date)
            print(result)
            upload_logs(result,DB_HOST,DB_USER,DB_PW,DB_DataBase,PORT)
