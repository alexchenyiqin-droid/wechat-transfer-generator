#!/usr/bin/env python3
"""
微信转账截图 Playwright 渲染服务
用法: python screenshot_server.py
默认监听 http://localhost:8081
POST /screenshot 接受 JSON body {
    "payee": "小牛修车",
    "amount": "1805.00",
    "note": "修理费",
    "transferTime": "2025年07月17日 09:25:32",
    "receiveTime": "2025年07月17日 15:24:06"
}
返回 PNG 图片
"""

import os
import json
import io
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).parent
HTML_FILE = ROOT / "wechat-transfer-generator.html"
CHROME = "/Users/alexchen/Library/Caches/ms-playwright/chromium-1228/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"

from flask import Flask, request, send_file, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def format_money(num_str):
    try:
        n = float(num_str)
        return f"{n:.2f}"
    except (ValueError, TypeError):
        return "0.00"

def render_screenshot(params):
    """用 Playwright 渲染截图并返回 PNG bytes"""
    payee = params.get("payee", "对方")
    amount_str = format_money(params.get("amount", "0.00"))
    note = params.get("note", "-")
    transfer_time = params.get("transferTime", "")
    receive_time = params.get("receiveTime", "")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = browser.new_page(
            viewport={"width": 400, "height": 900},
            device_scale_factor=2,
        )
        page.goto(f"file://{HTML_FILE}")
        page.wait_for_timeout(500)

        # 注入数据
        page.evaluate("""
            ([payee, amount, note, transferTime, receiveTime]) => {
                document.getElementById('payee').value = payee;
                document.getElementById('amount').value = amount;
                document.getElementById('note').value = note;
                document.getElementById('transferTime').value = transferTime;
                document.getElementById('receiveTime').value = receiveTime;
                // 触发 update
                ['payee','amount','note','transferTime','receiveTime'].forEach(id => {
                    const el = document.getElementById(id);
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                });
            }
        """, [payee, amount_str, note, transfer_time, receive_time])

        page.wait_for_timeout(300)

        capture = page.locator("#capture")
        screenshot_bytes = capture.screenshot(type="png")

        browser.close()
        return screenshot_bytes


@app.route("/screenshot", methods=["POST"])
def screenshot():
    params = request.get_json(force=True) or {}
    try:
        png_bytes = render_screenshot(params)
        return send_file(
            io.BytesIO(png_bytes),
            mimetype="image/png",
            as_attachment=True,
            download_name=f"微信转账_{params.get('payee', '对方')}_{params.get('amount', '0')}.png"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"ok": True})


if __name__ == "__main__":
    print(f"🚀 截图服务启动: http://localhost:8081")
    print(f"   模板: {HTML_FILE}")
    print(f"   Chrome: {CHROME}")
    app.run(host="127.0.0.1", port=8081, debug=False)
