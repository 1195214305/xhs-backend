"""
Note API Tests
"""
import urllib.parse
import json
from .base import BASE_URL, make_post_request, print_success, print_warning, print_error
import urllib.request


def test_note_page():
    """测试笔记评论 API"""
    print("\n[API] GET /api/note/page (笔记评论)")
    try:
        test_note_id = "695f0f1d00000000210317c5"
        test_xsec_token = "ABSWQGp8zRp5VzyF6DXyPCnEsSakbUyTGAP3_so8877G4="
        
        params = urllib.parse.urlencode({
            "note_id": test_note_id, "cursor": "",
            "xsec_token": test_xsec_token, "image_formats": "jpg,webp,avif"
        })
        
        req = urllib.request.Request(f"{BASE_URL}/api/note/page?{params}")
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            comments = data.get("data", {}).get("comments", [])
            print_success(f"获取笔记评论成功 (评论数: {len(comments)})")
            for i, comment in enumerate(comments[:3]):
                content = comment.get('content', '无内容')[:30]
                user = comment.get('user_info', {}).get('nickname', '未知')
                print(f"       [{i+1}] {user}: {content}...")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")


def test_note_detail():
    """测试笔记详情 API"""
    print("\n[API] POST /api/note/detail (笔记详情)")
    try:
        test_note_id = "6965aba6000000000e03c2a2"
        test_xsec_token = "AB2m6EqQi1pbRlTwRvPNNhTVyEFDjxlYoZBXgEcCczzEc="
        
        payload = {
            "source_note_id": test_note_id,
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {"need_body_topic": "1"},
            "xsec_source": "pc_feed",
            "xsec_token": test_xsec_token
        }
        data = make_post_request("/api/note/detail", payload)
        
        if data.get("success"):
            items = data.get("data", {}).get("items", [])
            if items:
                note_card = items[0].get("note_card", {})
                title = note_card.get("title", "无标题")[:30]
                user = note_card.get("user", {}).get("nickname", "未知")
                print_success("获取笔记详情成功")
                print(f"       标题: {title}")
                print(f"       作者: {user}")
            else:
                print_warning("获取成功但无数据")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")
