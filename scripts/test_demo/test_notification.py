"""
Notification API Tests
"""
from .base import make_get_request, print_success, print_warning, print_error


def test_notifications():
    """测试通知 API"""
    endpoints = [
        ("/api/notification/mentions", "评论和@"),
        ("/api/notification/connections", "新增关注"),
        ("/api/notification/likes", "赞和收藏"),
    ]
    
    for path, name in endpoints:
        print(f"\n[API] GET {path} ({name})")
        try:
            data = make_get_request(path)
            if data.get("success"):
                messages = data.get("data", {}).get("message_list", [])
                print_success(f"获取成功 (消息数: {len(messages)})")
            else:
                print_warning(data.get("msg", "无数据"))
        except Exception as e:
            print_error(f"Error: {e}")
