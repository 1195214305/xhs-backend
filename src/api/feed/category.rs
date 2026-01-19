use axum::{
    extract::{Path, State},
    response::IntoResponse,
    Json,
};
use std::sync::Arc;
use crate::{
    api::XhsApiClient,
    models::feed::HomefeedResponse,
    server::AppState,
};

/// Get feed for specific category (页面-主页发现-频道)
/// Path param: category (e.g., "fashion", "food", "travel")
/// 
/// 注意：分页参数目前由服务端默认值控制
/// 完整分页规则请参阅 doc/homefeed_pagination.md
#[utoipa::path(
    post,
    path = "/api/feed/homefeed/{category}",
    summary = "主页发现-频道",
    description = "获取指定频道的内容流。分页规则请参阅 doc/homefeed_pagination.md\n\n可用频道:\n- recommend: 推荐\n- fashion: 穿搭\n- food: 美食\n- cosmetics: 彩妆\n- movie_and_tv: 影视\n- career: 职场\n- love: 情感\n- household_product: 家居\n- gaming: 游戏\n- travel: 旅行\n- fitness: 健身",
    params(
        ("category" = String, Path, description = "频道名称: recommend/fashion/food/cosmetics/movie_and_tv/career/love/household_product/gaming/travel/fitness")
    ),
    responses(
        (status = 200, description = "Success", body = HomefeedResponse),
        (status = 500, description = "Internal Error")
    ),
    tag = "Feed"
)]
pub async fn get_category_feed(
    State(state): State<Arc<AppState>>,
    Path(category): Path<String>,
) -> impl axum::response::IntoResponse {
    match get_feed_internal(&state.api, &category).await {
        Ok(data) => Json(data).into_response(),
        Err(e) => Json(serde_json::json!({
            "code": -1,
            "success": false,
            "msg": e.to_string(),
            "data": null
        })).into_response(),
    }
}

async fn get_feed_internal(
    api: &XhsApiClient,
    category: &str,
) -> anyhow::Result<HomefeedResponse> {
    // Construct signature key: home_feed_fashion, home_feed_food, etc.
    let signature_key = if category == "recommend" {
        "home_feed_recommend".to_string()
    } else {
        format!("home_feed_{}", category)
    };

    // Use XhsApiClient with default payload
    let text = api.post(&signature_key).await?;
    let feed_resp: HomefeedResponse = serde_json::from_str(&text)?;
    Ok(feed_resp)
}

