# -*- coding: utf-8 -*-

import socket
import threading
#from weight_info import WeightInfo
#from user_info import UserInfo
from db_helper import DbHelper
import time
import json

HOST = '' #为空代表可用所有网卡
PORT = 50007
recv_size = 1024

'''
只是为了显示IP，仅仅测试一下
'''
def getipaddrs(hostname):
    result = socket.getaddrinfo(hostname, None, 0, socket.SOCK_STREAM)
    return [x[4][0] for x in result]

'''
初始化tcp连接和数据库连接
'''
def init_socket_sqlite():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    DbHelper.get_db_helper()
    return tcp_socket, None

'''
将体重信息转换为json格式字符串
'''
def info_list2json(_list, param):
    data = _list
    #分割,得到存有各个属性名称的列表
    names = param.split()
    '''
    1.将两个列表通过zip函数压缩
        如 [_id, weight, bmi, status, time] ,["011", 58.5, 20.3, "偏瘦", "20.."]
        合成[(_id, "011"), (weight, 58.5), (bmi,...)...]
    2.然后通过dict函数生成字典
    3.最外层套层[]生成一个列表
    '''
    data = [dict(zip(names, d)) for d in data]
    json_data = json.dumps(data, sort_keys=False, indent=4, \
            separators=(',', ': '), ensure_ascii=False)

    return json_data

'''
通讯函数
'''
def sub_comm(conn, addr):

    choice = 1

    data = conn.recv(recv_size)

    if data == bytes("2", encoding='utf-8'):
        choice = 2
    conn.sendall(bytes("==end by wth==\n", encoding='utf-8'))

    if choice == 2:
        data = conn.recv(recv_size)

        sql_user = "select * from userInfo  where Id = '{}' ".format(data.decode('utf-8'))
        sql_weight = "select * from WeightInfo where Id = '{}' order by Time".format(data.decode('utf-8'))

        res_user = DbHelper.db_query(sql_user)
        res_weight = DbHelper.db_query(sql_weight)

        param_weight = '_id weight bmi status time'
        param_user = '_id name sex height'

        str_user = info_list2json(res_user, param_user) + "\n==end by wth==\n"
        str_weight = info_list2json(res_weight, param_weight) + "\n==end by wth==\n"

        conn.sendall(bytes(str_user, encoding='utf-8'))

        data = conn.recv(recv_size) #用户确认用户是否收到第一个信息
        print(data)
        conn.sendall(bytes(str_weight, encoding='utf-8'))

    else:
        user_name = conn.recv(recv_size)
        conn.sendall(bytes("==end by wth==\n", encoding='utf-8'))
        user_pwd = conn.recv(recv_size)
        sql_is_exist = "select * from Login where Id = '{}' and Pwd = '{}'" \
            .format(user_name.decode(), user_pwd.decode())
        if DbHelper.db_is_exist_user(sql_is_exist):
            conn.sendall(bytes("true\n==end by wth==\n", encoding='utf-8'))
        else:
            conn.sendall(bytes("false\n==end by wth==\n", encoding='utf-8'))

    print("end")

    conn.close()

if __name__ == "__main__":
    #host_name = socket.gethostname()
    #print(getipaddrs(host_name))
    tcp_socket, _ = init_socket_sqlite()
    tcp_socket.bind((HOST, PORT))
    tcp_socket.listen(1) #num 最大连接数
    print(u'监听中')

    while True:
        conn, addr = tcp_socket.accept() #返回客户端的socket和ip地址
        print('Connected by', addr)
        threading.Thread(target=sub_comm, args=(conn, addr)).start()

    tcp_socket.close()
