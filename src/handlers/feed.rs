//! Feed HTTP Handlers
//! 
//! Handles: homefeed/recommend

use axum::{
    extract::State,
    response::IntoResponse,
    Json,
};
use std::sync::Arc;

use crate::api;
use crate::server::AppState;
use crate::models::feed::{HomefeedRequest, HomefeedResponse};

// ============================================================================
// Handlers
// ============================================================================

/// 页面-主页发现-推荐
/// 
/// 获取小红书主页推荐内容流
#[utoipa::path(
    post,
    path = "/api/feed/homefeed/recommend",
    tag = "xhs",
    summary = "页面-主页发现-推荐",
    request_body = HomefeedRequest,
    responses(
        (status = 200, description = "主页推荐内容", body = HomefeedResponse)
    )
)]
pub async fn homefeed_recommend_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    match api::feed::recommend::get_homefeed_recommend(&state.api).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}
