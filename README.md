# danke-rent-spider

蛋壳公寓的爬虫，支持以下功能

1. Docker直接部署
2. 新房源邮件提醒
3. 过滤相似房源


## 运行

1. 修改config.py配置

```py

# 邮箱配置，发送方qq邮箱需要授权码登陆，其他邮箱需要在设置中打开SMTP功能
mail = {
    'sender': '***@sina.cn',
    'host': 'smtp.sina.com',
    'receivers': ['***@qq.com'],
    'password': 'password',
    'subject_prefix': '租房爬虫信息'
}


# 这个是拼在搜索url中需要搜索的地方
locations = ('南山', '福田', '绿景虹湾', '侨香', '前海东岸')



```

2. 通过Docker Compose 运行

```py
    # cd到项目所在目录
    cd /app 
    docker-composr up -d
```
