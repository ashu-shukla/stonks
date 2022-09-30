import streamlit as st
import requests
from datetime import datetime
import plotly.graph_objects as go


st.set_page_config(
    page_title="Options Scanner",
    page_icon="🦈",
    layout="wide"
)
masterUrl = "https://www.nseindia.com/"
fiiDiiCashUrl = "https://www.nseindia.com/api/fiidiiTradeReact"
optionChainUrl = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'

basicheaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'
}


def nsefetch(url):
    with requests.Session() as s:
        setup = s.get(masterUrl, headers=basicheaders)
        resp = s.get(url, cookies=setup.cookies, headers=basicheaders)
        js = resp.json()
        return js


def getoptdata(type, entry):
    data = {}
    data['buy_qty'] = entry[type]['totalBuyQuantity']
    data['sell_qty'] = entry[type]['totalSellQuantity']
    data['iv'] = entry[type]['impliedVolatility']
    data['oi'] = entry[type]['openInterest']
    data['change_in_oi'] = entry[type]['changeinOpenInterest']
    data['pchange_in_oi'] = entry[type]['pchangeinOpenInterest']
    data['total_traded_volume'] = entry[type]['totalTradedVolume']
    data['last_price'] = entry[type]['lastPrice']
    data['change_in_price'] = entry[type]['change']
    data['pchange_in_price'] = entry[type]['pChange']
    data['buy_sell_diff'] = data['buy_qty']-data['sell_qty']
    return data


@st.cache(ttl=0.2)
def options():
    main = []
    data = nsefetch(optionChainUrl)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print('Fetched!', current_time)
    entries = data['filtered']['data']
    underlying = data['records']['underlyingValue']
    time = data['records']['timestamp']
    expiry_date = data['records']['expiryDates'][0]
    for entry in entries:
        strike = entry['strikePrice']
        ce_data = getoptdata('CE', entry)
        pe_data = getoptdata('PE', entry)
        main.append({'strike': strike, 'CE': ce_data, 'PE': pe_data})
    return main, time, underlying, expiry_date


def top_five_type(type, data, cmp, buy=False):
    main = []
    if type == 'CE':
        ans = list(filter(lambda x: x['strike'] <
                   cmp if buy else x['strike'] > cmp, data))
    else:
        ans = list(filter(lambda x: x['strike'] >
                   cmp if buy else x['strike'] < cmp, data))
    tfive = sorted(ans, key=lambda x: x[type]
                   ['buy_sell_diff'], reverse=buy)[:5]
    for x in tfive:
        data = {}
        data['Strike'] = x['strike']
        data['Buy_qty'] = x[type]['buy_qty']
        data['Sell_qty'] = x[type]['sell_qty']
        data['Difference'] = x[type]['buy_sell_diff']
        data['LTP'] = x[type]['last_price']
        main.append(data)
    return main


def oi_chart(data, cmp, range, change=True):
    # print(data)
    if change:
        oi = 'change_in_oi'
    else:
        oi = 'oi'
    strikes = []
    ce_change = []
    ce_pchange = []
    pe_change = []
    pe_pchange = []
    for entry in data:
        if entry['strike'] > cmp-range and entry['strike'] < cmp+range:
            strikes.append(entry['strike'])
            ce_change.append(entry['CE'][oi])
            pe_change.append(entry['PE'][oi])
            ce_pchange.append(f"{round(entry['CE']['pchange_in_oi'], 2)}%")
            pe_pchange.append(f"{round(entry['PE']['pchange_in_oi'], 2)}%")
    fig = go.Figure(data=[
        (go.Bar(name='PE', x=strikes, y=pe_change,
                hovertext=pe_pchange, marker_color='green', width=30)),
        go.Bar(name='CE', x=strikes, y=ce_change,
               hovertext=ce_pchange, width=30)
    ])
    fig.update_layout(
        barmode='group',
        title='Complete OI Bar Chart')
    st.plotly_chart(fig, use_container_width=True)


def top_five_oi(type, data, cmp, thresh):
    main = []
    if type == 'CE':
        ans = list(filter(lambda x: x['strike'] > cmp, data))
    else:
        ans = list(filter(lambda x: x['strike'] < cmp, data))
    tfive = sorted(ans, key=lambda x: x[type]
                   ['pchange_in_oi'], reverse=True)
    tfive = list(filter(lambda x: x[type]['last_price'] > thresh, tfive))[:5]
    for x in tfive:
        data = {}
        data['Strike'] = x['strike']
        data['OI'] = x[type]['oi']
        data['Change in OI'] = x[type]['change_in_oi']
        data['% change in OI'] = f"{round(x[type]['pchange_in_oi'], 2)}%"
        data['LTP'] = x[type]['last_price']
        data['Price Change'] = x[type]['change_in_price']
        main.append(data)
    return main


st.title('Options Scanner')
st.info('My one stop page to see everything related to options.')
data, time, cmp, expiry = options()
c1, c2, c3 = st.columns(3)
c1.metric('CMP', cmp)
c2.metric('Expiry Date', expiry)
c3.metric('Last Updated', time)
st.header('Top 5 sell/buy orders seen in OTM/ITM OPT:')
t1, t2 = st.tabs(["OTM Selling", "ITM Buying"])
with t1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('OTM PE:')
        toppe = top_five_type('PE', data, cmp)
        st.table(toppe)
    with col2:
        st.subheader('OTM CE:')
        topce = top_five_type('CE', data, cmp)
        st.table(topce)
with t2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('ITM CE:')
        topce = top_five_type('CE', data, cmp, True)
        st.table(topce)

    with col2:
        st.subheader('ITM PE:')
        toppe = top_five_type('PE', data, cmp, True)
        st.table(toppe)
st.subheader('Open Interest')
range = st.number_input('Enter option range(+-):', min_value=500, value=1500)
tab1, tab2 = st.tabs(["Open Interest", "Change in Open Interest"])
with tab1:
    oi_chart(data, cmp, range, False)
with tab2:
    oi_chart(data, cmp, range)
st.header('Top 5 OI jumps in %')
threshold = st.number_input('Enter price to scan above', min_value=0)
col3, col4 = st.columns(2)
with col3:
    st.subheader('OTM PE:')
    top_pe_oi = top_five_oi('PE', data, cmp, threshold)
    st.table(top_pe_oi)

with col4:
    st.subheader('OTM CE:')
    top_ce_oi = top_five_oi('CE', data, cmp, threshold)
    st.table(top_ce_oi)
