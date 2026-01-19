"""
User API Tests
"""
import urllib.request
import json
from .base import BASE_URL, print_success, print_warning, print_error


def test_user_me():
    """测试用户信息 API"""
    print("\n[API] GET /api/user/me")
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/user/me")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            user = data.get("data", {})
            print_success(f"用户: {user.get('nickname')} (ID: {user.get('red_id')})")
            return True
        else:
            print_warning(data.get("msg", "获取失败"))
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False
