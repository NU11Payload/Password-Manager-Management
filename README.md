# Password Manager Export Analyzer

A Python tool to analyze and parse through exported password manager data. This tool helps you easily search and filter through your password manager exports to find specific entries by domain, email, or display specific fields.

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```
> [!TIP]
> If you're just wanting the program, go to releases.
## Usage for the CLI


>[!IMPORTANT]
> The rest of this documentation and repository is either for development or the use of the CLI
> 

The script accepts CSV files exported from password managers. Most password managers allow you to export your data in CSV format.

Basic usage:
```bash
python password_analyzer.py your_export_file.csv
```

### Available Options

- `--columns`: Specify which columns to display
- `--domain`: Filter entries by domain/website
- `--email`: Search for entries containing specific email

### Examples

1. Show all entries:
```bash
python password_analyzer.py export.csv
```

2. Show only specific columns:
```bash
python password_analyzer.py export.csv --columns username url email
```

1. Filter by domain:
```bash
python password_analyzer.py export.csv --domain "google.com"
```

2. Search by email:
```bash
python password_analyzer.py export.csv --email "user@example.com"
```

3. Combine filters and column selection:
```bash
python password_analyzer.py export.csv --domain "google.com" --columns username url
```

## Features

- Support for CSV password manager exports
- Filter entries by domain/website
- Search by email/username
- Select specific columns to display
- Beautiful terminal output with color formatting
- Case-insensitive search 