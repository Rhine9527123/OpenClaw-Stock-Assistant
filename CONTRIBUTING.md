# 贡献指南

感谢你对 OpenClaw Stock Assistant 的兴趣！以下是参与贡献的指南。

## ?? 如何贡献

### 报告 Bug

1. 确认 Bug 尚未被报告
2. 创建新的 Issue，包含：
   - 清晰的标题
   - 重现步骤
   - 预期行为 vs 实际行为
   - 环境信息（Python版本、操作系统等）
   - 相关日志或截图

### 提交新功能

1. 先创建 Issue 讨论你的想法
2. 等待维护者反馈
3. Fork 仓库并创建分支
4. 实现功能并添加测试
5. 提交 Pull Request

### 改进文档

文档改进总是受欢迎的！可以直接提交 PR 修改：
- README.md
- docs/ 目录下的文档
- 代码注释

## ?? 代码规范

### Python 代码风格

- 遵循 [PEP 8](https://pep8.org/) 规范
- 使用 4 空格缩进
- 最大行长度 100 字符
- 使用有意义的变量名

### 提交信息规范

```
<type>: <subject>

<body>

<footer>
```

**类型 (type):**
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例:**
```
feat: 添加多股票同时监控功能

支持同时监控多只股票，生成对比报告。

Closes #123
```

## ?? 测试

### 运行测试

```bash
# 安装测试依赖
pip install pytest

# 运行测试
pytest tests/
```

### 添加测试

- 为新功能添加单元测试
- 确保测试覆盖主要代码路径
- 测试应该独立、可重复

## ?? Pull Request 流程

1. **Fork 仓库**
   ```bash
   git clone https://github.com/yourusername/openclaw-stock-assistant.git
   cd openclaw-stock-assistant
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

4. **推送到远程**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**
   - 填写清晰的标题和描述
   - 关联相关 Issue
   - 等待代码审查

## ?? 开发路线图

### 短期目标
- [ ] 添加更多技术指标（KDJ、布林带等）
- [ ] 支持港股、美股数据
- [ ] 添加邮件通知渠道

### 中期目标
- [ ] Web 管理界面
- [ ] 历史数据回测
- [ ] 策略模拟交易

### 长期目标
- [ ] AI 智能分析建议
- [ ] 多用户支持
- [ ] 移动端 App

## ?? 沟通渠道

- **Issue**: 功能请求和 Bug 报告
- **Discussion**: 一般性讨论
- **Email**: 私密问题

## ?? 行为准则

- 尊重所有参与者
- 欢迎新手，耐心解答
- 建设性批评
- 专注于技术本身

## ?? 感谢

感谢所有贡献者！你们的付出让这个项目变得更好。

---

如有疑问，欢迎随时联系维护者。
