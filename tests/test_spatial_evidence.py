from array import array
import math
import unittest

from data_loader import Spot
from sparse_loader import Feature, SparseDataset
from spatial_evidence import equal_mouse_summaries, normalized_count, summarize


def dataset(profiles, labels, mice=None):
    mice = mice or ['mouse1'] * len(profiles)
    spots = [Spot(str(j), mouse, 48, label, 0, 0)
             for j, (mouse, label) in enumerate(zip(mice, labels))]
    return SparseDataset([Feature('id1', 'Same', 'Gene Expression'), Feature('id2', 'Same', 'Gene Expression')],
                         spots, [array('I', (i for i, c in enumerate(p) if c)) for p in profiles],
                         [array('Q', (c for c in p if c)) for p in profiles], {s.barcode: s for s in spots})


class SpatialTests(unittest.TestCase):
    def test_hand_normalization_detection_and_known_contrast(self):
        data = dataset([[1, 3], [0, 4]], [True, False])
        libraries, qc, rows = summarize(data)
        self.assertEqual(libraries, [4, 4])
        self.assertEqual(qc[0]['retained_spots'], 2)
        self.assertAlmostEqual(rows[0]['annotated_mean'], math.log(2501))
        self.assertEqual(rows[0]['other_mean'], 0)
        self.assertEqual(rows[0]['difference'], rows[0]['annotated_mean'])
        self.assertEqual(rows[0]['annotated_detection'], 1)
        self.assertEqual(rows[0]['other_detection'], 0)
        self.assertLess(rows[1]['difference'], 0)
        self.assertEqual([r['feature_id'] for r in rows], ['id1', 'id2'])

    def test_identical_proportions_and_column_alignment(self):
        data = dataset([[1, 3], [2, 6]], [True, False])
        self.assertEqual(summarize(data)[2][0]['difference'], 0)
        data.spots.reverse()
        data.indices.reverse()
        data.values.reverse()
        self.assertEqual(summarize(data)[2][0]['difference'], 0)
        contrast = dataset([[1, 3], [0, 4]], [True, False])
        expected = summarize(contrast)[2]
        contrast.spots.reverse()
        contrast.indices.reverse()
        contrast.values.reverse()
        self.assertEqual(summarize(contrast)[2], expected)

    def test_zero_library_missing_group_and_zero_feature(self):
        data = dataset([[0, 0], [0, 4]], [True, False])
        libraries, qc, rows = summarize(data)
        self.assertIsNone(normalized_count(0, 0))
        self.assertEqual(qc[0]['excluded_zero_library'], 1)
        self.assertIsNone(rows[0]['annotated_mean'])
        self.assertIsNone(rows[0]['difference'])
        self.assertEqual(rows[0]['other_mean'], 0)
        self.assertEqual(rows[0]['status'], 'missing_group')
        self.assertIsNone(equal_mouse_summaries(rows)[1]['difference'])

    def test_equal_weight_mice_despite_unequal_spot_counts(self):
        data = dataset([[1, 3], [0, 4], [0, 4], [0, 4], [1, 3]],
                       [True, False, True, True, False], ['a', 'a', 'b', 'b', 'b'])
        rows = summarize(data)[2]
        aggregate = [r for r in equal_mouse_summaries(rows) if r['context'] == '48h' and r['feature_id'] == 'id1'][0]
        self.assertEqual(aggregate['available_mice'], 2)
        self.assertEqual(aggregate['difference'], 0)
        self.assertAlmostEqual(aggregate['annotated_mean'], math.log(2501) / 2)
        self.assertIsNone([r for r in equal_mouse_summaries(rows) if r['context'] == '48h_72h'][0]['difference'])

    def test_absent_group_and_invalid_sparse_columns(self):
        self.assertIsNone(summarize(dataset([[1, 3]], [True]))[2][0]['difference'])
        data = dataset([[1, 3]], [True])
        data.indices[0] = array('I', [0, 0])
        with self.assertRaises(ValueError):
            summarize(data)

    def test_time_contexts_stay_separate_and_combined_is_equal_weight(self):
        rows = []
        for time, effect in ((24, 99), (48, 2), (72, 4)):
            for mouse in ('a', 'b'):
                rows.append(dict(feature_id='id', symbol='X', mouse=f'{time}{mouse}',
                                 time_hours=time, difference=effect, annotated_mean=effect,
                                 other_mean=0, annotated_detection=1, other_detection=0))
        result = {r['context']: r for r in equal_mouse_summaries(rows)}
        self.assertEqual(result['24h_context']['difference'], 99)
        self.assertEqual(result['48h_72h']['difference'], 3)
        rows[-1]['difference'] = None
        result = {r['context']: r for r in equal_mouse_summaries(rows)}
        self.assertIsNone(result['48h_72h']['difference'])
        self.assertEqual(result['48h']['difference'], 2)
