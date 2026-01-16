# XHS-RS-TOOLS

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Language](https://img.shields.io/badge/language-Rust%20%7C%20Python-orange.svg)

**[仅供学习研究使用 / For Educational Purposes Only]**

## ⚠️ 免责声明 (Disclaimer)

1.  **学习用途**: 本项目仅供编程爱好者学习 Rust 与 Python 混合开发、逆向分析思路及浏览器自动化技术使用。
2.  **严禁商用**: 严禁将本项目用于任何商业用途、黑灰产或其他非法目的。
3.  **后果自负**: 使用本项目产生的任何后果（包括但不限于账号封禁、法律责任）由使用者自行承担。开发者不对任何衍生作品或使用行为负责。
4.  **接口变动**: 项目基于特定时间点的目标网站状态开发，不保证长期有效性。

## 📖 项目概述

本项目是一个基于 **Rust** (后端 API) 和 **Playwright** (前端采集) 的小红书 API 逆向与自动化工具集。

### 核心实现逻辑 (The "Secret Sauce")

小红书 Web 端接口的风控机制极为严格，核心在于：**Cookie、Request Header 与 X-S 签名强绑定**。
简单的签名生成往往无法通过校验，因为服务端会校验签名的生成环境（Cookie、Canvas 指纹等）是否与请求发起者一致。

本项目采用 **"Capture & Replay" (捕获与重放)** 策略解决此问题：
1.  **真实环境登录**: 使用 Playwright 模拟真实浏览器登录，获取合法的 Session 和 Cookie。
2.  **签名捕获**: 在浏览器操作过程中（如浏览 Feed、搜索），自动拦截并提取官方生成的合法 `X-s` 签名及其对应的完整 Payload。
3.  **持久化会话**: 将 (Cookie + Header + Signature + Payload) 作为一个原子单元存储。
4.  **服务端重放**: Rust 后端通过 API 暴露这些能力。当客户端请求某个接口时，后端会**强制使用**数据库中存储的、已通过验证的 Payload 和签名进行请求，从而完美规避反爬策略。

## 🚀 当前功能 (v1.3.0)

以下均为目前已实现并验证的功能，均基于 **"Pure Algorithm First" (纯算法优先)** 架构：

*   **全频道 Feed 采集**: 支持首页推荐及所有子频道（穿搭、美食、情感、游戏等 11 个频道）的数据获取。
*   **通知页采集**: 获取评论/@、新增关注、**赞和收藏** (NEW)。
*   **图文详情**: 获取指定笔记的评论列表，支持分页，支持动态参数签名。
*   **二维码扫码登录**: 从 DOM 中获取二维码图片信息。
*   **实时登录状态查询**: 通过 `/api/auth/qrcode-status` 轮询扫码状态。
*   **会话持久化**: 登录成功后自动保存 Session。

## 📅 开发日志 (Dev Log)

| 版本 | 日期 | 更新内容 | 备注 |
| :--- | :--- | :--- | :--- |
| **v1.3.0** | 2026-01-16 | **架构重构与接口补全** | |
| | | - 🏗️ **纯算法架构迁移**: 移除 Playwright 签名依赖，全面转向 Python Agent 实时签名 | 性能大幅提升，依赖减少 |
| | | - 🐛 **修复 406 错误**: 修正 Notifications 接口的签名参数处理逻辑 (URL 参数编码) | 解决了 Mentions/Connections 接口调用失败问题 |
| | | - 🎉 **新增接口**: 赞和收藏通知 (`/api/notification/likes`) | |
| | | - 🔧 **增强接口**: Note Page 支持动态 URL 参数签名 | 解决了 `note_id` 和 `xsec_token` 动态变化的签名问题 |
| | | - 🤖 **Agent 管理**: Rust 服务自动管理 Python Agent 生命周期 | 一键启动，无需手动运行 Python 脚本 |
| **v1.2.0** | 2026-01-16 | **新增端点与代码优化** | |
| | | - 🎉 新增 `/api/auth/qrcode-status` | 实时查询扫码登录状态 |
| | | - 🐛 修复 Python 脚本 UTF-8 编码问题 | |
| **v1.1.0** | 2026-01-15 | **新增接口与模块重构** | |
| | | - 新增通知页采集: `/api/notification/mentions` 和 `/connections` | |
| | | - 新增图文详情: `/api/note/page` | |

## 🛠️ 快速开始

### 1. 启动服务
只需运行 Rust 服务，它会自动启动 Python Agent：
```bash
cargo run
```

### 2. 运行测试
```bash
python client_demo.py
```

## 🔌 已验证 API 列表 (Implemented APIs)

| Category | Endpoint | Status | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `/api/auth/session` | ✅ | 检查 Session 有效性 |
| **Feed** | `/api/feed/homefeed/{category}` | ✅ | 11 个垂直频道 (recommend/fashion/food...) |
| **Notification** | `/api/notification/mentions` | ✅ | 获取评论和 @ 通知 |
| **Notification** | `/api/notification/connections` | ✅ | 获取新增关注通知 |
| **Notification** | `/api/notification/likes` | ✅ | **[NEW]** 获取赞和收藏通知 |
| **Note** | `/api/note/page` | ✅ | 获取笔记评论 (支持动态参数签名) |

## 📚 接口文档 (API Docs)

本项目内置 Swagger UI，启动服务后即可访问：
- **地址**: `http://localhost:3005/swagger-ui/`
- **使用**: 可在网页上直接发起请求测试接口。

## 👨‍💻 作者自述 (Author's Note)

### 项目起源与转型
本项目的灵感来源于我对 **RPA (Robotic Process Automation)** 技术及浏览器自动化控制的深入研究。
在前作 `xhs_tools` (1.1k stars) 的维护过程中，我深刻体会到单纯依赖 Python 脚本进行自动化操作的局限性。随着 AI 技术（特别是像 Google Gemini 这样具备强大浏览器理解能力的模型）的崛起，传统的硬编码自动化正在被智能代理所取代。

因此，我决定暂停旧项目的更新，转向探索架构更先进、性能更强劲的解决方案：
*   **架构升级**: 核心网络层采用 **Rust** 重写，确保极高的并发性能与类型安全。
*   **自动化基座**: 保留 Python (Playwright) 作为浏览器控制层，专注于处理复杂的 DOM 交互与人机验证。
*   **API 化**: 将所有功能封装为标准 HTTP 接口，为未来接入 AI Agent 或其他上层应用提供坚实基础。

### 法律/合规声明 (Legal Statement)
**请务必仔细阅读：**

1.  **技术研究性质**: 本项目本质上是一个 **浏览器自动化框架** 的实践案例。所有的“采集”行为均基于模拟真实用户的常规浏览操作（点击、滚动、网络请求），**不包含** 任何破解加密算法、绕过身份验证或其他攻击目标服务器安全机制的代码。
2.  **数据安全**: 本项目**不提供**任何现成的账号或 Cookie。用户必须通过官方渠道（扫码）进行合法登录。项目仅作为数据的本地处理工具，不收集、不上传任何用户敏感信息。
3.  **合规使用**: 请使用者严格遵守《中华人民共和国网络安全法》及目标网站的《用户服务协议》。严禁将本项目用于数据爬取（Scraping）、批量账号控制（Botting）或任何侵犯他人隐私/知识产权的商业行为。
4.  **免责条款**: 开源作者不对任何因使用本项目而导致的法律纠纷或账号损失承担责任。代码仅作为技术交流用途，下载后请于 24 小时内删除。

---
*以技术探索为名，行守法合规之事。*

## 📄 开源协议
MIT License
