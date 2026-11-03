#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短视频脚本文案合规扫描器
用法：
  python3 check_compliance.py <文件或目录> [更多路径...]
命中违禁词时：
  - 打印命中的分类、词、所在行号、上下文
  - 退出码 1（可用于 CI/发布卡点）
无命中退出码 0。
说明：这是机械初筛，不能替代人工合规判断；驾培/教培/单招类请另看 references/compliance.md。
"""
import os
import re
import sys

# 承诺类（驾培/教培/单招 + 通用收益）
PROMISE_WORDS = [
    "包过", "保过", "必过", "稳过", "包通过", "保证通过", "100%通过", "不过退款",
    "包录取", "保录取", "稳上", "包上", "内部名额", "内部指标", "内部渠道", "原题",
    "包拿证", "包拿", "交钱就能上", "包毕业",
    "稳赚", "必赚", "躺赚", "零风险", "无风险", "暴富", "年入百万", "月入百万",
    "保底收益", "包回本", "保证成交", "包成交", "包涨粉", "保证涨粉",
]

# 极限词（广告法），用词组避免“最后/最近”误报
ABSOLUTE_WORDS = [
    "最好", "最佳", "最强", "最优", "最低", "最高", "最大", "最便宜", "最划算",
    "第一名", "全网第一", "行业第一", "全国第一",
    "唯一", "首家", "首选", "顶级", "顶尖", "国家级", "世界级",
    "绝对", "永远", "100%", "百分百", "全网最低", "史上最",
]

# 违规私域引流
DRAIN_WORDS = ["加微信", "加我微信", "微信号", "加微", "vx", "VX", "V信", "威信",
               "加qq", "加QQ", "QQ群", "私信我微信"]
PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")

# 敏感（正能量红线粗筛）
SENSITIVE_WORDS = ["领导干部", "摆拍", "滞销"]

# 警示语境：同一行出现这些词时，违禁词是被当作“反面教材”引用的，不计入命中
# 例如：凡是跟你“包成交”的，扭头就走 / “包涨粉包成交”是坑
NEGATION_MARKERS = [
    "是坑", "扭头就走", "别信", "不要", "凡是", "警惕", "骗局", "跑路", "套路",
    "忽悠", "被坑", "坑了", "不靠谱", "骗子", "避免", "拒绝", "伪", "划走",
    "最怕", "避坑", "隐患",
]

CATEGORIES = [
    ("承诺类（包过/保底/暴富等）", PROMISE_WORDS),
    ("极限词（广告法）", ABSOLUTE_WORDS),
    ("违规私域引流（应导粉丝群）", DRAIN_WORDS),
    ("敏感/高风险表述", SENSITIVE_WORDS),
]

TEXT_SUFFIX = (".txt", ".md", ".srt", ".csv", ".json")


def has_negation_context(line):
    return any(marker in line for marker in NEGATION_MARKERS)


def find_word_hits(line, words):
    """按词长倒序匹配，长词命中后吞掉与之重叠的短词（如 加微信 吞掉 加微）。"""
    found = []
    occupied = []
    for w in sorted(words, key=len, reverse=True):
        start = 0
        while True:
            idx = line.find(w, start)
            if idx == -1:
                break
            span = (idx, idx + len(w))
            if not any(idx < e and idx + len(w) > s for s, e in occupied):
                warn = has_negation_context(line)
                found.append((w, span, warn))
                occupied.append(span)
            start = idx + len(w)
    return found


def scan_text(path):
    hits = []
    suppressed = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for lineno, line in enumerate(f, 1):
            for category, words in CATEGORIES:
                for w, _span, warn in find_word_hits(line, words):
                    if warn:
                        suppressed += 1
                        continue
                    hits.append((category, w, lineno, line.strip()[:60]))
            m = PHONE_RE.search(line)
            if m:
                hits.append(("疑似手机号（不应直接出现在字幕/评论）", m.group(0), lineno, line.strip()[:60]))
    return hits, suppressed


def collect_files(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                for n in names:
                    if n.lower().endswith(TEXT_SUFFIX):
                        files.append(os.path.join(root, n))
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"[跳过] 路径不存在：{p}", file=sys.stderr)
    return files


def main():
    if len(sys.argv) < 2:
        print("用法：python3 check_compliance.py <文件或目录> [更多路径...]", file=sys.stderr)
        sys.exit(2)
    files = collect_files(sys.argv[1:])
    if not files:
        print("没有可扫描的文本文件。", file=sys.stderr)
        sys.exit(2)

    total = 0
    suppressed_total = 0
    for path in files:
        hits, suppressed = scan_text(path)
        suppressed_total += suppressed
        if hits:
            print(f"\n## {path}")
            for category, word, lineno, ctx in hits:
                print(f"  - [{category}] 命中「{word}」 第{lineno}行：{ctx}")
            total += len(hits)

    print("\n" + "=" * 40)
    note = f"（已自动跳过 {suppressed_total} 处“避坑/警示”语境中的反面引用）" if suppressed_total else ""
    if total:
        print(f"扫描完成：发现 {total} 处疑似违规，请逐条修改后重扫。{note}")
        print("人工复核见 references/compliance.md。")
        sys.exit(1)
    print(f"扫描完成：未发现违禁词。{note}")
    print("仍需人工确认数据真实性、案例授权与行业表述。")
    sys.exit(0)


if __name__ == "__main__":
    main()
