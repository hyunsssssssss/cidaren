# 如何获取Token



## 对电脑微信抓包（推荐）

1. 在电脑启动Burp、Fiddler、Charles等工具，设置好相应代理
2. 打开电脑微信，浏览词达人任意页面
3. 在相应工具找到请求头，如：

```
GET /Student/Contest/List?timestamp=************&versions=1.2.0 HTTP/1.1
Host: gateway.vocabgo.com
Connection: close
Accept: application/json, text/plain, */*
Origin: https://app.vocabgo.com
UserToken: ******************************** （此处即Token）
X-Requested-With: XMLHttpRequest
Referer: https://app.vocabgo.com/student/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4
```



## 对手机微信进行抓包

1. 在电脑启动Burp、Fiddler、Charles等工具，手机上安装相应证书并设置代理
2. 打开微信，浏览词达人任意页面
3. 步骤同上