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

## 支持的 AI 提供商

| 提供商 | 参数 | 环境变量 |
|--------|------|----------|
| Claude (Anthropic) | `--provider anthropic` | `ANTHROPIC_API_KEY` |
| Gemini (Google) | `--provider gemini` | `GEMINI_API_KEY` |
| DeepSeek | `--provider deepseek` | `DEEPSEEK_API_KEY` |
| Kimi (Moonshot) | `--provider moonshot` | `MOONSHOT_API_KEY` |
| 通义千问 (阿里) | `--provider qwen` | `DASHSCOPE_API_KEY` |
| 豆包 (字节) | `--provider doubao` | `DOUBAO_API_KEY` |
| 智谱 GLM | `--provider zhipu` | `ZHIPU_API_KEY` |
| MiniMax | `--provider minimax` | `MINIMAX_API_KEY` |
| 百川 | `--provider baichuan` | `BAICHUAN_API_KEY` |
| 混元 (腾讯) | `--provider hunyuan` | `HUNYUAN_API_KEY` |
| 星火 (讯飞) | `--provider spark` | `SPARK_API_KEY` |

设置对应环境变量后**自动检测**，无需手动指定；也可用 `--provider` 强制指定。

## 安装

```bash
git clone https://github.com/superShen0916/daily-report-ai.git
cd daily-report-ai
pip install -r requirements.txt

# 如果用 Claude，额外安装
pip install anthropic

# 如果用 Gemini，额外安装
pip install google-generativeai
```

设置 API Key（设置你用的那个即可）：

```bash
export DEEPSEEK_API_KEY=your_key      # 推荐，价格便宜
export MOONSHOT_API_KEY=your_key      # Kimi
export DASHSCOPE_API_KEY=your_key     # 通义千问
export ANTHROPIC_API_KEY=your_key     # Claude
# ... 其他见上表
```

## 使用

```bash
# 生成今日日报（自动检测 AI）
python daily_report.py

# 摸鱼版
python daily_report.py --style moyu

# 指定用 DeepSeek，卷王版，统计最近 7 天
python daily_report.py --provider deepseek --style juanwang --days 7

# 指定仓库路径
python daily_report.py --repo /path/to/your/project --style formal

# 查看所有已配置的 AI 提供商
python daily_report.py --list-providers
```

## 参数说明

```
--style, -s      日报风格: formal | moyu | juanwang | tangping (默认: formal)
--days,  -d      统计最近几天的 commits (默认: 1)
--repo,  -r      git 仓库路径 (默认: 当前目录)
--provider, -p   指定 AI 提供商（默认自动检测）
--list-providers 列出所有支持的提供商及配置状态
```

## License

MIT
