#!/usr/bin/env python3
"""
打工人日报生成器 - 自动从 git commits 生成日报
用法: python daily_report.py [--style formal|moyu|juanwang|tangping] [--days 1] [--repo /path] [--provider deepseek]
"""

import subprocess
import argparse
import sys
import os
from datetime import datetime, timedelta


# ── 支持的 AI 提供商 ────────────────────────────────────────────────────────
# type: "openai_compat" 表示兼容 OpenAI 接口，使用 openai SDK
#       "anthropic"     表示使用原生 anthropic SDK
#       "gemini"        表示使用原生 google-generativeai SDK
PROVIDERS = {
    # ── 国际 ──
    "anthropic": {
        "name": "Claude (Anthropic)",
        "env":  "ANTHROPIC_API_KEY",
        "type": "anthropic",
        "model": "claude-opus-4-6",
    },
    "gemini": {
        "name": "Gemini (Google)",
        "env":  "GEMINI_API_KEY",
        "type": "gemini",
        "model": "gemini-2.0-flash",
    },
    # ── 国内 ──
    "deepseek": {
        "name": "DeepSeek",
        "env":  "DEEPSEEK_API_KEY",
        "type": "openai_compat",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "moonshot": {
        "name": "Kimi (Moonshot)",
        "env":  "MOONSHOT_API_KEY",
        "type": "openai_compat",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
    },
    "qwen": {
        "name": "通义千问 (Alibaba)",
        "env":  "DASHSCOPE_API_KEY",
        "type": "openai_compat",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-turbo",
    },
    "doubao": {
        "name": "豆包 (ByteDance)",
        "env":  "DOUBAO_API_KEY",
        "type": "openai_compat",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-pro-4k",
    },
    "zhipu": {
        "name": "智谱 GLM",
        "env":  "ZHIPU_API_KEY",
        "type": "openai_compat",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-4-flash",
    },
    "minimax": {
        "name": "MiniMax",
        "env":  "MINIMAX_API_KEY",
        "type": "openai_compat",
        "base_url": "https://api.minimax.chat/v1",
        "model": "abab6.5s-chat",
    },
    "baichuan": {
        "name": "百川 (Baichuan)",
        "env":  "BAICHUAN_API_KEY",
        "type": "openai_compat",
        "base_url": "https://api.baichuan-ai.com/v1",
        "model": "Baichuan4-Turbo",
    },
    "hunyuan": {
        "name": "混元 (Tencent)",
        "env":  "HUNYUAN_API_KEY",
        "type": "openai_compat",
        "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
        "model": "hunyuan-lite",
    },
    "spark": {
        "name": "星火 (iFlytek)",
        "env":  "SPARK_API_KEY",
        "type": "openai_compat",
        "base_url": "https://spark-api-open.xf-yun.com/v1",
        "model": "lite",
    },
}

# 自动检测优先级顺序
PROVIDER_PRIORITY = [
    "anthropic", "deepseek", "moonshot", "qwen", "doubao",
    "zhipu", "minimax", "baichuan", "hunyuan", "spark", "gemini",
]


# ── 日报风格 ────────────────────────────────────────────────────────────────
STYLES = {
    "formal": {
        "name": "正式版",
        "desc": "专业、简洁，适合汇报给领导",
        "prompt": "请用正式、专业的语气生成日报，条理清晰，突出工作成果和价值。"
    },
    "moyu": {
        "name": "摸鱼版",
        "desc": "字数多但信息量少，能水就水",
        "prompt": "请用模糊、冗长但听起来很忙的语气生成日报，多用'推进''跟进''落地''对齐'等词，字数多但尽量不透露具体信息。"
    },
    "juanwang": {
        "name": "卷王版",
        "desc": "加班、拼搏、突破，彰显你的努力",
        "prompt": "请用充满激情、强调艰辛付出的语气生成日报，要体现'攻坚克难''独自扛下''深夜奋战'等感觉，让领导觉得你非常努力。"
    },
    "tangping": {
        "name": "躺平版",
        "desc": "极简主义，能少说就少说",
        "prompt": "请用极简风格生成日报，越短越好，但要涵盖主要工作内容，最好控制在3句话以内。"
    }
}


# ── Git 工具 ────────────────────────────────────────────────────────────────
def get_git_commits(repo_path: str, days: int) -> str:
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
            cwd=repo_path, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"错误：无法读取 git 历史，请确认路径是 git 仓库：{repo_path}")
        print(f"详情：{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("错误：未找到 git 命令，请先安装 git")
        sys.exit(1)


def get_repo_name(repo_path: str) -> str:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path, capture_output=True, text=True
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            return url.rstrip("/").split("/")[-1].replace(".git", "")
    except Exception:
        pass
    return os.path.basename(os.path.abspath(repo_path))


# ── Prompt 构建 ─────────────────────────────────────────────────────────────
def build_prompt(commits: str, style: str, repo_name: str, days: int) -> tuple[str, str]:
    style_config = STYLES[style]
    period = "今日" if days == 1 else f"近 {days} 天"

    system_prompt = f"""你是一个帮程序员写工作日报的助手。
根据提供的 git commit 记录，生成一份工作日报。
{style_config['prompt']}
要求：
- 用中文输出
- 不要直接复制 commit message，要转化为工作描述
- 不要加任何前缀说明，直接输出日报内容
- 格式：先写今日工作内容（分点），再写明日计划（1-2条）"""

    user_message = f"""项目：{repo_name}
时间：{period}工作内容
风格：{style_config['name']} - {style_config['desc']}

git commit 记录：
{commits}

请生成日报："""

    return system_prompt, user_message


# ── AI 调用 ─────────────────────────────────────────────────────────────────
def generate_with_openai_compat(system_prompt: str, user_message: str, api_key: str, base_url: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        print("错误：请安装 openai 库: pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content


def generate_with_anthropic(system_prompt: str, user_message: str, api_key: str, model: str) -> str:
    try:
        import anthropic
    except ImportError:
        print("错误：请安装 anthropic 库: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text


def generate_with_gemini(system_prompt: str, user_message: str, api_key: str, model: str) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        print("错误：请安装 google-generativeai 库: pip install google-generativeai")
        sys.exit(1)

    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model_name=model, system_instruction=system_prompt)
    response = m.generate_content(user_message)
    return response.text


def detect_provider() -> str | None:
    """按优先级自动检测可用的 provider"""
    for name in PROVIDER_PRIORITY:
        p = PROVIDERS[name]
        if os.environ.get(p["env"]):
            return name
    return None


def generate_report(commits: str, style: str, repo_name: str, days: int, provider_name: str | None) -> str:
    if provider_name is None:
        provider_name = detect_provider()

    if provider_name is None:
        print("错误：未找到任何 API Key，请设置以下任意一个环境变量：\n")
        for name, p in PROVIDERS.items():
            print(f"  export {p['env']:<25} # {p['name']}")
        sys.exit(1)

    p = PROVIDERS[provider_name]
    api_key = os.environ.get(p["env"])
    if not api_key:
        print(f"错误：指定了 --provider {provider_name}，但未设置环境变量 {p['env']}")
        sys.exit(1)

    print(f"🤖 使用 {p['name']} ({p['model']}) 生成...\n")
    system_prompt, user_message = build_prompt(commits, style, repo_name, days)

    if p["type"] == "anthropic":
        return generate_with_anthropic(system_prompt, user_message, api_key, p["model"])
    elif p["type"] == "gemini":
        return generate_with_gemini(system_prompt, user_message, api_key, p["model"])
    else:
        return generate_with_openai_compat(system_prompt, user_message, api_key, p["base_url"], p["model"])


# ── CLI ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="打工人日报生成器 - 自动从 git commits 生成日报",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
风格说明:
  formal    正式版 - 专业简洁，适合汇报给领导
  moyu      摸鱼版 - 字数多但信息量少，能水就水
  juanwang  卷王版 - 加班拼搏，彰显你的努力
  tangping  躺平版 - 极简主义，能少说就少说

支持的 AI 提供商（设置对应 Key 后自动检测，或用 --provider 指定）:
{"".join(f"  {name:<12} {p['env']}" + chr(10) for name, p in PROVIDERS.items())}
示例:
  python daily_report.py
  python daily_report.py --style moyu
  python daily_report.py --provider deepseek --style juanwang --days 7
  python daily_report.py --repo /path/to/your/project --style formal
        """
    )
    parser.add_argument("--style", "-s", choices=list(STYLES.keys()), default="formal",
                        help="日报风格 (默认: formal)")
    parser.add_argument("--days", "-d", type=int, default=1,
                        help="统计最近几天的 commits (默认: 1)")
    parser.add_argument("--repo", "-r", default=".",
                        help="git 仓库路径 (默认: 当前目录)")
    parser.add_argument("--provider", "-p", choices=list(PROVIDERS.keys()), default=None,
                        help="指定 AI 提供商（默认自动检测）")
    parser.add_argument("--list-providers", action="store_true",
                        help="列出所有支持的 AI 提供商")

    args = parser.parse_args()

    if args.list_providers:
        print("支持的 AI 提供商：\n")
        for name, p in PROVIDERS.items():
            status = "✓ 已配置" if os.environ.get(p["env"]) else "  未配置"
            print(f"  {status}  {name:<12} {p['name']:<20} 环境变量: {p['env']}")
        return

    repo_path = os.path.abspath(args.repo)
    if not os.path.isdir(repo_path):
        print(f"错误：路径不存在：{repo_path}")
        sys.exit(1)

    print(f"📂 仓库：{repo_path}")
    print(f"🎨 风格：{STYLES[args.style]['name']} - {STYLES[args.style]['desc']}")
    print(f"📅 统计：最近 {args.days} 天\n")

    commits = get_git_commits(repo_path, args.days)
    if not commits:
        period = "今天" if args.days == 1 else f"最近 {args.days} 天"
        print(f"⚠️  {period}没有找到任何 commit 记录")
        sys.exit(0)

    commit_lines = commits.strip().split("\n")
    print(f"📝 找到 {len(commit_lines)} 条 commit，正在生成日报...\n")

    repo_name = get_repo_name(repo_path)
    report = generate_report(commits, args.style, repo_name, args.days, args.provider)

    print("=" * 50)
    print(f"  {STYLES[args.style]['name']}日报")
    print("=" * 50)
    print(report)
    print("=" * 50)


if __name__ == "__main__":
    main()
