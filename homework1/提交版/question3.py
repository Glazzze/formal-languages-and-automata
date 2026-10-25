TRANSITIONS = {
    "A": {"0": "A", "1": "B"},
    "B": {"0": "A", "1": "C"},
    "C": {"0": "C", "1": "C"},
}

START_STATE = "A"
ACCEPT_STATES = {"A", "B"}


def delta(q, a):
    """Return the state reached from q after reading a."""
    if q not in TRANSITIONS:
        raise ValueError(f"Unknown state: {q}")
    if a not in TRANSITIONS[q]:
        raise ValueError(f"Character is not in the input alphabet: {a}")
    return TRANSITIONS[q][a]


def Edelta(q, s):
    """Print each transition while reading s, then return the final state."""
    if q not in TRANSITIONS:
        raise ValueError(f"Unknown state: {q}")

    current_state = q
    for index, character in enumerate(s, start=1):
        next_state = delta(current_state, character)
        print(
            f"Step {index}: delta({current_state}, {character}) = {next_state}"
        )
        current_state = next_state
    return current_state


def run_case(label, input_string):
    print(f"{label}, input string: {input_string}")
    final_state = Edelta(START_STATE, input_string)
    result = "accepted" if final_state in ACCEPT_STATES else "rejected"
    print(f"Final state: {final_state}, result: {result}")
    print()


if __name__ == "__main__":
    run_case("Positive example", "101")
    run_case("Negative example", "111")
