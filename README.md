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
# 只允许站点前端访问；多个域名用英文逗号分隔
export ALLOWED_ORIGINS="https://chaotools.tech"
# 每个来源 IP 在限流窗口内的最大提交次数（默认 10 次/小时）
export RATE_LIMIT_MAX="10"
export RATE_LIMIT_WINDOW="3600"
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
    proxy_set_header X-Forwarded-For $remote_addr;
}
```

使用反向代理时，请额外设置 `TRUST_PROXY=1`，以便按真实访客 IP 限流。反向代理必须覆盖而非透传客户端提供的 `X-Forwarded-For` 请求头。

## License

MIT
