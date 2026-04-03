# 打工人日报生成器 🤖

> 摸鱼救星！自动读取 git commits，一键生成四种风格日报。

## 功能

根据你的 git commit 记录，用 AI 自动生成工作日报，支持四种风格：

| 风格 | 说明 |
|------|------|
| `formal` 正式版 | 专业简洁，适合汇报给领导 |
| `moyu` 摸鱼版 | 字数多但信息量少，能水就水 |
| `juanwang` 卷王版 | 加班拼搏，彰显你的努力 |
| `tangping` 躺平版 | 极简主义，能少说就少说 |

## 安装

```bash
git clone https://github.com/superShen0916/daily-report-ai.git
cd daily-report-ai
pip install -r requirements.txt
```

配置 API Key：

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

> 在 [Anthropic Console](https://console.anthropic.com/) 申请 API Key

## 使用

```bash
# 生成今日正式版日报（当前目录仓库）
python daily_report.py

# 摸鱼版
python daily_report.py --style moyu

# 卷王版，统计最近 7 天
python daily_report.py --style juanwang --days 7

# 指定仓库路径
python daily_report.py --repo /path/to/your/project --style formal

# 查看帮助
python daily_report.py --help
```

## 示例输出

**卷王版：**
```
今日工作内容：
1. 独自攻坚核心模块重构，克服重重技术难题，深夜完成关键逻辑优化
2. 紧急响应线上问题，快速定位并修复，确保业务稳定运行
3. 完善单元测试覆盖，对代码质量精益求精

明日计划：
1. 持续推进功能迭代，力争提前完成里程碑目标
2. 协助团队解决技术难点，共同攻克瓶颈
```

**摸鱼版：**
```
今日工作内容：
1. 积极推进相关工作的落地与对齐，持续跟进各项事项进展
2. 针对若干问题进行了深入的沟通与探讨，推动相关工作有序开展
3. 对现有方案进行了优化与完善，赋能后续工作的高效推进

明日计划：
1. 继续跟进相关工作，确保各项事项平稳推进
2. 积极拉通各方，进一步对齐目标
```

## 参数说明

```
--style, -s    日报风格: formal | moyu | juanwang | tangping (默认: formal)
--days,  -d    统计最近几天的 commits (默认: 1)
--repo,  -r    git 仓库路径 (默认: 当前目录)
```

## License

MIT
