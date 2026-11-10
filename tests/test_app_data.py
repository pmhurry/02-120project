"""Check barcode alignment and missing-versus-zero behavior for app maps."""
from array import array
import unittest

from app_data import spot_rows
from data_loader import Spot
from sparse_loader import Feature, SparseDataset


class AppDataTests(unittest.TestCase):
    def test_map_preserves_barcodes_coordinates_zero_and_missing(self):
        spots = [Spot('mouse_B', 'mouse', 48, False, 4, 9),
                 Spot('mouse_A', 'mouse', 48, True, 1, 2)]
        data = SparseDataset([Feature('id', 'gene', 'Gene Expression')], spots,
                             [array('I', [0]), array('I')],
                             [array('Q', [3]), array('Q')], {})
        rows = spot_rows(data, 'id')
        self.assertEqual([(r['barcode'], r['x'], r['y']) for r in rows],
                         [('mouse_B', 4, 9), ('mouse_A', 1, 2)])
        self.assertIsNone(rows[1]['expression'])
        data.features.append(Feature('zero', 'zero', 'Gene Expression'))
        zero = spot_rows(data, 'zero')
        self.assertEqual(zero[0]['expression'], 0)
        self.assertIsNone(zero[1]['expression'])
