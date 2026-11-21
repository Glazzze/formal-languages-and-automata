# -*- coding: utf-8 -*-
"""成员 A 的公共类基础测试与接口对齐检查。

运行（在 homework2 目录下）：

    python -m unittest -v test_automaton

覆盖四组内容：

1. ``Automaton`` 构造校验、复制语义、δ/接受/可达状态/打印；
2. 部分转移表补陷阱、字母表并集规范化；
3. 题图数据（M1、M2、DFA D）与 B、C 已交付数据的逐项对照；
4. 第一、二题通过公共类互操作：B 的等价函数、C 的最小化函数。
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import itertools
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import examples  # noqa: E402
import question1  # noqa: E402
from automaton import (  # noqa: E402
    TRAP_STATE,
    Automaton,
    common_alphabet,
    normalize_for_equivalence,
)


def _load_c_question2():
    """按最终提交布局加载 C 的 question2.py（让它导入根目录公共类）。"""
    path = ROOT / "C" / "question2.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("c_question2", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C_Q2 = _load_c_question2()


def _start(automaton):
    return (
        automaton.start_state
        if hasattr(automaton, "start_state")
        else automaton.start
    )


def _finals(automaton):
    return set(
        automaton.accepting_states
        if hasattr(automaton, "accepting_states")
        else automaton.finals
    )


def _structure(automaton):
    """Return a representation-neutral snapshot for cross-checking data."""
    states = list(automaton.states)
    raw = automaton.transitions
    if raw and all(isinstance(row, dict) for row in raw.values()):
        transitions = {state: dict(row) for state, row in raw.items()}
    else:
        transitions = {state: {} for state in states}
        for (state, symbol), target in raw.items():
            transitions.setdefault(state, {})[symbol] = target
    return (
        sorted(states),
        sorted(automaton.alphabet),
        _start(automaton),
        _finals(automaton),
        transitions,
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
        dfa = examples.question2_merge_dfa()
        self.assertEqual(dfa.reachable_states(), ["A", "B", "C"])

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
    def test_from_partial_adds_trap_and_preserves_language(self):
        dfa = examples.partial_endswith_1()
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
        dfa = examples.epsilon_only(["0"])
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
            common_alphabet(examples.question1_m1(), examples.empty_language(["a"])),
            ["0", "1", "a"],
        )

    def test_normalize_different_alphabet_equal_language(self):
        left = examples.epsilon_only(["0"])
        right = examples.epsilon_only(["0", "1"])
        left, right = normalize_for_equivalence(left, right)
        self.assertEqual(left.alphabet, right.alphabet)
        self.assertEqual(left.alphabet, ["0", "1"])
        _assert_same_language(self, left, right)

    def test_normalize_different_alphabet_empty_languages(self):
        left = examples.empty_language(["0"])
        right = examples.empty_language(["1"])
        left, right = normalize_for_equivalence(left, right)
        _assert_same_language(self, left, right)

    def test_normalize_requires_automaton(self):
        with self.assertRaises(TypeError):
            normalize_for_equivalence(_sample_dfa(), object())


class FigureDataTests(unittest.TestCase):
    def test_m1_and_m2_match_question1_builders(self):
        self.assertEqual(_structure(examples.question1_m1()),
                         _structure(question1.build_counterexample()[0]))
        self.assertEqual(_structure(examples.question1_m2()),
                         _structure(question1.build_counterexample()[1]))

    def test_m1_is_not_simply_ends_with_one(self):
        m1 = examples.question1_m1()
        m2 = examples.question1_m2()
        self.assertTrue(m1.accepts("1"))
        self.assertTrue(m1.accepts("01"))
        self.assertTrue(m1.accepts("101"))
        self.assertFalse(m1.accepts("11"))
        self.assertFalse(m1.accepts("011"))
        self.assertFalse(m1.accepts(""))
        self.assertTrue(m2.accepts(""))
        self.assertTrue(m2.accepts("11"))

    def test_positive_example_matches_question1_builders(self):
        p1, p2 = examples.question1_positive_example()
        b1, b2 = question1.build_positive_example()
        self.assertEqual(_structure(p1), _structure(b1))
        self.assertEqual(_structure(p2), _structure(b2))
        _assert_same_language(self, p1, p2, max_length=6)

    def test_dfa_d_has_expected_table(self):
        dfa = examples.question2_dfa_d()
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

    @unittest.skipUnless(C_Q2, "C/question2.py 尚未交付")
    def test_dfa_d_matches_c_builder(self):
        self.assertEqual(_structure(examples.question2_dfa_d()),
                         _structure(C_Q2.build_example_dfa_d()))

    @unittest.skipUnless(C_Q2, "C/question2.py 尚未交付")
    def test_custom_examples_match_c_builders(self):
        self.assertEqual(_structure(examples.question2_merge_dfa()),
                         _structure(C_Q2.build_custom_merge_dfa()))
        self.assertEqual(_structure(examples.question2_minimal_dfa()),
                         _structure(C_Q2.build_custom_minimal_dfa()))


class InterfaceAlignmentTests(unittest.TestCase):
    def test_question1_accepts_shared_automaton(self):
        m1, m2 = examples.question1_counterexample()
        p1, p2 = examples.question1_positive_example()
        self.assertFalse(question1.are_equivalent(m1, m2))
        self.assertTrue(question1.are_equivalent(p1, p2))

    @unittest.skipUnless(C_Q2, "C/question2.py 尚未交付")
    def test_c_minimization_uses_shared_class(self):
        dfa = examples.question2_dfa_d()
        minimized, mapping = C_Q2.minimize_dfa(dfa)
        self.assertIsInstance(minimized, Automaton)
        self.assertEqual(minimized.states, ["Q0", "Q1", "Q2"])
        self.assertEqual(minimized.alphabet, ["0", "1"])
        self.assertEqual(minimized.start_state, "Q1")
        self.assertEqual(minimized.accepting_states, {"Q0"})
        self.assertEqual(mapping["IS0"], mapping["S3"])
        self.assertEqual(mapping["S1"], mapping["S4"])
        self.assertTrue(question1.are_equivalent(dfa, minimized))

    @unittest.skipUnless(C_Q2, "C/question2.py 尚未交付")
    def test_c_minimization_is_detected_when_broken(self):
        from dataclasses import replace

        dfa = examples.question2_dfa_d()
        minimized, _ = C_Q2.minimize_dfa(dfa)
        wrong = replace(minimized, accepting_states=set())
        self.assertFalse(question1.are_equivalent(dfa, wrong))


if __name__ == "__main__":
    unittest.main(verbosity=2)
