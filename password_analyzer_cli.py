import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from password_analyzer import PasswordManagerAnalyzer
from config_manager import ConfigManager

class PasswordAnalyzerCLI:
    def __init__(self):
        self.console = Console()
        self.config = ConfigManager()
        self.analyzer = None

    def setup_cli(self):
        parser = argparse.ArgumentParser(description='Password Manager Export Analyzer CLI')
        parser.add_argument('file', help='Path to the password manager export file (CSV)')
        parser.add_argument('--interactive', '-i', action='store_true', 
                          help='Run in interactive mode')
        parser.add_argument('--domain', help='Filter by domain/website')
        parser.add_argument('--email', help='Search by email/username')
        parser.add_argument('--columns', nargs='+', help='Specific columns to display')
        parser.add_argument('--export', help='Export results to file')
        parser.add_argument('--format', choices=['csv', 'json', 'excel'], 
                          help='Export format (default: from config)')
        
        return parser.parse_args()

    def load_file(self, file_path):
        try:
            self.analyzer = PasswordManagerAnalyzer(file_path)
            if self.analyzer.data.empty:
                self.console.print("[red]No data found in the file[/red]")
                return False
            return True
        except Exception as e:
            self.console.print(f"[red]Error loading file: {str(e)}[/red]")
            return False
    
            

    def interactive_mode(self):
        """Run the analyzer in interactive mode."""
        # Load last used filters
        last_filters = self.config.get_last_filters()
        
        # Ask for filters
        domain = Prompt.ask("Enter domain to filter by", 
                          default=last_filters['domain'])
        email = Prompt.ask("Enter email to filter by", 
                          default=last_filters['email'])
        
        # Update config with new filters
        self.config.update_last_filters(domain, email)

        # Get available columns
        available_columns = self.analyzer.get_available_columns()
        last_selected = self.config.get_selected_columns()
        
        # Show available columns
        self.console.print("\nAvailable columns:")
        for i, col in enumerate(available_columns, 1):
            self.console.print(f"{i}. {col}")
        
        # Ask for columns
        selected_cols = []
        if last_selected:
            use_last = Confirm.ask(
                f"\nUse last selected columns? ({', '.join(last_selected)})",
                default=True
            )
            if use_last:
                selected_cols = last_selected
        
        if not selected_cols:
            self.console.print("\nEnter column numbers (comma-separated) or 'all':")
            selection = Prompt.ask("Selection")
            
            if selection.lower() == 'all':
                selected_cols = available_columns
            else:
                try:
                    indices = [int(i.strip()) - 1 for i in selection.split(',')]
                    selected_cols = [available_columns[i] for i in indices]
                except (ValueError, IndexError):
                    self.console.print("[red]Invalid selection, using all columns[/red]")
                    selected_cols = available_columns

        # Update config with selected columns
        self.config.update_selected_columns(selected_cols)

        # Ask about export
        if Confirm.ask("Export results to file?", default=False):
            export_path = Prompt.ask(
                "Enter export path",
                default=str(Path(self.config.get_last_export_path()) / "export.csv")
            )
            export_format = Prompt.ask(
                "Export format",
                choices=['csv', 'json', 'excel'],
                default=self.config.get_export_format()
            )
            self.config.update_export_format(export_format)
            self.config.update_last_export_path(str(Path(export_path).parent))
            return {
                'domain': domain,
                'email': email,
                'columns': selected_cols,
                'export': export_path,
                'format': export_format
            }

        return {
            'domain': domain,
            'email': email,
            'columns': selected_cols,
            'export': None,
            'format': None
        }

    def export_data(self, data, export_path, format_):
        """Export data to file."""
        try:
            path = Path(export_path)
            if format_ == 'csv':
                data.to_csv(path, index=False)
            elif format_ == 'json':
                data.to_json(path, orient='records', indent=2)
            elif format_ == 'excel':
                data.to_excel(path, index=False)
            self.console.print(f"[green]Data exported to {path}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error exporting data: {str(e)}[/red]")

    def display_results(self, data, columns=None):
        """Display results in a table."""
        if columns:
            display_data = data[columns]
        else:
            display_data = data

        table = Table(title="Password Manager Data Analysis")
        
        for col in display_data.columns:
            table.add_column(col.title(), style="cyan")

        for _, row in display_data.iterrows():
            table.add_row(*[str(val) for val in row])

        self.console.print(table)

    def run(self):
        args = self.setup_cli()
        
        if not self.load_file(args.file):
            return

        if args.interactive:
            options = self.interactive_mode()
        else:
            options = {
                'domain': args.domain,
                'email': args.email,
                'columns': args.columns,
                'export': args.export,
                'format': args.format or self.config.get_export_format()
            }

        # Apply filters
        filtered_data = self.analyzer.data.copy()
        
        if options['domain']:
            domain_filtered = self.analyzer.filter_by_domain(options['domain'])
            if not domain_filtered.empty:
                filtered_data = domain_filtered
            else:
                self.console.print(f"\n[yellow]No entries found for domain '{options['domain']}'[/yellow]")
                return

        if options['email']:
            email_filtered = self.analyzer.search_by_email(options['email'])
            if not email_filtered.empty:
                filtered_data = email_filtered
            else:
                self.console.print(f"\n[yellow]No entries found for email '{options['email']}'[/yellow]")
                return

        # Display results
        self.display_results(filtered_data, options['columns'])

        # Export if requested
        if options['export']:
            self.export_data(filtered_data, options['export'], options['format'])

def main():
    cli = PasswordAnalyzerCLI()
    cli.run()

if __name__ == "__main__":
    main() 