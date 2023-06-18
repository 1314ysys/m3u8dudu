# m3u8dudu
这是一个m3u8离线下载上传的网页软件。它通过ffmpeg解析链接并下载，支持通过Alist上传到网盘，同时支持通过Aria2下载文件链接；目前分为m3u8链接的离线下载和m3u8链接的在线播放两个部分。
# 1.前端页面效果及功能
## 页面效果
* 离线下载
![9fe71f412a090b68843c81834b73db22.png](:/675d43ccf2f44565917b98793ea26ab0)
* 在线播放
![69c4c28fe2a43f993dadfff2eaa28aca.png](:/52971dca5294479091e2136ac4893524)
## 实现功能
- 复制m3u8链接离线下载，支持批量离线下载
- 复制m3u8链接在线解析播放视频
- 支持Alist代理网盘的上传
- 支持Aria2服务器的下载任务提交
# 2.部署方式
### 源码部署
**1、必须有Python3+ffmpeg的环境**
Python必须安装以下依赖：
```
pip install Flask
pip install tqdm
pip install requests
```
**2、检查是否已安装ffmpeg**
进入linux系统
```
ffmpeg -version
```
如果有显示版本信息则说明安装成功
**3、复制或者下载源码到linux服务器上
```
git clone https://github.com/1314ysys/m3u8dudu.git
```
**4、使用python运行并注册为服务开机自启**
进入项目文件夹
```
cd m3u8dudu
```
使用任意文本编辑器编辑配置文件
```
nano config/config.ini
```
完成后保存退出，使用python运行
```
python3 app.py
```
![573fd30d3b836f9633855c94978de66e.png](https://github.com/1314ysys/imgbed/blob/main/573fd30d3b836f9633855c94978de66e.png)
出现如上图所示说明已成功运行
**注册为系统服务开机自启**
使用以下命令来创建一个服务：
```
sudo nano /etc/systemd/system/m3u8dudu.service
```
2、在编辑器中添加以下内容：
```
[Unit]
Description=M3u8dudu Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python /root/m3u8dudu/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```
保存退出并运行
```
systemctl start m3u8dudu.service
```
```
systemctl enable m3u8dudu.service
```
### docker镜像部署
**(已经封装了Python+FFmpeg环境，镜像大小50M左右)**
**1、必须安装docker**
**2、使用命令拉取镜像(支持AMD和ARM64架构)**
```
docker run -d -p 5000:5000 -v /root/out_path:/app/out_path -v /root/backup_m3u8_path:/app/backup_m3u8_path -v /root/config:/app/config lenfivil/m3u8dudu:latest
```
- -d 表示容器后台运行
-p 映射<本地5000端口>:<容器内端口5000> 容器内端口必须为5000
-v 映射本地输出视频下载输出路径
-v m3u8文件备份路径
-v 配置文件映射路径
### 配置文件说明
一般情况下只要修改自己的alist账号密码和上传下载路径就行了，一般情况下请不要修改**out_path**和**backup_m3u8_path**
**尤其是docker容器部署的方式**
```
# =======================下面是全局配置区域================================
#下载相关配置
#ffmpeg_path 为ffmpeg工具包的安装路径
#out_path 为转化后的mp4文件存放路径
#log_path_file 为日志文件存放路径
#file_path_m3u8 为待处理的m3u8链接地址文本路径
#backup_m3u8_path 为保存的m3u8文件路径
#路径后边必须加上/
[download_settings]
#ffmpeg_path = ffmpeg
out_path = /app/out_path/
log_path_file = /app/log.txt
file_path_m3u8 = /app/file.txt
backup_m3u8_path = /app/backup_m3u8_path/

#上传相关配置
#check_up #是否要开启上传选项
#base_url #网盘的地址
#UserName #alist网盘账号
#PassWord #alist网盘密码
#remote_path #要上传文件的网盘路径
[upload_settings]
check_up = yes
base_url = http://192.168.1.111:5344
UserName = admin
PassWord = 123456
remote_path = /BaiduYun/

#Aria2下载服务配置
#必须开启rpc接口服务
#check_aria2 #是否要开启aria2文件下载服务
#server_url 表示aria2的服务地址后面的/rpc可能为/jsonrpc
#passwd为rpc接口的密钥
[aria2_settings]
check_aria2 = yes
server_url = http://192.168.1.111:16800/rpc
token = pac_password
download_path = /opt/SrcCloud123/temp/downloads/
```

