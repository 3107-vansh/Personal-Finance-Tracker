from datetime import datetime

# Date format for all date inputs
DATE_FORMAT = "%d-%m-%Y"
CATEGORIES = {"I": "Income", "E": "Expense"}


def get_date(prompt, allow_default=False):
    """
    Prompt user for a date. If allow_default is True and input is empty,
    returns today's date.
    """
    date_str = input(prompt)
    if allow_default and not date_str:
        return datetime.today().strftime(DATE_FORMAT)

    try:
        valid_date = datetime.strptime(date_str, DATE_FORMAT)
        return valid_date.strftime(DATE_FORMAT)
    except ValueError:
        print("Invalid date format. Please enter the date in dd-mm-yyyy format.")
        return get_date(prompt, allow_default)


def get_amount():
    """
    Prompt user to enter an amount. The amount must be a positive number.
    """
    try:
        amount = float(input("Enter the amount: "))
        if amount <= 0:
            raise ValueError("Amount must be a positive, non-zero value.")
        return amount
    except ValueError as e:
        print(e)
        return get_amount()


def get_category():
    """
    Prompt user to enter a category. 'I' represents Income, 'E' represents Expense.
    """
    category = input("Enter the category ('I' for Income or 'E' for Expense): ").strip().upper()
    if category in CATEGORIES:
        return CATEGORIES[category]
    print("Invalid category. Please enter 'I' for Income or 'E' for Expense.")
    return get_category()


def get_description():
    """
    Prompt user to enter a description for the transaction.
    """
    return input("Enter a description (optional): ")
