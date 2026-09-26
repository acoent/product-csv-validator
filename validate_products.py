import argparse
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = ("sku", "name", "price", "quantity")


def validate(input_path: Path, output_dir: Path) -> dict:
    if not input_path.is_file():
        raise ValueError(f"Input file does not exist: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames or []
        missing = [column for column in REQUIRED if column not in headers]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))
        if len(headers) != len(set(headers)):
            raise ValueError("Duplicate column names in header")

        accepted, rejected, seen_skus = [], [], set()
        for line_number, row in enumerate(reader, start=2):
            errors = []
            if None in row:
                errors.append("extra fields")
                row.pop(None)
            clean = {key: (value or "").strip() for key, value in row.items()}
            sku = clean["sku"]
            if not sku:
                errors.append("sku is required")
            elif sku in seen_skus:
                errors.append("duplicate sku")
            else:
                seen_skus.add(sku)
            if not clean["name"]:
                errors.append("name is required")
            try:
                price = Decimal(clean["price"])
                if not price.is_finite() or price < 0:
                    raise InvalidOperation
                clean["price"] = str(price)
            except (InvalidOperation, ValueError):
                errors.append("price must be a non-negative number")
            try:
                quantity = int(clean["quantity"])
                if quantity < 0:
                    raise ValueError
                clean["quantity"] = str(quantity)
            except ValueError:
                errors.append("quantity must be a non-negative integer")
            if errors:
                rejected.append({**clean, "source_line": line_number, "errors": "; ".join(errors)})
            else:
                accepted.append(clean)

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, columns, rows in (
        ("accepted.csv", headers, accepted),
        ("rejected.csv", [*headers, "source_line", "errors"], rejected),
    ):
        with (output_dir / filename).open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    summary = {"total": len(accepted) + len(rejected), "accepted": len(accepted), "rejected": len(rejected)}
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV file with sku,name,price,quantity columns")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.input, args.output_dir)))
    except (ValueError, UnicodeError, csv.Error) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
