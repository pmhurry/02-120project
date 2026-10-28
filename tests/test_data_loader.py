import tempfile
from pathlib import Path
import unittest

from data_loader import load_dataset


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.meta = self.root / "meta.csv"
        self.matrix = self.root / "matrix.csv"
        self.meta.write_text(
            "Spot_barcode,Mouse,Time_point,Fibrogenic_spot,visium_coor_x,visium_coor_y\n"
            "b,mouse_b,48,0,20,30\na,mouse_a,24,1,10,15\nc,mouse_c,72,0,40,50\n"
        )

    def test_alignment_and_missing_expression(self):
        self.matrix.write_text("Gene_Name,a,b\nCol1a1,2,7\nCol1a1,3,8\n")
        data = load_dataset(self.matrix, self.meta)
        self.assertEqual([s.mouse for s in data.spots], ["mouse_a", "mouse_b"])
        self.assertEqual(list(data.counts[0]), [2, 7])
        self.assertEqual(data.genes, ["Col1a1", "Col1a1"])
        self.assertIn("c", data.metadata)
        self.assertNotIn("c", [s.barcode for s in data.spots])

    def test_unmatched_barcode_is_rejected(self):
        self.matrix.write_text("Gene_Name,unknown\nCol1a1,2\n")
        with self.assertRaisesRegex(ValueError, "lack metadata"):
            load_dataset(self.matrix, self.meta)

    def test_invalid_counts_are_rejected(self):
        for value in ["-1", "0.5", "nan", "inf"]:
            with self.subTest(value=value):
                self.matrix.write_text(f"Gene_Name,a\nCol1a1,{value}\n")
                with self.assertRaisesRegex(ValueError, "integer counts"):
                    load_dataset(self.matrix, self.meta)


if __name__ == "__main__":
    unittest.main()
