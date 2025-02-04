import pandas as pd
import argparse
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path

class PasswordManagerAnalyzer:
    def __init__(self, file_path):
        self.console = Console()
        self.load_data(file_path)

    def load_data(self, file_path):
        """Load the password manager export file."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.csv':
            self.data = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Please use CSV files.")
        
        # Standardize column names to lowercase
        self.data.columns = self.data.columns.str.lower()

    def get_available_columns(self):
        """Return list of available columns in the dataset."""
        return list(self.data.columns)

    def analyze_data(self, columns=None):
        """Display analysis of the password data."""
        if columns:
            display_data = self.data[columns]
        else:
            display_data = self.data

        table = Table(title="Password Manager Data Analysis")
        
        # Add columns to the table
        for col in display_data.columns:
            table.add_column(col.title(), style="cyan")

        # Add rows to the table
        for _, row in display_data.iterrows():
            table.add_row(*[str(val) for val in row])

        self.console.print(table)

    def filter_by_domain(self, domain):
        """Filter entries by domain/website."""
        domain_cols = [col for col in self.data.columns if 'url' in col.lower() or 'website' in col.lower()]
        if domain_cols:
            filtered = self.data[self.data[domain_cols[0]].str.contains(domain, case=False, na=False)]
            return filtered
        return pd.DataFrame()

    def search_by_email(self, email):
        """Search for entries containing specific email."""
        email_cols = [col for col in self.data.columns if 'email' in col.lower() or 'username' in col.lower()]
        if email_cols:
            filtered = self.data[self.data[email_cols[0]].str.contains(email, case=False, na=False)]
            return filtered
        return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Password Manager Export Analyzer')
    parser.add_argument('file', help='Path to the password manager export file (CSV)')
    parser.add_argument('--columns', nargs='+', help='Specific columns to display')
    parser.add_argument('--domain', help='Filter by domain/website')
    parser.add_argument('--email', help='Search by email/username')
    
    args = parser.parse_args()

    try:
        analyzer = PasswordManagerAnalyzer(args.file)
        
        if args.domain:
            filtered_data = analyzer.filter_by_domain(args.domain)
            if not filtered_data.empty:
                rprint(f"\n[green]Entries matching domain '{args.domain}':[/green]")
                analyzer.data = filtered_data
            else:
                rprint(f"\n[yellow]No entries found for domain '{args.domain}'[/yellow]")
                return

        if args.email:
            filtered_data = analyzer.search_by_email(args.email)
            if not filtered_data.empty:
                rprint(f"\n[green]Entries matching email '{args.email}':[/green]")
                analyzer.data = filtered_data
            else:
                rprint(f"\n[yellow]No entries found for email '{args.email}'[/yellow]")
                return

        if args.columns:
            available_cols = analyzer.get_available_columns()
            valid_cols = [col for col in args.columns if col.lower() in [c.lower() for c in available_cols]]
            if not valid_cols:
                rprint(f"\n[red]No valid columns specified. Available columns: {', '.join(available_cols)}[/red]")
                return
            analyzer.analyze_data(valid_cols)
        else:
            analyzer.analyze_data()

    except Exception as e:
        rprint(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    main() 