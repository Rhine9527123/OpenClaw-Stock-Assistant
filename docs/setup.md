# 部署指南

## 环境要求

### 系统要求
- **操作系统**: Windows 10/11, macOS, Linux
- **Python**: 3.7 或更高版本
- **内存**: 至少 2GB RAM
- **磁盘空间**: 至少 500MB 可用空间

### 必需软件
- Python 3.7+
- pip (Python 包管理器)
- Git (可选，用于克隆仓库)

## 快速开始

### 方式一：使用 Git 克隆

```bash
# 1. 克隆仓库
git clone https://github.com/Rhine9527123/QuantMorning.git
cd QuantMorning

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 5. 运行测试
python skills/stock-daily-report.py --code 588000
```

### 方式二：直接下载

```bash
# 1. 下载源码
wget https://github.com/Rhine9527123/QuantMorning/archive/main.zip
unzip main.zip
cd QuantMorning-main

# 2-5. 同上
```

## 详细配置

### 1. Python 环境配置

#### Windows
```powershell
# 检查 Python 版本
python --version

# 安装依赖
pip install pandas matplotlib requests
```

#### macOS
```bash
# 使用 Homebrew 安装 Python
brew install python

# 安装依赖
pip3 install pandas matplotlib requests
```

#### Linux (Ubuntu/Debian)
```bash
# 安装 Python 和 pip
sudo apt update
sudo apt install python3 python3-pip

# 安装依赖
pip3 install pandas matplotlib requests
```

### 2. 飞书配置

#### 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录后点击「创建应用」
3. 选择「企业自建应用」
4. 填写应用名称（如：QuantMorning）
5. 点击「创建」

#### 获取应用凭证

1. 进入应用详情页
2. 点击「凭证与基础信息」
3. 复制 `App ID` 和 `App Secret`
4. 填入 `.env` 文件

#### 开启机器人能力

1. 点击「机器人」菜单
2. 开启「机器人」开关
3. 设置机器人名称和头像

#### 获取 Chat ID

**方法一：通过群设置**
1. 在飞书群聊中点击右上角「...」
2. 选择「群设置」
3. 点击「群机器人」
4. 添加你创建的应用机器人
5. Chat ID 会在回调中显示

**方法二：通过 API**
```bash
# 获取用户或群的 open_id
curl -X POST \
  https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H 'Content-Type: application/json' \
  -d '{
    "app_id": "YOUR_APP_ID",
    "app_secret": "YOUR_APP_SECRET"
  }'
```

### 3. 环境变量配置

编辑 `.env` 文件：

```bash
# 飞书配置（必填）
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_CHAT_ID=oc_xxxxxxxxxxxxxxxxxxxxxxxx

# 股票配置（可选）
DEFAULT_STOCK_CODE=588000
WATCH_LIST=588000,000001,000858

# 定时配置（可选）
TIMEZONE=Asia/Shanghai
MORNING_REPORT_TIME=0 9 * * 1-5
CLOSE_REPORT_TIME=0 20 * * 1-5

# 数据配置（可选）
CACHE_MINUTES=5
CHART_RETENTION_DAYS=7
REPORT_RETENTION_DAYS=30
```

### 4. OpenClaw 配置

#### 安装 OpenClaw

```bash
# 安装 OpenClaw CLI
npm install -g openclaw

# 验证安装
openclaw --version
```

#### 配置定时任务

```bash
# 添加晨报 Agent
openclaw cron add \
  --name "每日晨报" \
  --schedule "0 9 * * 1-5" \
  --command "python skills/stock-daily-report.py --code 588000 --send"

# 添加收盘报告 Agent
openclaw cron add \
  --name "收盘报告" \
  --schedule "0 20 * * 1-5" \
  --command "python skills/stock-daily-report.py --code 588000 --send"

# 添加自检 Agent
openclaw cron add \
  --name "系统自检" \
  --schedule "40 7 * * *" \
  --command "python skills/stock-system-maintenance.py --fix --report"
```

## 验证安装

### 1. 测试数据获取

```bash
python -c "
from skills.stock_daily_report import DailyReportGenerator
gen = DailyReportGenerator()
data = gen.collect_technical_data('588000')
print(data)
"
```

### 2. 测试图表生成

```bash
python skills/stock-daily-report.py --code 588000
# 检查 charts/ 目录是否生成图片
```

### 3. 测试飞书推送

```bash
python skills/stock-daily-report.py --code 588000 --send
# 检查飞书是否收到消息
```

### 4. 测试系统自检

```bash
python skills/stock-system-maintenance.py --fix
```

## 常见问题

### Q1: 安装依赖时出错

**问题**: `pip install` 报错

**解决**:
```bash
# 更新 pip
pip install --upgrade pip

# 使用国内镜像
pip install pandas matplotlib requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 中文显示乱码

**问题**: 图表中文字符显示为方块

**解决**:
```bash
# Windows: 安装中文字体
# 下载 SimHei.ttf 放到 C:\Windows\Fonts\

# Linux: 安装中文字体
sudo apt install fonts-wqy-zenhei

# macOS: 安装中文字体
brew install font-wqy-zenhei
```

### Q3: Token 获取失败

**问题**: 飞书 Token 获取失败

**解决**:
1. 检查 App ID 和 App Secret 是否正确
2. 确认应用已发布（版本管理与发布）
3. 检查网络连接
4. 查看飞书开放平台日志

### Q4: 定时任务不执行

**问题**: 设置了定时任务但没有触发

**解决**:
```bash
# 检查定时任务列表
openclaw cron list

# 检查 OpenClaw 服务状态
openclaw status

# 手动触发测试
openclaw cron run --name "每日晨报"
```

### Q5: 数据源获取失败

**问题**: 东方财富 API 返回错误

**解决**:
1. 检查网络连接
2. 确认股票代码正确
3. 查看是否有 IP 限制
4. 系统会自动切换到备用数据源（腾讯财经）

## 生产环境部署

### 使用 systemd (Linux)

创建服务文件 `/etc/systemd/system/quantmorning.service`:

```ini
[Unit]
Description=QuantMorning Stock Assistant
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/QuantMorning
Environment=PYTHONPATH=/path/to/QuantMorning
ExecStart=/usr/bin/python3 skills/stock-daily-report.py --code 588000 --send
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable quantmorning
sudo systemctl start quantmorning
```

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "skills/stock-daily-report.py", "--code", "588000", "--send"]
```

构建和运行：
```bash
docker build -t quantmorning .
docker run -d --env-file .env quantmorning
```

## 更新维护

### 更新代码

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl restart quantmorning
```

### 备份数据

```bash
# 备份报告和图表
tar -czvf backup-$(date +%Y%m%d).tar.gz charts/ reports/ logs/

# 备份配置
cp .env .env.backup
```

## 获取帮助

- **GitHub Issues**: https://github.com/Rhine9527123/QuantMorning/issues
- **文档**: https://github.com/Rhine9527123/QuantMorning/tree/main/docs
- **邮件**: your-email@example.com
