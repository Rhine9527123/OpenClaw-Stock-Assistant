# 故障排除指南

## 数据获取问题

### 东方财富 API 连接失败

**症状**: `[ERROR] 东方财富 API 连接失败`

**原因**:
1. 网络连接问题
2. 东方财富服务器维护
3. IP 被限制

**解决**:
```python
# 系统会自动切换到备用数据源（腾讯财经）
# 无需手动干预
```

**手动测试**:
```bash
curl "https://push2.eastmoney.com/api/qt/stock/get?secid=1.588000&fields=f43,f44"
```

### 数据返回为空

**症状**: 获取到的数据为 None 或空字典

**原因**:
1. 股票代码错误
2. 该股票已退市
3. 非交易时间

**解决**:
```python
# 检查股票代码
# A股: 6位数字，如 588000, 000001
# 港股: 如 00700.HK
# 美股: 如 AAPL
```

## 图表生成问题

### 中文字体显示为方块

**症状**: 图表中的中文显示为 □□□

**解决**:

**Windows**:
```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题
```

**Linux**:
```bash
sudo apt-get install fonts-wqy-zenhei
```

**macOS**:
```bash
brew install font-wqy-zenhei
```

### 图表生成失败

**症状**: `[ERROR] 图表生成失败`

**原因**:
1. matplotlib 未安装
2. 数据为空
3. 权限问题（无法写入 charts/ 目录）

**解决**:
```bash
# 1. 安装依赖
pip install matplotlib

# 2. 检查目录权限
ls -la charts/

# 3. 手动创建目录
mkdir -p charts
```

## 飞书推送问题

### Token 获取失败

**症状**: `[ERROR] 获取飞书 Token 失败`

**原因**:
1. App ID 或 App Secret 错误
2. 应用未发布
3. 网络问题

**解决**:
```bash
# 1. 检查 .env 配置
cat .env | grep FEISHU

# 2. 确认应用已发布
# 飞书开放平台 -> 版本管理与发布 -> 创建版本 -> 发布

# 3. 手动测试 Token 获取
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"YOUR_APP_ID\",\"app_secret\":\"YOUR_APP_SECRET\"}"
```

### 消息发送失败

**症状**: `[ERROR] 消息发送失败`

**原因**:
1. Token 过期
2. Chat ID 错误
3. 消息内容格式错误
4. 超出频率限制

**解决**:
```bash
# 1. 删除旧 Token 缓存
rm .feishu_token

# 2. 检查 Chat ID
# 确保机器人已添加到群聊

# 3. 检查消息长度
# 单条消息不超过 20KB
```

### 图片发送失败

**症状**: 文字消息成功，图片消息失败

**原因**:
1. 图片文件不存在
2. 图片格式不支持（只支持 PNG/JPG）
3. 图片大小超过限制（最大 20MB）

**解决**:
```bash
# 检查图片文件
ls -lh charts/

# 检查图片格式
file charts/*.png
```

## 定时任务问题

### 任务不执行

**症状**: 设置了定时任务，但到时间不触发

**排查步骤**:
```bash
# 1. 检查任务列表
openclaw cron list

# 2. 检查 OpenClaw 服务
openclaw status

# 3. 检查日志
openclaw logs

# 4. 手动触发测试
openclaw cron run --name "每日晨报"
```

### 任务执行但失败

**症状**: 任务显示执行了，但没有收到飞书消息

**排查步骤**:
```bash
# 1. 查看任务日志
openclaw cron logs --name "每日晨报"

# 2. 手动执行脚本测试
python skills/stock-daily-report.py --code 588000 --send

# 3. 检查脚本权限
ls -la skills/*.py
```

## 系统自检问题

### 自检报告发送失败

**症状**: 自检完成，但报告没发送到飞书

**原因**:
1. 飞书配置错误
2. Token 过期
3. 网络问题

**解决**:
```bash
# 单独测试自检功能
python skills/stock-system-maintenance.py --fix

# 带报告发送
python skills/stock-system-maintenance.py --fix --report
```

## 性能问题

### 脚本执行太慢

**症状**: 生成报告需要很长时间（> 2分钟）

**原因**:
1. 网络延迟
2. 数据量大
3. 图表生成复杂

**优化**:
```python
# 1. 减少图表天数
python skills/stock-daily-report.py --code 588000 --days 5

# 2. 使用缓存
# 数据已自动缓存 5 分钟

# 3. 并行处理
# 系统已优化为并行数据收集
```

### 内存占用过高

**症状**: 脚本运行时内存占用大

**解决**:
```python
# 1. 定期清理缓存
python skills/stock-system-maintenance.py

# 2. 限制历史数据保留天数
# 修改 .env 中的 CHART_RETENTION_DAYS
```

## 日志查看

### 查看详细日志

```bash
# 查看自检日志
cat logs/self_check_*.log

# 查看维护日志
cat logs/maintenance_*.log

# 实时查看日志
tail -f logs/*.log
```

### 开启调试模式

编辑 `.env`:
```bash
LOG_LEVEL=DEBUG
```

## 获取帮助

如果以上方法都无法解决问题：

1. **查看日志**: `logs/` 目录下的最新日志文件
2. **提交 Issue**: https://github.com/Rhine9527123/QuantMorning/issues
3. **提供信息**:
   - 操作系统版本
   - Python 版本
   - 错误日志
   - 复现步骤
