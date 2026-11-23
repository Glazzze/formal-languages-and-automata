# -*- coding: utf-8 -*-
"""公共 DFA 类（第一、二题共用）。

本模块是第二次编程作业的唯一定义自动机类的位置。第一题的等价判定和
第二题的最小化都从这里导入 :class:`Automaton`，不要在各自的题目文件里
再复制一份类定义。

约定（与《接口说明.md》一致）：

* 状态名、字母表符号都用字符串表示；``states`` 与 ``alphabet`` 保留录入
  顺序，便于打印和核对。
* 转移表是**全函数**：每个状态对每个字母都必须有转移。缺转移、引用未知
  状态等输入一律视为录入错误并抛出 ``ValueError``，避免两题对同一份数据
  采用不同解释。
* 确实需要从“部分转移表”开始时，使用 :meth:`Automaton.from_partial`，
  由公共类统一补一个陷阱状态；不要在各题里各写一套补边规则。
* 两个自动机的字母表可能不同。判断语言关系前必须先统一到字母表并集，
  用 :func:`normalize_for_equivalence` 完成，不能因为字母表不同就直接
  判为不等价。
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set, Tuple


TRAP_STATE = "__trap__"


def _fresh_state_name(existing: Iterable[str], base: str = TRAP_STATE) -> str:
    """Return a state name not used in *existing* (used for trap states)."""
    existing = set(existing)
    if base not in existing:
        return base
    index = 1
    while f"{base}_{index}" in existing:
        index += 1
    return f"{base}_{index}"


def _as_str_list(values: Sequence[str], field_name: str) -> List[str]:
    """Copy an iterable of names and validate the element type."""
    result = list(values)
    for value in result:
        if not isinstance(value, str):
            raise TypeError(f"{field_name} 中的元素必须是字符串，收到 {value!r}。")
        if value == "":
            raise ValueError(f"{field_name} 中不允许空字符串。")
    return result


@dataclass(frozen=True)
class Automaton:
    """确定型有限自动机（DFA）。

    Parameters
    ----------
    states:
        状态名列表，保留录入顺序。
    alphabet:
        字母表符号列表，保留录入顺序。
    start_state:
        初态名，必须属于 ``states``。
    accepting_states:
        终态集合，必须是 ``states`` 的子集。
    transitions:
        嵌套字典 ``transitions[state][symbol] -> state``，必须是全函数。

    Notes
    -----
    构造时会复制传入的列表/集合/字典，因此之后修改调用方对象不会影响本
    实例。字段仍保持 ``List`` / ``Set`` 类型，与第二题现有代码和单元测试
    的断言一致（例如 ``minimized.states == ["Q0", "Q1"]``）。
    """

    states: List[str]
    alphabet: List[str]
    start_state: str
    accepting_states: Set[str]
    transitions: Dict[str, Dict[str, str]]

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

        # frozen dataclass 的标准写法：在 __post_init__ 中写入规范化后的副本。
        object.__setattr__(self, "states", states)
        object.__setattr__(self, "alphabet", alphabet)
        object.__setattr__(self, "accepting_states", accepting)
        object.__setattr__(self, "transitions", transitions)

    # ------------------------------------------------------------------
    # 基本查询
    # ------------------------------------------------------------------
    def delta(self, state: str, symbol: str) -> str:
        """Return δ(state, symbol), with explicit error messages."""
        if state not in self.states:
            raise ValueError(f"未知状态 {state!r}。")
        if symbol not in self.alphabet:
            raise ValueError(f"未知字母表符号 {symbol!r}。")
        return self.transitions[state][symbol]

    def is_final(self, state: str) -> bool:
        """Return whether *state* is accepting (convenience for callers)."""
        if state not in self.states:
            raise ValueError(f"未知状态 {state!r}。")
        return state in self.accepting_states

    def accepts(self, word: Sequence[str]) -> bool:
        """Read a sequence of symbols. A plain string is read character by character."""
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
        """Return all states reachable from the start state (sorted)."""
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
    def pretty_print(self, label: str = "DFA") -> None:
        """Print the five components and the complete transition table."""
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
    """Return the sorted union of the automatons' alphabets."""
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
