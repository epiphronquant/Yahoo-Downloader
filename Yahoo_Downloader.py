# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 14:58:22 2021

@author: angus
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import base64
from io import BytesIO

st.set_page_config(layout="wide")
st.title('Yahoo Downloader')
column_1, column_2 = st.columns(2) ### Divides page into 2 columns

with column_1:### ### Download Statements chart
    st.header ('Download Statements')
    ### boxes for input
    tickers = st.text_input("Type in a Yahoo Finance Ticker/Tickers in the format 1234.HK, 123456.SZ, 123456.SS, ABCD for HKEX, SZSE, SHSE and US Stocks respectively")
    tickers = tickers.split(',')
    tickers = map(str.strip, tickers)
    tickers = list(tickers)
    
    statement = st.selectbox(
          'What would you like to download?',
          ('Income Statement','Balance Sheet', 'Cash Flow'))
    st.write('You selected:', statement)
    
    frequency = st.selectbox(
          'What would you like to download?',
          ('Annual','Quarterly'))
    st.write('You selected:', frequency)
    
    @st.cache### function with cache to download data
    def statements_chart(tickers, statement, frequency):      
        output = pd.DataFrame()### initialize a dataframe
        for ticker in tickers: ### loop to download and clean statements
            ticker_name = ticker
            ticker = yf.Ticker(ticker)
            if frequency == 'Annual':
                if statement == 'Balance Sheet':
                    a = ticker.balance_sheet
                elif statement == 'Income Statement':
                    a = ticker.financials
                else:
                    a = ticker.cashflow
            else:
                if statement == 'Balance Sheet':
                    a = ticker.quarterly_balance_sheet
                elif statement == 'Income Statement':
                    a = ticker.quarterly_financials
                else:
                    a = ticker.quarterly_cashflow
            ### clean statements
            if statement == 'Balance Sheet':
                filters = ["Total Assets", "Total Liab", "Total Stockholder Equity", "Minority Interest", "Cash", "Short Term Investments", "Inventory", "Property Plant Equipment", "Net Receivables", "Total Current Assets", "Intangible Assets", "Other Current Assets", "Other Assets", "Good Will", "Long Term Investments", "Deferred Long Term Asset Charges", "Net Tangible Assets", "Accounts Payable", "Short Long Term Debt", "Other Current Liab", "Total Current Liabilities", "Deferred Long Term Liab", "Long Term Debt", "Other Liab", "Common Stock", "Capital Surplus", "Treasury Stock", "Other Stockholder Equity", "Retained Earnings"]
                a = a.reindex(filters)
            elif statement == 'Income Statement':
                filters = ["Total Revenue", "Cost Of Revenue", "Gross Profit", "Selling General Administrative", "Research Development", "Other Operating Expenses", "Operating Income", "Interest Expense", "Income Tax Expense", "Income Before Tax", "Discontinued Operations", "Net Income", "Net Income From Continuing Ops", "Net Income Applicable To Common Shares", "Effect Of Accounting Charges", "Extraordinary Items", "Non Recurring", "Other Items", "Total Other Income Expense Net", "Ebit", "Total Operating Expenses", "Minority Interest"]
                a = a.reindex(filters)
                a = a.drop(['Ebit','Total Operating Expenses', 'Minority Interest', 'Total Other Income Expense Net'], axis=0)
            else:
                filters = ["Total Cash From Operating Activities", "Total Cashflows From Investing Activities", "Total Cash From Financing Activities", "Effect Of Exchange Rate", "Change In Cash", "Capital Expenditures", "Change To Account Receivables", "Change To Inventory", "Change To Liabilities", "Change To Netincome", "Change To Operating Activities", "Depreciation", "Investments", "Issuance Of Stock", "Net Borrowings", "Net Income", "Dividends Paid", "Repurchase Of Stock", "Other Cashflows From Financing Activities", "Other Cashflows From Investing Activities"]
                a = a.reindex(filters)
            ### further clean the dataframe and attach it with previous
            a = a.T.reset_index(drop=False).T
            a = a.T.reset_index(drop=False).T
            a.iloc[0] = ticker_name
            output = pd.concat([output,a], ignore_index=False, axis = 1)
        return output
    output = statements_chart(tickers, statement, frequency)
    ### there is a glitch with streamlit so this temporairly fixes it and allows it to be displayed
    e = output.astype(str) 
    e = e.T.reset_index(drop=True).T
    st.dataframe(e)
    ### Adds the option to download data
    def to_excel(df, header):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', header = header)
        writer.save()
        processed_data = output.getvalue()
        return processed_data
    def get_table_download_link(df, header):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        val = to_excel(df, header)
        b64 = base64.b64encode(val)  # val looks like b'...'
        return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download xlsx</a>' # decode b'abc' => abc    
    st.markdown(get_table_download_link(output, False), unsafe_allow_html=True)

with column_2:##### Download various information chart
    st.header ('Download Various Other Information')
    tickers2 = st.text_input("Type in a Yahoo Finance Ticker/Tickers")
    tickers2 = tickers2.split(',') ### for some reason, we do not need to clean the tickers list as throughly as before and it works
    @st.cache(allow_output_mutation=True)
    def get_info(tickers2):
        a = pd.DataFrame()
        for ticker in tickers2:
            stock = yf.Ticker(ticker)
            b = stock.info
            c = pd.DataFrame.from_dict(b, orient='index', columns = [ticker]) 
            a = pd.concat ([a,c], axis = 1)

        return a
    a = get_info(tickers2)
    ### filter the data using a list generated by input
    filterer = st.text_input("Type in the things your are interested to gather, leave this blank for all info. e.g (marketCap, trailingPE, sharesOutstanding)")
    filterer = 'shortName,' + filterer ## attach short name on top for clarity
    
    if filterer == 'shortName,':
        a = a
    else:
        filterer = filterer.split (',')
        filterer = map(str.strip, filterer)
        a = a.loc[filterer]
    ### display dataframe
    d = a.astype(str) 
    st.dataframe(d)
    st.markdown(get_table_download_link(a, True), unsafe_allow_html=True) ### add option for download
