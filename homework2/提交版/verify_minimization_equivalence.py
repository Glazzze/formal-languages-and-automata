# -*- coding: utf-8 -*-
"""
成员 B：调用第一题 are_equivalent 复核成员 C 的最小化结果

复核:
    C 的 minimize_dfa 把原 DFA D 从 7 个状态合并成 3 个状态。
    合并必须「不改变语言」——原 DFA 和最小 DFA 对每个串的接受结果要完全一样。
    这正是第一题 are_equivalent 判定 L(原) == L(最小) 做的事情。

注意：本脚本只复核「语言等价性」。
    「结果已最小」由 C 的状态对标记法证明，不归等价函数管。

运行：在 homework2/提交版 目录下  python verify_minimization_equivalence.py
"""

from dataclasses import replace

from question1_dfa_equivalence import are_equivalent
from question2_dfa_minimization import (
    build_example_dfa_d,
    build_custom_merge_dfa,
    build_custom_minimal_dfa,
    minimize_dfa,
)

def check(label, builder):
    """构造一对原 DFA / 最小 DFA，用第一题函数复核它们的语言等价性。"""
    original = builder()
    minimized, mapping = minimize_dfa(original)

    equivalent = are_equivalent(original, minimized)

    print(f"[{label}]")
    print(f"  状态数: {len(original.states)} -> {len(minimized.states)}")
    print(f"  合并映射: {mapping}")
    print(f"  are_equivalent(原DFA, 最小DFA) = {equivalent}")
    print("  复核结论: " + ("等价，最小化没有改变语言" if equivalent else "不等价，最小化结果有误"))
    print()
    return equivalent


def main():
    print("=== 成员 B：用第一题等价函数复核第二题（成员 C）最小化结果 ===")
    print()

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
    print("[反向对照] 故意清空最小 DFA 的终态")
    print(f"  are_equivalent(原DFA, 错误DFA) = {detect}")
    print("  结论: " + ("成功检出错误" if not detect else "未能检出错误，检查函数"))
    print()

    print("=== 汇总 ===")
    print(f"三个最小化用例复核: {sum(results)}/{len(results)} 等价")
    print("反向对照: " + ("通过（能发现不等价）" if not detect else "失败"))
    if all(results) and not detect:
        print("全部通过：C 的最小化结果与原 DFA 语言一致。")
    else:
        raise AssertionError("复核未通过，请检查 minimize_dfa。")


if __name__ == "__main__":
    main()
