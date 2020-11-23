#coding: utf-8

import requests
import pprint
import yaml

pp = pprint.PrettyPrinter(indent=2)

private_gitlab__token = None

# endsWith /api/v3
gitlab_url = None

headers = None

name_id_map = {}

def initConfig():
    f = open("config.yaml", 'r', encoding="utf-8")
    file_data = f.read()
    f.close()

    data = yaml.load(file_data)
    private_gitlab__token = data['private_token']
    gitlab_url = data['gitlab_url']

    headers = {'PRIVATE-TOKEN': private_gitlab__token}

def initProjectId():

    temp_url = "{}{}".format(gitlab_url, "/projects?simple=true&per_page=100")
    r = requests.get(temp_url, headers=headers)

    print(r)

    for data in r.json():
        # print()
        name = data['name']
        p_id = data['id']
        name_id_map[name] = p_id

    pp.pprint(name_id_map)
    print(len(name_id_map))
# print(r.json())

def init():
    initProjectId()
    initConfig()

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
        return
    
    merge_request_id = r.json()['id']

    if True == auto_merge:
        accept_result =  acceptMR(project_name, src_name, dst_name, merge_request_id)

        # 打印日志
        print("[{}, {} -> {}] create MR success, and accept MR {},  merge_request_id {}".format(project_name, src_name, dst_name, \
            "success" if accept_result else "fail", merge_request_id))
    else:
        # 打印日志
        print("[{}, {} -> {}] create MR success,  merge_request_id {}".format(project_name, src_name, dst_name, merge_request_id))
    
    return merge_request_id
   
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
        print("acceptMR success, project_name {}, merge_request_id {}".format(project_name, merge_request_id))
        return True

    return True

def autoMerge(project_name, src_name, dst_name=None, branch_name=None, which_2_branch=None):
    if dst_name is None:
        # src -> dst
        createMR(project_name, src_name, dst_name, True)

    if branch_name not None and which_2_branch not None:

        # which_2_branch -> branch_name
        createMR(project_name, which_2_branch, branch_name, True)

        # branch_name -> develop
        createMR(project_name, branch_name, "develop", True)

        # which_2_branch -> master
        createMR(project_name, which_2_branch, "master", True)

# 初始化项目
init()


