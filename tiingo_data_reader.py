
# %%
import requests
import pandas as pd
from io import BytesIO
import datetime as dt

# %%
def api_key():
    
    '''This function asks the user for their api key and returns it. If the user enters "default" the default token is returned.'''
    
    while True:
        
        api_key = input('Enter your api key: ')
        print(f'API key: {api_key}')
        print(f'Checking API key...')
        
        url = f'https://api.tiingo.com/tiingo/daily/aapl/prices?startDate=2023-01-01&format=csv&token={api_key}'
        try:
            with requests.get(url) as response:
                with BytesIO(response.content) as data:
                    df = pd.read_csv(data,
                                     parse_dates= ['date'])
            break
        
        except:
            print('Invalid api key. Please try again.')
        
    return api_key

# %%
def configure():
    
    '''This function allows the user to configure the data they want to download.'''

    # get tickers from user
    valid_ticker_options = ['type', 'upload']
    while True:
        ticker_option = input('Enter "type" to type in tickers or "upload" to upload a list of tickers: ' )
        print(f'Ticker option: {ticker_option}')
        
        if ticker_option in valid_ticker_options:
                
            if ticker_option == 'upload':
                print('Please put your tickers in an excel or csv file with no header and then enter the file path.') 
                # check if file type is valid
                valid_extensions = ['.xlsx', '.csv', '.txt']
                while True:
                    file_path = input('Enter the file path: ')
                    print(f'Reading tickers from "{file_path}"')
                    file_path = file_path.replace('\\', '/')
                    if file_path.endswith(tuple(valid_extensions)):
                        break
                    else:
                        print('Invalid file type. Please upload an excel or csv file.')
                
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
        
        # check if file is valid
        while True:
            try:
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path, header=None)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path, header=None)
                elif file_path.endswith('.txt'):
                    df = pd.read_csv(file_path, sep=',', header=None)
                break
            
            except:
                print('Error reading file. Please check your file.')
                file_path = input('Enter the file path: ')
    
            
        # get ticker list from file
        tickers = df.iloc[:, 0].tolist()
        print(f'Tickers uploaded: ')
        print(tickers)
    
    
    # get frequency from user
    valid_frequency_options = ['daily', 'weekly', 'monthly', 'annually']
    while True:
        frequency = input('Enter "daily" or "weekly" or "monthly" or "annually" for data frequency: ')
        print(f'Frequency: {frequency}')
        
        if frequency in valid_frequency_options:
            if frequency == 'daily':
                print('Getting daily data...')
            
            elif frequency == 'monthly':
                print('Getting monthly data...')
            
            elif frequency  == 'weekly':
                print('Getting weekly data...')
            
            elif frequency == 'annually':
                print('Getting annual data...')

            break
        
        print('Invalid option. Please enter "daily" or "weekly" or "monthly" or "annually" for data frequency: ')
    
    
    # get start and end date from user
    while True:
        start = input('Enter start date (e.g. 2022-1-1): ')
        print(f'Start date: {start}')
        try:
            start = dt.datetime.strptime(start, '%Y-%m-%d').date()
            if start >= dt.datetime.today().date():
                print('Start date cannot be today or later than today. Please enter a valid start date.')
            else: 
                break
        except:
            print('Invalid date format. Please enter a valid start date.')
                
    while True:
        end = input('Enter end date (e.g. 2022-1-31): ')
        print(f'End date: {end}')
        try:
            end = dt.datetime.strptime(end, '%Y-%m-%d').date()
            if end >= dt.datetime.today().date():
                print('End date cannot be today or later than today. Please enter a valid end date.')
            elif end < start:
                print('End date cannot be earlier than start date. Please enter a valid end date.')
            else:
                break
        except:
            print('Invalid date format. Please enter a valid end date.')
    

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
# main function
def get_data():
    
    '''This function gets the data from Tiingo according to the user's input and saves it to an excel file.'''
    
    # get api key
    token = api_key()
    
    # get user input
    tickers, frequency, start, end = configure()
    
    # get data
    df_list = []
    for ticker in tickers:
        print(f'Getting data for {ticker}...')
        try:
            url, ticker = get_url(ticker, start, end, frequency, token)
            df = get_df(url, ticker)
            df_list.append(df)
        except:
            print(f'Could not get data for {ticker}.')
            continue
    
    # combine dataframes
    try:
        df = pd.concat(df_list, ignore_index=True)
        # save data to excel file
        excel_file_name = f'{start}_{end} {frequency} {dt.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        df.to_excel(excel_file_name, sheet_name='tiingo', index=False)  
        print(f'Data saved to "{excel_file_name}"')
    
    except:
        print('Could not get data for any of the tickers. Please check the tickers and try again.')

# %%
# run the main function
get_data()
