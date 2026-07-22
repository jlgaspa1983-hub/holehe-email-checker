# Holehe Email Checker Automation

Automated email reconnaissance tool using **holehe** to check if email addresses are registered on various websites.

## Features

✅ **Single Email Check** - Check one email at a time  
✅ **Bulk Email Check** - Sequential and parallel processing  
✅ **CSV/JSON Export** - Multiple output formats  
✅ **Results Analysis** - Statistics and reports  
✅ **Comprehensive Tests** - Full test coverage  

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup

```bash
# Clone or enter the repository
cd holehe-email-checker

# Run setup script
bash setup.sh

# Or install manually
pip install -r requirements.txt
```

## Usage

### 1. Single Email Check

```bash
python run_holehe_check.py
```

**Programmatic usage:**
```python
from run_holehe_check import HoleheChecker

checker = HoleheChecker()
results = checker.check_email("c.dmierc@gmail.com", only_used=True)
checker.print_summary(results)
```

### 2. Bulk Email Check (Sequential)

```bash
python bulk_email_checker.py
```

**Edit `bulk_email_checker.py` to change emails:**
```python
emails = [
    "email1@example.com",
    "email2@example.com",
    "email3@example.com",
]
```

### 3. Bulk Email Check (Parallel)

Uncomment in `bulk_email_checker.py`:
```python
results_par = bulk_checker.check_parallel(emails, max_workers=4)
```

### 4. Results Analysis

```bash
python results_analyzer.py
```

Generates:
- Website report
- Email report
- CSV summary

### 5. Run Tests

```bash
pytest test_holehe.py -v

# With coverage
pytest test_holehe.py -v --cov=.
```

## Command Line Reference

### Direct holehe usage

```bash
# Check single email
holehe c.dmierc@gmail.com --only-used --csv

# Check multiple sites
holehe c.dmierc@gmail.com

# Only specific site
holehe c.dmierc@gmail.com --only-site instagram
```

## Output Files

Results are saved to:
- `results/` - Single email check results
- `bulk_results/` - Bulk check results
- Generated files:
  - `bulk_results_*.json` - Full results
  - `bulk_results_*.csv` - Flattened results
  - `report_*.txt` - Human-readable report
  - `website_report_*.txt` - Website analysis
  - `email_report_*.txt` - Email analysis
  - `summary_*.csv` - CSV summary

## Project Structure

```
holehe-email-checker/
├── setup.sh                 # Setup script
├── requirements.txt         # Python dependencies
├── run_holehe_check.py      # Single email checker
├── bulk_email_checker.py    # Bulk email checker
├── results_analyzer.py      # Analysis tool
├── test_holehe.py          # Test suite
├── README.md               # This file
├── results/                # Single check results
└── bulk_results/           # Bulk check results
```

## Class Reference

### HoleheChecker

Main class for checking individual emails.

```python
checker = HoleheChecker(output_dir="results")

# Check email
result = checker.check_email(
    email="user@example.com",
    only_used=True,
    csv_output=True,
    timeout=60
)

# Save results
checker.save_results(result, format="json")

# Print summary
checker.print_summary(result)
```

### BulkHoleheChecker

Class for bulk email checking.

```python
bulk_checker = BulkHoleheChecker()

# Sequential check
results = bulk_checker.check_sequential(["email1@example.com", "email2@example.com"])

# Parallel check
results = bulk_checker.check_parallel(["email1@example.com", "email2@example.com"], max_workers=4)

# Save results
bulk_checker.save_bulk_results(format="json")

# Print summary
bulk_checker.print_bulk_summary()

# Export reports
bulk_checker.export_summary_report()
```

### ResultsAnalyzer

Analyze bulk results.

```python
analyzer = ResultsAnalyzer()
analyzer.load_results("bulk_results_20240101_120000.json")

# Get statistics
stats = analyzer.get_statistics()
analyzer.print_statistics()

# Export reports
analyzer.export_website_report()
analyzer.export_email_report()
analyzer.export_csv_summary()
```

## Examples

### Example 1: Check single email

```python
from run_holehe_check import HoleheChecker

checker = HoleheChecker()
results = checker.check_email("c.dmierc@gmail.com")
checker.print_summary(results)
checker.save_results(results, format="json")
```

### Example 2: Batch check with analysis

```python
from bulk_email_checker import BulkHoleheChecker
from results_analyzer import ResultsAnalyzer

# Check emails
bulk = BulkHoleheChecker()
results = bulk.check_sequential(["email1@example.com", "email2@example.com"])
bulk.save_bulk_results(format="json")

# Analyze results
analyzer = ResultsAnalyzer()
analyzer.load_results("bulk_results_latest.json")
analyzer.print_statistics()
analyzer.export_website_report()
```

### Example 3: Parallel processing

```python
from bulk_email_checker import BulkHoleheChecker

bulk = BulkHoleheChecker()
emails = [f"user{i}@example.com" for i in range(100)]

# Process 8 at a time
results = bulk.check_parallel(emails, max_workers=8)
bulk.print_bulk_summary()
bulk.save_bulk_results(format="json")
```

## Notes

- **Rate Limiting**: The tool includes polite delays to avoid rate limiting
- **Timeout**: Default timeout is 60 seconds per email
- **CSV Output**: Use `--csv` flag for cleaner parsing
- **Only Used**: Use `--only-used` to filter out "not found" results

## Troubleshooting

### holehe not found
```bash
pip install holehe
```

### Import errors
```bash
pip install -r requirements.txt
```

### Permission errors
```bash
chmod +x setup.sh
chmod +x run_holehe_check.py
```

### Tests failing
```bash
pytest test_holehe.py -v -s  # Verbose with output
```

## Legal Notice

This tool is for educational and authorized security testing purposes only. Ensure you have proper authorization before checking email addresses that don't belong to you.

## License

MIT
