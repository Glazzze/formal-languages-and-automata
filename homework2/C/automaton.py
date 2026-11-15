from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass(frozen=True)
class Automaton:
    """A deterministic finite automaton with a complete transition table."""

    states: List[str]
    alphabet: List[str]
    start_state: str
    accepting_states: Set[str]
    transitions: Dict[str, Dict[str, str]]

    def __post_init__(self) -> None:
        if len(set(self.states)) != len(self.states):
            raise ValueError("State names must be unique.")
        if len(set(self.alphabet)) != len(self.alphabet):
            raise ValueError("Alphabet symbols must be unique.")
        if self.start_state not in self.states:
            raise ValueError(f"Unknown start state {self.start_state!r}.")
        if not self.accepting_states.issubset(set(self.states)):
            raise ValueError("Accepting states must belong to the state set.")

        for state in self.states:
            if state not in self.transitions:
                raise ValueError(f"Missing transition table for state {state!r}.")
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]:
                    raise ValueError(
                        f"Missing transition for state {state!r} on {symbol!r}."
                    )
                target = self.transitions[state][symbol]
                if target not in self.states:
                    raise ValueError(
                        f"Transition from {state!r} on {symbol!r} points "
                        f"to unknown state {target!r}."
                    )

    def delta(self, state: str, symbol: str) -> str:
        if state not in self.states:
            raise ValueError(f"Unknown state {state!r}.")
        if symbol not in self.alphabet:
            raise ValueError(f"Unknown alphabet symbol {symbol!r}.")
        return self.transitions[state][symbol]

    def accepts(self, word: str) -> bool:
        current = self.start_state
        for symbol in word:
            current = self.delta(current, symbol)
        return current in self.accepting_states

    def reachable_states(self) -> List[str]:
        reached = {self.start_state}
        queue = [self.start_state]
        while queue:
            state = queue.pop(0)
            for symbol in self.alphabet:
                target = self.delta(state, symbol)
                if target not in reached:
                    reached.add(target)
                    queue.append(target)
        return sorted(reached)

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
