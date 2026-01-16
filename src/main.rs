use xhs_rs::server;
use xhs_rs::agent_manager;
use tracing::{info, warn, error};
use tracing_subscriber::fmt::time::OffsetTime;
use time::UtcOffset;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize logging with local timezone
    let offset = UtcOffset::current_local_offset().unwrap_or(UtcOffset::from_hms(8, 0, 0).unwrap());
    let timer = OffsetTime::new(offset, time::macros::format_description!(
        "[year]-[month]-[day]T[hour]:[minute]:[second].[subsecond digits:3]"
    ));
    
    tracing_subscriber::fmt()
        .with_timer(timer)
        .init();
    
    info!("Starting XHS Rust Tools Server...");
    
    // 自动启动 Python Signature Agent
    info!("Starting Python Signature Agent...");
    match agent_manager::start_agent() {
        Ok(_) => info!("Python Agent started successfully"),
        Err(e) => {
            warn!("Failed to start Python Agent: {}. Signature generation will fallback to stored signatures.", e);
        }
    }
    
    // 设置 Ctrl+C 信号处理，确保清理 Agent
    let shutdown = tokio::signal::ctrl_c();
    
    tokio::select! {
        result = server::start_server() => {
            if let Err(e) = result {
                error!("Server error: {}", e);
            }
        }
        _ = shutdown => {
            info!("Received shutdown signal, cleaning up...");
        }
    }
    
    // 清理 Agent 进程
    agent_manager::stop_agent();
    info!("Server stopped");

    Ok(())
}
