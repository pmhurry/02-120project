from array import array
import math
import unittest

from data_loader import Dataset, Spot
from scoring import score_dataset


def dataset(genes, rows):
    spots = [Spot(str(j), "mouse", 24, False, j, 0) for j in range(len(rows[0]))]
    return Dataset(genes, [array("d", row) for row in rows], spots, {s.barcode: s for s in spots})


class ScoringTests(unittest.TestCase):
    def test_identical_nonzero_profiles_score_exactly_zero(self):
        result = score_dataset(dataset(["marker", "other"], [[2, 2, 2], [8, 8, 8]]), ("marker",))
        self.assertEqual(result.scores, [0.0, 0.0, 0.0])
        self.assertEqual(result.reference_sds["marker"], 0.0)
        self.assertAlmostEqual(result.normalized_markers["marker"][0], math.log1p(2000))

    def test_depth_scaling_does_not_change_normalized_profile(self):
        result = score_dataset(dataset(["marker", "other"], [[2, 4], [8, 16]]), ("marker",))
        self.assertEqual(result.scores, [0.0, 0.0])

    def test_known_contrast_and_zero_library(self):
        result = score_dataset(dataset(["marker", "other"], [[0, 10, 0], [10, 0, 0]]), ("marker",))
        self.assertEqual(result.scores, [-1.0, 1.0, None])
        self.assertTrue(math.isnan(result.normalized_markers["marker"][2]))
        self.assertEqual(result.normalized_markers["marker"][0], 0.0)

    def test_all_zero_libraries_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "No positive-library"):
            score_dataset(dataset(["marker"], [[0, 0]]), ("marker",))

    def test_missing_and_duplicate_markers_are_rejected(self):
        for genes in (["other"], ["marker", "marker"]):
            with self.subTest(genes=genes), self.assertRaisesRegex(ValueError, "exactly one"):
                score_dataset(dataset(genes, [[1, 2] for _ in genes]), ("marker",))
