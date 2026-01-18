//! Note Detail API
//! 
//! Fetches the actual content of a note (title, description, images, etc.)

use axum::{
    extract::State,
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use utoipa::ToSchema;
use crate::server::AppState;

/// 笔记详情请求参数
#[derive(Debug, Clone, Deserialize, Serialize, ToSchema)]
pub struct NoteDetailRequest {
    /// 笔记 ID (必填)，例如 "6965aba6000000000e03c2a2"
    pub source_note_id: String,
    /// 图片格式 (默认: ["jpg", "webp", "avif"])
    #[serde(default = "default_image_formats")]
    pub image_formats: Vec<String>,
    /// 额外参数 (可选)，例如 {"need_body_topic": "1"}
    #[serde(default)]
    pub extra: Option<serde_json::Value>,
    /// xsec_source (默认: pc_feed)
    #[serde(default = "default_xsec_source")]
    pub xsec_source: String,
    /// xsec_token (必填，从 feed 接口返回的笔记信息中获取)
    pub xsec_token: String,
}

fn default_image_formats() -> Vec<String> {
    vec!["jpg".to_string(), "webp".to_string(), "avif".to_string()]
}

fn default_xsec_source() -> String {
    "pc_feed".to_string()
}

/// 笔记详情响应 (简化)
#[derive(Debug, Clone, Deserialize, Serialize, ToSchema)]
pub struct NoteDetailResponse {
    pub code: i32,
    pub success: bool,
    #[serde(default)]
    pub msg: Option<String>,
    #[serde(default)]
    pub data: Option<serde_json::Value>,
}

/// 获取笔记详情
/// 
/// 获取指定笔记的完整内容，包括标题、正文、图片、标签、互动数据等。
/// 这是点击 Feed 中某篇笔记后弹出的详情页内容。
/// 
/// 参数说明：
/// - `source_note_id`: 笔记ID，从 Feed 或搜索结果中获取
/// - `xsec_token`: 安全令牌，从 Feed 返回的笔记信息中获取
#[utoipa::path(
    post,
    path = "/api/note/detail",
    tag = "Note",
    summary = "笔记详情",
    description = "获取笔记完整内容（标题、正文、图片、标签、互动数据）。",
    request_body = NoteDetailRequest,
    responses(
        (status = 200, description = "笔记详情", body = NoteDetailResponse),
        (status = 500, description = "请求失败")
    )
)]
pub async fn get_note_detail(
    State(state): State<Arc<AppState>>,
    Json(req): Json<NoteDetailRequest>,
) -> impl IntoResponse {
    match get_note_detail_internal(&state.api, req).await {
        Ok(data) => Json(data).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

async fn get_note_detail_internal(
    api: &crate::api::XhsApiClient,
    req: NoteDetailRequest,
) -> anyhow::Result<NoteDetailResponse> {
    let path = "/api/sns/web/v1/feed";
    
    // 构造请求体
    let mut payload = serde_json::json!({
        "source_note_id": req.source_note_id,
        "image_formats": req.image_formats,
        "xsec_source": req.xsec_source,
        "xsec_token": req.xsec_token,
    });
    
    // 添加 extra 字段（如果存在）
    if let Some(extra) = req.extra {
        payload["extra"] = extra;
    }
    
    let text = api.post_algo(path, payload).await?;
    let response: NoteDetailResponse = serde_json::from_str(&text)?;
    Ok(response)
}
