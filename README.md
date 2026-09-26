# Product CSV Validator

A small Python command-line tool for preparing product catalogs for import. It reads a UTF-8 CSV, trims whitespace, validates `sku`, `name`, `price` and `quantity`, and writes accepted rows and rejected rows with line numbers and reasons. It uses only the Python standard library; no API keys or paid services are required.

## Run

Python 3.10+ (Windows Command Prompt, PowerShell, macOS or Linux). Run from the project directory. Keep the `examples` and `tests` folders when extracting the ZIP:

```bash
python validate_products.py examples/products.csv --output-dir output
```

The tool creates `output/accepted.csv`, `output/rejected.csv`, and `output/summary.json`. The example has two accepted rows and four rejected rows. Existing output files with those names are replaced.

Sample input: [`examples/products.csv`](examples/products.csv). The first two products pass; the other four demonstrate a duplicate SKU, an invalid price, a missing name and a negative quantity. To use your own file, replace `examples/products.csv` in the command with its path.

## Input rules

The CSV header must contain `sku,name,price,quantity` (additional columns are preserved). `sku` and `name` cannot be blank; SKUs must be unique within the input, with the first occurrence reserved even if another field on that row is invalid. `price` must be a finite non-negative decimal with a dot as the separator. `quantity` must be a non-negative integer. An extra value after the declared columns rejects that row. Leading and trailing whitespace is removed from all values.

## Tests

```bash
python -m unittest discover -s tests -v
```

For a real catalog, the required fields, duplicate policy and price formats should be agreed before use.
