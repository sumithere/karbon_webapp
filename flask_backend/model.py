import json
import datetime

class FLAGS:
    GREEN = 1
    AMBER = 2
    RED = 0
    MEDIUM_RISK = 3  # display purpose only
    WHITE = 4  # data is missing for this field

def latest_financial_index(data: dict):
    """
    Determine the index of the latest standalone financial entry in the data.
    """
    for index, financial in enumerate(data.get("financials")):
        if financial.get("nature") == "STANDALONE":
            return index
    return 0

def total_revenue(data, financial_index: int):
    """
    Calculate the total revenue from the financial data at the given index.
    """
    try:
        financial = data["financials"][financial_index]
        # print(financial)
        pnl_items = financial["pnl"]["lineItems"]
        net_revenue = pnl_items["net_revenue"] 
        return net_revenue
    except KeyError:
        return 0

def total_borrowing(data: dict, financial_index: int):
    """
    Calculate total borrowings (long-term + short-term) for the financial data at the given index.
    """
    try:
        financial = data["financials"][financial_index]
        balance_sheet = financial["bs"]["assets"]
        long_term_borrowing = balance_sheet["long_term_loans_and_advances"]
        short_term_borrowing = balance_sheet["short_term_loans_and_advances"]
        return (long_term_borrowing + short_term_borrowing)/total_revenue(dict,financial_index)
    except KeyError:
        return 0

def iscr(data: dict, financial_index: int):
    """
    Calculate the Interest Service Coverage Ratio (ISCR).
    """
    try:
        financial = data["financials"][financial_index]
        pnl_items = financial["pnl"]["lineItems"]
        
        # Calculate ISCR as (Profit Before Interest and Tax + Depreciation) / Interest Expenses
        profit_before_tax = pnl_items["profit_before_tax"]
        depreciation = pnl_items["depreciation"]
        profit_before_interest_and_tax = pnl_items["profit_before_interest_and_tax"]
        iscr_value = (profit_before_interest_and_tax + depreciation + 1) / (profit_before_interest_and_tax - profit_before_tax + 1)
        return iscr_value
    except KeyError:
        return 0

def iscr_flag(data: dict, financial_index: int):
    """
    Determine the flag based on the ISCR value.
    """
    iscr_value = iscr(data, financial_index)
    if iscr_value >= 2:
        return FLAGS.GREEN
    else:
        return FLAGS.RED

def total_revenue_5cr_flag(data: dict, financial_index: int):
    """
    Determine the flag based on total revenue exceeding 50 million.
    """
    revenue = total_revenue(data, financial_index)
    if revenue >= 50_000_000:
        return FLAGS.GREEN
    else:
        return FLAGS.RED

def borrowing_to_revenue_flag(data: dict, financial_index: int):
    """
    Determine the flag based on the ratio of total borrowings to total revenue.
    """
    borrowings = total_borrowing(data, financial_index)
    revenue = total_revenue(data, financial_index)

    if revenue == 0:  # Prevent division by zero
        return FLAGS.RED

    ratio = borrowings / revenue
    if ratio <= 0.25:
        return FLAGS.GREEN
    else:
        return FLAGS.AMBER

def probe_model_5l_profit(data: dict):
    """
    Evaluate various financial flags for the model.
    """
    lastest_financial_index_value = latest_financial_index(data)

    total_revenue_5cr_flag_value = total_revenue_5cr_flag(data, lastest_financial_index_value)
    borrowing_to_revenue_flag_value = borrowing_to_revenue_flag(data, lastest_financial_index_value)
    iscr_flag_value = iscr_flag(data, lastest_financial_index_value)

    return {
        "flags": {
            "TOTAL_REVENUE_5CR_FLAG": total_revenue_5cr_flag_value,
            "BORROWING_TO_REVENUE_FLAG": borrowing_to_revenue_flag_value,
            "ISCR_FLAG": iscr_flag_value,
        }
    }

if __name__ == "__main__":
    with open("data.json", "r") as file:
        content = file.read()
        data = json.loads(content)
        print(probe_model_5l_profit(data["data"]))
