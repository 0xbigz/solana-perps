import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import requests
import datetime
import base64
import os

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
)

fees = pd.read_excel("sol-spl-fees.xlsx")


def serve_layout():
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


def get_drift_prices():
    drift_p0 = requests.get(
        "https://mainnet-beta.history.drift.trade/trades/marketIndex/0"
    ).json()
    drift_p1 = requests.get(
        "https://mainnet-beta.history.drift.trade/trades/marketIndex/1"
    ).json()
    drift_p2 = requests.get(
        "https://mainnet-beta.history.drift.trade/trades/marketIndex/2"
    ).json()
    return [
        drift_p0["data"]["trades"],
        drift_p1["data"]["trades"],
        drift_p2["data"]["trades"],
    ]


mango_v_drift = pd.DataFrame(
    columns=["Platform", "SOL", "BTC", "ETH"], index=["Drift", "Mango"]
)

# image_filename = os.getcwd() + "/logo_drift.png"  # replace with your own image
# encoded_image = base64.b64encode(open(image_filename, "rb").read())


app = dash.Dash(__name__)
server = app.server

drift_prices = get_drift_prices()

app.layout = html.Div(
    [
        html.A(
            [
                html.Span(
                    [
                        html.Img(
                            src="https://pbs.twimg.com/profile_banners/1388194344390119426/1637877290/1500x500",
                            style={
                                "height": "4%",
                                "width": "4%",
                                "float": "left",
                                "position": "relative",
                                "padding-top": 0,
                                "padding-right": 10,
                            },
                        ),
                    ]
                )
            ],
            href="https://twitter.com/bigz_Pubkey",
        ),
        html.H2("platyperps"),
        html.H4("~comparing perputual swap prices on Solana DEXs~"),
        html.H4("(updates every 5 seconds, please be patient with loads! 🐢 )"),
        dcc.Loading(
            id="loading-1", type="default", children=html.Div(id="loading-output-1")
        ),
        dcc.Interval(
            id="interval-component",
            interval=1 * 5000,
            n_intervals=0,  # in milliseconds
        ),
        html.H5("Overview"),
        dash_table.DataTable(
            id="mango_v_drift_table",
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": True}
                for i in mango_v_drift.columns
            ],
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
        html.Br(),
        html.Br(),
        html.Br(),
        html.H5("By Asset"),
        dcc.Dropdown(
            id="dropdown",
            options=[
                {"label": i, "value": i} for i in ["SOL-PERP", "BTC-PERP", "ETH-PERP"]
            ],
            value="SOL-PERP",
        ),
        html.Div(id="live-update-text"),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H5("FAQ"),
        html.H3("Why are prices different?"),
        html.P(
            "perpetual swaps aren't fungible. you cant take a position on one platform and bring it to another. so the acessibility (drift on closed mainnet) + incentive structures(drift hourly funding rates vs mango continuous) + exchange risk (drift vAMM vs mango clob) will bring prices in line."
        ),
        html.P(
            "prices are currently `last trade`, mango's bid/ask price could be different."
        ),
        html.H3("When funding comparison/strategy explanation?"),
        html.P("soon (tm)"),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H5("Resources"),
        html.H4("readings"),
        html.A(
            "Drift litepaper (wip)",
            href="https://foregoing-script-fd0.notion.site/Drift-s-dAMM-ff154003aedb4efa83d6e7f4440cd4ab",
        ),
        html.Br(),
        html.A(
            "Mango litepaper",
            href="https://docs.mango.markets/litepaper",
        ),
        html.H4("sdk:"),
        html.A(
            "mango-explorer (python) ",
            href="https://github.com/blockworks-foundation/mango-explorer",
        ),
        html.Br(),
        html.A("drift-py (python)", href="https://github.com/drift-labs/drift-py"),
        html.H4("open source bots:"),
        html.A(
            "drifting-mango (chenwainuo)",
            href="https://github.com/chenwainuo/drifting-mango",
        )
        # html.Img(src=app.get_asset_url("logo_mango.svg")),
        # html.Img(src="data:image/png;base64,{}".format(encoded_image))
        # dash_table.DataTable(
        #     id="live_table",
        #     columns=[
        #         {"name": i, "id": i, "deletable": False, "selectable": True}
        #         for i in drift_prices[0][0].keys()
        #     ],
        #     data=drift_prices[0],
        #     # editable=True,
        #     # filter_action="native",
        #     sort_action="native",
        #     sort_mode="multi",
        #     column_selectable="single",
        #     row_selectable="multi",
        #     # row_deletable=True,
        #     selected_columns=[],
        #     selected_rows=[],
        #     page_action="native",
        #     page_current=0,
        #     page_size=5,
        # ),
        # html.H1("Mango SOL-PERP: " + str(serve_layout()["price"])),
        # html.Div(id="display-value"),
        # dash_table.DataTable(
        #     id="datatable-interactivity",
        #     columns=[
        #         {"name": i, "id": i, "deletable": False, "selectable": True}
        #         for i in df.columns
        #     ],
        #     data=df.to_dict("records"),
        #     editable=True,
        #     filter_action="native",
        #     sort_action="native",
        #     sort_mode="multi",
        #     column_selectable="single",
        #     row_selectable="multi",
        #     row_deletable=True,
        #     selected_columns=[],
        #     selected_rows=[],
        #     page_action="native",
        #     page_current=0,
        #     page_size=10,
        # ),
        # dash_table.DataTable(
        #     id="fees-data",
        #     columns=[
        #         {"name": i, "id": i, "deletable": False, "selectable": True}
        #         for i in fees.columns
        #     ],
        #     data=fees.to_dict("records"),
        #     editable=True,
        #     filter_action="native",
        #     sort_action="native",
        #     sort_mode="multi",
        #     column_selectable="single",
        #     row_selectable="multi",
        #     row_deletable=True,
        #     selected_columns=[],
        #     selected_rows=[],
        #     page_action="native",
        #     page_current=0,
        #     page_size=10,
        # ),
        # html.Div(id="datatable-interactivity-container"),
    ]
)


@app.callback(
    [
        Output("live-update-text", "children"),
        # Output("live_table", "data"),
        Output("mango_v_drift_table", "data"),
    ],
    [Input("interval-component", "n_intervals"), Input("dropdown", "value")],
)
def update_metrics(n, selected_value):
    maintenant = datetime.datetime.utcnow()

    mango_prices_full = serve_layout()
    drift_prices_full = get_drift_prices()

    drift_prices_selected = None
    rr = None
    style = {"padding": "5px", "fontSize": "16px"}

    dds = {}
    for key, val in ({0: "SOL", 1: "BTC", 2: "ETH"}).items():
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

        drift_price_latest = drift_prices[0]["afterPrice"]
        drift_price_change = drift_price_latest - drift_prices[1]["afterPrice"]
        drift_last_trade = (
            str(
                (maintenant - pd.to_datetime(drift_prices[0]["ts"] * 1e6)).seconds
            ).split(".")[0]
            + " seconds ago"
        )

        drift_sol_card = (
            str(round(drift_price_latest, 1))
            # + "\n (last trade: "
            # + drift_last_trade
            # + ")"
        )

        mango_sol_card = (
            str(round(mango_price_latest["price"], 1))
            # + "\n (last trade: "
            # + mango_last_trade
            # + ")"
        )
        dds[val] = [
            drift_sol_card,
            mango_sol_card,
        ]

        if val in selected_value:
            rr = [
                html.Div("prices for {}:".format(selected_value)),
                html.Br(),
                html.Img(
                    src="static/logo_drift.png",
                    style={
                        "height": "45px",
                        # "width": "2%",
                        "float": "left",
                        "position": "relative",
                        "padding-right": 10,
                    },
                ),
                html.Code(
                    "Drift Price: {0:.2f}".format(drift_price_latest), style=style
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
                    src="static/logo_mango.png",
                    style={
                        "height": "45px",
                        # "width": "22%",
                        "float": "left",
                        "position": "relative",
                        "padding-top": 0,
                        "padding-right": 10,
                    },
                ),
                html.Code(
                    "Mango Price: {0:.2f}".format(mango_price_latest["price"]),
                    style=style,
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
                # html.H4("Recent Drift Trades:"),
            ]

            drift_prices_selected = drift_prices

    mango_v_drift = pd.DataFrame(
        dds,
        index=["Drift", "Mango"],
    )

    mango_v_drift.index.name = "Platform"
    mango_v_drift = mango_v_drift.reset_index()
    # print(mango_v_drift)

    return [
        rr,
        # drift_prices_selected,
        mango_v_drift.to_dict("records"),
    ]


# @app.callback(
#     Output("datatable-interactivity", "style_data_conditional"),
#     Input("datatable-interactivity", "selected_columns"),
# )
# def update_styles(selected_columns):
#     return [
#         {"if": {"column_id": i}, "background_color": "#D2F3FF"}
#         for i in selected_columns
#     ]


# @app.callback(
#     Output("datatable-interactivity-container", "children"),
#     Input("datatable-interactivity", "derived_virtual_data"),
#     Input("datatable-interactivity", "derived_virtual_selected_rows"),
# )
# def update_graphs(rows, derived_virtual_selected_rows):
#     # When the table is first rendered, `derived_virtual_data` and
#     # `derived_virtual_selected_rows` will be `None`. This is due to an
#     # idiosyncrasy in Dash (unsupplied properties are always None and Dash
#     # calls the dependent callbacks when the component is first rendered).
#     # So, if `rows` is `None`, then the component was just rendered
#     # and its value will be the same as the component's dataframe.
#     # Instead of setting `None` in here, you could also set
#     # `derived_virtual_data=df.to_rows('dict')` when you initialize
#     # the component.
#     if derived_virtual_selected_rows is None:
#         derived_virtual_selected_rows = []

#     dff = df if rows is None else pd.DataFrame(rows)

#     colors = [
#         "#7FDBFF" if i in derived_virtual_selected_rows else "#0074D9"
#         for i in range(len(dff))
#     ]

#     return [
#         dcc.Graph(
#             id=column,
#             figure={
#                 "data": [
#                     {
#                         "x": dff["country"],
#                         "y": dff[column],
#                         "type": "bar",
#                         "marker": {"color": colors},
#                     }
#                 ],
#                 "layout": {
#                     "xaxis": {"automargin": True},
#                     "yaxis": {"automargin": True, "title": {"text": column}},
#                     "height": 250,
#                     "margin": {"t": 10, "l": 10, "r": 10},
#                 },
#             },
#         )
#         # check if column exists - user may have deleted it
#         # If `column.deletable=False`, then you don't
#         # need to do this check.
#         for column in ["pop", "lifeExp", "gdpPercap"]
#         if column in dff
#     ]


if __name__ == "__main__":
    app.run_server(debug=True)
