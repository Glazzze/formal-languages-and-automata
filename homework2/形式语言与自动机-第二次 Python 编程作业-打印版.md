# 形式语言与自动机：第二次 Python 编程作业

组长姓名：________________________________

组长学号：________________________________________

签署日期：____________年________月________日

## 小组成员与分工

| 姓名 | 分工 |
| --- | --- |
| 廖敏佳 | 公共 DFA 类、题图数据和基础测试 |
| 黄爱心 | 第一题语言等价判定、自构正例和第二题等价性复核 |
| 刘倪羽晗 | 第二题 DFA 最小化、状态合并和自构用例 |
| 刘嘉瑜 | 第三题堆栈判定、边界测试和跨题独立核验 |
| 刘雅静（组长） | 第二题输出、代码整合和最终验收 |

## 运行环境与方法

使用 Python 3.9 或以上版本，仅依赖标准库。进入 `homework2/提交版` 后运行以下命令。各题自动执行内置用例。

```bash
python3 question1_dfa_equivalence.py
python3 question2_dfa_minimization.py
python3 question3_stack_membership.py
```

第一、二题共用的 DFA 类、数据和输出模块见附录 A。验证命令和测试脚本见附录 B。打印稿省去部分注释和文档字符串。长文件按源码顺序分段展示。

## 第一题 · DFA 语言等价判定

### 题图反例与自构正例

依据课件 lec4-rs1 第 33–35 页，对两台 DFA 的状态对做广度优先搜索。搜索到接受性不同的状态对时，到达该状态对的输入就是区分串。若遍历完全部可达状态对仍未找到，两台 DFA 等价。字母表不同时先补齐到并集。

题图给出的两台 DFA 均使用字母表 `{0, 1}`。M1 的初态为 `A`、终态为 `B`。M2 的初态和唯一终态均为 `C`。

| DFA | 状态 | 输入 `0` | 输入 `1` |
| --- | --- | --- | --- |
| M1 | A | A | B |
| M1 | B | A | A |
| M2 | C | D | C |
| M2 | D | D | C |

M2 接受空串，M1 拒绝空串，因此最短区分串为 `ε`。

自构正例 P1 和 P2 的字母表也为 `{0, 1}`。P1 的初态为 `A`、终态为 `B`。P2 的初态为 `X`、终态为 `Z`。

| DFA | 状态 | 输入 `0` | 输入 `1` |
| --- | --- | --- | --- |
| P1 | A | B | A |
| P1 | B | B | A |
| P2 | X | Z | Y |
| P2 | Y | Z | X |
| P2 | Z | Z | X |

P2 的 `X` 和 `Y` 合并后得到与 P1 同构的 DFA。两者都接受以 `0` 结尾的二进制串，例如 `0`、`10` 和 `110`。

### 完整源码 · question1_dfa_equivalence.py

```python
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
    return _find_witness(a1, a2) is None
```

```python
def extra_checks():
    print("\n--- 边界情况自检 ---")

    left = empty_language(["0", "1"])
    right = epsilon_only(["0", "1"])
    print("初态接受性不同 :", "等价" if are_equivalent(left, right) else "不等价")

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
```

### 运行结果

```text
=== 第一题：DFA 语言等价判定===

【反例】lec4-rs1 第 34 页两个自动机
  判定结果: 不等价
  区分串  : ε(空串) -> 该串只被其中一个自动机接受
  are_equivalent(m1, m2) = False

【自构正例】2 状态 P1 与 3 状态 P2
  判定结果: 等价
  are_equivalent(p1, p2) = True
  语言说明: L(P1)=L(P2)={w∈{0,1}* | w 以 0 结尾}；
            P2 的 X、Y 为等价（不可区分）状态，合并后即 P1。

--- 边界情况自检 ---
初态接受性不同 : 不等价
状态同名       : 等价
含不可达状态   : 等价
字母表不同     : 等价
```

## 第二题 · DFA 最小化

### 题图 DFA 与自构用例

依据课件 lec4-rs1 第 42 页的状态对标记法，先选出从初态可达的状态。第 0 轮标记接受性不同的状态对，随后逐轮标记能转入已标记状态对的状态对。标记稳定后，合并其余不可区分的状态。

题图 DFA D 的字母表为 `{0, 1}`，初态为 `IS0`，终态集合为 `{FS2, FS5, FS6}`。

| 状态 | 输入 `0` | 输入 `1` |
| --- | --- | --- |
| IS0 | S1 | S1 |
| S1 | FS2 | FS5 |
| FS2 | IS0 | IS0 |
| S3 | S4 | S4 |
| S4 | FS5 | FS6 |
| FS5 | S3 | S3 |
| FS6 | IS0 | IS0 |

两组自构 DFA 的字母表均为 `{0, 1}`。用例 A 的初态为 `A`，终态集合为 `{B, C}`。用例 B 的初态和唯一终态均为 `E`。

| 用例 | 状态 | 输入 `0` | 输入 `1` |
| --- | --- | --- | --- |
| A | A | B | C |
| A | B | B | B |
| A | C | C | C |
| A | X | X | X |
| B | E | E | O |
| B | O | O | E |

用例 A 预期删除不可达状态 `X`，合并 `B` 和 `C`。用例 B 接受含偶数个 `1` 的串，两个状态可由空串区分，预期保留两个状态。

### 完整源码 · question2_dfa_minimization.py

```python
from __future__ import annotations

from itertools import product
from typing import Dict, List, Set, Tuple

from dfa import Automaton
from dfa_display import print_minimization
from dfa_examples import (
    question2_dfa_d as build_example_dfa_d,
    question2_merge_dfa as build_custom_merge_dfa,
    question2_minimal_dfa as build_custom_minimal_dfa,
)

Pair = Tuple[str, str]

def pair_key(first: str, second: str) -> Pair:
    return (first, second) if first < second else (second, first)
```

```python
def distinguishable_pair_rounds(dfa: Automaton) -> Dict[Pair, int]:
    states = dfa.reachable_states()
    marked: Dict[Pair, int] = {}

    # Round 0: the empty string distinguishes a final from a non-final state.
    for index, first in enumerate(states):
        for second in states[index + 1 :]:
            if (first in dfa.accepting_states) != (
                second in dfa.accepting_states
            ):
                marked[pair_key(first, second)] = 0

    round_number = 1
    while True:
        newly_marked: Set[Pair] = set()
        for index, first in enumerate(states):
            for second in states[index + 1 :]:
                pair = pair_key(first, second)
                if pair in marked:
                    continue
                for symbol in dfa.alphabet:
                    targets = pair_key(
                        dfa.delta(first, symbol), dfa.delta(second, symbol)
                    )
                    if targets in marked:
                        newly_marked.add(pair)
                        break
        if not newly_marked:
            break
        for pair in newly_marked:
            marked[pair] = round_number
        round_number += 1
    return marked
```

```python
def _equivalence_classes(
    states: List[str], distinguishable: Set[Pair]
) -> List[List[str]]:
    groups: List[List[str]] = []
    unassigned = set(states)
    for state in states:
        if state not in unassigned:
            continue
        group = [
            other
            for other in states
            if other in unassigned
            and (other == state or pair_key(state, other) not in distinguishable)
        ]
        groups.append(group)
        unassigned.difference_update(group)
    return groups
```

```python
def _build_minimized(
    dfa: Automaton, rounds: Dict[Pair, int]
) -> Tuple[Automaton, Dict[str, str]]:
    reachable = dfa.reachable_states()
    groups = _equivalence_classes(reachable, set(rounds))
    groups.sort(key=lambda group: group[0])

    state_mapping: Dict[str, str] = {}
    for index, group in enumerate(groups):
        for state in group:
            state_mapping[state] = f"Q{index}"

    minimized_states = [f"Q{index}" for index in range(len(groups))]
    minimized_accepting = {
        state_mapping[state]
        for state in dfa.accepting_states
        if state in state_mapping
    }
    minimized_transitions: Dict[str, Dict[str, str]] = {}
    for group in groups:
        representative = group[0]
        source = state_mapping[representative]
        minimized_transitions[source] = {
            symbol: state_mapping[dfa.delta(representative, symbol)]
            for symbol in dfa.alphabet
        }

    minimized = Automaton(
        states=minimized_states,
        alphabet=list(dfa.alphabet),
        start_state=state_mapping[dfa.start_state],
        accepting_states=minimized_accepting,
        transitions=minimized_transitions,
    )
    return minimized, state_mapping

def minimize_dfa(dfa: Automaton) -> Tuple[Automaton, Dict[str, str]]:
    return _build_minimized(dfa, distinguishable_pair_rounds(dfa))

def print_minimization_report(dfa: Automaton, label: str) -> None:
    rounds = distinguishable_pair_rounds(dfa)
    minimized, mapping = _build_minimized(dfa, rounds)
    print_minimization(dfa, minimized, mapping, rounds, label)

def verify_short_words(original: Automaton, minimized: Automaton, max_length: int = 5) -> None:
    for length in range(max_length + 1):
        for symbols in product(original.alphabet, repeat=length):
            if original.accepts(symbols) != minimized.accepts(symbols):
                raise AssertionError(f"Acceptance mismatch for {symbols!r}.")
```

```python
def run_self_tests() -> None:
    merge_dfa = build_custom_merge_dfa()
    merged, mapping = minimize_dfa(merge_dfa)
    assert mapping == {"A": "Q0", "B": "Q1", "C": "Q1"}
    assert "X" not in mapping
    assert len(merged.states) == 2
    verify_short_words(merge_dfa, merged)

    minimal_dfa = build_custom_minimal_dfa()
    unchanged, mapping = minimize_dfa(minimal_dfa)
    assert len(unchanged.states) == 2
    assert mapping == {"E": "Q0", "O": "Q1"}
    verify_short_words(minimal_dfa, unchanged)

if __name__ == "__main__":
    dfa_d = build_example_dfa_d()
    print("Member C: DFA minimization using state-pair marking")
    print_minimization_report(dfa_d, "Assignment DFA D")
    minimized_d, _ = minimize_dfa(dfa_d)
    verify_short_words(dfa_d, minimized_d)
    print("\nDFA D and its minimized result agree on all strings of length 0 through 5.")

    print_minimization_report(build_custom_merge_dfa(), "Custom test: merge equivalent states and remove unreachable state")
    print_minimization_report(build_custom_minimal_dfa(), "Custom test: already-minimal DFA")
    run_self_tests()
    print("\nAll self-tests passed.")
```

### 运行结果

以下为题图 DFA D 的合并映射及最终自动机。

```text
Unreachable states removed: []
Indistinguishable groups / merge mapping:
  Q0 = {FS2, FS5, FS6}
  Q1 = {IS0, S3}
  Q2 = {S1, S4}
Minimized DFA:
  States: ['Q0', 'Q1', 'Q2']
  Alphabet: ['0', '1']
  Start: Q1
  Accepting: ['Q0']
  Transitions:
    Q0: 0->Q1, 1->Q1
    Q1: 0->Q2, 1->Q2
    Q2: 0->Q0, 1->Q0
```

最小 DFA 的三个状态都可从 `Q1` 到达。`Q0` 是唯一终态，可用空串与 `Q1`、`Q2` 区分。`Q1` 和 `Q2` 读入 `0` 后分别到达非终态 `Q2` 和终态 `Q0`，因此也可区分。

两组自构用例的输出节选如下。

```text
Unreachable states removed: ['X']
Indistinguishable groups / merge mapping:
  Q0 = {A}
  Q1 = {B, C}

Unreachable states removed: []
Indistinguishable groups / merge mapping:
  Q0 = {E}
  Q1 = {O}

All self-tests passed.
```

## 第三题 · 堆栈判定

### 待判定语言与自行构造的用例

判定形如 `0^k 1^k` 的串，其中 `k ≥ 1`。每读一个前导 `0` 就压栈，之后每读一个 `1` 就匹配一个 `0`。`|` 是栈内阶段标记，表示已经开始匹配 `1`。输入结束时，栈中恰好只剩该标记才接受。

| 用例 | 预期 |
| --- | --- |
| `0011`、`01`、`000111` | 接受 |
| 空串、`0`、`1`、`00`、`11` | 拒绝 |
| `011`、`001`、`001111`、`00011` | 拒绝 |
| `0101`、`00110`、`10` | 拒绝 |
| `00a11` | 拒绝 |

判定函数的参数和局部变量只有输入 `s`、堆栈 `S` 和循环变量 `ch`，使用迭代实现。

### 完整源码 · question3_stack_membership.py

```python
def judge(s: str) -> bool:
    S = []

    for ch in s:
        if ch == "0":
            if S and S[-1] == "|":
                return False
            S.append("0")
        elif ch == "1":
            if not S:
                return False
            if S[-1] == "|":
                S.pop()
                if not S or S[-1] != "0":
                    return False
                S.pop()
                S.append("|")
            else:
                S.append("|")
                S.pop()
                S.pop()
                S.append("|")
        else:
            return False

    return S == ["|"]

if __name__ == "__main__":
    print("01：", "接受" if judge("01") else "拒绝")
    print("0011：", "接受" if judge("0011") else "拒绝")
    print("000111：", "接受" if judge("000111") else "拒绝")
    print("011：", "接受" if judge("011") else "拒绝")
    print("0101：", "接受" if judge("0101") else "拒绝")
    print("空串：", "接受" if judge("") else "拒绝")
```

### 运行结果

```text
01： 接受
0011： 接受
000111： 接受
011： 拒绝
0101： 拒绝
空串： 拒绝
```

## 附录 A · 第一、二题共用模块

### 完整源码 · dfa.py

```python
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set, Tuple

TRAP_STATE = "__trap__"

def _fresh_state_name(existing: Iterable[str], base: str = TRAP_STATE) -> str:
    existing = set(existing)
    if base not in existing:
        return base
    index = 1
    while f"{base}_{index}" in existing:
        index += 1
    return f"{base}_{index}"

def _as_str_list(values: Sequence[str], field_name: str) -> List[str]:
    result = list(values)
    for value in result:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} 中的元素必须是字符串，收到 {value!r}。")
        if value == "":
            raise ValueError(f"{field_name} 中不允许空字符串。")
    return result

@dataclass(frozen=True)
class Automaton:

    states: List[str]
    alphabet: List[str]
    start_state: str
    accepting_states: Set[str]
    transitions: Dict[str, Dict[str, str]]
```

```python
    def __post_init__(self) -> None:
        states = _as_str_list(self.states, "states")
        alphabet = _as_str_list(self.alphabet, "alphabet")

        if not states:
            raise ValueError("状态集合不能为空。")
        if len(set(states)) != len(states):
            raise ValueError("状态名必须唯一。")
        if len(set(alphabet)) != len(alphabet):
            raise ValueError("字母表符号必须唯一。")

        if not isinstance(self.start_state, str):
            raise TypeError("start_state 必须是字符串。")
        if self.start_state not in states:
            raise ValueError(f"初态 {self.start_state!r} 不在状态集合中。")

        accepting = set(self.accepting_states)
        for state in accepting:
            if not isinstance(state, str):
                raise TypeError("accepting_states 中的元素必须是字符串。")
        if not accepting.issubset(set(states)):
            raise ValueError("终态集合包含未知状态。")

        if not isinstance(self.transitions, dict):
            raise TypeError("transitions 必须是字典。")
        transitions: Dict[str, Dict[str, str]] = {}
        for state, row in self.transitions.items():
            if state not in states:
                raise ValueError(f"转移表含未知状态 {state!r}。")
            if not isinstance(row, dict):
                raise TypeError(f"状态 {state!r} 的转移必须是字典。")
            copied_row: Dict[str, str] = {}
            for symbol, target in row.items():
                if symbol not in alphabet:
                    raise ValueError(
                        f"状态 {state!r} 的转移含字母表外符号 {symbol!r}。"
                    )
                if not isinstance(target, str):
                    raise TypeError("转移目标必须是字符串状态名。")
                if target not in states:
                    raise ValueError(
                        f"转移 δ({state!r}, {symbol!r}) 指向未知状态 {target!r}。"
                    )
                copied_row[symbol] = target
            transitions[state] = copied_row

        for state in states:
            if state not in transitions:
                raise ValueError(f"缺少状态 {state!r} 的转移行。")
            for symbol in alphabet:
                if symbol not in transitions[state]:
                    raise ValueError(
                        f"缺少转移 δ({state!r}, {symbol!r})；"
                        "部分转移表请用 Automaton.from_partial 构造。"
                    )

        object.__setattr__(self, "states", states)
        object.__setattr__(self, "alphabet", alphabet)
        object.__setattr__(self, "accepting_states", accepting)
        object.__setattr__(self, "transitions", transitions)

    # ------------------------------------------------------------------
    # 基本查询
    # ------------------------------------------------------------------
```

```python
    def delta(self, state: str, symbol: str) -> str:
        if state not in self.states:
            raise ValueError(f"未知状态 {state!r}。")
        if symbol not in self.alphabet:
            raise ValueError(f"未知字母表符号 {symbol!r}。")
        return self.transitions[state][symbol]

    def is_final(self, state: str) -> bool:
        if state not in self.states:
            raise ValueError(f"未知状态 {state!r}。")
        return state in self.accepting_states

    def accepts(self, word: Sequence[str]) -> bool:
        if not isinstance(word, Sequence) or isinstance(word, (bytes, bytearray)):
            raise TypeError("输入必须是字符串或符号序列。")
        current = self.start_state
        for symbol in word:
            if not isinstance(symbol, str):
                raise TypeError("输入符号必须是字符串。")
            if symbol not in self.alphabet:
                raise ValueError(f"输入串含字母表外符号 {symbol!r}。")
            current = self.transitions[current][symbol]
        return current in self.accepting_states

    def reachable_states(self) -> List[str]:
        reached = {self.start_state}
        queue = deque([self.start_state])
        while queue:
            state = queue.popleft()
            for symbol in self.alphabet:
                target = self.transitions[state][symbol]
                if target not in reached:
                    reached.add(target)
                    queue.append(target)
        return sorted(reached)

    # ------------------------------------------------------------------
    # 输入规范化：部分转移表 / 不同字母表
    # ------------------------------------------------------------------
```

```python
    @classmethod
    def from_partial(
        cls,
        states: Sequence[str],
        alphabet: Sequence[str],
        start_state: str,
        accepting_states: Iterable[str],
        transitions: Dict[str, Dict[str, str]],
        trap_state: str = TRAP_STATE,
    ) -> "Automaton":
        """Build a total DFA from a possibly partial transition table.

        Missing transitions go to a rejecting sink. An existing trap is
        reused only if it is non-accepting and its explicit edges are self-loops.
        Explicit edges to a conflicting state keep their original targets.
        """
        states = _as_str_list(states, "states")
        alphabet = _as_str_list(alphabet, "alphabet")
        if not isinstance(trap_state, str) or trap_state == "":
            raise ValueError("trap_state 必须是非空字符串。")
        if not isinstance(transitions, dict):
            raise TypeError("transitions 必须是字典。")
        accepting_states = set(accepting_states)
        if not accepting_states.issubset(states):
            raise ValueError("终态集合包含未知状态。")

        raw: Dict[str, Dict[str, str]] = {}
        for state, row in transitions.items():
            if state not in states:
                raise ValueError(f"转移表含未知状态 {state!r}。")
            if not isinstance(row, dict):
                raise TypeError(f"状态 {state!r} 的转移必须是字典。")
            raw[state] = dict(row)

        needs_trap = False
        for row in raw.values():
            for symbol, target in row.items():
                if symbol not in alphabet:
                    raise ValueError(f"转移含字母表外符号 {symbol!r}。")
                if not isinstance(target, str):
                    raise TypeError("转移目标必须是字符串状态名。")
                if target not in states and target != trap_state:
                    raise ValueError(f"转移指向未知状态 {target!r}。")
                if target == trap_state and trap_state not in states:
                    needs_trap = True
        if any(
            symbol not in raw.get(state, {})
            for state in states
            for symbol in alphabet
        ):
            needs_trap = True

        if needs_trap:
            if trap_state in states and (
                trap_state in accepting_states
                or any(target != trap_state for target in raw.get(trap_state, {}).values())
            ):
                trap_state = _fresh_state_name(states, trap_state)
            if trap_state not in states:
                states.append(trap_state)

        total: Dict[str, Dict[str, str]] = {}
        for state in states:
            row = dict(raw.get(state, {}))
            for symbol in alphabet:
                row.setdefault(symbol, trap_state)
            total[state] = row

        return cls(
            states=states,
            alphabet=alphabet,
            start_state=start_state,
            accepting_states=accepting_states,
            transitions=total,
        )
```

```python
    def complete_to(self, alphabet: Iterable[str]) -> "Automaton":
        """Return an equivalent DFA whose alphabet is a superset of this one.

        Symbols that are not in the current alphabet lead to a fresh trap state,
        so the language over the old alphabet is unchanged and every new symbol
        is rejected.  If the current alphabet already covers *alphabet*, this
        instance is returned unchanged (it is immutable in practice).
        """
        extra: List[str] = []
        seen = set(self.alphabet)
        for symbol in alphabet:
            if not isinstance(symbol, str) or symbol == "":
                raise TypeError("字母表符号必须是非空字符串。")
            if symbol not in seen:
                seen.add(symbol)
                extra.append(symbol)
        if not extra:
            return self

        new_alphabet = list(self.alphabet) + extra
        trap = _fresh_state_name(self.states)
        transitions = {
            state: dict(self.transitions[state]) for state in self.states
        }
        for state in self.states:
            for symbol in extra:
                transitions[state][symbol] = trap
        transitions[trap] = {symbol: trap for symbol in new_alphabet}

        return Automaton(
            states=list(self.states) + [trap],
            alphabet=new_alphabet,
            start_state=self.start_state,
            accepting_states=set(self.accepting_states),
            transitions=transitions,
        )

    # ------------------------------------------------------------------
    # 输出
    # ------------------------------------------------------------------
```

```python
    def pretty_print(self, label: str = "DFA") -> None:
        print(f"{label}:")
        print(f"  States: {self.states}")
        print(f"  Alphabet: {self.alphabet}")
        print(f"  Start: {self.start_state}")
        print(f"  Accepting: {sorted(self.accepting_states)}")
        print("  Transitions:")
        for state in self.states:
            row = ", ".join(
                f"{symbol}->{self.transitions[state][symbol]}"
                for symbol in self.alphabet
            )
            print(f"    {state}: {row}")

def common_alphabet(*automata: Automaton) -> List[str]:
    symbols: Set[str] = set()
    for automaton in automata:
        if not isinstance(automaton, Automaton):
            raise TypeError("common_alphabet 只接受 Automaton 实例。")
        symbols.update(automaton.alphabet)
    return sorted(symbols)

def normalize_for_equivalence(
    left: Automaton, right: Automaton
) -> Tuple[Automaton, Automaton]:
    """Complete two DFAs over the union alphabet, ready for a product search.

    This is the interface the equivalence algorithm should call first.  It
    prevents the incorrect shortcut "different alphabets => not equivalent":
    ``{ε}`` over ``{0}`` and ``{ε}`` over ``{0,1}`` are the same language.
    """
    if not isinstance(left, Automaton) or not isinstance(right, Automaton):
        raise TypeError("normalize_for_equivalence 只接受 Automaton 实例。")
    alphabet = common_alphabet(left, right)
    return left.complete_to(alphabet), right.complete_to(alphabet)
```

### 完整源码 · dfa_examples.py

```python
from __future__ import annotations

from typing import List

from dfa import Automaton

def question1_m1() -> Automaton:
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
    return question1_m1(), question1_m2()

def question1_p1() -> Automaton:
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
```

```python
def question1_p2() -> Automaton:
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
    return question1_p1(), question1_p2()

def empty_language(alphabet: List[str]) -> Automaton:
    states = ["S"]
    return Automaton(
        states=states,
        alphabet=list(alphabet),
        start_state="S",
        accepting_states=set(),
        transitions={"S": {symbol: "S" for symbol in alphabet}},
    )

def epsilon_only(alphabet: List[str]) -> Automaton:
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
```

```python
def question2_dfa_d() -> Automaton:
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

def question2_merge_dfa() -> Automaton:
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
```

```python
def partial_endswith_1() -> Automaton:
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
```

### 完整源码 · dfa_display.py

```python
from dfa import Automaton

def print_minimization(
    dfa: Automaton,
    minimized: Automaton,
    mapping: dict[str, str],
    rounds: dict[tuple[str, str], int],
    label: str,
) -> None:
    reachable = dfa.reachable_states()
    unreachable = sorted(set(dfa.states) - set(reachable))

    print(f"\n{label}")
    print("-" * len(label))
    dfa.pretty_print("Input DFA")
    print("\nMarked distinguishable pairs:")
    if not rounds:
        print("  None")
    else:
        max_round = max(rounds.values())
        for round_number in range(max_round + 1):
            pairs = sorted(
                pair
                for pair, marked_round in rounds.items()
                if marked_round == round_number
            )
            print(f"  Round {round_number}: {pairs}")
    print(f"\nUnreachable states removed: {unreachable}")
    print("Indistinguishable groups / merge mapping:")
    groups = {}
    for state in reachable:
        groups.setdefault(mapping[state], []).append(state)
    for new_state in sorted(minimized.states):
        print(f"  {new_state} = {{{', '.join(groups[new_state])}}}")
    minimized.pretty_print("Minimized DFA")
```

## 附录 B · 验证结果与完整源码

在 `homework2/提交版` 中执行以下命令。

```bash
python3 -m unittest -v test_dfa test_dfa_minimization
python3 verify_minimization_equivalence.py
python3 verify_submission.py
```

- 44 项单元测试全部通过，含陷阱状态重名和多字符符号的回归用例。
- 第二题 3 组输入在最小化前后均等价。清空终态的对照用例被判为不等价。独立核验确认题图 DFA 的最小化结果全部可达且两两可区分，并核对了 511 个短串。
- 第三题 16 个边界用例全部通过。对字母表 `{0, 1, a}` 上长度 0 至 8 的 9,841 个串穷举比对，结果全部一致。

### 完整源码 · test_dfa.py

```python
from __future__ import annotations

import contextlib
import io
import itertools
import unittest

import dfa_examples
import question1_dfa_equivalence
import question2_dfa_minimization
from dfa import (
    TRAP_STATE,
    Automaton,
    common_alphabet,
    normalize_for_equivalence,
)

def _words(alphabet, max_length):
    for length in range(max_length + 1):
        for symbols in itertools.product(sorted(alphabet), repeat=length):
            yield "".join(symbols)

def _assert_same_language(testcase, left, right, max_length=5):
    left, right = normalize_for_equivalence(left, right)
    testcase.assertEqual(set(left.alphabet), set(right.alphabet))
    for word in _words(left.alphabet, max_length):
        testcase.assertEqual(
            left.accepts(word),
            right.accepts(word),
            msg=f"两个自动机在 {word!r} 上接受性不同",
        )

def _sample_dfa():
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

class AutomatonConstructionTests(unittest.TestCase):
```

```python
    def test_fields_keep_list_and_set_types(self):
        dfa = _sample_dfa()
        self.assertIsInstance(dfa.states, list)
        self.assertIsInstance(dfa.alphabet, list)
        self.assertIsInstance(dfa.accepting_states, set)

    def test_constructor_copies_mutable_arguments(self):
        states = ["A", "B"]
        alphabet = ["0", "1"]
        finals = {"B"}
        transitions = {
            "A": {"0": "B", "1": "A"},
            "B": {"0": "B", "1": "A"},
        }
        dfa = Automaton(states, alphabet, "A", finals, transitions)

        states.append("C")
        alphabet.append("2")
        finals.add("A")
        transitions["A"]["0"] = "A"

        self.assertEqual(dfa.states, ["A", "B"])
        self.assertEqual(dfa.alphabet, ["0", "1"])
        self.assertEqual(dfa.accepting_states, {"B"})
        self.assertEqual(dfa.delta("A", "0"), "B")

    def test_delta_and_accepts(self):
        dfa = _sample_dfa()   # 以 0 结尾
        self.assertEqual(dfa.delta("A", "0"), "B")
        self.assertTrue(dfa.accepts("0"))
        self.assertTrue(dfa.accepts("110"))
        self.assertFalse(dfa.accepts(""))
        self.assertFalse(dfa.accepts("1"))
        self.assertFalse(dfa.accepts("101"))

    def test_is_final_and_reachable_states(self):
        dfa = _sample_dfa()
        self.assertTrue(dfa.is_final("B"))
        self.assertFalse(dfa.is_final("A"))
        with self.assertRaises(ValueError):
            dfa.is_final("Z")
        self.assertEqual(dfa.reachable_states(), ["A", "B"])

    def test_reachable_states_ignores_unreachable(self):
        dfa = dfa_examples.question2_merge_dfa()
        self.assertEqual(dfa.reachable_states(), ["A", "B", "C"])
```

```python
    def test_pretty_print_contains_all_components(self):
        dfa = _sample_dfa()
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            dfa.pretty_print("示例")
        lines = buffer.getvalue().splitlines()
        self.assertEqual(lines[0], "示例:")
        self.assertIn("  States: ['A', 'B']", lines)
        self.assertIn("  Alphabet: ['0', '1']", lines)
        self.assertIn("  Start: A", lines)
        self.assertIn("  Accepting: ['B']", lines)
        self.assertIn("  Transitions:", lines)
        self.assertEqual(lines[-2], "    A: 0->B, 1->A")
        self.assertEqual(lines[-1], "    B: 0->B, 1->A")

    def test_rejects_duplicate_states(self):
        with self.assertRaises(ValueError):
            Automaton(["A", "A"], ["0"], "A", set(), {"A": {"0": "A"}})

    def test_rejects_duplicate_symbols(self):
        with self.assertRaises(ValueError):
            Automaton(["A"], ["0", "0"], "A", set(), {"A": {"0": "A"}})

    def test_rejects_unknown_start(self):
        with self.assertRaises(ValueError):
            Automaton(["A"], ["0"], "B", set(), {"A": {"0": "A"}})

    def test_rejects_unknown_accepting_state(self):
        with self.assertRaises(ValueError):
            Automaton(["A"], ["0"], "A", {"B"}, {"A": {"0": "A"}})

    def test_rejects_missing_transition(self):
        with self.assertRaises(ValueError) as ctx:
            Automaton(["A"], ["0", "1"], "A", set(), {"A": {"0": "A"}})
        self.assertIn("from_partial", str(ctx.exception))

    def test_rejects_missing_row(self):
        with self.assertRaises(ValueError):
            Automaton(["A", "B"], ["0"], "A", set(), {"A": {"0": "B"}})

    def test_rejects_unknown_source_state(self):
        with self.assertRaises(ValueError):
            Automaton(["A"], ["0"], "A", set(),
                      {"A": {"0": "A"}, "X": {"0": "A"}})

    def test_rejects_unknown_target_state(self):
        with self.assertRaises(ValueError):
            Automaton(["A"], ["0"], "A", set(), {"A": {"0": "X"}})
```

```python
    def test_rejects_symbol_outside_alphabet(self):
        with self.assertRaises(ValueError):
            Automaton(["A"], ["0"], "A", set(), {"A": {"0": "A", "1": "A"}})

    def test_rejects_empty_state_set(self):
        with self.assertRaises(ValueError):
            Automaton([], ["0"], "A", set(), {})

    def test_rejects_non_string_names(self):
        with self.assertRaises(TypeError):
            Automaton([1], ["0"], 1, set(), {1: {"0": 1}})

    def test_accepts_rejects_symbol_outside_alphabet(self):
        with self.assertRaises(ValueError):
            _sample_dfa().accepts("2")

    def test_accepts_rejects_non_string(self):
        with self.assertRaises(TypeError):
            _sample_dfa().accepts(0)

class TrapAndAlphabetTests(unittest.TestCase):
    def test_from_partial_does_not_reuse_accepting_trap_name(self):
        dfa = Automaton.from_partial(
            ["A", TRAP_STATE], ["0", "1"], "A", {TRAP_STATE},
            {"A": {"0": TRAP_STATE}},
        )
        sink = dfa.delta("A", "1")
        self.assertNotEqual(sink, TRAP_STATE)
        self.assertEqual(dfa.transitions[sink], {"0": sink, "1": sink})
        self.assertTrue(dfa.accepts("0"))
        self.assertFalse(dfa.accepts("1"))
        self.assertFalse(dfa.accepts("10"))

    def test_from_partial_does_not_reuse_trap_with_outgoing_edge(self):
        dfa = Automaton.from_partial(
            ["A", TRAP_STATE], ["0", "1"], "A", {"A"},
            {"A": {"0": TRAP_STATE}, TRAP_STATE: {"0": "A"}},
        )
        self.assertTrue(dfa.accepts("00"))
        self.assertFalse(dfa.accepts("10"))

    def test_from_partial_reuses_existing_rejecting_sink(self):
        dfa = Automaton.from_partial(
            ["A", TRAP_STATE], ["0", "1"], "A", {"A"},
            {"A": {"0": "A"}, TRAP_STATE: {"0": TRAP_STATE}},
        )
        self.assertEqual(dfa.states, ["A", TRAP_STATE])
        self.assertFalse(dfa.accepts("1"))
```

```python
    def test_from_partial_adds_trap_and_preserves_language(self):
        dfa = dfa_examples.partial_endswith_1()
        self.assertIn(TRAP_STATE, dfa.states)
        self.assertEqual(dfa.transitions[TRAP_STATE], {"0": TRAP_STATE, "1": TRAP_STATE})
        self.assertTrue(dfa.accepts("1"))
        self.assertTrue(dfa.accepts("01"))
        self.assertFalse(dfa.accepts(""))
        self.assertFalse(dfa.accepts("0"))

    def test_from_partial_noop_when_already_total(self):
        dfa = Automaton.from_partial(
            states=["A"], alphabet=["0"], start_state="A",
            accepting_states={"A"}, transitions={"A": {"0": "A"}},
        )
        self.assertEqual(dfa.states, ["A"])

    def test_from_partial_honours_explicit_trap_target(self):
        dfa = Automaton.from_partial(
            states=["A"], alphabet=["0"], start_state="A",
            accepting_states=set(), transitions={"A": {"0": "__trap__"}},
        )
        self.assertIn("__trap__", dfa.states)
        self.assertEqual(dfa.delta("A", "0"), "__trap__")

    def test_from_partial_rejects_typo_target(self):
        with self.assertRaises(ValueError):
            Automaton.from_partial(
                states=["A"], alphabet=["0"], start_state="A",
                accepting_states=set(), transitions={"A": {"0": "B"}},
            )

    def test_complete_to_union_alphabet_preserves_old_language(self):
        dfa = dfa_examples.epsilon_only(["0"])
        completed = dfa.complete_to(["0", "1"])
        self.assertEqual(completed.alphabet, ["0", "1"])
        self.assertIn(TRAP_STATE, completed.states)
        self.assertTrue(completed.accepts(""))
        self.assertFalse(completed.accepts("0"))
        self.assertFalse(completed.accepts("1"))

    def test_complete_to_returns_self_when_no_new_symbol(self):
        dfa = _sample_dfa()
        self.assertIs(dfa.complete_to(["0", "1"]), dfa)

    def test_common_alphabet_sorted_union(self):
        self.assertEqual(
            common_alphabet(dfa_examples.question1_m1(), dfa_examples.empty_language(["a"])),
            ["0", "1", "a"],
        )
```

```python
    def test_normalize_different_alphabet_equal_language(self):
        left = dfa_examples.epsilon_only(["0"])
        right = dfa_examples.epsilon_only(["0", "1"])
        left, right = normalize_for_equivalence(left, right)
        self.assertEqual(left.alphabet, right.alphabet)
        self.assertEqual(left.alphabet, ["0", "1"])
        _assert_same_language(self, left, right)

    def test_normalize_different_alphabet_empty_languages(self):
        left = dfa_examples.empty_language(["0"])
        right = dfa_examples.empty_language(["1"])
        left, right = normalize_for_equivalence(left, right)
        _assert_same_language(self, left, right)

    def test_normalize_requires_automaton(self):
        with self.assertRaises(TypeError):
            normalize_for_equivalence(_sample_dfa(), object())

class FigureDataTests(unittest.TestCase):
    def test_m1_is_not_simply_ends_with_one(self):
        m1 = dfa_examples.question1_m1()
        m2 = dfa_examples.question1_m2()
        self.assertTrue(m1.accepts("1"))
        self.assertTrue(m1.accepts("01"))
        self.assertTrue(m1.accepts("101"))
        self.assertFalse(m1.accepts("11"))
        self.assertTrue(m1.accepts("111"))
        self.assertFalse(m1.accepts("011"))
        self.assertFalse(m1.accepts(""))
        self.assertTrue(m2.accepts(""))
        self.assertTrue(m2.accepts("11"))

    def test_positive_example_accepts_words_ending_in_zero(self):
        p1, p2 = question1_dfa_equivalence.build_positive_example()
        for word in _words(["0", "1"], max_length=6):
            self.assertEqual(p1.accepts(word), word.endswith("0"))
            self.assertEqual(p2.accepts(word), word.endswith("0"))
```

```python
    def test_dfa_d_has_expected_table(self):
        dfa = dfa_examples.question2_dfa_d()
        self.assertEqual(
            dfa.states, ["IS0", "S1", "FS2", "S3", "S4", "FS5", "FS6"]
        )
        self.assertEqual(dfa.start_state, "IS0")
        self.assertEqual(dfa.accepting_states, {"FS2", "FS5", "FS6"})
        self.assertEqual(dfa.delta("IS0", "0"), "S1")
        self.assertEqual(dfa.delta("IS0", "1"), "S1")   # 题面特别注明
        expected = {
            "IS0": {"0": "S1", "1": "S1"},
            "S1": {"0": "FS2", "1": "FS5"},
            "FS2": {"0": "IS0", "1": "IS0"},
            "S3": {"0": "S4", "1": "S4"},
            "S4": {"0": "FS5", "1": "FS6"},
            "FS5": {"0": "S3", "1": "S3"},
            "FS6": {"0": "IS0", "1": "IS0"},
        }
        self.assertEqual(dfa.transitions, expected)
        self.assertEqual(sorted(dfa.reachable_states()), sorted(dfa.states))

class InterfaceAlignmentTests(unittest.TestCase):
    def test_question1_accepts_shared_automaton(self):
        m1, m2 = dfa_examples.question1_counterexample()
        p1, p2 = dfa_examples.question1_positive_example()
        self.assertFalse(question1_dfa_equivalence.are_equivalent(m1, m2))
        self.assertTrue(question1_dfa_equivalence.are_equivalent(p1, p2))

    def test_equivalence_over_different_alphabets(self):
        left = dfa_examples.epsilon_only(["0"])
        right = dfa_examples.epsilon_only(["0", "1"])
        self.assertTrue(question1_dfa_equivalence.are_equivalent(left, right))
        self.assertFalse(question1_dfa_equivalence.are_equivalent(left, dfa_examples.empty_language(["0", "1"])))

    def test_c_minimization_uses_shared_class(self):
        dfa = dfa_examples.question2_dfa_d()
        minimized, mapping = question2_dfa_minimization.minimize_dfa(dfa)
        self.assertIsInstance(minimized, Automaton)
        self.assertEqual(minimized.states, ["Q0", "Q1", "Q2"])
        self.assertEqual(minimized.alphabet, ["0", "1"])
        self.assertEqual(minimized.start_state, "Q1")
        self.assertEqual(minimized.accepting_states, {"Q0"})
        self.assertEqual(mapping["IS0"], mapping["S3"])
        self.assertEqual(mapping["S1"], mapping["S4"])
        self.assertTrue(question1_dfa_equivalence.are_equivalent(dfa, minimized))

    def test_c_minimization_is_detected_when_broken(self):
        from dataclasses import replace

        dfa = dfa_examples.question2_dfa_d()
        minimized, _ = question2_dfa_minimization.minimize_dfa(dfa)
        wrong = replace(minimized, accepting_states=set())
        self.assertFalse(question1_dfa_equivalence.are_equivalent(dfa, wrong))

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

### 完整源码 · test_dfa_minimization.py

```python
import unittest

from dfa import Automaton
from question1_dfa_equivalence import _find_witness
from question2_dfa_minimization import (
    build_custom_merge_dfa,
    build_custom_minimal_dfa,
    build_example_dfa_d,
    minimize_dfa,
    verify_short_words,
)
from verify_submission import as_dfa_dict, check_question2_short_strings

class MinimizeDfaTests(unittest.TestCase):
    def test_multicharacter_symbols_keep_their_boundaries(self):
        dfa = Automaton(
            ["A", "B"], ["a", "b", "ab"], "A", {"B"},
            {"A": {"a": "A", "b": "A", "ab": "B"},
             "B": {"a": "A", "b": "A", "ab": "B"}},
        )
        minimized, _ = minimize_dfa(dfa)
        self.assertTrue(dfa.accepts(("ab",)))
        self.assertFalse(dfa.accepts(("a", "b")))
        self.assertFalse(dfa.accepts("ab"))
        verify_short_words(dfa, minimized, max_length=2)
        self.assertEqual(check_question2_short_strings(
            as_dfa_dict(dfa), as_dfa_dict(minimized), max_length=2,
        ), 13)

        rejecting = Automaton(
            ["S"], dfa.alphabet, "S", set(), {"S": dict.fromkeys(dfa.alphabet, "S")},
        )
        self.assertEqual(_find_witness(dfa, rejecting), ("ab",))

    def test_assignment_dfa_has_three_minimal_states(self):
        dfa = build_example_dfa_d()
        minimized, mapping = minimize_dfa(dfa)

        self.assertEqual(len(minimized.states), 3)
        self.assertEqual(mapping["IS0"], mapping["S3"])
        self.assertEqual(mapping["S1"], mapping["S4"])
        self.assertEqual(mapping["FS2"], mapping["FS5"])
        self.assertEqual(mapping["FS5"], mapping["FS6"])
        self.assertEqual(dfa.delta("IS0", "0"), "S1")
        self.assertEqual(dfa.delta("IS0", "1"), "S1")
        verify_short_words(dfa, minimized)
```

```python
    def test_assignment_dfa_minimized_transition_table(self):
        dfa = build_example_dfa_d()
        minimized, _ = minimize_dfa(dfa)

        self.assertEqual(minimized.states, ["Q0", "Q1", "Q2"])
        self.assertEqual(minimized.alphabet, ["0", "1"])
        self.assertEqual(minimized.start_state, "Q1")
        self.assertEqual(minimized.accepting_states, {"Q0"})
        self.assertEqual(
            minimized.transitions,
            {
                "Q0": {"0": "Q1", "1": "Q1"},
                "Q1": {"0": "Q2", "1": "Q2"},
                "Q2": {"0": "Q0", "1": "Q0"},
            },
        )

    def test_equivalent_states_merge_and_unreachable_state_is_removed(self):
        dfa = build_custom_merge_dfa()
        minimized, mapping = minimize_dfa(dfa)

        self.assertEqual(mapping, {"A": "Q0", "B": "Q1", "C": "Q1"})
        self.assertNotIn("X", mapping)
        self.assertEqual(len(minimized.states), 2)
        verify_short_words(dfa, minimized)

    def test_already_minimal_dfa_keeps_both_states(self):
        dfa = build_custom_minimal_dfa()
        minimized, mapping = minimize_dfa(dfa)

        self.assertEqual(len(minimized.states), 2)
        self.assertEqual(mapping, {"E": "Q0", "O": "Q1"})
        verify_short_words(dfa, minimized)

if __name__ == "__main__":
    unittest.main()
```

### 完整源码 · verify_minimization_equivalence.py

```python
from dataclasses import replace

from question1_dfa_equivalence import are_equivalent
from question2_dfa_minimization import (
    build_example_dfa_d,
    build_custom_merge_dfa,
    build_custom_minimal_dfa,
    minimize_dfa,
)

def check(label, builder):
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
```

### 完整源码 · verify_submission.py

```python
from itertools import product

import question1_dfa_equivalence
import question2_dfa_minimization
from question3_stack_membership import judge

Q1_MACHINE_1 = {
    "Q": {"A", "B"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("A", "0"): "A",
        ("A", "1"): "B",
        ("B", "0"): "A",
        ("B", "1"): "A",
    },
    "q0": "A",
    "F": {"B"},
}

Q1_MACHINE_2 = {
    "Q": {"C", "D"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("C", "0"): "D",
        ("C", "1"): "C",
        ("D", "0"): "D",
        ("D", "1"): "C",
    },
    "q0": "C",
    "F": {"C"},
}

Q2_MACHINE_D = {
    "Q": {"IS0", "S1", "FS2", "S3", "S4", "FS5", "FS6"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("IS0", "0"): "S1",
        ("IS0", "1"): "S1",
        ("S1", "0"): "FS2",
        ("S1", "1"): "FS5",
        ("FS2", "0"): "IS0",
        ("FS2", "1"): "IS0",
        ("S3", "0"): "S4",
        ("S3", "1"): "S4",
        ("S4", "0"): "FS5",
        ("S4", "1"): "FS6",
        ("FS5", "0"): "S3",
        ("FS5", "1"): "S3",
        ("FS6", "0"): "IS0",
        ("FS6", "1"): "IS0",
    },
    "q0": "IS0",
    "F": {"FS2", "FS5", "FS6"},
}

Q2_EXPECTED_MIN = {
    "Q": {"X", "Y", "Z"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("X", "0"): "Y",
        ("X", "1"): "Y",
        ("Y", "0"): "Z",
        ("Y", "1"): "Z",
        ("Z", "0"): "X",
        ("Z", "1"): "X",
    },
    "q0": "X",
    "F": {"Z"},
}

SELFTEST_1 = {
    "Q": {"P0", "P1"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("P0", "0"): "P0",
        ("P0", "1"): "P1",
        ("P1", "0"): "P0",
        ("P1", "1"): "P1",
    },
    "q0": "P0",
    "F": {"P1"},
}

SELFTEST_2 = {
    "Q": {"R0", "R1", "R2"},
    "SIGMA": {"0", "1"},
    "DELTA": {
        ("R0", "0"): "R0",
        ("R0", "1"): "R1",
        ("R1", "0"): "R0",
        ("R1", "1"): "R2",
        ("R2", "0"): "R0",
        ("R2", "1"): "R2",
    },
    "q0": "R0",
    "F": {"R1", "R2"},
}
```

```python
def dfa_accepts(dfa, word):
    current = dfa["q0"]
    for symbol in word:
        if symbol not in dfa["SIGMA"]:
            raise ValueError(f"字符 {symbol!r} 不在字母表中")
        try:
            current = dfa["DELTA"][(current, symbol)]
        except KeyError:
            raise ValueError(f"缺少转移：({current}, {symbol})") from None
    return current in dfa["F"]

def words(alphabet, max_length):
    if max_length < 0:
        raise ValueError("max_length 不能为负数")
    for length in range(max_length + 1):
        yield from product(sorted(alphabet), repeat=length)

def check_dfa(dfa, name="自动机"):
    problems = []
    if not dfa["Q"]:
        problems.append("状态集合为空")
    if dfa["q0"] not in dfa["Q"]:
        problems.append(f"初态 {dfa['q0']} 不在状态集合中")
    if not set(dfa["F"]) <= set(dfa["Q"]):
        problems.append(f"终态 {sorted(set(dfa['F']) - set(dfa['Q']), key=str)} 不在状态集合中")
    for state in dfa["Q"]:
        for symbol in dfa["SIGMA"]:
            target = dfa["DELTA"].get((state, symbol))
            if target is None:
                problems.append(f"缺少转移 ({state}, {symbol})")
            elif target not in dfa["Q"]:
                problems.append(f"转移 ({state}, {symbol}) 指向未知状态 {target}")
    for state, symbol in dfa["DELTA"]:
        if state not in dfa["Q"] or symbol not in dfa["SIGMA"]:
            problems.append(f"转移 ({state}, {symbol}) 的起点或字符不合法")
    if problems:
        raise AssertionError(f"{name} 数据有误：" + "；".join(problems))

def _show(word):
    if not word:
        return "ε"
    return "".join(word) if all(len(symbol) == 1 for symbol in word) else repr(word)

def _witness(parent, pair):
    symbols = []
    while parent[pair] is not None:
        pair, symbol = parent[pair]
        symbols.append(symbol)
    return tuple(reversed(symbols))
```

```python
def _search(first, second, start, symbols, is_final):
    parent = {start: None}
    frontier = [start]
    while frontier:
        next_frontier = []
        for pair in frontier:
            if is_final(pair[0], pair[1]):
                return _witness(parent, pair)
            for symbol in symbols:
                child = (first(pair[0], symbol), second(pair[1], symbol))
                if child not in parent:
                    parent[child] = (pair, symbol)
                    next_frontier.append(child)
        frontier = next_frontier
    return None

def equivalent_by_product(dfa_a, dfa_b):
    if dfa_a["SIGMA"] != dfa_b["SIGMA"]:
        raise ValueError("两个 DFA 必须使用相同字母表")
    check_dfa(dfa_a, "第一个自动机")
    check_dfa(dfa_b, "第二个自动机")
    witness = _search(
        lambda state, symbol: dfa_a["DELTA"][(state, symbol)],
        lambda state, symbol: dfa_b["DELTA"][(state, symbol)],
        (dfa_a["q0"], dfa_b["q0"]),
        sorted(dfa_a["SIGMA"]),
        lambda state_a, state_b: (state_a in dfa_a["F"]) != (state_b in dfa_b["F"]),
    )
    return witness is None, witness

def reachable_states(dfa):
    seen = {dfa["q0"]}
    stack = [dfa["q0"]]
    while stack:
        state = stack.pop()
        for symbol in dfa["SIGMA"]:
            target = dfa["DELTA"][(state, symbol)]
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return seen
```

```python
def distinguishing_string(dfa, state_a, state_b):
    return _search(
        lambda state, symbol: dfa["DELTA"][(state, symbol)],
        lambda state, symbol: dfa["DELTA"][(state, symbol)],
        (state_a, state_b),
        sorted(dfa["SIGMA"]),
        lambda left, right: (left in dfa["F"]) != (right in dfa["F"]),
    )

def check_minimality(dfa, name="自动机"):
    check_dfa(dfa, name)
    unreachable = set(dfa["Q"]) - reachable_states(dfa)
    if unreachable:
        raise AssertionError(f"{name} 存在不可达状态：{sorted(unreachable, key=str)}")
    states = sorted(dfa["Q"], key=str)
    for index, state_a in enumerate(states):
        for state_b in states[index + 1:]:
            if distinguishing_string(dfa, state_a, state_b) is None:
                raise AssertionError(f"{name} 中状态 {state_a} 与 {state_b} 不可区分")
    return len(states)

def check_question1_short_strings(
    dfa_a, dfa_b, reported_equivalent, expected_equivalent, max_length=4
):
    if dfa_a["SIGMA"] != dfa_b["SIGMA"]:
        raise ValueError("短串比较要求两个 DFA 使用相同字母表")
    mismatches = [
        word for word in words(dfa_a["SIGMA"], max_length)
        if dfa_accepts(dfa_a, word) != dfa_accepts(dfa_b, word)
    ]
    if bool(reported_equivalent) != expected_equivalent:
        raise AssertionError("第一题等价判定结果与独立预期不符")
    if expected_equivalent and mismatches:
        raise AssertionError(f"发现区分串：{_show(mismatches[0])}")
    if not expected_equivalent and not mismatches:
        raise AssertionError(
            f"长度不超过 {max_length} 的枚举未找到区分串；请加大上界"
        )
    return len(list(words(dfa_a["SIGMA"], max_length))), mismatches

def check_question2_short_strings(original, minimized, max_length=6):
    if original["SIGMA"] != minimized["SIGMA"]:
        raise ValueError("原 DFA 与最小化 DFA 必须使用相同字母表")
    for word in words(original["SIGMA"], max_length):
        if dfa_accepts(original, word) != dfa_accepts(minimized, word):
            raise AssertionError(f"最小化前后语言不一致，区分串：{_show(word)}")
    return len(list(words(original["SIGMA"], max_length)))
```

```python
def merge_mapping(original, minimized):
    variants = [
        dict(minimized, q0=state) for state in sorted(minimized["Q"], key=str)
    ]
    mapping = {}
    for state in sorted(original["Q"], key=str):
        matches = [
            variant["q0"] for variant in variants
            if equivalent_by_product(_start_at(original, state), variant)[0]
        ]
        if len(matches) != 1:
            raise AssertionError(f"状态 {state} 无法唯一对应到最小化状态：{matches}")
        mapping[state] = matches[0]
    return mapping

def _start_at(dfa, state):
    return dict(dfa, q0=state)

def as_dfa_dict(machine):
    return {
        "Q": set(machine.states),
        "SIGMA": set(machine.alphabet),
        "DELTA": {
            (state, symbol): target
            for state, row in machine.transitions.items()
            for symbol, target in row.items()
        },
        "q0": machine.start_state,
        "F": set(machine.accepting_states),
    }

def _partitions(mapping):
    groups = {}
    for state, target in mapping.items():
        groups.setdefault(target, set()).add(state)
    return {frozenset(group) for group in groups.values()}
```

```python
def verify_integration():
    print("== 跨题集成核验：组内实际代码 ==")
    counter_m1, counter_m2 = question1_dfa_equivalence.build_counterexample()
    dfa_m1, dfa_m2 = as_dfa_dict(counter_m1), as_dfa_dict(counter_m2)
    if (dfa_m1, dfa_m2) != (Q1_MACHINE_1, Q1_MACHINE_2):
        raise AssertionError("第一题数据与独立录入的题图不一致")
    reported = question1_dfa_equivalence.are_equivalent(counter_m1, counter_m2)
    independent, witness = equivalent_by_product(dfa_m1, dfa_m2)
    if reported != independent:
        raise AssertionError(
            f"第一题反例：B 判定 {reported}，独立判定 {independent}"
        )
    if independent:
        raise AssertionError("第一题反例应不等价")
    print(f"  第一题反例：B 与独立判定一致（不等价，区分串 {_show(witness)}）")

    positive_p1, positive_p2 = question1_dfa_equivalence.build_positive_example()
    reported = question1_dfa_equivalence.are_equivalent(positive_p1, positive_p2)
    independent, witness = equivalent_by_product(
        as_dfa_dict(positive_p1), as_dfa_dict(positive_p2)
    )
    if reported != independent or not independent:
        raise AssertionError(
            f"第一题正例：B 判定 {reported}，独立判定 {independent}"
        )
    print("  第一题正例：B 与独立判定一致（等价）")

    original_obj = question2_dfa_minimization.build_example_dfa_d()
    original = as_dfa_dict(original_obj)
    if original != Q2_MACHINE_D:
        raise AssertionError("第二题数据与独立录入的题图不一致")
    minimized_obj, mapping = question2_dfa_minimization.minimize_dfa(original_obj)
    minimized = as_dfa_dict(minimized_obj)
    check_dfa(original, "C 的题图 D")
    check_dfa(minimized, "C 的最小化结果")
    state_count = check_minimality(minimized, "C 的最小化结果")
    counted = check_question2_short_strings(original, minimized, max_length=8)
    if not equivalent_by_product(original, minimized)[0]:
        raise AssertionError("C 的最小化结果与原 DFA 不等价")
    if _partitions(mapping) != _partitions(merge_mapping(original, minimized)):
        raise AssertionError("C 的合并映射与独立核验得到的合并关系不一致")
    print(
        f"  第二题：C 的最小化结果 {state_count} 个状态，"
        f"可达且两两可区分，与原 DFA 等价，{counted} 个短串一致"
    )
    print(f"  第二题合并关系一致：{sorted((sorted(g) for g in _partitions(mapping)), key=lambda g: g[0])}")
```

```python
def verify_question3_variable_limit():
    print("== 第三题：变量限制审查 ==")
    code = judge.__code__
    allowed = {"s", "S", "ch"}
    extra = set(code.co_varnames) - allowed
    if extra:
        raise AssertionError(f"判定函数出现额外局部变量：{sorted(extra)}")
    if "judge" in code.co_names:
        raise AssertionError("判定函数中出现递归调用")
    print(f"  局部变量：{sorted(code.co_varnames)}；仅参数 s、堆栈 S、循环变量 ch")
    print("  未发现递归调用")

def _reference_member(word):
    zeros = len(word) - len(word.lstrip("0"))
    return zeros > 0 and word == "0" * zeros + "1" * zeros

def verify_question3_exhaustive(max_length=8):
    checked = 0
    for symbols in words("01a", max_length):
        word = "".join(symbols)
        if judge(word) != _reference_member(word):
            raise AssertionError(f"第三题穷举不一致：{_show(word)!r}")
        checked += 1
    print(f"第三题穷举（字母表 {{0,1,a}}，长度 0～{max_length}）：{checked} 个串全部一致")
```

```python
def verify_question3_boundaries():
    cases = (
        ("01", True),
        ("0011", True),
        ("000111", True),
        ("", False),
        ("0", False),
        ("1", False),
        ("00", False),
        ("11", False),
        ("011", False),
        ("001", False),
        ("0101", False),
        ("00110", False),
        ("10", False),
        ("00a11", False),
        ("001111", False),
        ("00011", False),
    )
    for input_string, expected in cases:
        actual = judge(input_string)
        if actual != expected:
            raise AssertionError(
                f"第三题用例 {input_string!r} 预期 {expected}，实际 {actual}"
            )
        verdict = "接受" if expected else "拒绝"
        print(f"  第三题 {_show(input_string)!r}: 预期{verdict}，实际{verdict}（通过）")
    print(f"第三题边界测试：{len(cases)}/{len(cases)} 通过")

def verify_question1():
    print("== 第一题：题图两个自动机 ==")
    check_dfa(Q1_MACHINE_1, "题图自动机 1")
    check_dfa(Q1_MACHINE_2, "题图自动机 2")
    equivalent, witness = equivalent_by_product(Q1_MACHINE_1, Q1_MACHINE_2)
    if equivalent:
        raise AssertionError("题图两个自动机应不等价")
    counted, mismatches = check_question1_short_strings(
        Q1_MACHINE_1, Q1_MACHINE_2, False, False, max_length=5
    )
    print(f"  乘积自动机判定：不等价，最短区分串 {_show(witness)}")
    print(f"  短串核对：枚举 {counted} 个串，首次发现差异 {_show(mismatches[0])}")
    selftest_equivalent, _ = equivalent_by_product(SELFTEST_1, SELFTEST_2)
    if not selftest_equivalent:
        raise AssertionError("核验器自检失败：构造的一对等价自动机被判为不等价")
    counted, _ = check_question1_short_strings(
        SELFTEST_1, SELFTEST_2, True, True, max_length=5
    )
    print(f"  核验器自检：一对等价自动机（2 状态与 3 状态）判定等价，枚举 {counted} 个串一致")
```

```python
def verify_question2():
    print("== 第二题：7 状态自动机 D ==")
    check_dfa(Q2_MACHINE_D, "题图自动机 D")
    if len(Q2_MACHINE_D["Q"]) != 7:
        raise AssertionError("题图自动机 D 应为 7 个状态")
    unreachable = set(Q2_MACHINE_D["Q"]) - reachable_states(Q2_MACHINE_D)
    if unreachable:
        raise AssertionError(f"题图自动机 D 存在不可达状态：{sorted(unreachable, key=str)}")

    equivalent, witness = equivalent_by_product(Q2_MACHINE_D, Q2_EXPECTED_MIN)
    if not equivalent:
        raise AssertionError(f"独立预期与实际不符，区分串：{_show(witness)}")
    for word in words({"0", "1"}, 8):
        if dfa_accepts(Q2_MACHINE_D, word) != (len(word) % 3 == 2):
            raise AssertionError(f"自动机 D 接受性与长度关系不符：{word!r}")
    print("  自动机 D 的语言：长度模 3 余 2 的 0/1 串（长度 0～8 共 511 个串核对一致）")

    count = check_minimality(Q2_EXPECTED_MIN, "独立预期最小自动机")
    counted = check_question2_short_strings(Q2_MACHINE_D, Q2_EXPECTED_MIN, max_length=8)
    print(f"  独立预期：{count} 个状态，全部可达且两两可区分，短串 {counted} 个一致")

    mapping = merge_mapping(Q2_MACHINE_D, Q2_EXPECTED_MIN)
    groups = {}
    for state, target in mapping.items():
        groups.setdefault(target, []).append(state)
    for target in sorted(groups, key=str):
        print(f"  合并关系：{target} <- {{{', '.join(groups[target])}}}")
    print("  最小化 DFA 的预期转移表：")
    for state in sorted(Q2_EXPECTED_MIN["Q"], key=str):
        mark = ("->" if state == Q2_EXPECTED_MIN["q0"] else "") + (
            "*" if state in Q2_EXPECTED_MIN["F"] else ""
        )
        row = [Q2_EXPECTED_MIN["DELTA"][(state, symbol)] for symbol in sorted(Q2_EXPECTED_MIN["SIGMA"])]
        print(f"    {mark:<4}{state:<4}0->{row[0]:<4}1->{row[1]}")
    return count, mapping

if __name__ == "__main__":
    verify_question3_variable_limit()
    verify_question3_boundaries()
    verify_question3_exhaustive()
    verify_question1()
    minimum_states, merge = verify_question2()
    verify_integration()
    print(
        "集成核验：B 的 question1_dfa_equivalence.py 与 C 的 question2_dfa_minimization.py 已与实际对象对照；"
        f"第二题最小状态数 {minimum_states}。"
    )
```
