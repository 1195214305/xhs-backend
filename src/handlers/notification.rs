//! Notification HTTP Handlers
//! 
//! Handles: mentions, connections, likes

use axum::{
    extract::State,
    response::IntoResponse,
    Json,
};
use std::sync::Arc;

use crate::api;
use crate::server::AppState;

// ============================================================================
// Handlers
// ============================================================================

/// 通知页-评论和@
/// 
/// 获取评论和@通知列表
#[utoipa::path(
    get,
    path = "/api/notification/mentions",
    tag = "xhs",
    summary = "通知页-评论和@",
    responses(
        (status = 200, description = "评论和@通知列表")
    )
)]
pub async fn mentions_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    match api::notification::mentions::get_mentions(&state.api).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

/// 通知页-新增关注
/// 
/// 获取新增关注通知列表
#[utoipa::path(
    get,
    path = "/api/notification/connections",
    tag = "xhs",
    summary = "通知页-新增关注",
    responses(
        (status = 200, description = "新增关注通知列表")
    )
)]
pub async fn connections_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    match api::notification::connections::get_connections(&state.api).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

/// 通知页-赞和收藏
/// 
/// 获取赞和收藏通知列表
#[utoipa::path(
    get,
    path = "/api/notification/likes",
    tag = "xhs",
    summary = "通知页-赞和收藏",
    responses(
        (status = 200, description = "赞和收藏通知列表")
    )
)]
pub async fn likes_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    match api::notification::likes::get_likes(&state.api).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}
