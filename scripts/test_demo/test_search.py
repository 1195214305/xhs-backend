"""
Search API Tests
"""
import time
import urllib.parse
import urllib.request
import json
from .base import BASE_URL, print_success, print_warning, print_error


def test_trending():
    """测试热搜 API"""
    print("\n[API] GET /api/search/trending")
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/search/trending")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            queries = data.get("data", {}).get("queries", [])
            print_success("热搜 (Top 3):")
            for q in queries[:3]:
                print(f"       - {q.get('title', q.get('search_word', 'N/A'))}")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")


def test_search_recommend():
    """测试搜索推荐 API"""
    print("\n[API] GET /api/search/recommend (搜索推荐)")
    try:
        keyword = "台州"
        encoded_kw = urllib.parse.quote(keyword)
        req = urllib.request.Request(f"{BASE_URL}/api/search/recommend?keyword={encoded_kw}")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            items = data.get("data", {}).get("sug_items", [])
            print_success(f"获取搜索推荐成功 (关键词: {keyword}, 结果数: {len(items)})")
            for i, item in enumerate(items[:3], 1):
                print(f"       [{i}] {item.get('text', 'N/A')} ({item.get('type', 'unknown')})")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")


def test_search_notes() -> str:
    """测试搜索笔记 API"""
    print("\n[API] POST /api/search/notes (搜索笔记)")
    search_id = f"demo_sid_{int(time.time())}"
    try:
        payload = {
            "keyword": "台州招聘",
            "page": 1,
            "page_size": 10,
            "sort": "general",
            "note_type": 0,
            "search_id": search_id,
            "filters": [],
            "geo": "",
            "image_formats": ["jpg", "webp"]
        }
        data_json = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/api/search/notes", 
            data=data_json, 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            items = data.get("data", {}).get("items", [])
            print_success(f"获取搜索笔记成功 (ID: {search_id}, 结果: {len(items)})")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")
    return search_id


def test_search_onebox(search_id: str):
    """测试 OneBox API"""
    if not search_id:
        return
    print("\n[API] POST /api/search/onebox")
    try:
        payload = {
            "keyword": "台州招聘",
            "search_id": search_id,
            "biz_type": "web_search_user"
        }
        data_json = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/api/search/onebox", 
            data=data_json, 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        print_success(f"OneBox 调用完成: {data.get('msg')}, Success: {data.get('success')}")
    except Exception as e:
        print_error(f"Error: {e}")


def test_search_user(search_id: str):
    """测试用户搜索 API"""
    if not search_id:
        return
    print("\n[API] POST /api/search/usersearch (搜索用户)")
    try:
        payload = {
            "keyword": "台州招聘",
            "search_id": search_id,
            "page": 1,
            "page_size": 15,
            "biz_type": "web_search_user"
        }
        data_json = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BASE_URL}/api/search/usersearch", 
            data=data_json, 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            users = data.get("data", {}).get("users", [])
            print_success(f"获取用户列表成功 (Count: {len(users)})")
            if users:
                user = users[0]
                print(f"       [1] {user.get('name')} (红薯号: {user.get('red_id')})")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")


def test_search_filter(search_id: str):
    """测试 Filter API"""
    if not search_id:
        return
    print("\n[API] GET /api/search/filter")
    try:
        keyword = urllib.parse.quote("台州招聘")
        sid = urllib.parse.quote(search_id)
        url = f"{BASE_URL}/api/search/filter?keyword={keyword}&search_id={sid}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success"):
            filters = data.get("data", {}).get("filters", [])
            print_success(f"获取筛选器成功 (Filter Count: {len(filters)})")
        else:
            print_warning(data.get("msg", "无数据"))
    except Exception as e:
        print_error(f"Error: {e}")
