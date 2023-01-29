# USTC-Course-Helper
---
## 功能
- [x] 查询特定课程当前人数
- [ ] 自动提交个性化申请
- [ ] 支持同时监控多课程人数

## 使用
### 准备
* 安装依赖
```python
pip install -r requirements.txt
```
* 在 `./data/cookies.txt` 文件内，填入登入教务系统后的对应 Cookies.
```txt
SVRNAME: []
SESSION: []
fine_auth_token: []
fine_remember_login: -1
```
### 监视课程 / 自动提交申请
```py
# 监视某一课程人数
python main.py -w [目标课程编号]

# 例如
python main.py -w HS1614.01
> 二次元医学社会史: 60 / 60
```

## 安全问题
**您的 cookies 仅用于通过统一身份认证以及教务系统认证，此代码不会将您的敏感信息上传至其他任何服务器。**