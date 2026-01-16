pub mod api;
pub mod auth;  // New authentication module
pub mod client;
pub mod models;
pub mod utils;
pub mod server;
pub mod signature;  // 纯算法签名服务模块
pub mod agent_manager;  // Python Agent 进程管理

pub use client::XhsClient;
pub use auth::{UserCredentials, CredentialStorage, AuthService};

