# OpenClaw Stock Assistant

基于 OpenClaw 的股票投资助手，支持每日晨报自动生成、技术指标分析、可视化图表和飞书消息推送。

## 效果展示

### 飞书消息效果
![飞书消息](screenshots/feishu-message-1.png)

### 生成的图表
![图表](screenshots/chart-preview.png)

### 终端运行
![终端](screenshots/terminal-1.png)

### 系统自检
![自检](screenshots/system-check.png)

## 特性

- **Zero-Token 设计** - 直接执行 Python 脚本，最小化 AI Token 消耗
- **多数据源支持** - 东方财富、腾讯财经自动故障转移
- **自检修复系统** - 晨报发送前自动检查和修复
- **飞书深度集成** - 支持文字+图片消息推送
- **可视化图表** - 自动生成价格走势、涨跌幅图表
- **定时自动化** - 支持定时生成晨报和收盘报告

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/openclaw-stock-assistant.git
cd openclaw-stock-assistant
```

### 2. 安装依赖

```bash
pip install pandas matplotlib requests
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的飞书配置
```

### 4. 运行测试

```bash
# 生成报告（不发送）
python skills/stock-daily-report.py --code 588000

# 生成并发送到飞书
python skills/stock-daily-report.py --code 588000 --send
```

## 项目结构

```
openclaw-stock-assistant/
├── .env.example              # 环境变量模板
├── README.md                 # 项目说明
├── skills/                   # 核心功能脚本
├── agents/                   # Agent 配置模板
├── screenshots/              # 效果截图
└── examples/                 # 使用示例
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| FEISHU_APP_ID | 飞书应用 ID | 是 |
| FEISHU_APP_SECRET | 飞书应用密钥 | 是 |
| FEISHU_CHAT_ID | 飞书群聊 ID | 是 |
| DEFAULT_STOCK_CODE | 默认股票代码 | 否 |
| WATCH_LIST | 监控股票列表 | 否 |

## 使用示例

### 生成每日晨报

```bash
python skills/stock-daily-report.py --code 588000 --send
```

### 系统自检

```bash
python skills/stock-system-maintenance.py --fix
```

## 许可证

本项目采用 MIT 许可证开源。
