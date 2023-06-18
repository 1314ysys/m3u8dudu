import requests
import json
import os
from tqdm import tqdm
from urllib.parse import quote
import configparser
import datetime

#=========下面是上传配置=====================
config = configparser.ConfigParser()
config.read("./config/config.ini",encoding="utf-8")#读取本地配置文件

base_url = config.get("upload_settings", "base_url")
UserName = config.get("upload_settings", "UserName")
PassWord = config.get("upload_settings", "PassWord")
remote_path = config.get("upload_settings", "remote_path")
log_path_file = config.get("download_settings", "log_path_file")

def login():
    url = base_url + '/api/auth/login'
    d = {'Username': UserName, 'Password': PassWord}
    try:
        r = requests.post(url, data=d)
        totalmess = (r.text)
        data = json.loads(r.text)
        if data.get('code') == '200' or data.get('code') == 200:
            with open(log_path_file, 'a', encoding="utf-8") as log_file:
                log_file.write("网盘登陆成功!\n")
            token = data.get('data').get('token')
            return(token)
        else:
            with open(log_path_file, 'a', encoding="utf-8") as log_file:
                log_file.write("网盘登陆失败!请检查网盘配置和网络！\n")
                log_file.write("错误信息:%s"%totalmess)
    except Exception as e:
        with open(log_path_file, 'a', encoding="utf-8") as log_file:
            log_file.write("登录错误！请稍后再试！\n")
            log_file.writelines("错误信息:%s"%e)
        return None


def upload_alist(local_file_path, title):
    '''
    ## 上传指定文件到网盘
    local_file_path ：传入本地完整文件路径
    title:传入文件名
    '''
    with open(log_path_file, 'a', encoding="utf-8") as log_file:#写入日志
        log_file.write(title+".mp4"+"开始上传\n")
        print("开始上传！")
        # 登录
    token = login()
    if token:
        # 上传文件
        url2 = base_url + "/api/fs/put"
        file_size = os.path.getsize(local_file_path)  # 获取文件大小
        ori_url = remote_path + title + ".mp4"  # filename #上传到网盘的原始字符串
        Encode_url = quote(ori_url, 'utf-8')  # 对文件名进行URL编码
        with open(log_path_file, 'a', encoding="utf-8") as log_file:
            log_file.write("token获取成功!\n")
        headers = {
            "Authorization": token,
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
            "File-Path": Encode_url,
        }
        with open(log_path_file, 'a', encoding="utf-8") as log_file:#写入日志
            log_file.write(title+".mp4"+"正在上传...\n")
        with open(local_file_path, "rb") as f:#将本地文件转为二进制流
            databins = tqdm(desc="读取进度", total=file_size, unit="B", iterable=f.read())
        with open(log_path_file, 'a', encoding="utf-8") as log_file:#写入日志
            res = requests.put(url=url2, data=(bytes(databins)), headers=headers)
            res = json.loads(res.text)#解析返回数据
            if res["code"] == "200" or res["code"] == 200:
                with open(log_path_file, 'a', encoding="utf-8") as log_file:#写入日志
                    log_file.write(title+".mp4"+"上传成功！\n")
                    print("上传成功！")
                    log_file.write("上传结束时间：%s\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                with open(log_path_file, 'a', encoding="utf-8") as log_file:#写入日志
                    log_file.write("上传失败！\n错误信息：%s\n" % res)
                    log_file.write("上传结束时间：%s\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

