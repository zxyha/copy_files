import subprocess
import os
from tqdm import tqdm
import shutil
from datetime import datetime

class shutil_copy:
    def __init__(self,src_dir,target_dir) -> None:
        self._src_dir = src_dir
        self.target_dir = target_dir

    @property
    def src_dir(self):
        return self._src_dir
    
    @src_dir.setter
    def src_dir(self,folder):
        self._src_dir = folder

    def copy_files_xcopy(self):    
        copy_cmd = ['xcopy', self.src_dir, self.target_dir, '/E', '/I']
        p_copy = subprocess.Popen(copy_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        output_lines = p_copy.stdout.readlines() # 读取所有输出行
        total_lines = len(output_lines)# 获取输出行的总数
        # 使用 tqdm 显示进度条
        for line in tqdm(output_lines, total=total_lines, unit='行'):
            line = line.strip()
            # 在这里可以根据需要进行进度信息的处理和显示

        print("图片数据拷贝完成") 
        
    def copy_files(self,start_time , end_time):    
        # 获取源文件夹中的所有文件列表
        files = os.listdir(self.src_dir)
        copy_files = []
        for file in files:
            file_path = os.path.join(self.src_dir, file)
            if os.path.isfile(file_path):
                modified_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if start_time <= modified_time <= end_time:
                     copy_files.append(file_path)
        if len(copy_files) == 0:
            print('该时段没有可下载文件！')
            return
        
        # 遍历文件列表，筛选符合时间范围的文件，并进行拷贝
        copy_len = len(copy_files)
        for index,file_path in enumerate(copy_files):
            shutil.copy2(file_path, self.target_dir)
            print(f'{index+1}/{copy_len}',file,'downloaded')




