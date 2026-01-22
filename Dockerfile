# 多阶段构建 - Rust 编译阶段
# 使用最新稳定版 Rust 1.84+
FROM rust:1.84-slim-bookworm AS rust-builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制 Cargo 文件
COPY Cargo.toml Cargo.lock ./

# 创建虚拟 src 以缓存依赖
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release || true
RUN rm -rf src

# 复制实际源码并构建
COPY src ./src
RUN touch src/main.rs && cargo build --release

# 最终运行阶段
FROM python:3.11-slim-bookworm

WORKDIR /app

# 安装系统依赖和 supervisord
RUN apt-get update && apt-get install -y \
    libssl3 \
    ca-certificates \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 安装 Playwright 依赖
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN playwright install chromium

# 复制 Rust 二进制文件
COPY --from=rust-builder /app/target/release/xhs-rs /app/xhs-rs

# 复制 Python 脚本
COPY scripts ./scripts

# 创建 supervisord 配置
RUN echo '[supervisord]\n\
nodaemon=true\n\
logfile=/dev/null\n\
logfile_maxbytes=0\n\
\n\
[program:python-agent]\n\
command=python -m uvicorn scripts.agent_server:app --host 127.0.0.1 --port 8765\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
\n\
[program:rust-server]\n\
command=/app/xhs-rs\n\
directory=/app\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
' > /etc/supervisor/conf.d/app.conf

# 设置环境变量
ENV PORT=3000
ENV RUST_LOG=info
ENV PYTHON_AGENT_URL=http://127.0.0.1:8765

# 暴露端口
EXPOSE 3000

# 使用 supervisord 同时启动两个服务
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/app.conf"]
