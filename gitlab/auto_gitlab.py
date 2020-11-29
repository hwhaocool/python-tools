#coding: utf-8

import requests
import pprint
import yaml
import os
import sys

pp = pprint.PrettyPrinter(indent=2)

name_id_map = {}

def initConfig():

    head, tail = os.path.split(os.path.realpath(__file__))
    yaml_path = os.path.join(head, "config.yaml")

    f = open(yaml_path, 'r', encoding="utf-8")
    file_data = f.read()
    f.close()

    data = yaml.load(file_data, Loader=yaml.SafeLoader)

    initGitlab(data)
    initBranchPipeLine(data)

# 初始化 gitlab 相关
def initGitlab(data):
    global private_gitlab__token
    global gitlab_url
    global headers

    private_gitlab__token = data['private_token']
    gitlab_url = data['gitlab_url']

    headers = {'PRIVATE-TOKEN': private_gitlab__token}

# 初始化 代码分支流水线相关
def initBranchPipeLine(data):
    global project_branch_dict
    project_branch_dict = {}

    config_list = data['config']
    for config in config_list:
        name = config['name']

        pipeline = config['pipeline']

        pipe_list = analysis(pipeline)

        # key 是 project name, value 是一个二元数组列表
        print(name)
        project_branch_dict[name] = pipe_list

# 分析 项目的合并配置
def analysis(pipeline):
    pipe_list = []

    for src, dst in pipeline.items():
        # 数组
        # print(dst)

        for a in dst:
            if isinstance(a, dict):
                append(pipe_list, src, a)
            elif isinstance(a, str):
                pipe_list.append((src, a))

    # 打印 pipeline
    # pp.pprint(pipe_list)
    return pipe_list

# 是一个递归函数，递归分析
def append(pipe_list, src_branch, branch_dict):
    for key, value in branch_dict.items():

        # value 是数组
        # src --> key  可以组成一个组合
        pipe_list.append((src_branch, key))

        for a in value:
            if isinstance(a, dict):
                append(pipe_list, key, a)
            elif isinstance(a, str):
                pipe_list.append((key, a))

def initProjectId():

    temp_url = "{}{}".format(gitlab_url, "/projects?simple=true&per_page=100")
    r = requests.get(temp_url, headers=headers)

    for data in r.json():
        name = data['name']
        p_id = data['id']
        name_id_map[name] = p_id

def init():
    initConfig()

    initProjectId()

# 创建分支
def createBranch(project_name, src_name, dst_name):
    p_id = name_id_map.get(project_name, "000")
    if "000" == p_id:
        print("error! do not konw id of project {}".format(project_name))
        return

    current_url = "/projects/{}/repository/branches".format(p_id)
    temp_url = "{}{}?branch_name={}&ref={}".format(gitlab_url, current_url, dst_name, src_name)
    r = requests.post(temp_url, headers=headers)
    if 200 != r.status_code:
        print("create error, project_name {}, src_name {}, dst_name{}".format(project_name, src_name, dst_name))

def createMR(project_name, src_name, dst_name, auto_merge=False):
    p_id = name_id_map.get(project_name, "000")
    if "000" == p_id:
        print("error! do not konw id of project {}".format(project_name))
        return

    current_url = "/projects/{}/merge_requests".format(p_id)
    temp_url = "{}{}?branch_name={}&ref={}".format(gitlab_url, current_url, dst_name, src_name)

    data = {
        'id': p_id,
        'source_branch': src_name,
        'target_branch': dst_name,
        'title': "auto merge {} -> {}".format(src_name, dst_name)
    }

    r = requests.post(temp_url, headers=headers, data = data)
    if r.status_code >= 300:
        print("create MR error, project_name {}, src_name {}, dst_name{}".format(project_name, src_name, dst_name))
        print(r.status_code)
        print(r.text)
        return False
    
    merge_request_id = r.json()['id']

    if True == auto_merge:
        accept_result =  acceptMR(project_name, src_name, dst_name, merge_request_id)

        # 打印日志
        print("[{}, {} -> {}] create MR success, and accept MR {},  merge_request_id {}".format(project_name, src_name, dst_name, \
            "success" if accept_result else "fail", merge_request_id))

        return accept_result
    else:
        # 打印日志
        print("[{}, {} -> {}] create MR success,  merge_request_id {}".format(project_name, src_name, dst_name, merge_request_id))
    
    return True
   
def closeMR():
    print()

def acceptMR(project_name, src_name, dst_name, merge_request_id):
    p_id = name_id_map.get(project_name, "000")
    if "000" == p_id:
        print("error! do not konw id of project {}".format(project_name))
        return False

    current_url = "/projects/{}/merge_requests/{}/merge".format(p_id, merge_request_id)
    temp_url = "{}{}?branch_name={}&ref={}".format(gitlab_url, current_url, dst_name, src_name)
    r = requests.put(temp_url, headers=headers)

    if 405 == r.status_code:
        print("acceptMR error, have conflicts! project_name {}, merge_request_id {}".format(project_name, merge_request_id))
        return False

    if 406 == r.status_code:
        print("acceptMR error, merge request is already merged or closed! project_name {}, merge_request_id {}".format(project_name, merge_request_id))
        return False

    if 409 == r.status_code:
        print("acceptMR error, SHA does not match HEAD of source branch! project_name {}, merge_request_id {}".format(project_name, merge_request_id))
        return False

    if 401 == r.status_code:
        print("acceptMR error,  don't have permissions to accept this merge request! project_name {}, merge_request_id {}".format(project_name, merge_request_id))
        return False

    if 200 == r.status_code:
        # print("acceptMR success, project_name {}, merge_request_id {}".format(project_name, merge_request_id))
        return True

    return True

def autoMerge(project_name, src_name, dst_name=None, branch_name=None, which_2_branch=None):
    if dst_name is not None:
        # src -> dst
        # print("src -> dst")
        result = createMR(project_name, src_name, dst_name, True)
        if not result:
            return

    if branch_name  is not None and which_2_branch  is not None:

        # print("which_2_branch -> branch -> develop -> master")

        # which_2_branch -> branch_name
        result = createMR(project_name, which_2_branch, branch_name, True)
        if not result:
            return

        # branch_name -> develop
        result = createMR(project_name, branch_name, "develop", True)
        if not result:
            return

        # which_2_branch -> master
        result = createMR(project_name, which_2_branch, "master", True)
        if not result:
            return

def autoMerge2(project_name):

    pipeline = project_branch_dict.get(project_name, None)
    if pipeline is None:
        print("error! project [{}] do not exist in config.yaml".format(project_name))
        return

    for item in pipeline:
        src_name = item[0]
        dst_name = item[1]
        result = createMR(project_name, src_name, dst_name, True)
        if not result:
            return

def printUsage():
    print("you missing project name in cmd")
    print("demo: python auto_gitlab.py my_project_name")

def start():
    if len(sys.argv) < 2:
        printUsage()
        return

    project_name = sys.argv[1]

    # 初始化项目
    init()
    
    autoMerge2(project_name) 

# 开始
start()
