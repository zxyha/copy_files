import paramiko
import os
#from tqdm import tqdm 
from datetime import datetime


class ssh_copy:
    def __init__(self,local_folder,cloud_folder) -> None:
        self._local_folder = local_folder
        self.cloud_folder = cloud_folder
        self._is_connect = False

    @property
    def is_connect(self):
        return self._is_connect

    @is_connect.setter
    def is_connect(self,new_is_connect):
        self._is_connect = new_is_connect

    @property
    def local_folder(self):
        return self._local_folder
    
    @local_folder.setter
    def local_folder(self,folder):
        self._local_folder = folder

    def ssh_connect(self,hostname,port,username,password):
        if self.is_connect:
            return
        # 创建 SSH 客户端对象并连接到远程主机
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(hostname, port, username, password)
        except paramiko.ssh_exception.SSHException as e:
            print("SSH connection failed:", str(e))
            return False
        else:
            self.is_connect = True
            return True

    def ssh_disconnect(self):
        # 关闭 SSH 连接
        if self.is_connect:
            self.client.close()
            self.is_connect = False
    
    def list_files_local(self,folder,start_time , end_time):
        files = os.listdir(folder)
        ret_files = []
        for file in files:
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                modified_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if start_time <= modified_time <= end_time:
                    ret_files.append(file) 
        return ret_files
    
    def list_files_cloud(self,folder,start_time , end_time):
        # 执行find命令获取文件列表
        command = f"find {folder} -type f -newermt '{start_time}' ! -newermt '{end_time}'"
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        file_list = output.splitlines() # 解析命令输出，获取文件列表
        return file_list
    
    def push_files(self,start_time , end_time): 
        if not self.is_connect:
            return
        copy_files = self.list_files_local(self.local_folder,start_time , end_time)
        if len(copy_files) == 0:
            print('该时段没有可下载文件！')
            return

        copy_len = len(copy_files)
        with self.client.open_sftp() as sftp:
            for index,file in enumerate(copy_files):
                src_file_path = os.path.join(self.local_folder, file)
                dst_file_path = os.path.join(self.cloud_folder, file)
                stdin, stdout, stderr = self.client.exec_command(f"ls {dst_file_path}")
                if stdout.channel.recv_exit_status() == 0: #文件存在
                    print(f'{index+1}/{copy_len}',file,'existed')
                else:
                    # 使用 SCP 将源文件拷贝到目标主机
                    sftp.put(src_file_path, dst_file_path)
                    print(f'{index+1}/{copy_len}',file,'uploaded')
        print(f'files pushed to {self.cloud_folder}')
                    

    def pull_files(self,start_time , end_time,dst_folder): 
        if not self.is_connect:
            return
        download_files = self.list_files_cloud(self.cloud_folder,start_time , end_time)
        if len(download_files) == 0:
            print('该时段没有可下载文件！')
            return
        
        #检测是否需要新建文件夹
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)

        download_len = len(download_files)
        with self.client.open_sftp() as sftp:
            for index,file in enumerate(download_files):
                src_file_path = file
                dst_file_path = os.path.join(dst_folder, os.path.basename(file))
                if os.path.exists(dst_file_path):
                    print(f'{index+1}/{download_len}',file,'existed')
                else:
                    # 使用 SCP 将源文件拷贝到目标主机
                    sftp.get(src_file_path, dst_file_path)
                    print(f'{index+1}/{download_len}',file,'downloaded')
        print(f'files saved to {dst_folder}')



