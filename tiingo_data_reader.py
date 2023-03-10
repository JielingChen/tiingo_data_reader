# %%
# Description: This script will download historical stock/forex/crypto/mutual fund/ETF data from Tiingo.com using API key and save it in an Excel file.

import requests
import pandas as pd
from io import BytesIO
import datetime as dt

# %%
def api_key():
    
    '''This function asks the user for their api key and returns it.'''
    
    api_key = input('Enter your api key: ')
        
    return api_key

# %%
def configure():
    
    '''This function allows the user to configure the data they want to download.'''

    # get tickers from user
    valid_ticker_options = ['type', 'upload']
    while True:
        ticker_option = input('Enter "type" to type in tickers or "upload" to upload a list of tickers: ' )
    
        if ticker_option in valid_ticker_options:
                
            if ticker_option == 'upload':
                print('Please put your tickers in an excel or csv file as a column with no header, and then enter the file path.')
                file_path = input('Enter the file path: ')
                file_path = file_path.replace('\\', '/')
                print(f'Reading tickers from "{file_path}"')
                
            elif ticker_option == 'type':
                print('Please type in the tickers.')
                
            break
        
        print('Invalid option. Please enter "type" to type in tickers or "upload" to upload a ticker list: ')
    
    if ticker_option == 'type':
        tickers = []
        while True:
            ticker = input('Enter ticker (e.g. AAPL) or "done" to exit: ')
            print(f'{ticker}')
            if ticker == 'done':
                break
            tickers.append(ticker)
    
    elif ticker_option == 'upload':
        while True:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, header=None)
                break
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, header=None)
                break
            elif file_path.endswith('.txt'):
                df = pd.read_csv(file_path, sep=',', header=None)
                break
            
            print('Invalid file type. Please upload an excel or csv file.')
            file_path = input('Enter the file path: ')
            
        tickers = df.iloc[:, 0].tolist()
    
    
    # get frequency from user
    valid_frequency_options = ['daily', 'weekly', 'monthly', 'annually']
    while True:
        frequency = input('Enter "daily" or "weekly" or "monthly" or "annually" for data frequency: ')
        
        if frequency in valid_frequency_options:
            if frequency == 'daily':
                print('Getting daily data...')
            
            elif frequency == 'monthly':
                print('Getting monthly data...')
            
            elif frequency  == 'weekly':
                print('Getting weekly data...')
            
            elif frequency == 'annually':
                print('Getting annually data...')

            break
        
        print('Invalid option. Please enter "daily" or "weekly" or "monthly" or "annually" for data frequency: ')
    
    
    # get start and end date from user
    while True:
        while True:
            start = input('Enter start date (e.g. 2022-1-1): ')
            start = dt.datetime.strptime(start, '%Y-%m-%d').date()
            if start >= dt.datetime.today().date():
                print('Start date cannot be today or later than today. Please enter a valid start date.')
            else: 
                print(f'Start date: {start}')
                break
        
        while True:
            end = input('Enter end date (e.g. 2022-1-31): ')
            end = dt.datetime.strptime(end, '%Y-%m-%d').date()
            if end >= dt.datetime.today().date():
                print('End date cannot be today or later than today. Please enter a valid end date.')
            else:
                print(f'End date: {end}')
                break
            
        if start <= end:
            break
           
        print('End date cannot be earlier than start date. Please enter start date and end date again.')
    

    return tickers, frequency, start, end

# %%
def get_url(ticker, start, end, resampleFreq, token):
    
    '''This function returns the url for the api call.'''
    
    startDate = f'{start.year}-{str(start.month).zfill(2)}-{str(start.day).zfill(2)}'
    endDate = f'{end.year}-{str(end.month).zfill(2)}-{str(end.day).zfill(2)}'
    
    url = f'https://api.tiingo.com/tiingo/daily/{ticker.lower()}/prices?startDate={startDate}&endDate={endDate}&format=csv&resampleFreq={resampleFreq}&token={token}'
    
    return url, ticker

# %%
def get_df(url, ticker):
    
    '''This function returns a dataframe with the data from the url.'''
    
    # get data from url
    with requests.get(url) as response:
        with BytesIO(response.content) as data:
            df = pd.read_csv(data,
                             parse_dates= ['date'])
            
    # insert ticker column
    df.insert(0, 'ticker', ticker)
    
    return df

# %%
def get_data():
    
    '''This function gets the data from Tiingo according to the user's input and saves it to an excel file.'''
    
    # get api key
    token = api_key()
    
    # get user input
    tickers, frequency, start, end = configure()
    
    # get data
    df_list = []
    for ticker in tickers:
        try:
            print(f'Getting data for {ticker}...')
            url, ticker = get_url(ticker, start, end, frequency, token)
            df = get_df(url, ticker)
            df_list.append(df)
        except:
            print(f'Could not get data for {ticker}...')
            continue
    
    # combine dataframes
    df = pd.concat(df_list, ignore_index=True)
 
    # save data to excel file
    excel_file_name = f'{start}_{end} {frequency} {dt.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    df.to_excel(excel_file_name, sheet_name='tiingo', index=False)  
     
    print(f'Data saved to "{excel_file_name}"')

# %%
# run the main function
get_data()
