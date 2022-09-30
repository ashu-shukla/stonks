import streamlit as st
import yfinance as yf

st.title('2-Day HL Entry Signal Generator')
st.info('Open of the next days candle should be inside the previous 2Days high and low!')
option = st.text_area('Enter stock symbols:',
                      'Reliance, ITC, Tata Motors, SBIN ', 1)
symbols = option.split(',')
tickers = []
for symbol in symbols:
    symbol = (symbol+'.ns').upper()
    symbol = symbol.replace(" ", "")
    tickers.append(symbol)

tickers
data = yf.download(
    tickers=tickers,
    period='1mo',
    interval='1d',
    group_by='ticker',
    threads=True
)
df = data.dropna()
with st.expander('Daily Dataframe recieved:'):
    df
for ticker in tickers:
    st.subheader(ticker)
    dt = df[ticker]
    last_2_recs = dt.tail(2)
    la = last_2_recs.drop(['Open', 'Adj Close', 'Volume'], axis=1)
    # ba = la.rename(columns={"Date": "date"}, inplace=True)
    la.reset_index(inplace=True)
    la['Date'] = la['Date'].dt.strftime('%d-%m-%Y')
    max_high = la['High'].max()
    min_low = la['Low'].min()
    col1, col2 = st.columns(2)
    with col1:
        with st.expander('Dataset to refer'):
            la
        st.info(f'Lowest Low {round(min_low,2)}')
        st.info(f'Highest High {round(max_high,2)}')
    with col2:
        st.error(f'Short Entry: {round(min_low*(1-0.0015),2)}')
        st.success(f'Long Entry: {round(max_high*(1+0.0015),2)}')
