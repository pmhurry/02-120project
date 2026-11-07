"""Evidence collection must retain returned trials and expose disagreements."""

import unittest

from gather_target_data import canonical, merge_evidence


class EvidenceTests(unittest.TestCase):
    def test_returned_trial_subsets_are_unioned_without_duplicates(self):
        a = {"id": "target", "trials": [{"id": "trial1", "stage": "PHASE_2"}]}
        b = {"id": "target", "trials": [{"id": "trial2", "stage": "PHASE_1"},
                                         {"id": "trial1", "stage": "PHASE_2"}]}
        result = merge_evidence(a, b)
        self.assertEqual({t["id"] for t in result["trials"]}, {"trial1", "trial2"})
        self.assertEqual(len(result["trials"]), 2)

    def test_conflicting_evidence_cannot_be_overwritten(self):
        for a, b in [({"score": 0.2}, {"score": 0.3}),
                     ([{"id": "trial", "stage": "PHASE_1"}],
                      [{"id": "trial", "stage": "PHASE_2"}])]:
            with self.subTest(a=a), self.assertRaisesRegex(ValueError, "Conflicting"):
                merge_evidence(a, b)

    def test_list_order_does_not_change_evidence(self):
        a = [{"id": "b", "events": ["x", "y"]}, {"id": "a", "events": []}]
        b = [{"id": "a", "events": []}, {"id": "b", "events": ["y", "x"]}]
        self.assertEqual(canonical(a), canonical(b))


if __name__ == "__main__":
    unittest.main()
