import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

from ui import header, footer, driftsummary, mangosummary

import requests
import datetime

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)

fees = pd.read_excel("sol-spl-fees.xlsx")


def get_coin_gecko():
    return requests.get(
        "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=solana%2Cbitcoin%2Cethereum&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    ).json()


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
        return [mango_sol_candles, mango_btc_candles, mango_eth_candles]
    except:
        return [[{"price": np.nan, "time": np.nan}] * 2] * 3


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
        return [mango_sol_candles, mango_btc_candles, mango_eth_candles]
    except:
        return [[{"markPrice": np.nan, "time": np.nan}] * 2] * 3


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
        print(market_summary)
        mm = market_summary.set_index("FIELD").loc[
            ["mark_price", "last_mark_price_twap_ts"]
        ]
        mm.index = ["afterPrice", "ts"]
        # mm.columns = [0, 1, 2]
        res = mm.T.to_dict("records")
        print(res[0])
        return res
    except Exception as e:
        print(e)
        return [[{"afterPrice": np.nan, "ts": np.nan}] * 2] * 3


mango_v_drift = pd.DataFrame(
    [["loading..."] * 4] * 4,
    columns=["Protocol", "SOL", "BTC", "ETH"],
)
mango_v_drift["Protocol"] = pd.Series(["Drift", "Mango", "Bonfida", "(CoinGecko)"])

# image_filename = os.getcwd() + "/logo_drift.png"  # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, "rb").read())


app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        header.make_header(),
        dcc.Loading(
            id="loading-1", type="default", children=html.Div(id="loading-output-1")
        ),
        html.Div("loading...", id="tab-content"),
        html.Br(),
        html.Br(),
        html.Br(),
    ]
)


def page_1_layout():
    return html.Div(
        [
            html.Div(
                "last update: ... (updates every 10 seconds)", id="last-update-ts"
            ),
            # html.H6("(updates every 10 seconds)"),
            # html.H1("Protocol Compare"),
            dcc.Interval(
                id="interval-component",
                interval=1 * 7500,
                n_intervals=0,  # in milliseconds
            ),
            html.H5("Overview"),
            html.Div(
                [
                    dash_table.DataTable(
                        id="mango_v_drift_table",
                        columns=[
                            {"name": i, "id": i, "deletable": False, "selectable": True}
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
                        row_deletable=True,
                        selected_columns=[],
                        selected_rows=[],
                        page_action="native",
                        page_current=0,
                        page_size=5,
                    ),
                ],
                style={
                    "max-width": "500px",
                },
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.H5("Price By Asset"),
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
                    html.Div("loading...", id="live-update-text"),
                ],
                style={
                    "max-width": "500px",
                },
            ),
        ]
    )


drift = driftsummary.drift_py()


page_2_layout = html.Div(
    [
        html.H5("Drift Summary"),
        driftsummary.make_drift_summary(drift),
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
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("dropdown", "value"),
    ],
)
def update_metrics(n, selected_value):
    maintenant = datetime.datetime.utcnow()

    global drift
    drift = driftsummary.drift_py()

    mango_prices_full = get_mango_prices()
    fida_prices_full = get_fida_prices()
    drift_prices_full = get_drift_prices(drift)

    drift_prices_selected = None
    rr = None
    style = {"padding": "5px", "fontSize": "16px"}
    coingeckp = get_coin_gecko()
    dds = {}
    for key, val in ({0: "SOL", 1: "BTC", 2: "ETH"}).items():
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
            "{:.2f}".format(drift_price_latest)
            # + "\n (last trade: "
            # + drift_last_trade
            # + ")"
        )

        mango_sol_card = (
            "{:.2f}".format(mango_price_latest["price"])
            # + "\n (last trade: "
            # + mango_last_trade
            # + ")"
        )

        fida_sol_card = (
            "{:.2f}".format(fida_price_latest["markPrice"])
            # + "\n (last trade: "
            # + drift_last_trade
            # + ")"
        )

        coingecko_card1 = [x for x in coingeckp if x["symbol"].lower() == val.lower()][
            0
        ]

        dds[val] = [
            drift_sol_card,
            mango_sol_card,
            fida_sol_card,
            "{:.2f}".format(coingecko_card1["current_price"]),
        ]

        if val in selected_value:
            rr = [
                html.Div(
                    "{}".format(selected_value)
                    + " (coingecko:{:.2f})".format(coingecko_card1["current_price"]),
                ),
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

    mango_v_drift = pd.DataFrame(
        dds,
        index=["Drift", "Mango", "Bonfida", "(CoinGecko)"],
    )

    mango_v_drift.index.name = "Protocol"
    mango_v_drift = mango_v_drift.reset_index()
    # print(mango_v_drift)

    return [
        html.Span(
            [
                html.Code(
                    " last update: " + maintenant.strftime("%Y/%m/%d %H:%M:%S UTC")
                ),
                html.H6("(updates every 10 seconds)"),
            ]
        ),
        rr,
        # drift_prices_selected,
        mango_v_drift.to_dict("records"),
    ]


if __name__ == "__main__":
    app.run_server(debug=True)
