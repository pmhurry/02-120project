import gzip
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from data_loader import Spot
from sparse_loader import SparseDataset, read_archive


class SparseLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "sample.zip"
        self.spot = Spot("t_24h_m1_B_1", "t_24h_m1", 24, True, 1, 2)
        self.metadata = {self.spot.barcode: self.spot}

    def archive(self, matrix="2 2 3\n2 2 4\n1 1 99\n1 2 3\n"):
        with zipfile.ZipFile(self.path, "w") as archive:
            for name, content in {
                "features.tsv.gz": "id1\tSame\tGene Expression\nid2\tSame\tGene Expression\n",
                "barcodes.tsv.gz": "A-1\nB-1\n",
                "matrix.mtx.gz": "%%MatrixMarket matrix coordinate integer general\n% test\n" + matrix,
            }.items():
                archive.writestr("sample/outs/raw_feature_bc_matrix/" + name, gzip.compress(content.encode()))
        return hashlib.md5(self.path.read_bytes()).hexdigest()

    def test_select_metadata_sort_coordinates_and_preserve_ids(self):
        checksum = self.archive()
        features, spots, indices, values = read_archive(self.path, "24_m1", self.metadata, checksum)
        data = SparseDataset(features, spots, indices, values, self.metadata)
        self.assertEqual(spots, [self.spot])
        self.assertEqual([f.feature_id for f in features], ["id1", "id2"])
        self.assertEqual([data.count(i, 0) for i in range(2)], [3, 4])
        self.assertEqual(data.feature_index("id2"), 1)
        with self.assertRaisesRegex(ValueError, "uniquely"):
            data.feature_index("Same")

    def test_measured_zero_is_implicit(self):
        checksum = self.archive("2 2 1\n2 2 4\n")
        f, s, i, v = read_archive(self.path, "24_m1", self.metadata, checksum)
        self.assertEqual(SparseDataset(f, s, i, v, self.metadata).count(0, 0), 0)

    def test_checksum_and_missing_barcodes_fail(self):
        checksum = self.archive()
        with self.assertRaisesRegex(ValueError, "Checksum"):
            read_archive(self.path, "24_m1", self.metadata, "wrong")
        missing = Spot("t_24h_m1_C_1", "t_24h_m1", 24, False, 0, 0)
        with self.assertRaisesRegex(ValueError, "Missing metadata"):
            read_archive(self.path, "24_m1", {missing.barcode: missing}, checksum)

    def test_malformed_counts_dimensions_and_entries_fail(self):
        for matrix in ["2 2 1\n1 2 -1\n", "3 2 0\n", "2 2 2\n1 2 1\n",
                       "2 2 1\n3 2 1\n", "2 2 2\n1 2 1\n1 2 2\n"]:
            with self.subTest(matrix=matrix):
                checksum = self.archive(matrix)
                with self.assertRaises(ValueError):
                    read_archive(self.path, "24_m1", self.metadata, checksum)
