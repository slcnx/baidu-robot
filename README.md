# 说明

此项目，借助cqhttp http post, 对qq 群提问自动答疑。

# 原理
当一个人提问时，就将问题在baidu搜索中获取出结果，基于Xpath取出所有链接，python随机拿一个，发给这个朋友。
避免疯狂输出，就限制，一个群5分钟才可以回复一次。

# 安装
## 配置QQ号
编辑config.yml文件，将QQ列，添加自己的qq
```diff
account: # 账号相关
+  uin:  # QQ账号
```
## 配置当前主机的ip
编辑config.yml文件，将消息推送到指定端口, 由于在容器中监听所以，就使用宿主机地址。
```diff
  - http:
      # 服务端监听地址
      host: 0.0.0.0
      # 服务端监听端口
      port: 5700
      # 反向HTTP超时时间, 单位秒
      # 最小值为5，小于5将会忽略本项设置
      timeout: 5
      middlewares:
        <<: *default # 引用默认中间件
      # 反向HTTP POST地址列表
      post:
+      - url: '192.168.1.222:9000' # 地址
      #  secret: ''           # 密钥
      #- url: 127.0.0.1:5701 # 地址
      #  secret: ''          # 密钥
```
编辑test-v2.py文件，替换所有 `http://192.168.1.222:5700` 为docker宿主机映射的地址。
```bash
+ proxypool_url = 'http://192.168.1.237:5555/random'  # 替换成proxypool运行的地址
```

## 启动go-cqhttp
```bash
bash start-qq.sh
```
启动后，使用需要扫码登陆
```bash
docker logs -f qq
```

## 启动 qq-agent
启动前，需要修改-v路径，"G:/dockerfile/go-cqhttp/send.log" 这个是答疑的路径
```bash
bash  start-qq-agent.sh
```

## 启动proxypool
https://github.com/Python3WebSpider/ProxyPool/tree/1de4f95d3ac8b7fc1657f8e4fd127b263709be0a#docker-%E8%BF%90%E8%A1%8C

请勿非法使用，仅供学习交流！
