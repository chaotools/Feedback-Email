# Feedback Email API

简单的网站反馈邮件服务，接收用户反馈后发送 HTML 格式邮件到指定邮箱。

## 功能

- 🌐 接收 POST `/api/feedback` 请求
- 📧 支持 Bug Report / Suggestion / Other 三种类型
- 🎨 精美的 HTML 邮件模板
- 🔒 敏感信息通过环境变量配置

## 快速开始

### 1. 克隆
```bash
git clone https://github.com/chaotools/feedback-api.git
cd feedback-api
```

### 2. 配置环境变量
```bash
export SMTP_HOST="smtp.163.com"
export SMTP_PORT="465"
export SMTP_USER="your_email@163.com"
export SMTP_PASS="your_password"
export TO_EMAIL="your_email@163.com"
```

### 3. 运行
```bash
pip install -r requirements.txt
python3 feedback_api.py
```

### 4. 测试
```bash
python3 feedback_api.py --test
```

## API

### POST /api/feedback

**请求：**
```json
{
  "name": "张三",
  "email": "user@example.com",
  "type": "suggestion",
  "message": "建议添加深色模式"
}
```

**响应：**
```json
{"ok": true, "message": "Feedback sent!"}
```

## 使用 Nginx 代理（可选）

```nginx
location /api/feedback {
    proxy_pass http://127.0.0.1:8999;
    proxy_set_header Host $host;
}
```

## License

MIT
