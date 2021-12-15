import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import sys
from multiprocessing import Pool



# pd.options.display.float_format = "${:.5f}".format

from ui import header, footer, driftsummary, mangosummary

import requests
import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


sys.path.append("mango-explorer/")
import decimal
import mango

# df = pd.read_csv(
#     "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
# )

fees = pd.read_excel("sol-spl-fees.xlsx")


# def get_coin_gecko():
#     return requests.get(
#         "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=solana%2Cbitcoin%2Cethereum&order=market_cap_desc&per_page=100&page=1&sparkline=false"
#     ).json()


def get_mango_prices():
    try:
        mango_sol_candles = requests.get(
            "https://event-history-api-candles.herokuapp.com/trades/address/2TgaaVoHgnSeEtXvWTx13zQeTf4hYWAMEiMQdcG6EwHi"
        ).json()["data"]
        mango_btc_candles = requests.get(
            "https://event-history-api-candles.herokuapp.com/trades/address/DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8"
        ).json()["data"]
        mango_eth_candles = requests.get(
            "https://event-history-api-candles.herokuapp.com/trades/address/DVXWg6mfwFvHQbGyaHke4h3LE9pSkgbooDSDgA4JBC8d"
        ).json()["data"]
        mango_avax_candles = requests.get(
        'https://event-history-api-candles.herokuapp.com/trades/address/EAC7jtzsoQwCbXj1M3DapWrNLnc3MBwXAarvWDPr2ZV9'
        ).json()["data"]
        mango_bnb_candles = requests.get(
            'https://event-history-api-candles.herokuapp.com/trades/address/CqxX2QupYiYafBSbA519j4vRVxxecidbh2zwX66Lmqem'
        ).json()["data"]
        return [mango_sol_candles, mango_btc_candles, mango_eth_candles] \
        + [[{"price": np.nan, "time": 0}] * 2] \
        + [mango_avax_candles, mango_bnb_candles]
    except:
        return [[{"price": np.nan, "time": np.nan}] * 2] * 6


def get_fida_prices():
    try:
        mango_sol_candles = requests.get(
            "https://serum-api.bonfida.com/perps/trades?market=jeVdn6rxFPLpCH9E6jmk39NTNx2zgTmKiVXBDiApXaV"
        ).json()["data"]
        mango_btc_candles = requests.get(
            "https://serum-api.bonfida.com/perps/trades?market=475P8ZX3NrzyEMJSFHt9KCMjPpWBWGa6oNxkWcwww2BR"
        ).json()["data"]
        mango_eth_candles = requests.get(
            "https://serum-api.bonfida.com/perps/trades?market=3ds9ZtmQfHED17tXShfC1xEsZcfCvmT8huNG79wa4MHg"
        ).json()["data"]
        return [mango_sol_candles, mango_btc_candles, mango_eth_candles]+[[{"markPrice": np.nan, "time": 0}] * 2] * 3
    except:
        return [[{"markPrice": np.nan, "time": 0}] * 2] * 6


def get_drift_prices(drift):
    try:
        # drift_p0 = requests.get(
        #     "https://mainnet-beta.history.drift.trade/trades/marketIndex/0"
        # ).json()
        # drift_p1 = requests.get(
        #     "https://mainnet-beta.history.drift.trade/trades/marketIndex/1"
        # ).json()
        # drift_p2 = requests.get(
        #     "https://mainnet-beta.history.drift.trade/trades/marketIndex/2"
        # ).json()
        # return [
        #     drift_p0["data"]["trades"],
        #     drift_p1["data"]["trades"],
        #     drift_p2["data"]["trades"],
        # ]
        market_summary = driftsummary.drift_market_summary_df(drift)
        # print(market_summary)
        mm = market_summary.set_index("FIELD").loc[
            ["mark_price", "last_mark_price_twap_ts"]
        ]
        mm.index = ["afterPrice", "ts"]
        # mm.columns = [0, 1, 2]
        res = mm.T.to_dict("records")
        # print(res[0])
        return res
    except Exception as e:
        print(e)
        return [[{"afterPrice": np.nan, "ts": np.nan}] * 2] * 3



mango_v_drift = pd.DataFrame(
    [["loading..."] * 4] * 4,
    columns=["Protocol", "SOL", "BTC", "ETH"],
)
mango_v_drift["Protocol"] = pd.Series(["Drift", "Mango", "Bonfida", "(CoinGecko)"])
ftx_funds = [{
    "success": False,
    "result": {
        "volume": np.nan,
        "nextFundingRate": np.nan,
        "nextFundingTime": "2021-12-03T21:00:00+00:00",
        "openInterest": np.nan,
    },
}]*5

ftx_px = [{"success":False,
"result":{"name":"AVAX-PERP","underlying":np.nan, "description":"Avalanche Perpetual Futures",
"type":"perpetual","expiry":True,"perpetual":True,"expired":False,"enabled":False,
"postOnly":False,"priceIncrement":0.001,"sizeIncrement":0.1,"last":84.491,"bid":84.498,
"ask":84.531,"index":np.nan,"mark":np.nan,"imfFactor":0.002,"lowerBound":80.257,"upperBound":88.733,
"underlyingDescription":"Avalanche","expiryDescription":"Perpetual","moveStart":None,
"marginPrice":84.535,"positionLimitWeight":100.0,"group":"perpetual","change1h":-0.013858591043243936,
"change24h":-0.07248110071208347,"changeBod":np.nan,"volumeUsd24h":212413536.68,
"volume":np.nan,"openInterest":np.nan,"openInterestUsd":np.nan}}] * 5

mango_v_drift_by_asset = html.Div("loading...")

# image_filename = os.getcwd() + "/logo_drift.png"  # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, "rb").read())

platyperps_last_update_1 = html.Div()

app = dash.Dash(__name__)
app.title = "Platyperps | Solana Perp Platforms Side-By-Side"
server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        header.make_header(),
        dcc.Loading(
            id="loading-1", type="default", children=html.Div(id="loading-output-1")
        ),
        html.Div("loading...", id="tab-content"),
        # html.Br(),
        # html.Br(),
        # html.Br(),
    ]
)

context = mangosummary.mango_py()


def make_funding_table():

    ASSETS = ("SOL", "BTC", "ETH", "LUNA", "AVAX", "BNB")
    # import requests
    def load_mango_data(market="SOL-PERP"):
        # Find the addresses associated with the Perp market
        perp_stub = context.market_lookup.find_by_symbol("perp:" + market)
        # Load the rest of the on-chain metadata of the market
        perp_market = mango.ensure_market_loaded(context, perp_stub)
        # z = perp_market.fetch_funding(context)
        return perp_market
    try:
        mfund_sol, mfund_btc, mfund_eth, mfund_avax, mfund_bnb = (
            load_mango_data("SOL-PERP"),
            load_mango_data("BTC-PERP"),
            load_mango_data("ETH-PERP"),
            load_mango_data("AVAX-PERP"),
            load_mango_data("BNB-PERP"),
        )
        mango_fund_rate = [
            float(mfund.fetch_funding(context).rate) if mfund is not None else np.nan
            for mfund in [mfund_sol, mfund_btc, mfund_eth, None, mfund_avax, mfund_bnb]
        ]
        
    except:
        mango_fund_rate = [np.nan]*6
        
    try:
        global ftx_funds
        ftx_funds = [
            requests.get("https://ftx.com/api/futures/%s-PERP/stats" % x).json()
            for x in ASSETS
        ]

        global ftx_px
        ftx_px = [
        requests.get("https://ftx.com/api/futures/%s-PERP" % x).json()
            for x in ASSETS

        ]
    except:
        ftx_funds = [{
            "success": False,
            "result": {
                "volume": np.nan,
                "nextFundingRate": np.nan,
                "nextFundingTime": "2021-12-03T21:00:00+00:00",
                "openInterest": np.nan,
            },
        }]*len(ASSETS)

        ftx_px = [{"success":False,
        "result":{"name":"AVAX-PERP","underlying":np.nan, "description":"Avalanche Perpetual Futures",
        "type":"perpetual","expiry":True,"perpetual":True,"expired":False,"enabled":False,
        "postOnly":False,"priceIncrement":0.001,"sizeIncrement":0.1,"last":84.491,"bid":84.498,
        "ask":84.531,"index":np.nan,"mark":np.nan,"imfFactor":0.002,"lowerBound":80.257,"upperBound":88.733,
        "underlyingDescription":"Avalanche","expiryDescription":"Perpetual","moveStart":None,
        "marginPrice":84.535,"positionLimitWeight":100.0,"group":"perpetual","change1h":-0.013858591043243936,
        "change24h":-0.07248110071208347,"changeBod":np.nan,"volumeUsd24h":212413536.68,
        "volume":np.nan,"openInterest":np.nan,"openInterestUsd":np.nan}}] * len(ASSETS)


    ftx_fund_rate = [z["result"]["nextFundingRate"] for z in ftx_funds]
    
    drift_m_sum = drift.market_summary().T
    drift_fund_rate = (
        (drift_m_sum["last_mark_price_twap"] - drift_m_sum["last_oracle_price_twap"])
        / drift_m_sum["last_oracle_price_twap"]
    ) / 24

    funding_rate_df = pd.concat(
        [pd.Series(ftx_fund_rate), pd.Series(mango_fund_rate), drift_fund_rate], axis=1
    ).T
    funding_rate_df.index = ["(FTX)", "Mango", "Drift"]
    funding_rate_df.index.name = "Protocol"
    funding_rate_df.columns = ["SOL", "BTC", "ETH", "LUNA", "AVAX", 'BNB']
    funding_rate_df = funding_rate_df * 100
    for col in funding_rate_df.columns:
        funding_rate_df[col] = funding_rate_df[col].map("{:,.5f}%".format)

    funding_rate_df = funding_rate_df.reset_index()

    # make volume table too
    bonfida_markets = {
        "BTC": "475P8ZX3NrzyEMJSFHt9KCMjPpWBWGa6oNxkWcwww2BR",
        "SOL": "jeVdn6rxFPLpCH9E6jmk39NTNx2zgTmKiVXBDiApXaV",
        "ETH": "3ds9ZtmQfHED17tXShfC1xEsZcfCvmT8huNG79wa4MHg",
    }

    mango_markets = {
        "BTC": "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        "SOL": "2TgaaVoHgnSeEtXvWTx13zQeTf4hYWAMEiMQdcG6EwHi",
        "ETH": "DVXWg6mfwFvHQbGyaHke4h3LE9pSkgbooDSDgA4JBC8d",
        "AVAX": "EAC7jtzsoQwCbXj1M3DapWrNLnc3MBwXAarvWDPr2ZV9",
        "BNB": "CqxX2QupYiYafBSbA519j4vRVxxecidbh2zwX66Lmqem",
    }

    drift_markets = {v: str(k) for k,v in driftsummary.MARKET_INDEX_TO_PERP.items()}
    print(drift_markets)
    try:
        fida_volume = [
            requests.get(
                "https://serum-api.bonfida.com/perps/volume?market=%s"
                % bonfida_markets[x]
            ).json()["data"]["volume"]
            for x in ("SOL", "BTC", "ETH")
        ]
    except:
        fida_volume = [np.nan] * 3

    try:
        mango_volume = [
            requests.get(
                "https://event-history-api.herokuapp.com/stats/perps/%s"
                % mango_markets[x]
            ).json()["data"]["volume"]
            for x in ("SOL", "BTC", "ETH")
        ] +\
            [np.nan]\
            + \
            [    requests.get(
                "https://event-history-api.herokuapp.com/stats/perps/%s"
                % mango_markets[x]
            ).json()["data"]["volume"]
            for x in ("AVAX", "BNB")]
    except:
        mango_volume = [np.nan] * 3

    try:
        drift_volume = [
            requests.get(
                "https://mainnet-beta.history.drift.trade/stats/24HourVolume?marketIndex=%s"
                % drift_markets[x+'-PERP']
            ).json()["data"]["volume"]
            for x in ("SOL", "BTC", "ETH", "LUNA", "AVAX", "BNB")
        ]
    except:
        drift_volume = [np.nan] * 5

    ftx_volume = [z["result"]["volume"] for z in ftx_funds]

    volumes = pd.DataFrame(
        [ftx_volume, mango_volume, drift_volume, fida_volume],
        index=[
            "(FTX)",
            "Mango",
            "Drift",
            "Bonfida",
        ],
    )
    volumes.iloc[[0], :] *= np.array([[160, 48000, 3900, 66, 84, 520]])  # todo lol
    for col in volumes.columns:
        volumes[col] = volumes[col].astype(float).map("${:,.0f}".format)
    volumes = volumes.reset_index()
    volumes.columns = ["Protocol", "SOL", "BTC", "ETH", "LUNA", "AVAX", "BNB"]
    # volumes

    return funding_rate_df, volumes, ftx_px


drift = driftsummary.drift_py()

funding_table, volume_table, ftx_px = make_funding_table()



mango_prices_full = get_mango_prices()
fida_prices_full = get_fida_prices()
drift_prices_full = get_drift_prices(drift)

def page_1_layout():

    return html.Div(
        [
            html.Br(),
            html.Div(platyperps_last_update_1, id="last-update-ts"),
            # html.H6("(updates every 10 seconds)"),
            # html.H1("Protocol Compare"),
            dcc.Interval(
                id="interval-component",
                interval=1 * 1000,
                n_intervals=0,  # in milliseconds
            ),
            html.H5("Overview"),
            html.H6("Price"),
            html.Span(
                [
                    html.Div(
                        [
                            dash_table.DataTable(
                                id="mango_v_drift_table",
                                columns=[
                                    {
                                        "name": i,
                                        "id": i,
                                        # "deletable": False,
                                        "selectable": False,
                                    }
                                    for i in mango_v_drift.columns
                                ],
                                style_data={
                                    "whiteSpace": "normal",
                                    "height": "auto",
                                    "lineHeight": "15px",
                                },
                                data=mango_v_drift.to_dict("records"),
                                # editable=True,
                                # filter_action="native",
                                sort_action="native",
                                sort_mode="multi",
                                # column_selectable="single",
                                # row_selectable="multi",
                                # row_deletable=True,
                                selected_columns=[],
                                selected_rows=[],
                                page_action="native",
                                page_current=0,
                                page_size=5,
                            ),
                        ],
                        style={
                            "max-width": "700px",
                            "margin": "auto",
                            # "display": "inline",
                        },
                    ),
                    # dcc.Graph(
                    #     id="mango_v_drift_graph",
                    #     style={
                    #         "max-width": "500px",
                    #     },
                    # ),
                ]
            ),
            html.Br(),
            html.H6("1h Funding Rates"),
            html.Div(
                [
                    dash_table.DataTable(
                        id="funding_table",
                        columns=[
                            {
                                "name": i,
                                "id": i,
                                "deletable": False,
                                "selectable": True,
                            }
                            for i in funding_table.columns
                        ],
                        style_data={
                            "whiteSpace": "normal",
                            "height": "auto",
                            "lineHeight": "15px",
                        },
                        data=funding_table.to_dict("records"),
    #                      style_data_conditional=[
    #     {
    #         'if': {
    #             'filter_query': '{{%s}} contains "%"'.format(col),
    #         },
    #         'backgroundColor': '#FFF',
    #         'color': 'green'
    #     } for col in funding_table.columns
    # ],
       style_data_conditional=[
        {
            'if': {
                'filter_query': '{SOL} contains "-"',
            },
            'backgroundColor': '#FFF',
            'color': 'green'
        } 
    ],
                        # editable=True,
                        # filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        # column_selectable="single",
                        # row_selectable="multi",
                        # row_deletable=True,
                        selected_columns=[],
                        selected_rows=[],
                        page_action="native",
                        page_current=0,
                        page_size=5,
                    ),
                ],
                style={
                    "max-width": "700px",
                    "margin": "auto",
                },
            ),
            html.Br(),
            html.H6("24h Volume"),
            html.Div(
                [
                    dash_table.DataTable(
                        id="volume_table",
                        columns=[
                            {
                                "name": i,
                                "id": i,
                                "deletable": False,
                                "selectable": True,
                            }
                            for i in volume_table.columns
                        ],
                        style_data={
                            "whiteSpace": "normal",
                            "height": "auto",
                            "lineHeight": "15px",
                        },
                        data=volume_table.to_dict("records"),
                        # editable=True,
                        # filter_action="native",
                        sort_action="native",
                        sort_mode="multi",
                        # column_selectable="single",
                        # row_selectable="multi",
                        # row_deletable=True,
                        selected_columns=[],
                        selected_rows=[],
                        page_action="native",
                        page_current=0,
                        page_size=5,
                    ),
                ],
                style={
                    "max-width": "700px",
                    "margin": "auto",
                },
            ),
            html.Br(),
            html.H5("Details By Asset"),
            html.Div(
                [
                    dcc.Dropdown(
                        id="dropdown",
                        options=[
                            {"label": i, "value": i}
                            for i in ["SOL-PERP", "BTC-PERP", "ETH-PERP"]
                        ],
                        value="SOL-PERP",
                    ),
                    html.Div(mango_v_drift_by_asset, id="live-update-text"),
                ],
                style={"max-width": "500px", "margin": "auto", "text-align": "left"},
            ),
        ],
        style={
            "text-align": "center",
            "margin": "auto",
        },
    )


@app.callback(
    [
        Output("refresh-btn-out", "children"),
        Output("drift-py-last-update", "children"),
        Output("drift-summary-id", "children"),
        Output("btn-refresh-1", "children"),
    ],
    Input("btn-refresh-1", "n_clicks"),
)
def displayClick(btn1):
    newdrift = driftsummary.drift_py()
    print("loaded new drift")

    lastudatestr = (
        "last update: " + newdrift.last_update.strftime("%Y/%m/%d: %H:%M:%S") + " UTC"
    )
    summary_html = driftsummary.make_drift_summary(newdrift)

    global drift
    drift = newdrift

    return btn1, lastudatestr, summary_html, "refresh"


@app.callback(
    [
        Output("btn-refresh-1", "disable"),
    ],
    Input("btn-refresh-1", "n_clicks"),
)
def displayClickLoading(btn1):
    return [True]


page_2_layout = html.Div(
    [
        html.H5("Drift Summary"),
        html.Button(
            "refresh",
            id="btn-refresh-1",
            n_clicks=0,
        ),
        html.Code(
            "",
            id="refresh-btn-out",
        ),
        html.Code(
            "last update: " + drift.last_update.strftime("%Y/%m/%d: %H:%M:%S") + " UTC",
            id="drift-py-last-update",
        ),
        html.Br(),
        html.A(
            "Insurance Fund",
            href="https://solscan.io/account/Bzjkrm1bFwVXUaV9HTnwxFrPtNso7dnwPQamhqSxtuhZ#splTransfer",
        ),
        " | ",
        html.A(
            " Collateral Vault",
            href="https://solscan.io/account/6W9yiHDCW9EpropkFV8R3rPiL8LVWUHSiys3YeW6AT6S#splTransfer",
        ),
        html.Br(),
        dcc.Loading(
            id="loading-2",
            children=[html.Div("loading...", id="drift-summary-id")],
            type="circle",
        ),
        html.Br(),
    ]
)


page_3_layout = html.Div(
    [
        html.H5("Mango Summary"),
        mangosummary.make_pyth_summary(),
        mangosummary.make_mango_summary(),
        html.Br(),
    ]
)

page_faq_layout = html.Div(
    [
        footer.make_footer(),
    ]
)

page_resources_layout = html.Div(
    [
        footer.make_resources(),
    ]
)


@app.callback(
    [
        dash.dependencies.Output("tab-content", "children"),
        dash.dependencies.Output("tab-compare", "style"),
        dash.dependencies.Output("tab-drift", "style"),
        dash.dependencies.Output("tab-mango", "style"),
    ],
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/" or pathname == "/compare":
        return page_1_layout(), {"background-color": "gray", "color": "white"}, {}, {}
    elif pathname == "/drift":
        return page_2_layout, {}, {"background-color": "gray", "color": "white"}, {}
    elif pathname == "/mango":
        return page_3_layout, {}, {}, {"background-color": "gray", "color": "white"}
    elif pathname == "/faq":
        return page_faq_layout, {}, {}, {}
    elif pathname == "/resources":
        return page_resources_layout, {}, {}, {}
    else:
        return (
            html.Div([html.H1("Error 404 - Page not found")]),
            {},
            {},
            {"background-color": "white", "color": "black"},
        )


@app.callback(
    [
        Output("last-update-ts", "children"),
        Output("live-update-text", "children"),
        # Output("live_table", "data"),
        Output("mango_v_drift_table", "data"),
        Output("funding_table", "data"),
        Output("volume_table", "data"),
        # Output("mango_v_drift_graph", "figure"),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("dropdown", "value"),
    ],
)
def update_metrics(n, selected_value):
    maintenant = datetime.datetime.utcnow()

    if (maintenant - maintenant_data).seconds > 15:
        get_new_data() # fire and forget async_foo()
    maintenant = datetime.datetime.utcnow()

    drift_prices_selected = None
    rr = None
    style = {"padding": "5px", "fontSize": "16px"}
    # coingeckp = get_coin_gecko()
    dds = {}
    for key, val in ({0: "SOL", 1: "BTC", 2: "ETH", 3:'LUNA', 4:'AVAX', 5: "BNB"}).items():
        fida_prices = fida_prices_full[key]
        fida_price_latest = fida_prices[0]
        fida_price_change = fida_price_latest["markPrice"] - fida_prices[1]["markPrice"]
        # mango_price_change_dir = "up" if mango_price_change > 0 else "down"
        # print(fida_price_latest)
        fida_last_trade = (
            str(
                (
                    maintenant - pd.to_datetime(int(fida_price_latest["time"]) * 1e9)
                ).seconds
            ).split(".")[0]
            + " seconds ago"
        )

        mango_prices = mango_prices_full[key]
        mango_price_latest = mango_prices[0]
        mango_price_change = mango_price_latest["price"] - mango_prices[1]["price"]
        # mango_price_change_dir = "up" if mango_price_change > 0 else "down"
        mango_last_trade = (
            str(
                (maintenant - pd.to_datetime(mango_price_latest["time"] * 1e6)).seconds
            ).split(".")[0]
            + " seconds ago"
        )

        drift_prices = drift_prices_full[key]

        drift_price_latest = drift_prices["afterPrice"]
        drift_price_change = (
            np.nan
        )  # 0  # drift_price_latest - drift_prices[1]["afterPrice"]
        drift_last_trade = (
            str((maintenant - pd.to_datetime(drift_prices["ts"])).seconds).split(".")[0]
            + " seconds ago"
        )

        drift_sol_card = (
            "${:.2f}".format(drift_price_latest)
            # + "\n (last trade: "
            # + drift_last_trade
            # + ")"
        )

        mango_sol_card = (
            "${:.2f}".format(mango_price_latest["price"])
            # + "\n (last trade: "
            # + mango_last_trade
            # + ")"
        )

        fida_sol_card = (
            "${:.2f}".format(fida_price_latest["markPrice"])
            # + "\n (last trade: "
            # + drift_last_trade
            # + ")"
        )
        ftx_price_latest = ftx_px[key]['result']['mark']
        ftx_sol_card = "${:.2f}".format(ftx_price_latest)

        # coingecko_card1 = [x for x in coingeckp if x["symbol"].lower() == val.lower()][
        #     0
        # ]

        dds[val] = [
            ftx_sol_card,
            mango_sol_card,
                        drift_sol_card,

            fida_sol_card,
            
            # "{:.2f}".format(coingecko_card1["current_price"]),
        ]

        if val in selected_value:
            global mango_v_drift_by_asset
            mango_v_drift_by_asset = [
                # html.Div(
                #     "{}".format(selected_value)
                #     + " (coingecko: ${:.2f})".format(coingecko_card1["current_price"]),
                # ),
                html.Br(),
                html.Img(
                    src="assets/logo_drift.png",
                    style={
                        "height": "45px",
                        # "width": "2%",
                        "float": "left",
                        "position": "relative",
                        "padding-right": 10,
                    },
                ),
                html.A(
                    html.Code(
                        "Drift "
                        + selected_value
                        + ": {0:.2f}".format(drift_price_latest),
                        style=style,
                    ),
                    href="https://alpha.drift.trade/" + selected_value.split("-")[0],
                    target="_",
                ),
                html.Br(),
                html.Code(
                    "last trade: delta={0:.4f}, time=".format(drift_price_change)
                    + drift_last_trade
                    + "",
                    # style=style,
                ),
                html.Br(),
                html.Br(),
                html.Img(
                    src="assets/logo_mango.png",
                    style={
                        "height": "45px",
                        # "width": "22%",
                        "float": "left",
                        "position": "relative",
                        "padding-top": 0,
                        "padding-right": 10,
                    },
                ),
                html.A(
                    html.Code(
                        "Mango "
                        + selected_value
                        + ": {0:.2f}".format(mango_price_latest["price"]),
                        style=style,
                    ),
                    href="https://trade.mango.markets/market?name=" + selected_value,
                    target="_",
                ),
                html.Br(),
                html.Code(
                    "last trade: delta={0:.4f}, time=".format(mango_price_change)
                    + mango_last_trade
                    + "",
                    # style=style,
                ),
                html.Br(),
                html.Br(),
                html.Img(
                    src="assets/bonfidalogo.png",
                    style={
                        "height": "45px",
                        # "width": "22%",
                        "float": "left",
                        "position": "relative",
                        "padding-top": 0,
                        "padding-right": 8,
                    },
                ),
                html.A(
                    html.Code(
                        "Bonfida "
                        + selected_value
                        + ": {0:.2f}".format(fida_price_latest["markPrice"]),
                        style=style,
                    ),
                    href="https://perps.bonfida.org/#/trade/"
                    + selected_value.replace("-", ""),
                    target="_",
                ),
                html.Br(),
                html.Code(
                    "last trade: delta={0:.4f}, time=".format(fida_price_change)
                    + fida_last_trade
                    + "",
                    # style=style,
                ),
                # html.H4("Recent Drift Trades:"),
            ]

            drift_prices_selected = drift_prices

    global mango_v_drift
    mango_v_drift = pd.DataFrame(
        dds,
        index=pd.Index([ '(FTX)',  "Mango", "Drift", "Bonfida",], name='Protocol'),
    ).reset_index()

    global platyperps_last_update_1
    platyperps_last_update_1 = html.Span(
        [
            html.Code(
                [
                    " last update: "
                    + maintenant_data.strftime("%Y/%m/%d %H:%M:%S")
                    + " UTC ",
                ],
                style={"display": "inline"},
            ),
            html.H6("(%i seconds ago)" % ((maintenant-maintenant_data).seconds + 1), style={'display':'inline'}),
            # html.H6(" (updates every 15 seconds)", style={"display": "inline"}),
        ]
    )

    return [
        platyperps_last_update_1,
        mango_v_drift_by_asset,
        # drift_prices_selected,
        mango_v_drift.to_dict("records"),
        funding_table.to_dict("records"),
        volume_table.to_dict("records"),
        # pd.DataFrame(mango_prices_full).plot(),
    ]
maintenant_data =  datetime.datetime.utcnow()
lock = 0

def get_new_data():
    now = datetime.datetime.utcnow()
    
    global maintenant_data
    global lock
    if lock == 1 and (now - maintenant_data).seconds < 60:
        return

    lock = 1

    global drift
    drift = driftsummary.drift_py()

    global mango_prices_full
    mango_prices_full = get_mango_prices()

    global fida_prices_full
    fida_prices_full = get_fida_prices()

    global drift_prices_full
    drift_prices_full = get_drift_prices(drift)

    f, v, fx = make_funding_table()
    global funding_table
    funding_table = f

    global volume_table
    volume_table = v
    print(volume_table)

    global ftx_px
    ftx_px = fx

    maintenant_data = now

    lock = 0

import time

# def get_new_data_every(period=15):
#     print("get_new_data_every")
#     """Update the data every 'period' seconds"""
#     while True:
#         get_new_data()
#         print("data updated")
#         time.sleep(period)

# def start_multi():
#     executor = ThreadPoolExecutor(max_workers=1)
#     executor.submit(get_new_data_every)

if __name__ == "__main__":
    # start_multi()
    app.run_server(debug=True)
