import streamlit as st
from utils import fetch_data


# Main function to run the Streamlit application
def main():
    # Set up the webpage title and favicon
    st.set_page_config(page_title='Financial Statements Tool', page_icon=':bar_chart:')

    # Display the main title of the page
    st.title('Financial Data Tool')

    # Get the stock ticker input from the user
    ticker = st.text_input('Please input a stock ticker: ').upper().strip()

    # Initialize session state variable for button click tracking
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = None

    # Initialize session state variables for storing fetched financial data
    if 'income_statement_df' not in st.session_state:
        st.session_state.income_statement_df = None
    if 'balance_sheet_df' not in st.session_state:
        st.session_state.balance_sheet_df = None
    if 'cash_flow_df' not in st.session_state:
        st.session_state.cash_flow_df = None

    # Fetch financial data when "Fetch Financial Statements" button is clicked
    if st.button("Fetch Financial Statements"):
        try:
            # Fetch the financial statements data and store it in session state
            st.session_state.income_statement_df, st.session_state.balance_sheet_df, st.session_state.cash_flow_df = fetch_data.fetch_financial_statements(ticker)
        except Exception as e:
            # Display an error message if fetching data fails
            st.error(f'An error has occurred: {e}')

    # Create a dropdown menu for users to select which financial statement to view
    statement_tab_selection = st.selectbox("Choose a Financial Statement",
                                           ["Income Statement", "Balance Sheet", "Cash Flow"])

    # Display the selected financial statement if data is available
    if st.session_state.income_statement_df is not None:
        if statement_tab_selection == "Income Statement":
            st.subheader('Income Statement')
            st.dataframe(st.session_state.income_statement_df)
        elif statement_tab_selection == "Balance Sheet":
            st.subheader('Balance Sheet')
            st.dataframe(st.session_state.balance_sheet_df)
        elif statement_tab_selection == "Cash Flow":
            st.subheader('Cash Flow Statement')
            st.dataframe(st.session_state.cash_flow_df)


if __name__ == "__main__":
    main()
