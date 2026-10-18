"""第四题：使用子集构造法将题目中的 NFA 转换为 DFA。"""

from collections import deque


# 转移表中每个值都是状态集合；本题没有 epsilon 转移。
NFA = {
    1: {"r": {2, 4}, "b": {5}},
    2: {"r": {4, 6}, "b": {1, 3, 5}},
    3: {"r": {2, 6}, "b": {5}},
    4: {"r": {2, 8}, "b": {1, 5, 7}},
    5: {"r": {2, 4, 6, 8}, "b": {1, 3, 7, 9}},
    6: {"r": {2, 8}, "b": {3, 5, 9}},
    7: {"r": {4, 8}, "b": {5}},
    8: {"r": {4, 6}, "b": {5, 7, 9}},
    9: {"r": {6, 8}, "b": {5}},
}
ALPHABET = ("r", "b")
START = 1
FINAL = {9}


def subset_construction(nfa, alphabet, start, final):
    """返回可达 DFA 状态、转移表、初态和终态集合。

    DFA 的一个状态是 NFA 状态的子集，使用 frozenset 作为字典键。
    对子集 S 和字符 a，delta_D(S, a) = 并集{delta_N(q, a): q 属于 S}。
    """
    dfa_start = frozenset({start})
    states = [dfa_start]
    discovered = {dfa_start}
    pending = deque([dfa_start])
    transitions = {}

    while pending:
        current = pending.popleft()
        transitions[current] = {}
        for symbol in alphabet:
            target = set()
            for state in current:
                target.update(nfa[state][symbol])
            target = frozenset(target)
            transitions[current][symbol] = target

            if target not in discovered:
                discovered.add(target)
                states.append(target)
                pending.append(target)

    # 子集中只要包含一个 NFA 终态，该子集就是 DFA 终态。
    dfa_final = {state for state in states if state & final}
    return states, transitions, dfa_start, dfa_final


def format_subset(states):
    return "{" + ",".join(str(state) for state in sorted(states)) + "}"


def print_dfa(states, transitions, start, final, alphabet):
    names = {state: f"D{i}" for i, state in enumerate(states)}
    print("DFA 转移表（-> 表示初态，* 表示终态）")
    print(f"{'标记':<6}{'状态':<8}{'NFA 状态子集':<24}" +
          "".join(f"{symbol:<8}" for symbol in alphabet))
    print("-" * 60)
    for state in states:
        mark = ("->" if state == start else "") + ("*" if state in final else "")
        targets = "".join(f"{names[transitions[state][a]]:<8}" for a in alphabet)
        print(f"{mark:<6}{names[state]:<8}{format_subset(state):<24}{targets}")
    print(f"\n状态数：{len(states)}")
    print("初态：" + names[start])
    print("终态：" + ", ".join(names[state] for state in states if state in final))


if __name__ == "__main__":
    dfa_states, dfa_delta, dfa_start, dfa_final = subset_construction(
        NFA, ALPHABET, START, FINAL
    )
    print_dfa(dfa_states, dfa_delta, dfa_start, dfa_final, ALPHABET)
