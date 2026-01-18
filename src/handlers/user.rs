//! User HTTP Handlers
//! 
//! Handles: user/me

use axum::{
    extract::State,
    response::IntoResponse,
    Json,
};
use std::sync::Arc;

use crate::api;
use crate::server::AppState;
use crate::models::user::UserMeResponse;

// ============================================================================
// Handlers
// ============================================================================

/// 页面-我
/// 
/// 获取当前登录用户的个人信息
#[utoipa::path(
    get,
    path = "/api/user/me",
    tag = "xhs",
    summary = "页面-我",
    responses(
        (status = 200, description = "当前用户信息（未登录时返回 Not logged in）", body = UserMeResponse)
    )
)]
pub async fn user_me_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    match api::user::get_current_user(&state.api).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}
