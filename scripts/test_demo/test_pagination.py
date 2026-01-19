"""
Pagination Test for Homefeed

根据 doc/homefeed_pagination.md 的规则实现分页测试
"""
import time
import json
import urllib.request
from .base import BASE_URL, print_success, print_warning, print_error


def test_homefeed_pagination():
    """测试 Homefeed 分页功能 (请求3页)
    
    分页规则:
    - 首次请求: note_index = 任意值 (默认35)
    - 后续请求: note_index = 上次传入值 + 上次返回数量 + 1
    - 特例: 第二次请求 = 0 + 首次返回数量 + 1
    """
    print("\n" + "-" * 50)
    print("[API] POST /api/feed/homefeed/fashion (分页测试)")
    print("-" * 50)
    
    category = "fashion"
    cursor_score = ""
    note_index = 35  # 首次任意值
    refresh_type = 1
    all_cards = []
    
    for page in range(3):
        print(f"\n  📄 Page {page + 1}:")
        try:
            # 构建完整的 payload (服务端会使用默认值，这里只是传递参考)
            payload = {
                "cursor_score": cursor_score,
                "num": 43,
                "refresh_type": refresh_type,
                "note_index": note_index,
                "unread_begin_note_id": "",
                "unread_end_note_id": "",
                "unread_note_count": 0,
                "category": f"homefeed.{category}_v3",
                "search_key": "",
                "need_num": 18,
                "image_formats": ["jpg", "webp", "avif"],
                "need_filter_image": False
            }
            
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f"{BASE_URL}/api/feed/homefeed/{category}",
                data=req_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get("success"):
                items = data.get("data", {}).get("items", [])
                new_cursor = data.get("data", {}).get("cursor_score", "")
                all_cards.extend(items)
                
                print(f"     ✅ 返回 {len(items)} 条")
                print(f"     📍 note_index: {note_index}")
                print(f"     🔗 cursor_score: {new_cursor[:20]}..." if new_cursor else "     🔗 cursor_score: (none)")
                
                # 更新分页参数 (按规则: next = prev + count + 1)
                cursor_score = new_cursor
                if page == 0:
                    # 特例: 第二次请求 = 0 + 首次返回数量 + 1
                    note_index = 0 + len(items) + 1
                else:
                    note_index = note_index + len(items) + 1
                refresh_type = 3  # 后续都是滚动加载
                
                time.sleep(1)  # 间隔1秒，避免风控
            else:
                print_warning(data.get("msg", "无数据"))
                break
        except Exception as e:
            print_error(f"Error: {e}")
            break
    
    print(f"\n  📊 分页测试完成: 共获取 {len(all_cards)} 条笔记")
