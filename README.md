# USTC-Course-Helper
---
## 功能
- [x] 查询特定课程当前人数
- [ ] 自动提交个性化申请
- [ ] 支持同时监控多课程人数

## 使用
查询某一课程：
```py
pip install -r requirements.txt
python main.py [学号] [密码] [目标课程编号]

# 例如
python main.py PB21000000 passwd12 HS1614.01
> 二次元医学社会史: 60 / 60
```

## 安全问题
**您的学号和密码仅用于通过统一身份认证，此代码不会将您的敏感信息上传至其他任何服务器。**