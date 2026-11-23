"""第二题：按状态对标记法最小化 DFA。"""

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
    """Return an unordered state pair in a canonical order."""
    return (first, second) if first < second else (second, first)


def distinguishable_pair_rounds(dfa: Automaton) -> Dict[Pair, int]:
    """Return each reachable distinguishable pair and the round it is marked."""
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


def _build_minimized(
    dfa: Automaton, rounds: Dict[Pair, int]
) -> Tuple[Automaton, Dict[str, str]]:
    """Build the quotient DFA from precomputed pair-marking rounds."""
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
    """Minimize a DFA by state-pair marking and return it with the state mapping.

    Unreachable states are removed first. The mapping contains reachable original
    states only; absent original states were removed as unreachable.
    """
    return _build_minimized(dfa, distinguishable_pair_rounds(dfa))


def print_minimization_report(dfa: Automaton, label: str) -> None:
    rounds = distinguishable_pair_rounds(dfa)
    minimized, mapping = _build_minimized(dfa, rounds)
    print_minimization(dfa, minimized, mapping, rounds, label)


def verify_short_words(original: Automaton, minimized: Automaton, max_length: int = 5) -> None:
    """Supplementary bounded check; the pair-marking algorithm is the proof."""
    for length in range(max_length + 1):
        for symbols in product(original.alphabet, repeat=length):
            if original.accepts(symbols) != minimized.accepts(symbols):
                raise AssertionError(f"Acceptance mismatch for {symbols!r}.")


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
