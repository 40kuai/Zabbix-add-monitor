#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import settings
class Zabbix:
    def __init__(self,url):
        self.url = url
        self.header = {"Content-Type": "application/json"}
        self.auth = self.zabbix_login()
    def zabbix_login(self):
        # 通过配置文件信息登录获取auth，认证成功返回true
        data = json.dumps( {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user":"%(user)s"%{"user":settings.username},
                "password":"%(password)s"%{"password":settings.password},
            },
            "id": 1,
            "auth": None
        })
        auth_key = self.get_data(data)["result"]
        return auth_key

    def get_data(self,data):
        '''专门向zabbix api发送请求'''
        header ={"Content-Type": "application/json"}
        ret = requests.post(self.url,data=data,headers=header)
        return json.loads(ret.text)

    def hostgroup_get(self):
        '''返回zabbix的项目组信息'''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": [
                    "groupid",
                    "name"
                ],
            },
            "id": 1,
            "auth": "{auth}".format(auth=self.auth)
        })
        return self.get_data(data)

    def tempaltes_get(self):
        '''获取默认模板的信息'''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": [
                    "templateid"
                ],
                "filter":{
                    "name":["Basis"]
                }
            },
            "id": 1,
            "auth": "{auth}".format(auth=self.auth)
        })
        return self.get_data(data)

    def host_create(self,host,ip,group,templateid):
        '''添加监控'''
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": "{host}".format(host=host),
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": "{ip}".format(ip=ip),
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": [
                    {
                        "groupid": "{group}".format(group=group)
                    }
                ],
                "templates": [
                    {
                        "templateid": "{templateid}".format(templateid=templateid)
                    }
                ],
            },
            "auth": "{auth}".format(auth=self.auth),
            "id": 1
        })
        return self.get_data(data)
class Action_zabbix:
    def __init__(self):
        self.zabbix = Zabbix(settings.zabbix_api)
    def add_monitor(self):
        group_list = self.zabbix.hostgroup_get()["result"]
        group_id_list =[]
        print(group_list)
        for group_info in group_list:
            print(group_info["groupid"],'\t',group_info["name"])
            group_id_list.append(group_info["groupid"])
        while True:         # 用户输入项目组ID
            group_id = input("请输入添加项目的id:")
            if group_id in group_id_list:
                break
            else:
                pass
        tempaltes_id = self.zabbix.tempaltes_get()["result"][0]["templateid"]
        with open("ipaddr",'r') as ip_host:
            for line in ip_host:
                host = line.split(":")[0]
                ip = line.split(":")[1]
                ret = self.zabbix.host_create(host,ip,group_id,tempaltes_id)
                if ret.get("result"):
                    print("add right ",host)
                else:
                    print('error')

if __name__ == '__main__':
    action=Action_zabbix()
    action.add_monitor()
