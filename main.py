import pandas as pd
import csv
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description
import matplotlib.pyplot as plt


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
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added successfully.")

    @classmethod
    def get_all_transactions(cls):
        df = pd.read_csv(cls.CSV_FILE)
        if df.empty:
            print("No transactions found.")
        return df

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        if df.empty:
            print("No transactions found in the CSV file.")
            return df

        df["date"] = pd.to_datetime(df["date"], format=cls.DATE_FORMAT)
        start_date_dt = datetime.strptime(start_date, cls.DATE_FORMAT)
        end_date_dt = datetime.strptime(end_date, cls.DATE_FORMAT)

        mask = (df["date"] >= start_date_dt) & (df["date"] <= end_date_dt)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transactions found in the given date range.")
        else:
            print(
                f"Transactions from {start_date_dt.strftime(cls.DATE_FORMAT)} to {end_date_dt.strftime(cls.DATE_FORMAT)}"
            )
            print(
                filtered_df.to_string(
                    index=True, 
                    formatters={"date": lambda x: x.strftime(cls.DATE_FORMAT)}
                )
            )

            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            print("\nSummary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Savings: ${(total_income - total_expense):.2f}")

        return filtered_df

    @classmethod
    def update_csv(cls, df):
        """Overwrite CSV file with DataFrame data."""
        df.to_csv(cls.CSV_FILE, index=False)
    
    @classmethod
    def edit_entry(cls, index, date, amount, category, description):
        df = pd.read_csv(cls.CSV_FILE)
        if index not in df.index:
            print("Invalid transaction index.")
            return
        df.at[index, "date"] = date
        df.at[index, "amount"] = amount
        df.at[index, "category"] = category
        df.at[index, "description"] = description
        cls.update_csv(df)
        print("Transaction updated successfully.")

    @classmethod
    def delete_entry(cls, index):
        df = pd.read_csv(cls.CSV_FILE)
        if index not in df.index:
            print("Invalid transaction index.")
            return
        df = df.drop(index)
        df.reset_index(drop=True, inplace=True)
        cls.update_csv(df)
        print("Transaction deleted successfully.")


def add():
    CSV.initialize_csv()
    date = get_date("Enter the date of the transaction (dd-mm-yyyy) or press enter for today's date: ", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def edit_transaction():
    CSV.initialize_csv()
    df = CSV.get_all_transactions()
    if df.empty:
        return

    print("Existing Transactions:")
    df.index = df.index  # Ensure index is shown
    print(df.to_string(index=True))
    try:
        index = int(input("Enter the index of the transaction to edit: "))
    except ValueError:
        print("Invalid input. Please enter a valid integer index.")
        return

    # Prompt user for new details (press enter to skip editing a field)
    current_row = df.loc[index]
    new_date = input(f"Enter new date (dd-mm-yyyy) [{current_row['date']}]: ") or current_row["date"]
    new_amount_input = input(f"Enter new amount [{current_row['amount']}]: ")
    new_amount = float(new_amount_input) if new_amount_input else current_row["amount"]
    new_category_input = input(f"Enter new category ('I' for Income or 'E' for Expense) [{current_row['category']}]: ")
    if new_category_input:
        new_category = {"I": "Income", "E": "Expense"}.get(new_category_input.upper(), current_row["category"])
    else:
        new_category = current_row["category"]
    new_description = input(f"Enter new description [{current_row['description']}]: ") or current_row["description"]

    CSV.edit_entry(index, new_date, new_amount, new_category, new_description)


def delete_transaction():
    CSV.initialize_csv()
    df = CSV.get_all_transactions()
    if df.empty:
        return

    print("Existing Transactions:")
    print(df.to_string(index=True))
    try:
        index = int(input("Enter the index of the transaction to delete: "))
    except ValueError:
        print("Invalid input. Please enter a valid integer index.")
        return

    confirm = input("Are you sure you want to delete this transaction? (y/n): ")
    if confirm.lower() == "y":
        CSV.delete_entry(index)
    else:
        print("Deletion cancelled.")


def plot_transactions(df):
    if df.empty:
        print("No data to plot.")
        return

    # Ensure date column is datetime and sorted
    df["date"] = pd.to_datetime(df["date"], format=CSV.DATE_FORMAT)
    df = df.sort_values("date")
    df.set_index("date", inplace=True)

    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    CSV.initialize_csv()
    while True:
        print("\n--- Personal Finance Tracker ---")
        print("1. Add a new transaction")
        print("2. View transactions and summary within a date range")
        print("3. Edit an existing transaction")
        print("4. Delete a transaction")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            add()
        elif choice == "2":
            start_date = get_date("Enter the start date (dd-mm-yyyy): ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
            if not df.empty and input("Do you want to see a plot? (y/n): ").lower() == "y":
                plot_transactions(df)
        elif choice == "3":
            edit_transaction()
        elif choice == "4":
            delete_transaction()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
