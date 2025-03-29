import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Import CSV and data_entry functions from your modules.
# For example, if they are in main.py and data_entry.py:
# from main import CSV
# from data_entry import get_date, get_amount, get_category, get_description

# For this example, we'll assume CSV is available as defined earlier.
# (Make sure the CSV class and DATE_FORMAT variable are accessible.)

# If not already done, initialize CSV
# (Make sure finance_data.csv exists or is created as needed.)
try:
    from main import CSV
except ImportError:
    # Minimal CSV class for demo purposes if import fails.
    class CSV:
        CSV_FILE = "finance_data.csv"
        COLUMNS = ["date", "amount", "category", "description"]
        DATE_FORMAT = "%d-%m-%Y"
    
        @classmethod
        def initialize_csv(cls):
            try:
                pd.read_csv(cls.CSV_FILE)
            except FileNotFoundError:
                df = pd.DataFrame(columns=cls.COLUMNS)
                df.to_csv(cls.CSV_FILE, index=False)
    
        @classmethod
        def add_entry(cls, date, amount, category, description):
            new_entry = {"date": date, "amount": amount, "category": category, "description": description}
            df = pd.read_csv(cls.CSV_FILE)
            df = df.append(new_entry, ignore_index=True)
            df.to_csv(cls.CSV_FILE, index=False)
    
        @classmethod
        def get_all_transactions(cls):
            return pd.read_csv(cls.CSV_FILE)
    
        @classmethod
        def update_csv(cls, df):
            df.to_csv(cls.CSV_FILE, index=False)
    
        @classmethod
        def edit_entry(cls, index, date, amount, category, description):
            df = pd.read_csv(cls.CSV_FILE)
            if index < 0 or index >= len(df):
                print("Invalid index")
                return
            df.at[index, "date"] = date
            df.at[index, "amount"] = amount
            df.at[index, "category"] = category
            df.at[index, "description"] = description
            cls.update_csv(df)
    
        @classmethod
        def delete_entry(cls, index):
            df = pd.read_csv(cls.CSV_FILE)
            if index < 0 or index >= len(df):
                print("Invalid index")
                return
            df = df.drop(index).reset_index(drop=True)
            cls.update_csv(df)
            
CSV.initialize_csv()


# -------------------
# GUI Application
# -------------------
class FinanceTrackerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracker")
        self.geometry("900x600")
        
        # Create a Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create frames for different tabs
        self.tab_add = ttk.Frame(self.notebook)
        self.tab_view = ttk.Frame(self.notebook)
        self.tab_edit = ttk.Frame(self.notebook)
        self.tab_delete = ttk.Frame(self.notebook)
        self.tab_plot = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_add, text="Add Transaction")
        self.notebook.add(self.tab_view, text="View Transactions")
        self.notebook.add(self.tab_edit, text="Edit Transaction")
        self.notebook.add(self.tab_delete, text="Delete Transaction")
        self.notebook.add(self.tab_plot, text="Plot Transactions")
        
        self.create_add_tab()
        self.create_view_tab()
        self.create_edit_tab()
        self.create_delete_tab()
        self.create_plot_tab()

    # ---------- ADD TAB ----------
    def create_add_tab(self):
        frm = self.tab_add
        
        tk.Label(frm, text="Date (dd-mm-yyyy):").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.entry_date = tk.Entry(frm)
        self.entry_date.grid(row=0, column=1, padx=10, pady=10)
        self.entry_date.insert(0, datetime.today().strftime(CSV.DATE_FORMAT))
        
        tk.Label(frm, text="Amount:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.entry_amount = tk.Entry(frm)
        self.entry_amount.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(frm, text="Category:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.combo_category = ttk.Combobox(frm, values=["Income", "Expense"], state="readonly")
        self.combo_category.grid(row=2, column=1, padx=10, pady=10)
        self.combo_category.current(0)
        
        tk.Label(frm, text="Description:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.entry_description = tk.Entry(frm)
        self.entry_description.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Button(frm, text="Add Transaction", command=self.add_transaction).grid(row=4, column=0, columnspan=2, pady=20)
    
    def add_transaction(self):
        date = self.entry_date.get().strip()
        amount_str = self.entry_amount.get().strip()
        category = self.combo_category.get().strip()
        description = self.entry_description.get().strip()
        
        # Validate date
        try:
            datetime.strptime(date, CSV.DATE_FORMAT)
        except ValueError:
            messagebox.showerror("Invalid Date", f"Enter date in format: {CSV.DATE_FORMAT}")
            return
        
        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Enter a valid positive amount.")
            return
        
        CSV.add_entry(date, amount, category, description)
        messagebox.showinfo("Success", "Transaction added successfully!")
        self.entry_amount.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.refresh_all_tables()

    # ---------- VIEW TAB ----------
    def create_view_tab(self):
        frm = self.tab_view
        
        # Date filters
        filter_frame = ttk.Frame(frm)
        filter_frame.pack(pady=10)
        
        tk.Label(filter_frame, text="Start Date (dd-mm-yyyy):").grid(row=0, column=0, padx=5)
        self.view_start_date = tk.Entry(filter_frame, width=12)
        self.view_start_date.grid(row=0, column=1, padx=5)
        self.view_start_date.insert(0, datetime.today().strftime(CSV.DATE_FORMAT))
        
        tk.Label(filter_frame, text="End Date (dd-mm-yyyy):").grid(row=0, column=2, padx=5)
        self.view_end_date = tk.Entry(filter_frame, width=12)
        self.view_end_date.grid(row=0, column=3, padx=5)
        self.view_end_date.insert(0, datetime.today().strftime(CSV.DATE_FORMAT))
        
        tk.Button(filter_frame, text="Filter", command=self.filter_transactions).grid(row=0, column=4, padx=5)
        
        # Treeview for transactions
        self.tree_view = ttk.Treeview(frm, columns=("Index", "Date", "Amount", "Category", "Description"), show="headings")
        self.tree_view.heading("Index", text="Index")
        self.tree_view.heading("Date", text="Date")
        self.tree_view.heading("Amount", text="Amount")
        self.tree_view.heading("Category", text="Category")
        self.tree_view.heading("Description", text="Description")
        self.tree_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.refresh_view_table()
    
    def refresh_view_table(self):
        for row in self.tree_view.get_children():
            self.tree_view.delete(row)
        
        df = CSV.get_all_transactions()
        if df is None or df.empty:
            return
        for idx, row in df.iterrows():
            self.tree_view.insert("", tk.END, values=(idx, row["date"], row["amount"], row["category"], row["description"]))
    
    def filter_transactions(self):
        start_date = self.view_start_date.get().strip()
        end_date = self.view_end_date.get().strip()
        try:
            start_dt = datetime.strptime(start_date, CSV.DATE_FORMAT)
            end_dt = datetime.strptime(end_date, CSV.DATE_FORMAT)
        except ValueError:
            messagebox.showerror("Invalid Date", f"Please enter dates in {CSV.DATE_FORMAT} format.")
            return
        
        # Read and filter data
        df = CSV.get_all_transactions()
        if df.empty:
            messagebox.showinfo("No Data", "No transactions available.")
            return
        df["date"] = pd.to_datetime(df["date"], format=CSV.DATE_FORMAT)
        mask = (df["date"] >= start_dt) & (df["date"] <= end_dt)
        filtered = df.loc[mask]
        
        for row in self.tree_view.get_children():
            self.tree_view.delete(row)
        for idx, row in filtered.iterrows():
            self.tree_view.insert("", tk.END, values=(idx, row["date"].strftime(CSV.DATE_FORMAT), row["amount"], row["category"], row["description"]))
    
    # ---------- EDIT TAB ----------
    def create_edit_tab(self):
        frm = self.tab_edit
        
        # Show table of transactions with indices
        self.tree_edit = ttk.Treeview(frm, columns=("Index", "Date", "Amount", "Category", "Description"), show="headings", height=10)
        self.tree_edit.heading("Index", text="Index")
        self.tree_edit.heading("Date", text="Date")
        self.tree_edit.heading("Amount", text="Amount")
        self.tree_edit.heading("Category", text="Category")
        self.tree_edit.heading("Description", text="Description")
        self.tree_edit.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Load Transactions", command=self.refresh_edit_table).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_selected).grid(row=0, column=1, padx=5)
    
    def refresh_edit_table(self):
        for row in self.tree_edit.get_children():
            self.tree_edit.delete(row)
        
        df = CSV.get_all_transactions()
        if df.empty:
            return
        for idx, row in df.iterrows():
            self.tree_edit.insert("", tk.END, values=(idx, row["date"], row["amount"], row["category"], row["description"]))
    
    def edit_selected(self):
        selected = self.tree_edit.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a transaction to edit.")
            return
        values = self.tree_edit.item(selected, "values")
        index = int(values[0])
        # Open a new window for editing
        EditWindow(self, index)
    
    # ---------- DELETE TAB ----------
    def create_delete_tab(self):
        frm = self.tab_delete
        
        self.tree_delete = ttk.Treeview(frm, columns=("Index", "Date", "Amount", "Category", "Description"), show="headings", height=10)
        self.tree_delete.heading("Index", text="Index")
        self.tree_delete.heading("Date", text="Date")
        self.tree_delete.heading("Amount", text="Amount")
        self.tree_delete.heading("Category", text="Category")
        self.tree_delete.heading("Description", text="Description")
        self.tree_delete.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Load Transactions", command=self.refresh_delete_table).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).grid(row=0, column=1, padx=5)
    
    def refresh_delete_table(self):
        for row in self.tree_delete.get_children():
            self.tree_delete.delete(row)
        
        df = CSV.get_all_transactions()
        if df.empty:
            return
        for idx, row in df.iterrows():
            self.tree_delete.insert("", tk.END, values=(idx, row["date"], row["amount"], row["category"], row["description"]))
    
    def delete_selected(self):
        selected = self.tree_delete.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select a transaction to delete.")
            return
        values = self.tree_delete.item(selected, "values")
        index = int(values[0])
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected transaction?")
        if confirm:
            CSV.delete_entry(index)
            messagebox.showinfo("Deleted", "Transaction deleted successfully.")
            self.refresh_delete_table()
            self.refresh_view_table()
            self.refresh_edit_table()
    
    # ---------- PLOT TAB ----------
    def create_plot_tab(self):
        frm = self.tab_plot
        
        # Date filter for plotting
        filter_frame = ttk.Frame(frm)
        filter_frame.pack(pady=10)
        
        tk.Label(filter_frame, text="Start Date (dd-mm-yyyy):").grid(row=0, column=0, padx=5)
        self.plot_start_date = tk.Entry(filter_frame, width=12)
        self.plot_start_date.grid(row=0, column=1, padx=5)
        self.plot_start_date.insert(0, datetime.today().strftime(CSV.DATE_FORMAT))
        
        tk.Label(filter_frame, text="End Date (dd-mm-yyyy):").grid(row=0, column=2, padx=5)
        self.plot_end_date = tk.Entry(filter_frame, width=12)
        self.plot_end_date.grid(row=0, column=3, padx=5)
        self.plot_end_date.insert(0, datetime.today().strftime(CSV.DATE_FORMAT))
        
        tk.Button(filter_frame, text="Plot Transactions", command=self.plot_transactions).grid(row=0, column=4, padx=5)
    
    def plot_transactions(self):
        start_date = self.plot_start_date.get().strip()
        end_date = self.plot_end_date.get().strip()
        try:
            start_dt = datetime.strptime(start_date, CSV.DATE_FORMAT)
            end_dt = datetime.strptime(end_date, CSV.DATE_FORMAT)
        except ValueError:
            messagebox.showerror("Invalid Date", f"Enter dates in {CSV.DATE_FORMAT} format.")
            return
        
        df = CSV.get_all_transactions()
        if df.empty:
            messagebox.showinfo("No Data", "No transactions available.")
            return
        
        df["date"] = pd.to_datetime(df["date"], format=CSV.DATE_FORMAT)
        df = df.sort_values("date")
        mask = (df["date"] >= start_dt) & (df["date"] <= end_dt)
        filtered = df.loc[mask]
        if filtered.empty:
            messagebox.showinfo("No Data", "No transactions in the selected range.")
            return
        
        # Resample and plot data
        filtered.set_index("date", inplace=True)
        income_df = filtered[filtered["category"] == "Income"].resample("D").sum().reindex(filtered.index, fill_value=0)
        expense_df = filtered[filtered["category"] == "Expense"].resample("D").sum().reindex(filtered.index, fill_value=0)
        
        plt.figure(figsize=(10, 5))
        plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
        plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.title("Income and Expenses Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

    def refresh_all_tables(self):
        self.refresh_view_table()
        self.refresh_edit_table()
        self.refresh_delete_table()


# ---------- EDIT WINDOW ----------
class EditWindow(tk.Toplevel):
    def __init__(self, parent, index):
        super().__init__(parent)
        self.index = index
        self.title("Edit Transaction")
        
        df = CSV.get_all_transactions()
        try:
            record = df.loc[index]
        except KeyError:
            messagebox.showerror("Error", "Transaction not found.")
            self.destroy()
            return
        
        tk.Label(self, text="Date (dd-mm-yyyy):").grid(row=0, column=0, padx=10, pady=10)
        self.entry_date = tk.Entry(self)
        self.entry_date.grid(row=0, column=1, padx=10, pady=10)
        self.entry_date.insert(0, record["date"])
        
        tk.Label(self, text="Amount:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_amount = tk.Entry(self)
        self.entry_amount.grid(row=1, column=1, padx=10, pady=10)
        self.entry_amount.insert(0, record["amount"])
        
        tk.Label(self, text="Category:").grid(row=2, column=0, padx=10, pady=10)
        self.combo_category = ttk.Combobox(self, values=["Income", "Expense"], state="readonly")
        self.combo_category.grid(row=2, column=1, padx=10, pady=10)
        self.combo_category.set(record["category"])
        
        tk.Label(self, text="Description:").grid(row=3, column=0, padx=10, pady=10)
        self.entry_description = tk.Entry(self)
        self.entry_description.grid(row=3, column=1, padx=10, pady=10)
        self.entry_description.insert(0, record["description"])
        
        tk.Button(self, text="Save Changes", command=self.save_changes).grid(row=4, column=0, columnspan=2, pady=20)
    
    def save_changes(self):
        new_date = self.entry_date.get().strip()
        new_amount_str = self.entry_amount.get().strip()
        new_category = self.combo_category.get().strip()
        new_description = self.entry_description.get().strip()
        
        try:
            datetime.strptime(new_date, CSV.DATE_FORMAT)
        except ValueError:
            messagebox.showerror("Invalid Date", f"Enter date in format: {CSV.DATE_FORMAT}")
            return
        
        try:
            new_amount = float(new_amount_str)
            if new_amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Amount", "Enter a valid positive amount.")
            return
        
        CSV.edit_entry(self.index, new_date, new_amount, new_category, new_description)
        messagebox.showinfo("Success", "Transaction updated successfully.")
        self.destroy()


if __name__ == "__main__":
    app = FinanceTrackerGUI()
    app.mainloop()

