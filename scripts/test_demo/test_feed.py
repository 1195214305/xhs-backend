"""
Feed API Tests
"""
import json
import urllib.request
from .base import BASE_URL, print_success, print_warning, print_error


def test_homefeed():
    """测试推荐流 API"""
    print("\n[API] POST /api/feed/homefeed/recommend")
    try:
        req_data = json.dumps({
            "cursor_score": "", "num": 5, "refresh_type": 1,
            "note_index": 0, "category": "homefeed_recommend"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"{BASE_URL}/api/feed/homefeed/recommend",
            data=req_data, headers={'Content-Type': 'application/json'}, method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            items = data.get("data", {}).get("items", [])
            print_success(f"获取推荐流成功 (共 {len(items)} 条)")
            for i, item in enumerate(items[:3]):
                if "note_card" in item:
                    note = item["note_card"]
                    title = note.get('display_title', note.get('title', '无标题'))[:25]
                    author = note.get('user', {}).get('nickname', '未知')
                    print(f"       [{i+1}] {title}... (作者: {author})")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")


def test_category_feeds():
    """测试所有分类 Feed API"""
    categories = [
        ("fashion", "穿搭"), ("food", "美食"), ("cosmetics", "彩妆"),
        ("movie_and_tv", "影视"), ("career", "职场"), ("love", "情感"),
        ("household_product", "家居"), ("gaming", "游戏"),
        ("travel", "旅行"), ("fitness", "健身"),
    ]
    
    for cat_key, cat_name in categories:
        print(f"\n[API] POST /api/feed/homefeed/{cat_key} ({cat_name})")
        try:
            req_data = json.dumps({
                "cursor_score": "", "num": 5, "refresh_type": 1,
                "note_index": 0, "category": f"homefeed.{cat_key}_v3"
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{BASE_URL}/api/feed/homefeed/{cat_key}",
                data=req_data, headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get("success"):
                items = data.get("data", {}).get("items", [])
                print_success(f"获取{cat_name}成功 (共 {len(items)} 条)")
            else:
                print_warning(data.get("msg", "无数据"))
        except Exception as e:
            print_error(f"Error: {e}")
