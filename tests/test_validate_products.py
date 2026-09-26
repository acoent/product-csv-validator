import csv
import json
import tempfile
import unittest
from pathlib import Path

from validate_products import validate


class ValidateProductsTests(unittest.TestCase):
    def test_separates_bad_rows_and_reports_source_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.csv"
            input_path.write_text(
                "sku,name,price,quantity\nA,  Mug  ,12.50,2\nA,Duplicate,4,1\n"
                "B,Bad,NaN,2\nC,Missing,,0\nD,Valid,0,0\n",
                encoding="utf-8",
            )
            summary = validate(input_path, root / "output")
            self.assertEqual(summary, {"total": 5, "accepted": 2, "rejected": 3})
            with (root / "output/accepted.csv").open(newline="") as stream:
                accepted = list(csv.DictReader(stream))
            self.assertEqual([row["sku"] for row in accepted], ["A", "D"])
            self.assertEqual(accepted[0]["name"], "Mug")
            with (root / "output/rejected.csv").open(newline="") as stream:
                rejected = list(csv.DictReader(stream))
            self.assertEqual(rejected[0]["source_line"], "3")
            self.assertEqual(rejected[0]["errors"], "duplicate sku")
            self.assertIn("price", rejected[1]["errors"])
            self.assertEqual(json.loads((root / "output/summary.json").read_text()), summary)

    def test_missing_columns_fails_without_writing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "input.csv").write_text("sku,name\nA,Item\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "price, quantity"):
                validate(root / "input.csv", root / "output")
            self.assertFalse((root / "output").exists())

    def test_extra_fields_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "input.csv").write_text("sku,name,price,quantity\nA,Item,1,2,extra\n", encoding="utf-8")
            self.assertEqual(validate(root / "input.csv", root / "output")["rejected"], 1)


if __name__ == "__main__":
    unittest.main()
