#coding: utf-8

import os
import json
import time

ali_log_file = raw_input("input full file path:")

ali_log_file_path, ali_log_file_name =  os.path.split(os.path.realpath(ali_log_file))

print(" 分割之后是： ")
print(ali_log_file_path)
print(ali_log_file_name)


f = open(ali_log_file, "r")

file_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 

# 新的文件完整路径
new_file_name = os.path.join(ali_log_file_path, file_name)
print(new_file_name)

gc_log = open(new_file_name + ".log", "w")

for data in f.readlines():
    log = json.loads(data)

    content = log["content"]

    # print(content)

    gc_log.write(content + "\n")
    # break

f.close()

gc_log.close()