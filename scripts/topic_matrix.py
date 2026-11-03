#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六维裂变选题矩阵生成器
用法：
  python3 topic_matrix.py --brief brief.json [--limit 30]
brief.json 示例：
{
  "industry": "驾校",
  "motifs": ["学员为什么还没报名就先刷抖音比价"],
  "forms": ["口播", "跟拍", "图文"],
  "audiences": ["新手学生", "家长", "同行老板"],
  "stages": ["认知", "信息搜集", "方案评估", "购买决策", "使用复购"],
  "timings": ["日常", "开学季", "寒暑假"],
  "depths": ["知识层", "经验层", "认知层"],
  "emotions": ["恐惧", "好奇", "共鸣"]
}
缺省维度会使用内置默认值。输出 Markdown 选题卡。
"""
import argparse
import json
import sys
from itertools import product

DEFAULTS = {
    "forms": ["口播", "跟拍", "访谈", "剧情", "图文", "直播切片"],
    "audiences": ["新手", "进阶", "高端"],
    "stages": ["认知", "信息搜集", "方案评估", "购买决策", "使用复购"],
    "timings": ["日常"],
    "depths": ["知识层", "经验层", "认知层"],
    "emotions": ["恐惧", "好奇", "共鸣", "爽感"],
}

# 决策场景对应的内容目的，用于自动拼选题
STAGE_PURPOSE = {
    "认知": "唤醒需求：行业痛点/风险警示/认知纠偏",
    "信息搜集": "提供信息：方法干货/工具资源/对比",
    "方案评估": "建立优势：案例拆解/数据对比/客户证言",
    "购买决策": "消除顾虑：常见疑问/服务流程/售后",
    "使用复购": "促进复购转介绍：使用教程/成功案例",
}

# 情绪对应的钩子建议
EMOTION_HOOK = {
    "恐惧": "痛点直击/后果预警式钩子",
    "愤怒": "情绪爆发式钩子",
    "焦虑": "痛点直击式钩子",
    "好奇": "悬念提问/反常识钩子",
    "共鸣": "强共鸣提问式钩子",
    "爽感": "结果前置式钩子",
}


def load_brief(path):
    with open(path, "r", encoding="utf-8") as f:
        brief = json.load(f)
    for key, val in DEFAULTS.items():
        if key not in brief or not brief[key]:
            brief[key] = val
    brief.setdefault("industry", "本行业")
    brief.setdefault("motifs", [])
    return brief


def build_matrix(brief, limit):
    lines = []
    lines.append(f"# 选题矩阵 · {brief['industry']}")
    lines.append("")
    if brief["motifs"]:
        lines.append("## 一、母题（三核生根）")
        for i, m in enumerate(brief["motifs"], 1):
            lines.append(f"{i}. {m}")
        lines.append("")

    lines.append("## 二、六维裂变选题卡")
    lines.append("")
    lines.append("| 编号 | 受众 | 决策场景 | 时机 | 推荐形式 | 深度 | 情绪 | 选题方向 | 钩子建议 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")

    count = 0
    # 消费端组合：受众 × 决策场景 × 时机；生产端按规则轮换推荐
    forms = brief["forms"]
    depths = brief["depths"]
    emotions = brief["emotions"]
    for idx, (aud, stage, timing) in enumerate(
        product(brief["audiences"], brief["stages"], brief["timings"]), 1
    ):
        if idx > limit:
            break
        form = forms[(idx - 1) % len(forms)]
        depth = depths[(idx - 1) % len(depths)]
        emotion = emotions[(idx - 1) % len(emotions)]
        motif = brief["motifs"][(idx - 1) % len(brief["motifs"])] if brief["motifs"] else f"{brief['industry']}的典型问题"
        direction = f"{STAGE_PURPOSE.get(stage, stage)}：围绕「{motif}」"
        hook = EMOTION_HOOK.get(emotion, "悬念提问式钩子")
        lines.append(f"| {idx:02d} | {aud} | {stage} | {timing} | {form} | {depth} | {emotion} | {direction} | {hook} |")
        count = idx

    lines.append("")
    lines.append(f"共生成 {count} 个选题卡。建议：每个选题先按四段式写脚本，再过合规检查。")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="六维裂变选题矩阵生成器")
    ap.add_argument("--brief", required=True, help="brief.json 路径")
    ap.add_argument("--limit", type=int, default=30, help="最多生成多少个选题卡（默认30）")
    args = ap.parse_args()
    try:
        brief = load_brief(args.brief)
    except FileNotFoundError:
        print(f"找不到 brief 文件：{args.brief}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"brief.json 格式错误：{e}", file=sys.stderr)
        sys.exit(2)
    print(build_matrix(brief, args.limit))


if __name__ == "__main__":
    main()
