# -*- coding: utf-8 -*-
"""
Vercel Serverless Function - Minimal Webhook Handler

This is a lightweight handler for Vercel deployment that:
1. Handles health checks
2. Receives Bot webhooks (Feishu, DingTalk)
3. Does NOT import heavy dependencies (pandas, numpy, etc.)

For full analysis functionality, use the local deployment or Docker.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import parse_qs, urlparse

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function handler"""

    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "":
            self._send_json(200, {
                "status": "ok",
                "message": "A股自选股智能分析系统 - Vercel Edition",
                "note": "This is a minimal deployment. For full analysis, use local or Docker deployment.",
                "endpoints": {
                    "GET /": "This page",
                    "GET /health": "Health check",
                    "POST /bot/feishu": "Feishu webhook",
                    "POST /bot/dingtalk": "DingTalk webhook",
                }
            })
        elif path == "/health":
            self._send_json(200, {"status": "healthy", "deployment": "vercel"})
        else:
            self._send_json(404, {"error": "Not Found", "path": path})

    def do_POST(self):
        """Handle POST requests (webhooks)"""
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        if path == "/bot/feishu":
            self._handle_feishu_webhook(body)
        elif path == "/bot/dingtalk":
            self._handle_dingtalk_webhook(body)
        else:
            self._send_json(404, {"error": "Not Found", "path": path})

    def _handle_feishu_webhook(self, body: bytes):
        """Handle Feishu webhook - URL verification and message receipt"""
        try:
            data = json.loads(body.decode("utf-8"))
            
            # URL Verification challenge
            if "challenge" in data:
                self._send_json(200, {"challenge": data["challenge"]})
                return

            # Event callback
            event_type = data.get("header", {}).get("event_type", "")
            
            # For now, just acknowledge receipt
            # Full processing would require the heavy dependencies
            self._send_json(200, {
                "code": 0,
                "msg": "received",
                "event_type": event_type,
                "note": "Full analysis requires local/Docker deployment"
            })

        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _handle_dingtalk_webhook(self, body: bytes):
        """Handle DingTalk webhook"""
        try:
            data = json.loads(body.decode("utf-8"))
            
            # Just acknowledge receipt
            self._send_json(200, {
                "msgtype": "text",
                "text": {
                    "content": "收到消息。完整分析功能请使用本地或 Docker 部署。"
                }
            })

        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _send_json(self, status: int, data: dict):
        """Send JSON response"""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
