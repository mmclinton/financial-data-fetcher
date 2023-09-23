import requests
import pandas as pd
import streamlit as st
import re

# API endpoint and key constants
API_ENDPOINT = 'https://financialmodelingprep.com/api/v3/'
API_KEY = 'ac76b26ade0e3d4febd0d77b1b84ef0e'


def clean_camel_case_columns(camel_case_string):
    """Clean camel-case strings by adding spaces and capitalizing words."""
    # Add a space before every capital letter that isn't at the start of the string
    spaced_string = re.sub(r'(?<=[a-z])([A-Z])', r' \1', camel_case_string)

    # Capitalize the first letter of the string
    return spaced_string.title()


def create_url_from_input(ticker):
    # TODO: make a definition
    # Construct the URL using the API endpoint and key
    income_statement_url = f'{API_ENDPOINT}income-statement/{ticker}?apikey={API_KEY}'
    balance_sheet_url = f'{API_ENDPOINT}balance-sheet-statement/{ticker}?apikey={API_KEY}'
    cash_flow_url = f'{API_ENDPOINT}cash-flow-statement/{ticker}?apikey={API_KEY}'

    return income_statement_url, balance_sheet_url, cash_flow_url


def call_api_get_json(income_statement_url, balance_sheet_url, cash_flow_url):
    # TODO: make a definition
    # Calls api using the URL and gets the json for each statement
    income_statement = requests.get(income_statement_url).json()
    balance_sheet = requests.get(balance_sheet_url).json()
    cash_flow = requests.get(cash_flow_url).json()

    return income_statement, balance_sheet, cash_flow


def create_dataframe(income_statement, balance_sheet, cash_flow):
    # TODO: make a definition
    # Creating a pandas dataframe for each financial statement
    income_statement_df = pd.DataFrame(income_statement)
    balance_sheet_df = pd.DataFrame(balance_sheet)
    cash_flow_df = pd.DataFrame(cash_flow)

    return income_statement_df, balance_sheet_df, cash_flow_df


def transpose_financial_statements(income_statement_df, balance_sheet_df, cash_flow_df):
    """Transpose each financial statement dataframe."""
    income_statement_df = income_statement_df.transpose()
    balance_sheet_df = balance_sheet_df.transpose()
    cash_flow_df = cash_flow_df.transpose()

    return income_statement_df, balance_sheet_df, cash_flow_df


def set_headers_and_drop_columns(income_statement_df, balance_sheet_df, cash_flow_df):
    """This function sets the financial statement's headers to the SEC filing date and drops indices that are not a
    part of traditional financial statements."""
    # Making the dataframe's header the 'date' row - this is the SEC 10k filing date
    income_statement_df.columns = income_statement_df.loc['date']
    balance_sheet_df.columns = balance_sheet_df.loc['date']
    cash_flow_df.columns = cash_flow_df.loc["date"]

    # Dropping the dataframe's unnecessary rows
    index_to_drop = ['date', 'symbol', 'reportedCurrency', 'cik', 'fillingDate', 'acceptedDate', 'calendarYear',
                     'period', 'link', 'finalLink']
    income_statement_df.drop(index_to_drop, inplace=True, errors="ignore")
    balance_sheet_df.drop(index_to_drop, inplace=True, errors="ignore")
    cash_flow_df.drop(index_to_drop, inplace=True, errors="ignore")

    return income_statement_df, balance_sheet_df, cash_flow_df


def clean_statement_indices(income_statement_df, balance_sheet_df, cash_flow_df):
    """This function cleans the camel-case index names by calling the camel_case_columns function."""
    # Add a space before every capital letter that isn't at the start of the string
    income_statement_df.index = income_statement_df.index.map(clean_camel_case_columns)
    balance_sheet_df.index = balance_sheet_df.index.map(clean_camel_case_columns)
    cash_flow_df.index = cash_flow_df.index.map(clean_camel_case_columns)

    return income_statement_df, balance_sheet_df, cash_flow_df


def manual_rename_indices(income_statement_df, balance_sheet_df, cash_flow_df):
    """Manually rename certain dataframe indices for clarity."""
    # Renaming specific indices for each dataframe
    income_statement_df.rename(
        index={'Ebitda': 'EBITDA', 'Eps': 'EPS', 'Ebitdaratio': 'EBITDA Ratio', 'Epsdiluted': 'EPS Diluted',
               'Selling General And Administrative Expenses': 'SG&A Expenses'}, inplace=True)
    balance_sheet_df.rename(index={'Accumulated Other Comprehensive Income Loss': 'Accumulated Other Income'},
                            inplace=True)
    cash_flow_df.rename(index={'Net Cash Used Provided By Financing Activities': 'Net Cash By Financing Activities',
                               'Net Cash Provided By Operating Activities': 'Net Cash by Operating Activities',
                               'Investments In Property Plant And Equipment': 'Investments in PP&E',
                               'Net Cash Used For Investing Activites': 'Net Cash For Investing Activities'},
                        inplace=True)

    return income_statement_df, balance_sheet_df, cash_flow_df


@st.cache_data
def fetch_financial_statements(ticker):
    """This function fetches financial statements from the API endpoint, creates a dataframe for each, and calls all
    data cleaning functions. This is the only function in 'fetch_data.py' called by the main function in 'app.py'."""
    try:
        # FUNCTION: create_url_from_input
        income_statement_url, balance_sheet_url, cash_flow_url = create_url_from_input(ticker)

        # FUNCTION: call_api_get_json
        income_statement, balance_sheet, cash_flow = call_api_get_json(income_statement_url,
                                                                       balance_sheet_url,
                                                                       cash_flow_url)

        # FUNCTION: create_dataframe
        income_statement_df, balance_sheet_df, cash_flow_df = create_dataframe(income_statement,
                                                                               balance_sheet,
                                                                               cash_flow)

        # FUNCTION: transpose_financial_statements
        income_statement_df, balance_sheet_df, cash_flow_df = transpose_financial_statements(income_statement_df,
                                                                                             balance_sheet_df,
                                                                                             cash_flow_df)

        # FUNCTION: set_headers_and_drop_columns
        income_statement_df, balance_sheet_df, cash_flow_df = set_headers_and_drop_columns(income_statement_df,
                                                                                           balance_sheet_df,
                                                                                           cash_flow_df)

        # FUNCTION: clean_statement_indices
        income_statement_df, balance_sheet_df, cash_flow_df = clean_statement_indices(income_statement_df,
                                                                                      balance_sheet_df,
                                                                                      cash_flow_df)
        # FUNCTION: manual_rename_indices
        income_statement_df, balance_sheet_df, cash_flow_df = manual_rename_indices(income_statement_df,
                                                                                    balance_sheet_df,
                                                                                    cash_flow_df)

    except Exception as e:
        print(f'Error fetching financial statements: {e}')
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    return income_statement_df, balance_sheet_df, cash_flow_df
