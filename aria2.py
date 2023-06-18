import xmlrpc.client
import configparser
import datetime
from urllib.parse import urlparse, unquote
import json
import time
from tqdm import tqdm
config = configparser.ConfigParser()
config.read("./config/config.ini",encoding="utf-8")#读取本地配置文件

# 连接到 Aria2 RPC 接口
try: server_url = config.get("aria2_settings", "server_url")
except: server_url = "http://127.0.0.1:6800/rpc"
try: token = config.get("aria2_settings", "token")
except: token = "prc_password"
try: download_path = config.get("aria2_settings", "download_path")
except: download_path = "./"
try:log_path_file = config.get("download_settings", "log_path_file")
except:log_path_file = "./log.txt"

aria2 = xmlrpc.client.ServerProxy(server_url, allow_none=True)

def get_filename_from_url(url):
    parsed_url = urlparse(url)
    filename = unquote(parsed_url.path.split('/')[-1])
    return filename

def get_tasks_list():
    list_token = 'token:' + token
    tasks = aria2.aria2.tellActive(list_token)
    # 打印任务列表
    for task in tasks: 
        # 将输入字符串解析为 Python 对象
        obj = json.loads(task)
        # 输出一些字段
        gid = (obj['gid'])                  # 下载任务的 GID
        status = (obj['status'])               # 下载状态
        completeLength = int((obj['completedLength']))/1024/1024      # 已下载文件大小
        totalLength = int((obj['totalLength']))/1024/1024          # 文件总大小
        downloadSpeed = (obj['downloadSpeed'])        # 下载速度
        dir = (obj['dir'])               #保存路径
        return(f"当前下载列表\n\
               下载任务gid:{gid}\t\
               下载状态:{status}\t\
               已下载文件大小:{completeLength}MB\t\
               文件总大小:{totalLength}MB\t\
               下载速度:{downloadSpeed}\t\
               保存路径:{dir}\n\
               ")

def update_last_line(filename, new_line):#更新指定文件的最后一行
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if len(lines) > 0:  # 如果读到内容，更新最后一行
            lines[-1] = new_line + '\n'
            with open(filename, 'w', encoding='utf-8') as file:
                file.writelines(lines)
        else:  # 如果没有读到内容，直接写入
            with open(filename, 'w', encoding='utf-8') as file:
                file.writelines(new_line)
    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(f"{filename} not found.")
            return None

def adduri(uri):
    title = get_filename_from_url(uri)
    try:
        gid = aria2.aria2.addUri(
            f'token:{token}',
            [f'{uri}'],
            {'dir': download_path}
        )
        with open(log_path_file,"a",encoding="utf-8")as log_file:
            log_file.writelines("已经提交到aria2服务器,该任务{title}下载中...\n")
        
        while True:
            status = aria2.aria2.tellStatus(f'token:{token}', gid, ['status', 'totalLength', 'completedLength'])
            if status['status'] == 'complete':
                with open(log_path_file, "a", encoding="utf-8") as log_file:
                    log_file.writelines(f"任务{title}下载完成\n")
                    log_file.writelines("下载结束时间%s\n"%datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    print(f"任务{title}下载完成\n")
                break
            else:
                total_size = int(status['totalLength'])
                downloaded_size = int(status['completedLength'])
                progress = downloaded_size / total_size * 100 if total_size > 0 else 0
                ss = (f"文件名:{title}: 已完成:{progress:.2f}%")
                update_last_line(log_path_file,"".join(ss))#写入日志文件
                tqdm.write(f"{title}: {progress:.2f}%")
                time.sleep(0.1)
    except Exception as e:
        with open(log_path_file,"a",encoding="utf-8")as log_file:
            log_file.writelines("提交错误！请检查aria2服务器配置\n")
            log_file.writelines("错误信息:%s\n"%e)
        

#测试程序
# url2 = f'https://cdn-haokanapk.baidu.com/haokanapk/apk/baiduhaokan1015351b.apk'
# url = f'https://nchc.dl.sourceforge.net/project/orwelldevcpp/Setup%20Releases/Dev-Cpp%205.11%20TDM-GCC%204.9.2%20Setup.exe'
# adduri(url2)


