"""第一题：DFA 语言等价判定。"""

from collections import deque

from dfa import Automaton, normalize_for_equivalence
from dfa_examples import (
    empty_language,
    epsilon_only,
    question1_counterexample as build_counterexample,
    question1_positive_example as build_positive_example,
)


def _find_witness(a1: Automaton, a2: Automaton):
    """返回一条“只被其中一个自动机接受”的区分串；若两语言等价则返回 None。

    这正是乘积 DFA 中从初态对出发、到达“恰有一个分量为终态”的状态对的路径标签。
    """
    a1, a2 = normalize_for_equivalence(a1, a2)
    start_pair = (a1.start_state, a2.start_state)
    visited = {start_pair}
    queue = deque([(start_pair, ())])   # (状态对, 到达它的字符串)

    while queue:
        (q, r), word = queue.popleft()

        # 异或：恰好一个分量为终态 -> word 属于 symmetric difference
        if (q in a1.accepting_states) != (r in a2.accepting_states):
            return word

        for a in sorted(a1.alphabet):   # 排序只为输出可复现
            nxt = (a1.delta(q, a), a2.delta(r, a))
            if nxt not in visited:      # 不可达状态天然被跳过
                visited.add(nxt)
                queue.append((nxt, word + (a,)))

    return None


def are_equivalent(a1: Automaton, a2: Automaton) -> bool:
    """判定两个 DFA 接受的语言是否等价：等价 True，不等价 False。"""
    return _find_witness(a1, a2) is None


def extra_checks():
    print("\n--- 边界情况自检 ---")

    # 初态接受性不同。
    left = empty_language(["0", "1"])
    right = epsilon_only(["0", "1"])
    print("初态接受性不同 :", "等价" if are_equivalent(left, right) else "不等价")

    # 同名状态属于各自的自动机。
    left, _ = build_positive_example()
    right, _ = build_positive_example()
    print("状态同名       :", "等价" if are_equivalent(left, right) else "不等价")

    # 新增一个不可达终态，不影响原自动机的语言。
    right = Automaton(
        states=left.states + ["U"],
        alphabet=left.alphabet,
        start_state=left.start_state,
        accepting_states=left.accepting_states | {"U"},
        transitions=dict(left.transitions, U={"0": "U", "1": "U"}),
    )
    print("含不可达状态   :", "等价" if are_equivalent(left, right) else "不等价")

    left = epsilon_only(["0"])
    right = epsilon_only(["0", "1"])
    print("字母表不同     :", "等价" if are_equivalent(left, right) else "不等价")


def main():
    print("=== 第一题：DFA 语言等价判定===")

    # 反例
    m1, m2 = build_counterexample()
    witness = _find_witness(m1, m2)
    print("\n【反例】lec4-rs1 第 34 页两个自动机")
    print("  判定结果:", "不等价" if witness is not None else "等价")
    if witness is not None:
        shown = "".join(witness) if all(len(symbol) == 1 for symbol in witness) else repr(witness)
        shown = shown or "ε(空串)"
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
