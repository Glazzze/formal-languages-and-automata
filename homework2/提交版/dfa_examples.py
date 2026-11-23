# -*- coding: utf-8 -*-
"""第二次编程作业的自动机数据：题图用例 + 自构用例。

本文件由成员 A（廖敏佳）维护，第一、二题都从这里取题图数据：

* 第一题反例：作业 PDF 第 1 页 / 课件 lec4-rs1 第 34 页的两个自动机。
* 第二题输入：作业 PDF 第 2 页的 7 状态自动机 D。

自构用例部分收录成员 B、C 已交付的用例（注释中注明来源），这样最终提交
包只需要一份数据；各题直接引用本文件的构造函数。

运行 ``python dfa_examples.py`` 可打印全部自动机，便于人工核对。
"""

from __future__ import annotations

from typing import List

from dfa import Automaton


# ----------------------------------------------------------------------
# 第一题：题图反例（lec4-rs1 第 34 页）
# ----------------------------------------------------------------------
def question1_m1() -> Automaton:
    """题图上面的自动机 M1：接受末尾连续 1 的个数为奇数的串。

    A --0--> A, A --1--> B, B --0/1--> A；初态 A，终态 {B}。
    """
    return Automaton(
        states=["A", "B"],
        alphabet=["0", "1"],
        start_state="A",
        accepting_states={"B"},
        transitions={
            "A": {"0": "A", "1": "B"},
            "B": {"0": "A", "1": "A"},
        },
    )


def question1_m2() -> Automaton:
    """题图下面的自动机 M2：接受 ε 以及“以 1 结尾的串”。

    C 既是初态又是终态；C --1--> C, C --0--> D, D --0--> D, D --1--> C。
    最短区分串是 ε：M2 接受、M1 拒绝。
    """
    return Automaton(
        states=["C", "D"],
        alphabet=["0", "1"],
        start_state="C",
        accepting_states={"C"},
        transitions={
            "C": {"0": "D", "1": "C"},
            "D": {"0": "D", "1": "C"},
        },
    )


def question1_counterexample():
    """Return ``(M1, M2)``, the two automatons from the assignment figure."""
    return question1_m1(), question1_m2()


# ----------------------------------------------------------------------
# 第一题：自构正例（成员 B 提供，与 question1_dfa_equivalence.py 的 build_positive_example 一致）
# ----------------------------------------------------------------------
def question1_p1() -> Automaton:
    """2 状态 DFA P1：接受 {w ∈ {0,1}* | w 以 0 结尾}。"""
    return Automaton(
        states=["A", "B"],
        alphabet=["0", "1"],
        start_state="A",
        accepting_states={"B"},
        transitions={
            "A": {"0": "B", "1": "A"},
            "B": {"0": "B", "1": "A"},
        },
    )


def question1_p2() -> Automaton:
    """3 状态 DFA P2：与 P1 同语言，但 X、Y 是两个不可区分的非终态。

    X --0--> Z, X --1--> Y; Y --0--> Z, Y --1--> X; Z --0--> Z, Z --1--> X。
    合并 X、Y 后得到 P1，因此 L(P2) = L(P1) = “以 0 结尾”。
    """
    return Automaton(
        states=["X", "Y", "Z"],
        alphabet=["0", "1"],
        start_state="X",
        accepting_states={"Z"},
        transitions={
            "X": {"0": "Z", "1": "Y"},
            "Y": {"0": "Z", "1": "X"},
            "Z": {"0": "Z", "1": "X"},
        },
    )


def question1_positive_example():
    """Return ``(P1, P2)``, a self-built pair of equivalent DFAs."""
    return question1_p1(), question1_p2()


# ----------------------------------------------------------------------
# 第一题：字母表不同的边界用例（用于规范化接口自检）
# ----------------------------------------------------------------------
def empty_language(alphabet: List[str]) -> Automaton:
    """DFA for ∅ over the given alphabet (one non-accepting sink)."""
    states = ["S"]
    return Automaton(
        states=states,
        alphabet=list(alphabet),
        start_state="S",
        accepting_states=set(),
        transitions={"S": {symbol: "S" for symbol in alphabet}},
    )


def epsilon_only(alphabet: List[str]) -> Automaton:
    """DFA for {ε} over the given alphabet."""
    return Automaton(
        states=["S", "T"],
        alphabet=list(alphabet),
        start_state="S",
        accepting_states={"S"},
        transitions={
            "S": {symbol: "T" for symbol in alphabet},
            "T": {symbol: "T" for symbol in alphabet},
        },
    )


# ----------------------------------------------------------------------
# 第二题：题图 7 状态自动机 D（作业 PDF 第 2 页）
# ----------------------------------------------------------------------
def question2_dfa_d() -> Automaton:
    """题图 DFA D。

    状态：IS0, S1, FS2, S3, S4, FS5, FS6
    初态：IS0；终态：{FS2, FS5, FS6}；字母表：{0, 1}
    注意题面特别说明：IS0 在 0 和 1 上都转移到 S1。
    """
    return Automaton(
        states=["IS0", "S1", "FS2", "S3", "S4", "FS5", "FS6"],
        alphabet=["0", "1"],
        start_state="IS0",
        accepting_states={"FS2", "FS5", "FS6"},
        transitions={
            "IS0": {"0": "S1", "1": "S1"},
            "S1": {"0": "FS2", "1": "FS5"},
            "FS2": {"0": "IS0", "1": "IS0"},
            "S3": {"0": "S4", "1": "S4"},
            "S4": {"0": "FS5", "1": "FS6"},
            "FS5": {"0": "S3", "1": "S3"},
            "FS6": {"0": "IS0", "1": "IS0"},
        },
    )


# ----------------------------------------------------------------------
# 第二题：自构用例（成员 C 提供，与 question2_dfa_minimization.py 的构造函数一致）
# ----------------------------------------------------------------------
def question2_merge_dfa() -> Automaton:
    """自构 DFA：B、C 等价可合并，X 不可达应删除。"""
    return Automaton(
        states=["A", "B", "C", "X"],
        alphabet=["0", "1"],
        start_state="A",
        accepting_states={"B", "C"},
        transitions={
            "A": {"0": "B", "1": "C"},
            "B": {"0": "B", "1": "B"},
            "C": {"0": "C", "1": "C"},
            "X": {"0": "X", "1": "X"},
        },
    )


def question2_minimal_dfa() -> Automaton:
    """自构 DFA：识别“1 的个数为偶数”的两状态最小 DFA。"""
    return Automaton(
        states=["E", "O"],
        alphabet=["0", "1"],
        start_state="E",
        accepting_states={"E"},
        transitions={
            "E": {"0": "E", "1": "O"},
            "O": {"0": "O", "1": "E"},
        },
    )


# ----------------------------------------------------------------------
# 公共类的部分转移表约定示例
# ----------------------------------------------------------------------
def partial_endswith_1() -> Automaton:
    """A partial table for “strings ending in 1”, completed with a trap.

    ``P --0--> P`` and ``P --1--> Q`` are given; Q's transitions are missing.
    ``from_partial`` fills them with ``__trap__`` and appends that state, so
    the resulting DFA is total and still accepts exactly the strings ending
    in 1 (``11`` reaches the trap because Q is not a final state).
    """
    return Automaton.from_partial(
        states=["P", "Q"],
        alphabet=["0", "1"],
        start_state="P",
        accepting_states={"Q"},
        transitions={"P": {"0": "P", "1": "Q"}},
        trap_state="__trap__",
    )


def main() -> None:
    examples = [
        ("第一题反例 M1（题图）", question1_m1),
        ("第一题反例 M2（题图）", question1_m2),
        ("第一题正例 P1（B 自构）", question1_p1),
        ("第一题正例 P2（B 自构）", question1_p2),
        ("第二题 DFA D（题图）", question2_dfa_d),
        ("第二题自构：合并 + 删除不可达", question2_merge_dfa),
        ("第二题自构：已最小", question2_minimal_dfa),
        ("部分转移表补陷阱", partial_endswith_1),
    ]
    for label, builder in examples:
        builder().pretty_print(label)
        print()


if __name__ == "__main__":
    main()
