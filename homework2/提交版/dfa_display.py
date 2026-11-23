"""打印第二题的状态对标记、状态合并关系和完整自动机。"""

from dfa import Automaton


def print_minimization(
    dfa: Automaton,
    minimized: Automaton,
    mapping: dict[str, str],
    rounds: dict[tuple[str, str], int],
    label: str,
) -> None:
    """输出原 DFA、各轮标记以及最小化结果。"""
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

