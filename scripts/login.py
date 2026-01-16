#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XHS Login Script - Simplified Version (Pure Algorithm Architecture)

仅负责登录和 Cookie 获取，签名通过纯算法实时生成。

Supports:
- Interactive login with QR code display
- Headless mode with JSON output
- Cookie extraction for API signature generation
"""

import sys
import io

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import asyncio
import argparse
from playwright.async_api import async_playwright

# Import from xhs_playwright package (simplified imports)
from xhs_playwright import save_credentials
from xhs_playwright.browser import (
    create_browser_context,
    setup_anti_detection,
    navigate_to_login,
    wait_for_login_complete,
    QrCodeStatusMonitor,
)
from xhs_playwright.qr_code import extract_from_page


async def run_extract_qr(headless: bool = False) -> dict:
    """
    Extract QR code only mode.
    
    Returns:
        dict with qr_base64, qr_ascii, success
    """
    async with async_playwright() as p:
        browser, context = await create_browser_context(p, headless)
        page = await context.new_page()
        await setup_anti_detection(page)
        
        await navigate_to_login(page)
        qr_result = await extract_from_page(page)
        
        await browser.close()
        return qr_result


async def run_login(headless: bool = False, json_mode: bool = False) -> dict:
    """
    Simplified login flow - Cookie only, no signature capture.
    
    纯算法架构下，签名通过 xhshow 库实时生成，
    此脚本仅负责登录并获取 Cookie。
    
    Args:
        headless: Run browser headlessly
        json_mode: Output JSON only (for API integration)
        
    Returns:
        dict with success, user_id, cookie_count
    """
    result = {
        "success": False,
        "user_id": None,
        "cookie_count": 0,
        "error": None
    }
    
    async with async_playwright() as p:
        browser, context = await create_browser_context(p, headless)
        page = await context.new_page()
        await setup_anti_detection(page)
        
        # Set up QR status monitoring (response)
        qr_monitor = QrCodeStatusMonitor()
        page.on("response", qr_monitor.create_response_handler())
        
        # Navigate and show login
        if not await navigate_to_login(page):
            result["error"] = "Failed to navigate to login"
            await browser.close()
            return result
        
        # Extract and display QR
        qr_result = await extract_from_page(page)
        
        if qr_result["success"]:
            if json_mode:
                print(json.dumps({
                    "success": True,
                    "step": "qrcode",
                    "qr_base64": qr_result["base64"]
                }), flush=True)
            else:
                print("\n" + "="*50)
                print("  扫描以下二维码登录小红书:")
                print("="*50)
                print(qr_result["ascii"])
                print("="*50 + "\n")
        else:
            result["error"] = "Failed to extract QR code"
            await browser.close()
            return result
        
        # Wait for login
        if not json_mode:
            print("等待登录", end="", flush=True)
        
        login_result = await wait_for_login_complete(page, context)
        
        if not login_result["success"]:
            result["error"] = "Login timeout or failed"
            await browser.close()
            return result
        
        if not json_mode:
            print("\n\n✅ 登录成功！")
        
        # Output QR status with login_info if available
        if json_mode and qr_monitor.is_logged_in():
            qr_status_response = qr_monitor.get_full_response()
            print(json.dumps({
                "success": True,
                "step": "qrcode_status",
                "data": qr_status_response.get("data", {})
            }), flush=True)
        
        # Save credentials (Cookie only, no signatures needed)
        cookies = login_result["cookies"]
        user_id = save_credentials(cookies)  # x_s_common 不再需要
        
        if qr_monitor.login_info:
            result["login_info"] = qr_monitor.login_info
        
        if not json_mode:
            print(f"[Login] ✅ Cookie 已保存 (User ID: {user_id})")
            print("[Login] 纯算法架构：签名将在 API 请求时实时生成，无需采集")
        
        result["success"] = True
        result["user_id"] = user_id
        result["cookie_count"] = len(cookies)
        
        # 关闭浏览器 - 无需等待签名采集
        await browser.close()
    
    # Output JSON if in json_mode
    if json_mode and result["success"]:
        print(json.dumps(result))
    
    return result


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="XHS Login Script (Pure Algo Mode)")
    parser.add_argument("--mode", choices=["login", "extract-qr"], default="login",
                        help="Operation mode")
    parser.add_argument("--headless", action="store_true", 
                        help="Run browser headlessly")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON format (for API integration)")
    
    args = parser.parse_args()
    
    if args.mode == "extract-qr":
        result = asyncio.run(run_extract_qr(headless=args.headless))
        if args.json:
            print(json.dumps(result))
    else:
        asyncio.run(run_login(headless=args.headless, json_mode=args.json))


if __name__ == "__main__":
    main()

