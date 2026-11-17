# -*- coding: utf-8 -*-
"""
成员 B：调用第一题 are_equivalent 复核成员 C 的最小化结果

复核:
    C 的 minimize_dfa 把原 DFA D 从 7 个状态合并成 3 个状态。
    合并必须「不改变语言」——原 DFA 和最小 DFA 对每个串的接受结果要完全一样。
    这正是第一题 are_equivalent 判定 L(原) == L(最小) 做的事情。

注意：本脚本只复核「语言等价性」。
    「结果已最小」由 C 的状态对标记法证明，不归等价函数管。

运行：在 homework2 目录下  python verify_minimization.py
"""

import os
import sys
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                       # 找 question1.py
sys.path.insert(0, os.path.join(HERE, "C"))    # 找 C/automaton.py 和 C/question2.py

from question1 import are_equivalent           # 第一题的通用等价函数
from question2 import (                        # 第二题（成员 C）的构造与最小化
    build_example_dfa_d,
    build_custom_merge_dfa,
    build_custom_minimal_dfa,
    minimize_dfa,
)

_lines = []


def emit(text=""):
    print(text)
    _lines.append(text)


def check(label, builder):
    """构造一对原 DFA / 最小 DFA，用第一题函数复核它们的语言等价性。"""
    original = builder()
    minimized, mapping = minimize_dfa(original)

    # 直接调用！question1 已做接口适配，能接收 C 的 Automaton
    equivalent = are_equivalent(original, minimized)

    emit(f"[{label}]")
    emit(f"  状态数: {len(original.states)} -> {len(minimized.states)}")
    emit(f"  合并映射: {mapping}")
    emit(f"  are_equivalent(原DFA, 最小DFA) = {equivalent}")
    emit("  复核结论: " + ("等价，最小化没有改变语言" if equivalent else "不等价，最小化结果有误"))
    emit()
    return equivalent


def main():
    emit("=== 成员 B：用第一题等价函数复核第二题（成员 C）最小化结果 ===")
    emit()

    results = [
        check("作业题 DFA D（7 状态 -> 3 状态）", build_example_dfa_d),
        check("自构：合并 B/C 并删除不可达 X", build_custom_merge_dfa),
        check("自构：本来就已最小的 2 状态 DFA", build_custom_minimal_dfa),
    ]

    # 反向对照：把最小 DFA 的终态清空，验证以确保这个函数真能抓出错误
    original = build_example_dfa_d()
    minimized, _ = minimize_dfa(original)
    wrong = replace(minimized, accepting_states=set())
    detect = are_equivalent(original, wrong)
    emit("[反向对照] 故意清空最小 DFA 的终态")
    emit(f"  are_equivalent(原DFA, 错误DFA) = {detect}")
    emit("  结论: " + ("成功检出错误" if not detect else "未能检出错误，检查函数"))
    emit()

    emit("=== 汇总 ===")
    emit(f"三个最小化用例复核: {sum(results)}/{len(results)} 等价")
    emit("反向对照: " + ("通过（能发现不等价）" if not detect else "失败"))
    if all(results) and not detect:
        emit("全部通过：C 的最小化结果与原 DFA 语言一致。")
    else:
        raise AssertionError("复核未通过，请检查 minimize_dfa。")

    with open(os.path.join(HERE, "复核运行结果.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(_lines) + "\n")


if __name__ == "__main__":
    main()
