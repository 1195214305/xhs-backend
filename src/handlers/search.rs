//! Search-related HTTP Handlers
//! 
//! Handles: trending, recommend, notes, onebox, filter, usersearch

use axum::{
    extract::{State, Query},
    response::IntoResponse,
    Json,
};
use std::sync::Arc;

use crate::api;
use crate::server::AppState;
use crate::models::search::{
    SearchNotesRequest, SearchNotesResponse,
    SearchOneboxRequest, SearchOneboxResponse,
    SearchFilterResponse,
    SearchUserRequest, SearchUserResponse,
    QueryTrendingResponse,
    SearchRecommendResponse,
};

// ============================================================================
// Query Parameter Structs
// ============================================================================

#[derive(serde::Deserialize, utoipa::IntoParams)]
pub struct SearchParams {
    pub keyword: String,
}

#[derive(serde::Deserialize, utoipa::IntoParams)]
pub struct SearchFilterParams {
    pub keyword: String,
    pub search_id: String,
}

// ============================================================================
// Handlers
// ============================================================================

/// 猜你想搜
/// 
/// 获取小红书首页搜索框的热门搜索推荐词
#[utoipa::path(
    get,
    path = "/api/search/trending",
    tag = "xhs",
    summary = "猜你想搜",
    responses(
        (status = 200, description = "热门搜索词列表", body = QueryTrendingResponse)
    )
)]
pub async fn query_trending_handler(
    State(state): State<Arc<AppState>>,
) -> impl IntoResponse {
    match api::search::query_trending(&state.api).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

/// 搜索推荐 (联想词)
/// 
/// 根据关键词获取搜索建议
#[utoipa::path(
    get,
    path = "/api/search/recommend",
    tag = "Search",
    summary = "搜索推荐",
    params(
        SearchParams
    ),
    responses(
        (status = 200, description = "搜索推荐列表", body = SearchRecommendResponse)
    )
)]
pub async fn search_recommend_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SearchParams>,
) -> impl IntoResponse {
    match api::search::recommend_search(&state.api, &params.keyword).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

/// 搜索笔记
/// 
/// 获取关键词搜索的笔记列表
#[utoipa::path(
    post,
    path = "/api/search/notes",
    tag = "Search",
    summary = "搜索笔记",
    request_body = SearchNotesRequest,
    responses(
        (status = 200, description = "笔记列表", body = SearchNotesResponse)
    )
)]
pub async fn search_notes_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<SearchNotesRequest>,
) -> impl IntoResponse {
    match api::search::search_notes(&state.api, req).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

/// 搜索 OneBox
/// 
/// 获取搜索聚合信息
#[utoipa::path(
    post,
    path = "/api/search/onebox",
    tag = "Search",
    summary = "搜索 OneBox",
    request_body = SearchOneboxRequest,
    responses(
        (status = 200, description = "OneBox 结果", body = SearchOneboxResponse)
    )
)]
pub async fn search_onebox_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<SearchOneboxRequest>,
) -> impl IntoResponse {
    match api::search::search_onebox(&state.api, req).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

/// 搜索筛选器
/// 
/// 获取搜索筛选选项
#[utoipa::path(
    get,
    path = "/api/search/filter",
    tag = "Search",
    summary = "搜索筛选器",
    params(
        SearchFilterParams
    ),
    responses(
        (status = 200, description = "筛选选项", body = SearchFilterResponse)
    )
)]
pub async fn search_filter_handler(
    State(state): State<Arc<AppState>>,
    Query(params): Query<SearchFilterParams>,
) -> impl IntoResponse {
    match api::search::search_filter(&state.api, &params.keyword, &params.search_id).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

/// 搜索用户
/// 
/// 搜索小红书用户
#[utoipa::path(
    post,
    path = "/api/search/usersearch",
    tag = "Search",
    summary = "搜索用户",
    request_body = SearchUserRequest,
    responses(
        (status = 200, description = "用户搜索结果", body = SearchUserResponse)
    )
)]
pub async fn search_user_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<SearchUserRequest>,
) -> impl IntoResponse {
    match api::search::search_user(&state.api, req).await {
        Ok(res) => Json(res).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}
