import subprocess
import os
import re
import random
import string
from urllib.parse import urlparse
from flask import Flask, render_template, request
import requests
from tqdm import tqdm
import upload
import configparser
import datetime
import aria2

'''
m3u8视频在线下载软件
version = 0.9.1
desc = 正式版
'''
# =======================下面是全局配置区域================================
#下载相关配置
config = configparser.ConfigParser()
config.read("./config/config.ini",encoding="utf-8")#读取本地配置文件

try: ffmpeg_path = config.get("download_settings", "ffmpeg_path")
except: ffmpeg_path = "ffmpeg"
try:out_path = config.get("download_settings", "out_path")
except:out_path = "./out_path/"
try:log_path_file = config.get("download_settings", "log_path_file")
except:log_path_file = "./log.txt"
try:file_path_m3u8 = config.get("download_settings", "file_path_m3u8")
except:file_path_m3u8 = "./file.txt"
try:backup_m3u8_path = config.get("download_settings", "backup_m3u8_path")
except:backup_m3u8_file = "./BackupM3u8/"
try:check_up = (config.get("upload_settings", "check_up").upper())
except:check_up = "no"
try:check_aria2 = (config.get("aria2_settings", "check_aria2").upper())
except:check_aria2 = "no"

app = Flask(__name__)

def check_input_type(input_str):
    # 判断是否为URL链接或包含m3u8的链接
    url_pattern = r'^https?://.*?\.m3u8.*?$'
    if re.match(url_pattern, input_str):
        return 1
    elif 'http' in input_str and '.' in input_str.split('/')[-1]:
        return 2
    else:
        return 3


def check_file_exists(file_name):
    for file in os.listdir(out_path):
        if file == file_name or file == file_name + '.mp4':
            return True
    return False

def backup_m3u8_file(url, save_dir, file_name):
    file_name = file_name+".m3u8"#构成完整文件名
    # 创建保存文件的文件夹
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # 发送请求并下载文件
    response = requests.get(url)
    with open(os.path.join(save_dir, file_name), 'wb') as f:
        f.write(response.content)

def generate_random_string(length=8):
    # 生成包含所有小写字母的字符集(string.ascii_lowercase)
    chars = string.ascii_lowercase
    # 随机选择并拼接指定长度的字符
    return ''.join(random.choice(chars) for _ in range(length))


def get_m3u8_info_with_progress(m3u8_url,fullname,log_file):
    # 发送HTTP请求获取m3u8文件内容
    r = requests.get(m3u8_url)
    m3u8_content = r.text
    
    # 使用正则表达式解析m3u8文件获取总分片数和总时长
    pattern_duration = re.compile(r'#EXT-X-TARGETDURATION:(\d+)')
    results_duration = pattern_duration.findall(m3u8_content)
    total_duration = sum([int(result) for result in results_duration])
        
    pattern_segments = re.compile(r'#EXTINF:\d+')
    results_segments = pattern_segments.findall(m3u8_content)
    total_segments = len(results_segments)
    
    # 打开日志文件，并将进度条写入日志
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'正在下载来自 {m3u8_url}的m3u8文件\n标题:{fullname}.mp4\n')
        f.write(f'总分片数: {total_segments}\n')

    # 显示进度条
    pbar = tqdm(total=total_segments)
    return (total_segments, total_duration, pbar)

def down_video_with_progress(downm3u8, fullname, log_file):
    # 获取总分片数和总时长，并创建进度条
    total_segments, _, pbar = get_m3u8_info_with_progress(downm3u8, fullname, log_file)
    
    # 打开log.txt文件，并将ffmpeg命令写入日志
    with open(log_file, 'a', encoding='utf-8') as f:
        downm3u8 = "\"%s\""%(downm3u8)#解除链接中带有特殊字符&的BUG
        cmd = ffmpeg_path+' -i ' + downm3u8 + ' -c copy '+out_path+fullname+'.mp4 -y'
        f.write(f'使用命令: {cmd}\n')

    # 执行ffmpeg命令，并将进度条写入日志
    task = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    pattern = re.compile(r"Opening '(.+?)' for reading")
    while True:
        line = task.stderr.readline()
        if not line:
            break
        # 匹配当前下载的分片名称
        match = pattern.search(line.decode('utf-8'))
        if match:
            pbar.update(1)
            # 将进度条写入日志
            ss = (f'下载进度 {fullname}{".mp4"} ({pbar.n}/{total_segments})')
            aria2.update_last_line(log_file,"".join(ss))
    task.communicate()
    
    # 在log.txt文件中记录任务完成和进程回收信息
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("该视频已下载完成!\n")
        task.kill()
        f.write("下载结束时间：%s\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 关闭进度条
    pbar.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play')
def play():
    return render_template('play.html')


@app.route('/download', methods=['POST'])
def download():
    # 处理表单数据
    file_content = request.form.get('file_content')#从前端获取的表单数据

    # 生成保存链接的临时文件，保存在指定目录下
    with open(file_path_m3u8, 'w', encoding='utf-8') as f:
        f.write(file_content)
    # 打开文件并按行读取内容
    with open(file_path_m3u8, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n') # 去除换行符
            if not line.strip(): # 如果行内容为空，则跳过不做处理
                continue
            # 对非空行进行处理，例如打印该行内容
            print(line)
            # 分割每一行
            line_data = line.strip().split(" ")
            # 处理每一行的内容
            linem3u8 = "".join(line_data[0])
            if len(line_data) > 1 and line_data[1]:
                title = "".join(line_data[1])
            else:
                title = generate_random_string()
                if check_file_exists(title):
                    title = title + '_'+ generate_random_string()
            # 检查是否是合法的 URL
            if check_input_type(linem3u8)==1:#如果是在线m3u8地址
                with open(log_path_file, 'a', encoding='utf-8') as f:
                    f.write(f"{linem3u8}是m3u8视频链接\n")
                    f.write(f"正在保存该文件\n")
                backup_m3u8_file(linem3u8,backup_m3u8_path,title)
                try:#开始下载
                    down_video_with_progress(linem3u8, title, log_path_file)
                except Exception as e:
                    with open(log_path_file, 'a', encoding='utf-8') as f:
                        f.write("下载错误!请检查相关配置!\n错误信息%s\n"%e)
                fullname = out_path+title+".mp4"#组成本地路径文件名
                if check_up=="YES":
                    if os.path.exists(fullname):
                        try:
                            upload.upload_alist(fullname,title)#开始上传
                        except Exception as e:
                            with open(log_path_file, 'a', encoding='utf-8') as f:
                                 f.write("上传错误!请检查相关配置!\n错误信息%s\n"%e)
                    else:
                        with open(log_path_file, 'a', encoding='utf-8') as f:
                            f.write("本地文件未找到！上传失败！\n")
                else:
                    with open(log_path_file, 'a', encoding='utf-8') as f:
                        f.write("上传选项未开,不上传文件!\n")
            elif check_input_type(linem3u8)==2:#如果是文件
                with open(log_path_file, 'a', encoding='utf-8') as f:
                    f.write(f"{linem3u8}是文件下载链接\n")
                if check_aria2 == "YES":
                    with open(log_path_file, 'a', encoding='utf-8') as f:
                        f.write(f"正在连接到aria2服务...\n")
                    aria2.adduri(linem3u8)
                else:
                    with open(log_path_file, 'a', encoding='utf-8') as f:
                            f.write("aria2选项未开,请检查配置！")
            elif check_input_type(linem3u8)==3:
                with open(log_path_file, 'a', encoding='utf-8') as f:
                    f.write('链接： {} 不合法\n'.format(linem3u8))
                    f.write("跳过执行下一个链接\n")
                    
    # 清空链接地址
    with open(file_path_m3u8, 'w', encoding='utf-8') as f:
        f.write('')
    with open(log_path_file,"a",encoding="utf-8") as log_file:
        log_file.write('所有文件已处理完成，链接地址已清空')
    return ""


@app.route('/log')
def get_log():
    with open(log_path_file, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/clear_log')
def clear_log():
    with open(log_path_file, 'w', encoding='utf-8') as f:
        f.write('')
    return 'OK'

if __name__ == '__main__':
    #如果文件夹不存在则创建
    if not os.path.exists(out_path):#输出文件夹
        os.mkdir(out_path)
    if not os.path.exists(backup_m3u8_path):#备份文件夹
        os.mkdir(backup_m3u8_path)
    #如果某些日志和临时文件不存在则创建
    if not os.path.exists(log_path_file):#日志文件
        open(log_path_file, 'w').close()
    if not os.path.exists(file_path_m3u8):#临时链接保存文件
        open(file_path_m3u8, 'w').close()
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)

