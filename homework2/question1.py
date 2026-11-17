# -*- coding: utf-8 -*-
"""
question1.py —— 形式语言与自动机 小组作业 第一题：DFA 语言等价判定
"""

from collections import deque


class DFA:
    """确定型有限自动机（公共数据类型）

    name       : 便于打印的名字
    states     : 状态名集合（用字符串表示，两个自动机可以用相同的状态名）
    alphabet   : 字母表符号集合
    start      : 初态名
    finals     : 终态名集合
    transitions: dict[(state, symbol)] -> state，必须是全函数
    """

    def __init__(self, name, states, alphabet, start, finals, transitions):
        self.name = name
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.start = start
        self.finals = set(finals)
        self.transitions = dict(transitions)

        # 合法性检查：防止出现自动机写错的情况
        assert start in self.states, f"{name}: 初态 {start} 不在状态集合中"
        assert self.finals <= self.states, f"{name}: 终态集合含未知状态"
        for (q, a), nxt in self.transitions.items():
            assert q in self.states and nxt in self.states, f"{name}: 转移含未知状态"
            assert a in self.alphabet, f"{name}: 转移含字母表外符号 {a}"
        for q in self.states:                      # DFA 要求转移是全函数
            for a in self.alphabet:
                assert (q, a) in self.transitions, f"{name}: 缺少 δ({q},{a})"

    def delta(self, q, a):
        """转移函数 δ(q, a)"""
        return self.transitions[(q, a)]

    def is_final(self, q):
        return q in self.finals

    def __repr__(self):
        return f"DFA({self.name})"


def _find_witness(a1, a2):
    """返回一条“只被其中一个自动机接受”的区分串；若两语言等价则返回 None。

    这正是乘积 DFA 中从初态对出发、到达“恰有一个分量为终态”的状态对的路径标签。
    """
    if a1.alphabet != a2.alphabet:
        return "<字母表不同>"          # 字母表不同则语言不可能相同

    start_pair = (a1.start, a2.start)
    visited = {start_pair}
    queue = deque([(start_pair, "")])   # (状态对, 到达它的字符串)

    while queue:
        (q, r), word = queue.popleft()

        # 异或：恰好一个分量为终态 -> word 属于 symmetric difference
        if (q in a1.finals) != (r in a2.finals):
            return word

        for a in sorted(a1.alphabet):   # 排序只为输出可复现
            nxt = (a1.delta(q, a), a2.delta(r, a))
            if nxt not in visited:      # 不可达状态天然被跳过
                visited.add(nxt)
                queue.append((nxt, word + a))

    return None


def are_equivalent(a1, a2):
    """判定两个 DFA 接受的语言是否等价：等价 True，不等价 False。"""
    return _find_witness(a1, a2) is None


# ----------------------------------------------------------------------
# 反例：第1题图（课件第 34 页）的两个自动机
# ----------------------------------------------------------------------
def build_counterexample():
    # 上面那个：A 初态、B 终态
    #   A --0--> A, A --1--> B, B --0/1--> A
    #   接受“以 1 结尾”的非空串
    m1 = DFA(
        name="M1(题图-上)",
        states=["A", "B"],
        alphabet=["0", "1"],
        start="A",
        finals=["B"],
        transitions={
            ("A", "0"): "A",
            ("A", "1"): "B",
            ("B", "0"): "A",
            ("B", "1"): "A",
        },
    )

    # 下面那个：C 既是初态又是终态、D 非终态
    #   C --1--> C, C --0--> D, D --0--> D, D --1--> C
    #   接受“以 1 结尾的串”以及空串 ε
    m2 = DFA(
        name="M2(题图-下)",
        states=["C", "D"],
        alphabet=["0", "1"],
        start="C",
        finals=["C"],
        transitions={
            ("C", "0"): "D",
            ("C", "1"): "C",
            ("D", "0"): "D",
            ("D", "1"): "C",
        },
    )
    return m1, m2


# ----------------------------------------------------------------------
# 自构正例：两个状态数 / 结构都不同、但语言相同的自动机
# ----------------------------------------------------------------------
def build_positive_example():
    # P1：2 个状态，接受 Σ* 中“以 0 结尾”的串
    #   A(初态,非终) --0--> B(终态)，读 1 回 A；B 读 0 留 B、读 1 回 A
    p1 = DFA(
        name="P1(2状态)",
        states=["A", "B"],
        alphabet=["0", "1"],
        start="A",
        finals=["B"],
        transitions={
            ("A", "0"): "B",
            ("A", "1"): "A",
            ("B", "0"): "B",
            ("B", "1"): "A",
        },
    )

    # P2：3 个状态，结构不同：X、Y 是“不可区分”（等价）的两个非终态
    #   X(初态,非终) --0--> Z(终态), --1--> Y
    #   Y(非终)      --0--> Z,        --1--> X
    #   Z(终态)      --0--> Z,        --1--> X
    # X 与 Y 对未来输入的接受行为完全一样，合并后正好就是 P1，
    # 所以 L(P2)=L(P1)={w | w 以 0 结尾}。
    p2 = DFA(
        name="P2(3状态)",
        states=["X", "Y", "Z"],
        alphabet=["0", "1"],
        start="X",
        finals=["Z"],
        transitions={
            ("X", "0"): "Z",
            ("X", "1"): "Y",
            ("Y", "0"): "Z",
            ("Y", "1"): "X",
            ("Z", "0"): "Z",
            ("Z", "1"): "X",
        },
    )
    return p1, p2


def extra_checks():
    print("\n--- 边界情况自检 ---")

    # 1) 初态接受性不同：一个拒绝 ε、一个接受 ε
    e1 = DFA("E1", ["p"], ["0", "1"], "p", [],
             {("p", "0"): "p", ("p", "1"): "p"})
    e2 = DFA("E2", ["q"], ["0", "1"], "q", ["q"],
             {("q", "0"): "q", ("q", "1"): "q"})
    print("初态接受性不同 :", "等价" if are_equivalent(e1, e2) else "不等价")

    # 2) 两个自动机使用相同的状态名，组件仍按各自身份区分
    s1 = DFA("S1", ["q0", "q1"], ["0", "1"], "q0", ["q1"],
             {("q0", "0"): "q1", ("q0", "1"): "q0",
              ("q1", "0"): "q1", ("q1", "1"): "q0"})
    s2 = DFA("S2", ["q0", "q1"], ["0", "1"], "q0", ["q1"],
             {("q0", "0"): "q1", ("q0", "1"): "q0",
              ("q1", "0"): "q1", ("q1", "1"): "q0"})
    print("状态同名       :", "等价" if are_equivalent(s1, s2) else "不等价")

    # 3) 不可达状态（含不可达终态）不影响语言
    u1 = DFA("U1", ["a", "b"], ["0", "1"], "a", ["b"],
             {("a", "0"): "b", ("a", "1"): "a",
              ("b", "0"): "b", ("b", "1"): "a"})
    u2 = DFA("U2", ["a", "b", "c"], ["0", "1"], "a", ["b", "c"],
             {("a", "0"): "b", ("a", "1"): "a",
              ("b", "0"): "b", ("b", "1"): "a",
              ("c", "0"): "c", ("c", "1"): "c"})   # c 不可达
    print("含不可达状态   :", "等价" if are_equivalent(u1, u2) else "不等价")


def main():
    print("=== 第一题：DFA 语言等价判定===")

    # 反例
    m1, m2 = build_counterexample()
    witness = _find_witness(m1, m2)
    shown = witness if witness else "ε(空串)"
    print("\n【反例】lec4-rs1第 34 页两个自动机")
    print("  判定结果:", "不等价" if witness is not None else "等价")
    print("  区分串  :", shown, "-> 该串只被其中一个自动机接受")
    print("  are_equivalent(m1, m2) =", are_equivalent(m1, m2))

    # 正例
    p1, p2 = build_positive_example()
    print("\n【自构正例】2 状态 P1 与 3 状态 P2")
    print("  判定结果:", "等价" if are_equivalent(p1, p2) else "不等价")
    print("  are_equivalent(p1, p2) =", are_equivalent(p1, p2))
    print("  语言说明: L(P1)=L(P2)={w∈{0,1}* | w 以 0 结尾}；")
    print("            P2 的 X、Y 为等价（不可区分）状态，合并后即 P1。")

    extra_checks()


if __name__ == "__main__":
    main()
