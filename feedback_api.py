#!/usr/bin/env python3
"""Feedback Email API - Simple feedback to email service"""

import os
import smtplib
import json
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# ====== CONFIG (from environment) ======
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.163.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASS = os.getenv('SMTP_PASS', '')
TO_EMAIL = os.getenv('TO_EMAIL', SMTP_USER)

PORT = int(os.getenv('PORT', '8999'))


class FeedbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if '/api/feedback' in args[0]:
            print(f"[{self.log_date_time_string()}] {args[0]}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path != '/api/feedback':
            self.send_json(404, {'error': 'Not found'})
            return

        length = int(self.headers.get('Content-Length', 0))
        if length > 10000:
            self.send_json(413, {'error': 'Request too large'})
            return

        try:
            body = self.rfile.read(length)
            data = json.loads(body.decode('utf-8'))
        except Exception as e:
            self.send_json(400, {'error': f'Invalid JSON: {e}'})
            return

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        fb_type = data.get('type', 'other').strip()
        message = (data.get('message') or data.get('msg') or '').strip()

        if not name or len(name) < 1 or len(name) > 20:
            self.send_json(400, {'error': 'Invalid name'})
            return
        if not message or len(message) < 5 or len(message) > 2000:
            self.send_json(400, {'error': 'Message must be 5-2000 chars'})
            return

        type_labels = {
            'bug': '\U0001f41b Bug Report',
            'suggestion': '\U0001f4a1 Suggestion',
            'other': '\U0001f4ac Other',
        }
        type_name = type_labels.get(fb_type, type_labels['other'])

        try:
            send_email(name, email, fb_type, type_name, message)
            self.send_json(200, {'ok': True, 'message': 'Feedback sent!'})
            print(f"[OK] Feedback from {name} ({fb_type})")
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            self.send_json(500, {'error': f'Failed to send: {str(e)}'})

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))


def send_email(name, email, fb_type, type_name, message):
    subject = f"[chaotools反馈] {type_name} - from {name}"

    text_body = f"""你收到一条来自 chaotools.tech 的反馈：

称呼：{name}
邮箱：{email or '未填写'}
类型：{type_name}
时间：{formatdate(localtime=True)}

内容：
{message}

此邮件由网站反馈系统自动发送，请勿直接回复。
"""

    html_body = f"""
<div style="max-width:560px;margin:0 auto;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#333;">
<div style="background:linear-gradient(135deg,#070b12,#0d1526);padding:24px;border-radius:14px 14px 0 0;text-align:center;">
<span style="font-size:32px;">&#128172;</span>
<h2 style="color:#00ff9d;margin:10px 0 0;font-family:'Courier New',monospace;letter-spacing:2px;">FEEDBACK</h2>
<p style="color:#6b7d99;font-size:12px;margin-top:6px;">来自 CHAOTOOLS HUB 的用户反馈</p>
</div>

<div style="background:#fff;padding:28px 24px;border-radius:0 0 14px 14px;border:1px solid #eee;border-top:none;">
<table style="width:100%;font-size:14px;line-height:2;">
<tr><td style="color:#888;width:80px;padding:4px 0;border-bottom:1px solid #f0f0f0;"><b>称呼</b></td><td style="border-bottom:1px solid #f0f0f0;">{name}</td></tr>
<tr><td style="color:#888;padding:4px 0;border-bottom:1px solid #f0f0f0;"><b>邮箱</b></td><td style="border-bottom:1px solid #f0f0f0;">{email or '<span style="color:#aaa">未填写</span>'}</td></tr>
<tr><td style="color:#888;padding:4px 0;border-bottom:1px solid #f0f0f0;"><b>类型</b></td><td style="border-bottom:1px solid #f0f0f0;">{type_name}</td></tr>
<tr><td style="color:#888;padding:4px 0;border-bottom:1px solid #f0f0f0;"><b>时间</b></td><td style="border-bottom:1px solid #f0f0f0;">{formatdate(localtime=True)}</td></tr>
</table>

<div style="margin-top:20px;padding:16px;background:#f9fafb;border-radius:10px;border-left:3px solid #00ff9d;">
<p style="color:#888;font-size:12px;margin-bottom:8px;"><b>详细内容</b></p>
<pre style="white-space:pre-wrap;font-size:14px;line-height:1.7;margin:0;color:#333;">{message}</pre>
</div>
</div>

<p style="text-align:center;color:#bbb;font-size:11px;margin-top:20px;">
由 <span style="color:#00ff9d;">CHAOTOOLS HUB</span> 反馈系统自动发送 · 请勿直接回复
</p>
</div>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = f"Chaotools反馈 <{SMTP_USER}>"
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)

    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(SMTP_USER, [TO_EMAIL], msg.as_string())
    server.quit()


if __name__ == '__main__':
    # Check required env vars
    if not SMTP_USER or not SMTP_PASS:
        print("[ERROR] SMTP_USER and SMTP_PASS environment variables are required")
        sys.exit(1)

    server = HTTPServer(('127.0.0.1', PORT), FeedbackHandler)
    print(f"[*] Feedback API on http://127.0.0.1:{PORT}")
    
    if '--test' in sys.argv:
        print("[TEST] Sending test email...")
        try:
            send_email('测试用户', 'test@example.com', 'bug', 'Bug Report', '测试消息')
            print('[TEST OK] Email sent!')
        except Exception as e:
            print(f'[TEST FAIL] {e}')
    else:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Server stopped")
            sys.exit(0)
