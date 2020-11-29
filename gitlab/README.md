
自动在gitlab上合代码
----


## 配置

```yaml

private_token: Qxxxx

gitlab_url: host/api/v3

config:
  - name: your-project-name
    pipeline:
      hotfix-9.1.1: 
        - hotfix-9.2.1:
            - branch_9.3:
              - develop
            - product
        - master
```

解释  
`private_token` 就是 gitlab -> profile -> account -> private token  
`gitlab_url` 就是 `gitlab 域名` + `/api/v3`  
`config` 就是 代码合并的配置  

`name` 项目名称，和 `gitlab` 要对应起来  
`pipeline` 就是合并的流水线，上面的实例最后的流程是：

```
hotfix-9.1.1 -> hotfix-9.2.1
hotfix-9.2.1 -> branch_9.3
branch_9.3   -> develop

hotfix-9.2.1 -> product

hotfix-9.1.1 -> master
```

## 使用

```
python auto_gitlab.py my_project_name
```