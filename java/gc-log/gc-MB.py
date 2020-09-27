#coding: utf-8

import os
import json
import time

import sys  

import re

reload(sys)  
sys.setdefaultencoding('utf8')

def gen_size_desc(num):
    num = int(num)
    if num <= 1024:
        return "%dK" % num
    if num > 1024:
        return "%.1fM" % (num / 1024)
    if num > 1024 * 1024:
        return "%.1fG" % (num / (1024 *1024))
    

# compile regex
size_pattern = re.compile("[0-9]+K")

ali_log_file = raw_input("input full file path:")

ali_log_file_path, ali_log_file_name =  os.path.split(os.path.realpath(ali_log_file))

print("spilt are")
print(ali_log_file_path)
print(ali_log_file_name)


f = open(ali_log_file, "r")

file_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 

# 新的文件完整路径
new_file_name = os.path.join(ali_log_file_path, file_name)
print(new_file_name)

new_log = open(new_file_name + ".log", "w")

for data in f.readlines():
    
    # 正则表达式匹配所有
    result = size_pattern.findall(data)
    
    if len(result) > 0 :
        for num_k in result:
            num = num_k[:-1]
            data = data.replace(num_k, gen_size_desc(num))
            
    # print(content)
    
    if data.lstrip().startswith("}"):
        data += "\n"

    new_log.write(data)
    # break

f.close()


new_log.close()