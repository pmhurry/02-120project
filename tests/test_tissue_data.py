import unittest

from gather_tissue_data import collect_rna, rna_summary


class TissueTests(unittest.TestCase):
    def test_missing_and_measured_zero_remain_distinct(self):
        missing = rna_summary({})
        measured = rna_summary({"liver": 0, "kidney": 0})
        self.assertIsNone(missing["liver_ntpm"])
        self.assertIsNone(missing["max_non_liver_ntpm"])
        self.assertEqual(measured["liver_ntpm"], 0)
        self.assertEqual(measured["max_non_liver_ntpm"], 0)

    def test_non_liver_maximum_preserves_ties(self):
        result = rna_summary({"liver": 100, "heart": 4, "kidney": 4, "lung": 0.5})
        self.assertEqual(result["max_non_liver_ntpm"], 4)
        self.assertEqual(result["max_non_liver_tissues"], "heart|kidney")
        self.assertEqual(result["non_liver_tissues_ge_1_ntpm"], 2)

    def test_duplicates_and_invalid_rna_are_rejected(self):
        row = {"Gene": "id", "Tissue": "liver", "nTPM": "1"}
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            collect_rna([row, row])
        for value in ["-1", "nan", "inf"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                collect_rna([{**row, "nTPM": value}])
