import unittest

from question2 import (
    build_custom_merge_dfa,
    build_custom_minimal_dfa,
    build_example_dfa_d,
    minimize_dfa,
    verify_short_words,
)


class MinimizeDfaTests(unittest.TestCase):
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
