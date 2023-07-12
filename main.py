from shutil_copy import shutil_copy
from ssh_copy import ssh_copy
import time
from datetime import datetime
import getpass
import subprocess
import yaml
from typing import Dict, Any
import os

config_file_path = 'config.yaml'
yaml_config: Dict[str, Any]

host_share_folder = ''  #共享文件夹路径
local_pics_folder = r'D:\download_files'             #本地主机存储路径
remote_folder_path = r'/home/admin/by_share/'        #云端主机存储路径

file_download = shutil_copy(host_share_folder,local_pics_folder)    #下载到本机
ssh_copyer = ssh_copy(host_share_folder,remote_folder_path)         #上传至云端

#读取配置信息
def load_or_create_config():
    global host_share_folder
    global yaml_config

    # 检查配置文件是否存在
    if not os.path.exists(config_file_path):
        # 创建新的配置文件
        default_config = {
            'host_share_folder': ''
        }
        # 写入默认配置到文件
        with open(config_file_path, 'w') as f:
            yaml.dump(default_config, f)

    # 读取配置文件
    with open(config_file_path, 'r') as f:
        yaml_config = yaml.safe_load(f)

    # 获取 share_host 字段的值
    host_share_folder = yaml_config.get('host_share_folder')
    file_download.src_dir = host_share_folder
    ssh_copyer.local_folder = host_share_folder
    

#登录共享主机
def login_share_host():
    global host_share_folder

    share_host_ip=input('请输入共享主机IP：')
    share_folder = input('请输入共享文件夹名称：')
    ex_str=r'\\'
    host_share_folder = f'{ex_str}{share_host_ip}\{share_folder}'
    username = input('请输入登录用户名：')
    while True:
        password = getpass.getpass('请输入登录密码：')
        # 构建执行命令的字符串
        login_cmd = ['net', 'use', host_share_folder, '/user:' +  username, password]

        # 使用 subprocess 模块执行命令行命令以登录到共享文件夹
        p_login = subprocess.Popen(login_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,error = p_login.communicate()
        if error:
            print("登录失败:", error.decode('gbk'))
        else:
            print(f'成功登录到{host_share_folder}')
            break
    
    yaml_config['host_share_folder'] = host_share_folder
    file_download.src_dir = host_share_folder
    ssh_copyer.local_folder = host_share_folder

    with open(config_file_path, 'w') as f:
        yaml.dump(yaml_config, f)

    return True       

#登录远程主机
def login_remote_host():
    if ssh_copyer.is_connect:
        return
    hostname = input('请输入远程主机地址：')
    port = 22
    username = input('请输入远程主机登录用户名：')
    while True:
        password = getpass.getpass('请输入远程主机登录密码：')
        is_suc = ssh_copyer.ssh_connect(hostname,port,username,password)
        if is_suc:
            print('登录成功')
            break
        else :
            print('登录失败')

#拷贝文件
def copy_files(is_push=True):
    start_time_str = input('开始时间（格式：20230101000000）：')
    start_time = datetime.strptime(start_time_str, '%Y%m%d%H%M%S')
    time_now = datetime.now()
    end_time_str = input('结束时间（格式：20230101000000）：') or time_now.strftime('%Y%m%d%H%M%S')
    end_time = datetime.strptime(end_time_str, '%Y%m%d%H%M%S')
    if is_push:
        #file_download.copy_files(start_time,end_time) 
        ssh_copyer.push_files(start_time,end_time)
    else:
        ssh_copyer.pull_files(start_time,end_time,f'{local_pics_folder}\cloud_files')
    
#实时拷贝文件
def copy_files_real_time():
    start_time_str = input('开始时间（格式：20230101000000）：')
    start_time = datetime.strptime(start_time_str, '%Y%m%d%H%M%S')
    timer_interval = input('时间间隔（秒）：')
    latest_time = start_time
    while True:
        time_now = datetime.now()
        #file_download.copy_files(latest_time,time_now)
        ssh_copyer.push_files(latest_time,time_now) 
        latest_time = time_now
        time.sleep(int(timer_interval))


if __name__ == '__main__':

    #读取配置信息
    load_or_create_config()

    #无配置信息则强制登录
    if not host_share_folder:
        login_share_host()   

    tips_str = \
    f'''
    0：退出
    1：登录文件共享主机（每台主机只需要登录一次）
    2：上传指定时段文件至云端
    3：自动检测并实时上传最新文件
    4：从云端下载文件至本地主机
    '''
    print(tips_str)
    while True:
        cmd_str = input('请输入操作指令：')

        if cmd_str != '0' and cmd_str != '1':
            login_remote_host()  # 连接远程主机
        
        if cmd_str == '0':
            break
        elif cmd_str == '1':
            login_share_host()
        elif cmd_str == '2':
            copy_files()
        elif cmd_str == '3':
            copy_files_real_time()
        elif cmd_str == '4':
            copy_files(False)
        
        
            
    # 关闭 SSH 连接
    ssh_copyer.ssh_disconnect()

   

