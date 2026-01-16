"""
Playwright browser management for XHS automation
"""

import json
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .config import (
    BROWSER_ARGS,
    EXTRA_HEADERS,
    ANTI_DETECTION_JS,
    XHS_EXPLORE_URL,
    QR_SELECTORS,
    LOGIN_TIMEOUT_SECONDS,
    QRCODE_STATUS_URL,
)


class QrCodeStatusMonitor:
    """
    监听二维码登录状态的 XHR response。
    
    状态码:
        0 - 未扫码
        1 - 已扫码，等待确认
        2 - 登录成功 (包含 login_info)
    """
    
    def __init__(self):
        self.latest_status = None
        self.login_info = None
        self._status_history = []
    
    def create_response_handler(self):
        """创建 response 事件处理器"""
        async def handler(response):
            try:
                if QRCODE_STATUS_URL in response.url and response.status == 200:
                    data = await response.json()
                    if data.get("success") and "data" in data:
                        status_data = data["data"]
                        code_status = status_data.get("code_status")
                        
                        self.latest_status = data  # 保存完整响应
                        self._status_history.append(code_status)
                        
                        # 登录成功时保存 login_info
                        if code_status == 2 and "login_info" in status_data:
                            self.login_info = status_data["login_info"]
                            print(f"[QR Monitor] 登录成功! user_id: {self.login_info.get('user_id')}")
                        elif code_status == 1:
                            print("[QR Monitor] 已扫码，等待确认...")
            except Exception as e:
                # 忽略 JSON 解析错误等
                pass
        return handler
    
    def get_code_status(self) -> int:
        """获取当前状态码"""
        if self.latest_status:
            return self.latest_status.get("data", {}).get("code_status", -1)
        return -1
    
    def is_logged_in(self) -> bool:
        """检查是否登录成功"""
        return self.get_code_status() == 2
    
    def get_full_response(self) -> dict:
        """获取完整的最新响应（全量返回）"""
        return self.latest_status or {"code": -1, "success": False, "msg": "未获取到状态"}



async def create_browser_context(
    playwright,
    headless: bool = False
) -> tuple[Browser, BrowserContext]:
    """
    Create a Playwright browser and context with anti-detection settings.
    
    Args:
        playwright: Playwright instance
        headless: Whether to run headless
        
    Returns:
        Tuple of (browser, context)
    """
    browser = await playwright.chromium.launch(
        headless=headless,
        args=BROWSER_ARGS
    )
    
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 800},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        locale='zh-CN',
        extra_http_headers=EXTRA_HEADERS
    )
    
    return browser, context


async def setup_anti_detection(page: Page) -> None:
    """
    Apply anti-detection JavaScript to page.
    
    Args:
        page: Playwright page object
    """
    await page.add_init_script(ANTI_DETECTION_JS)


async def navigate_to_login(page: Page) -> bool:
    """
    Navigate to XHS explore page where login modal auto-appears.
    
    Args:
        page: Playwright page object
        
    Returns:
        True if login modal appeared, False otherwise
    """
    await page.goto(XHS_EXPLORE_URL, wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    
    try:
        # Wait for QR code modal to appear (auto-popup on explore page)
        qr_wrapper = page.locator(QR_SELECTORS["qr_wrapper"])
        await qr_wrapper.wait_for(timeout=10000, state="visible")
        return True
    except Exception as e:
        print(f"[Browser] Login modal did not appear: {e}")
        return False


async def wait_for_login_complete(
    page: Page,
    context: BrowserContext,
    timeout: int = LOGIN_TIMEOUT_SECONDS
) -> dict:
    """
    Wait for user to complete QR code login.
    
    Strategies:
    1. URL redirect to /user/profile
    2. Visual element (Avatar) appearance
    3. Cookie change (if web_session updates)
    4. Login modal disappearance
    
    Args:
        page: Playwright page object
        context: Browser context
        timeout: Maximum wait time in seconds
        
    Returns:
        dict with 'success', 'cookies', 'user_info' keys
    """
    result = {
        "success": False,
        "cookies": {},
        "user_info": None,
        "status": "waiting"
    }
    
    # Capture initial state
    initial_cookies = await context.cookies()
    initial_web_session = next((c['value'] for c in initial_cookies if c['name'] == 'web_session'), None)
    
    print(f"[Browser] 等待登录... (初始 Session: {initial_web_session[:10] + '...' if initial_web_session else 'None'})")
    
    poll_interval = 2000  # 2 seconds
    max_polls = (timeout * 1000) // poll_interval
    
    for i in range(int(max_polls)):
        try:
            await page.wait_for_timeout(poll_interval)
        except Exception as e:
            # Handle browser/page closed by user
            if "Target" in str(e) and "closed" in str(e):
                print("\n[Browser] 用户关闭了浏览器窗口")
                result["status"] = "cancelled"
                result["error"] = "Browser was closed by user"
                return result
            raise
        
        # 1. URL Check
        current_url = page.url
        if "/user/profile/" in current_url:
            print(f"[Browser] 登录成功: 检测到 URL 跳转 ({current_url})")
            result["status"] = "confirmed"
            break
            
        # 2. Visual Check (Avatar)
        try:
            avatar = page.locator(".user-side-bar .avatar-item, .side-bar .avatar-item")
            if await avatar.count() > 0 and await avatar.is_visible():
                print("[Browser] 登录成功: 检测到用户头像")
                result["status"] = "confirmed"
                break
        except:
            pass
            
        # 3. Cookie Change Check
        current_cookies = await context.cookies()
        current_web_session = next((c['value'] for c in current_cookies if c['name'] == 'web_session'), None)
        
        if current_web_session and current_web_session != initial_web_session:
             # Double check: sometimes session refreshes but user not logged in? 
             # Usually a change in web_session + presence of other cookies (like 'sid' or 'ur_id') is a good sign
             print(f"[Browser] 登录成功: 检测到 Session 变化")
             result["status"] = "confirmed"
             result["cookies"] = {c['name']: c['value'] for c in current_cookies}
             break
             
        # 4. Login Modal Gone (Weak check, maybe user closed it?)
        # Only use this if coupled with a valid session cookie
        if current_web_session:
             try:
                 qr_img = page.locator(QR_SELECTORS["qr_image"])
                 if not await qr_img.is_visible():
                     # QR gone and we have session... assume success?
                     # Let's wait one more loop to be sure or verify avatar
                     pass 
             except:
                 pass
            
    if result["status"] == "confirmed":
        # Wait a bit for cookies to settle
        await page.wait_for_timeout(2000)
        
        # Get final cookies
        cookies = await context.cookies()
        result["cookies"] = {c['name']: c['value'] for c in cookies}
        result["success"] = True
    
    return result



