# Homefeed 分页payload指南

本文档详细说明 Homefeed (主页发现) 接口的分页机制。

## 接口概述

| 项目 | 说明 |
|------|------|
| 端点 | `POST /api/feed/homefeed/{category}` |
| 用途 | 获取指定频道的笔记 Feed |
| 分页 | 游标分页 (cursor-based) |

## 频道列表

| category 值 | 频道名称 |
|-------------|----------|
| `homefeed_recommend` | 推荐 |
| `homefeed.fashion_v3` | 穿搭 |
| `homefeed.food_v3` | 美食 |
| `homefeed.cosmetics_v3` | 彩妆 |
| `homefeed.movie_and_tv_v3` | 影视 |
| `homefeed.career_v3` | 职场 |
| `homefeed.love_v3` | 情感 |
| `homefeed.household_product_v3` | 家居 |
| `homefeed.gaming_v3` | 游戏 |
| `homefeed.travel_v3` | 旅行 |
| `homefeed.fitness_v3` | 健身 |

## 请求参数

### 完整 Payload 结构

```json
{
  "cursor_score": "",
  "num": 43,
  "refresh_type": 1,
  "note_index": 35,
  "unread_begin_note_id": "",
  "unread_end_note_id": "",
  "unread_note_count": 0,
  "category": "homefeed.fashion_v3",
  "search_key": "",
  "need_num": 18,
  "image_formats": ["jpg", "webp", "avif"],
  "need_filter_image": false
}
```

### 参数分类

| 分类 | 字段 | 类型 | 说明 |
|------|------|------|------|
| **动态** | `cursor_score` | string | 分页游标，首次为空，后续用 Response 返回值 |
| **动态** | `note_index` | int | 累积索引，按公式计算 |
| **动态** | `refresh_type` | int | 1=首次加载，3=滚动加载更多 |
| **业务** | `category` | string | 频道标识 |
| **可固定** | `num` | int | 建议固定为 43 |
| **可固定** | `need_num` | int | 建议 18-20 |
| **可固定** | `image_formats` | array | 建议 `["jpg","webp","avif"]` |
| **可固定** | `search_key` | string | 留空 |
| **可固定** | `need_filter_image` | bool | false |
| **可固定** | `unread_*` | - | 均留空/0 |

首次请求:  note_index = 35

后续请求:  note_index = 上次传入的note_index + 上次返回的card数量 + 1

特例:     第二次请求 = 0 + 首次返回数量 + 1

### 计算示例

| 请求 | note_index | 返回数量 | 下次 note_index |
|:----:|:----------:|:--------:|:---------------:|
| 1 | 35 | 15 | 0 + 15 + 1 = **16** |
| 2 | 16 | 8 | 16 + 8 + 1 = **25** |
| 3 | 25 | 8 | 25 + 8 + 1 = **34** |
| 4 | 34 | 8 | 34 + 8 + 1 = **43** |
| 5 | 43 | 8 | 43 + 8 + 1 = **52** |

### cursor_score 规则

- 首次请求: `cursor_score = ""`
- 后续请求: `cursor_score = Response.data.cursor_score`

## 客户端示例代码

### Python 示例

```python
import requests
import time

BASE_URL = "http://localhost:3005"
category = "homefeed.fashion_v3"

# 初始状态
cursor_score = ""
note_index = 35  # 首次任意值
refresh_type = 1
all_cards = []

# 连续抓取 5 页
for page in range(5):
    payload = {
        "cursor_score": cursor_score,
        "num": 43,
        "refresh_type": refresh_type,
        "note_index": note_index,
        "unread_begin_note_id": "",
        "unread_end_note_id": "",
        "unread_note_count": 0,
        "category": category,
        "search_key": "",
        "need_num": 18,
        "image_formats": ["jpg", "webp", "avif"],
        "need_filter_image": False
    }
    
    resp = requests.post(f"{BASE_URL}/api/feed/homefeed/{category}", json=payload)
    data = resp.json()
    
    if data.get("success"):
        items = data["data"]["items"]
        all_cards.extend(items)
        print(f"Page {page+1}: got {len(items)} cards, total: {len(all_cards)}")
        
        # 更新分页参数
        cursor_score = data["data"]["cursor_score"]
        if page == 0:
            note_index = 0 + len(items) + 1
        else:
            note_index = note_index + len(items) + 1
        refresh_type = 3  # 后续都是滚动加载
        
        time.sleep(1)  # 建议间隔 1 秒，避免触发风控
    else:
        print(f"Error: {data.get('msg')}")
        break

print(f"\nTotal cards collected: {len(all_cards)}")
```

## 注意事项

> [!WARNING]
> **风控提醒**: 请求间隔建议 ≥ 1 秒，短时间内大量请求可能触发反爬机制。

> [!TIP]
> **返回数量**: `need_num` 是期望值，实际返回由服务端决定，通常 ≤ need_num。

> [!NOTE]
> **响应中的 cursor_score**: 用于获取下一页内容，务必保存。

> [!CAUTION]
> **风险提示**: 分页由 `cursor_score` 和 `note_index` 两个参数共同决定，用户在浏览器中鼠标滚动触发的api请求其refresh_type字段为3，每次请求后得到8个新的note_card。若参数填写错误或不符合正常用户行为模式，可能被服务端检测为异常请求，导致账号封禁或警告。**使用本接口产生的风险由用户自行承担**。

