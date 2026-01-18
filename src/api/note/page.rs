use axum::{
    extract::{Query, State},
    response::IntoResponse,
    Json,
};
use serde::Deserialize;
use std::sync::Arc;
use crate::server::AppState;

/// 笔记评论页请求参数
#[derive(Deserialize, utoipa::IntoParams)]
pub struct NotePageParams {
    /// 笔记 ID (必填)
    pub note_id: String,
    /// 分页游标 (可选，首次请求为空)
    #[serde(default)]
    pub cursor: String,
    /// 置顶评论 ID (可选)
    #[serde(default)]
    pub top_comment_id: String,
    /// 图片格式 (默认: jpg,webp,avif)
    #[serde(default = "default_image_formats")]
    pub image_formats: String,
    /// xsec_token (必填)
    pub xsec_token: String,
}

fn default_image_formats() -> String {
    "jpg,webp,avif".to_string()
}

/// 笔记评论列表
/// 
/// 获取指定笔记的评论列表，支持分页。
/// 注：此接口仅返回评论内容，如需获取笔记正文请使用 `/api/note/detail`。
/// 
/// 参数说明：
/// - `note_id`: 笔记ID，从笔记URL或Feed中获取
/// - `cursor`: 分页游标，首次请求为空，后续请求使用上次返回的cursor
/// - `xsec_token`: 安全令牌，从笔记详情页获取
#[utoipa::path(
    get,
    path = "/api/note/page",
    tag = "Note",
    summary = "笔记评论列表",
    description = "获取指定笔记的评论内容（分页）。如需获取笔记正文，请使用 /api/note/detail 接口。",
    params(NotePageParams),
    responses(
        (status = 200, description = "评论列表（原始JSON）"),
        (status = 500, description = "请求失败")
    )
)]
pub async fn get_note_page(
    State(state): State<Arc<AppState>>,
    Query(params): Query<NotePageParams>,
) -> impl IntoResponse {
    match get_note_page_internal(&state.api, params).await {
        Ok(data) => Json(data).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

async fn get_note_page_internal(
    api: &crate::api::XhsApiClient,
    params: NotePageParams,
) -> anyhow::Result<serde_json::Value> {
    // 构造完整 URL（note_page 是 GET 请求，参数在 URL 中）
    let url = format!(
        "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={}&cursor={}&top_comment_id={}&image_formats={}&xsec_token={}",
        params.note_id,
        params.cursor,
        params.top_comment_id,
        params.image_formats,
        urlencoding::encode(&params.xsec_token)
    );
    
    // 使用公共模块发送请求
    let text = api.get_with_url("note_page", &url).await?;
    let response: serde_json::Value = serde_json::from_str(&text)?;
    Ok(response)
}
