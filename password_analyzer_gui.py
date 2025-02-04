import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
from password_analyzer import PasswordManagerAnalyzer
import ttkthemes
from operator import itemgetter

class PasswordAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager Analyzer")
        self.root.geometry("1000x600")
        
        # Apply modern theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("arc")  # Modern looking theme
        
        self.analyzer = None
        self.sort_column = None
        self.sort_reverse = False
        self.setup_gui()

    def setup_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_path = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        file_entry.grid(row=0, column=0, padx=5)
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=1, padx=5)

        # Search filters
        filter_frame = ttk.LabelFrame(main_frame, text="Search Filters", padding="5")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(filter_frame, text="Domain:").grid(row=0, column=0, padx=5)
        self.domain_var = tk.StringVar()
        self.domain_entry = ttk.Entry(filter_frame, textvariable=self.domain_var)
        self.domain_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Email:").grid(row=0, column=2, padx=5)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(filter_frame, textvariable=self.email_var)
        self.email_entry.grid(row=0, column=3, padx=5)

        search_btn = ttk.Button(filter_frame, text="Search", command=self.search)
        search_btn.grid(row=0, column=4, padx=5)

        # Column selection
        columns_frame = ttk.LabelFrame(main_frame, text="Columns", padding="5")
        columns_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.columns_listbox = tk.Listbox(columns_frame, selectmode=tk.MULTIPLE, height=10)
        self.columns_listbox.pack(fill=tk.BOTH, expand=True)

        # Results section with export button
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Add export button above results
        export_btn = ttk.Button(results_frame, text="Export Results", command=self.export_results)
        export_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Create Treeview with sorting enabled
        self.tree = ttk.Treeview(results_frame, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(2, weight=1)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.load_file()

    def load_file(self):
        try:
            self.analyzer = PasswordManagerAnalyzer(self.file_path.get())
            self.update_columns_list()
            self.search()  # Initial display of data
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_columns_list(self):
        self.columns_listbox.delete(0, tk.END)
        for column in self.analyzer.get_available_columns():
            self.columns_listbox.insert(tk.END, column)

    def get_selected_columns(self):
        selected_indices = self.columns_listbox.curselection()
        if not selected_indices:
            return None
        return [self.columns_listbox.get(i) for i in selected_indices]

    def search(self):
        if not self.analyzer:
            messagebox.showwarning("Warning", "Please load a file first")
            return

        # Apply filters
        filtered_data = self.analyzer.data.copy()
        
        if self.domain_var.get():
            domain_filtered = self.analyzer.filter_by_domain(self.domain_var.get())
            if not domain_filtered.empty:
                filtered_data = domain_filtered

        if self.email_var.get():
            email_filtered = self.analyzer.search_by_email(self.email_var.get())
            if not email_filtered.empty:
                filtered_data = email_filtered

        # Update treeview
        self.update_treeview(filtered_data)

    def treeview_sort_column(self, col, reverse):
        """Sort treeview content when a column header is clicked."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        
        # Convert to appropriate type for sorting
        def convert_value(value):
            try:
                # Try to convert to float first (for numeric values)
                return float(value)
            except ValueError:
                # If not numeric, return as lowercase string for case-insensitive sorting
                return str(value).lower()
        
        items.sort(key=lambda x: convert_value(x[0]), reverse=reverse)
        
        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)

        # Reverse sort next time
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))
        
        # Update sort indicators in column headers
        for column in self.tree["columns"]:
            if column == col:
                # Show sort indicator (↑ or ↓)
                self.tree.heading(column, text=f"{column.title()} {'↓' if reverse else '↑'}")
            else:
                # Remove sort indicator from other columns
                self.tree.heading(column, text=column.title())

    def update_treeview(self, data):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get selected columns or use all columns
        selected_columns = self.get_selected_columns()
        if selected_columns:
            display_data = data[selected_columns]
        else:
            display_data = data

        # Configure columns
        self.tree["columns"] = list(display_data.columns)
        for col in display_data.columns:
            self.tree.heading(col, text=col.title(),
                            command=lambda c=col: self.treeview_sort_column(c, False))
            self.tree.column(col, width=100)  # Adjust width as needed

        # Add data
        for idx, row in display_data.iterrows():
            self.tree.insert("", tk.END, values=list(row))

        # If there was a previous sort column, apply the sort
        if self.sort_column and self.sort_column in display_data.columns:
            self.treeview_sort_column(self.sort_column, self.sort_reverse)

    def export_results(self):
        if not self.analyzer or not self.tree.get_children():
            messagebox.showwarning("Warning", "No data to export")
            return
            
        # Get the current filtered data
        filtered_data = self.get_current_filtered_data()
        
        # Ask for export location and format
        file_types = [
            ('CSV files', '*.csv'),
            ('Excel files', '*.xlsx'),
            ('JSON files', '*.json')
        ]
        export_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=file_types
        )
        
        if export_path:
            try:
                format_ = Path(export_path).suffix.lower()
                if format_ == '.csv':
                    filtered_data.to_csv(export_path, index=False)
                elif format_ == '.xlsx':
                    filtered_data.to_excel(export_path, index=False)
                elif format_ == '.json':
                    filtered_data.to_json(export_path, orient='records', indent=2)
                    
                messagebox.showinfo("Success", f"Data exported successfully to {export_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def get_current_filtered_data(self):
        # Get the currently displayed data
        data = []
        columns = self.tree["columns"]
        
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            data.append(dict(zip(columns, values)))
            
        return pd.DataFrame(data)

def main():
    root = tk.Tk()
    app = PasswordAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 