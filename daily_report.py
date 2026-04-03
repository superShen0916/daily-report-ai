#!/usr/bin/env python3
"""
打工人日报生成器 - 自动从 git commits 生成日报
用法: python daily_report.py [--style formal|moyu|juanwang|tangping] [--days 1] [--repo /path]
"""

import subprocess
import argparse
import sys
import os
from datetime import datetime, timedelta

try:
    import anthropic
except ImportError:
    print("请先安装依赖: pip install anthropic")
    sys.exit(1)


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


def get_git_commits(repo_path: str, days: int) -> str:
    """获取指定天数内的 git commits"""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--no-merges", "--author-date-is-committer-date"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.strip()
        if not commits:
            return ""
        return commits
    except subprocess.CalledProcessError as e:
        print(f"错误：无法读取 git 历史，请确认路径是 git 仓库：{repo_path}")
        print(f"详情：{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("错误：未找到 git 命令，请先安装 git")
        sys.exit(1)


def get_repo_name(repo_path: str) -> str:
    """获取仓库名称"""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            return url.rstrip("/").split("/")[-1].replace(".git", "")
    except Exception:
        pass
    return os.path.basename(os.path.abspath(repo_path))


def generate_report(commits: str, style: str, repo_name: str, days: int) -> str:
    """调用 Claude API 生成日报"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误：请设置环境变量 ANTHROPIC_API_KEY")
        print("  export ANTHROPIC_API_KEY=your_api_key")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
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

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return message.content[0].text


def main():
    parser = argparse.ArgumentParser(
        description="打工人日报生成器 - 自动从 git commits 生成日报",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
风格说明:
  formal    正式版 - 专业简洁，适合汇报给领导
  moyu      摸鱼版 - 字数多但信息量少，能水就水
  juanwang  卷王版 - 加班拼搏，彰显你的努力
  tangping  躺平版 - 极简主义，能少说就少说

示例:
  python daily_report.py
  python daily_report.py --style moyu
  python daily_report.py --style juanwang --days 7
  python daily_report.py --repo /path/to/your/project --style formal
        """
    )
    parser.add_argument(
        "--style", "-s",
        choices=list(STYLES.keys()),
        default="formal",
        help="日报风格 (默认: formal)"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=1,
        help="统计最近几天的 commits (默认: 1)"
    )
    parser.add_argument(
        "--repo", "-r",
        default=".",
        help="git 仓库路径 (默认: 当前目录)"
    )

    args = parser.parse_args()

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
    report = generate_report(commits, args.style, repo_name, args.days)

    print("=" * 50)
    print(f"  {STYLES[args.style]['name']}日报")
    print("=" * 50)
    print(report)
    print("=" * 50)


if __name__ == "__main__":
    main()
