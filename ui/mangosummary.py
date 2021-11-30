from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

pd.options.plotting.backend = "plotly"
from ui import header

import requests
import datetime
import base64
import os
import asyncio


import sys

sys.path.append("mango-explorer/")
import decimal
import mango
import os
import time
import dash
import mango
import threading

context = mango.ContextBuilder.build(cluster_name="mainnet")


def stream_pyth(market="SOL/USDC"):
    # Load the market
    stub = context.market_lookup.find_by_symbol(market)
    market = mango.ensure_market_loaded(context, stub)

    pyth = mango.create_oracle_provider(context, "pyth")
    pyth_mkt = pyth.oracle_for_market(context, market)
    return pyth_mkt


def load_mango_data(market="SOL-PERP"):
    # Find the addresses associated with the Perp market
    perp_stub = context.market_lookup.find_by_symbol("perp:" + market)

    # Load the rest of the on-chain metadata of the market
    perp_market = mango.ensure_market_loaded(context, perp_stub)
    # z = perp_market.fetch_funding(context)
    return perp_market
    # bb = ob.asks[0]
    # return (bb.price, bb.quantity)


import dash_core_components as dcc
import dash_html_components as html


pyth_loader = stream_pyth()


def make_pyth_summary() -> html.Header:

    maintenant = datetime.datetime.utcnow()

    MARKET = "SOL-PERP"
    pythprice = pyth_loader.fetch_price(MARKET.split("-")[0] + "/USDC")
    pythstr = ": {:.2f} ± {:.2f}".format(
        float(pythprice.mid_price), float(pythprice.confidence)
    )
    perp_market = load_mango_data(MARKET)
    z = perp_market.fetch_funding(context)

    return html.Header(
        children=
        # Icon and title container
        # html.Div(
        #     className="dash-title-container",
        #     children=[
        #         html.Img(className="dash-icon", src="assets/img/ship-1.svg"),
        #         html.H1(className="dash-title", children=["Dash ports analytics"]),
        #     ],
        # ),
        [
            html.Code(
                [
                    html.Code(
                        "last update: "
                        + maintenant.strftime("%Y/%m/%d: %H:%M:%S")
                        + " UTC"
                    ),
                    html.Br(),
                    """#BIG TODO HERE#""",
                    html.Br(),
                    html.Span(
                        [
                            html.A(
                                "pyth",
                                href="https://pyth.network/markets/?cluster=mainnet-beta#BTC/USD",
                                target="_",
                            ),
                            pythstr,
                        ]
                    ),
                    html.Br(),
                    html.Code(z.rate),
                ]
            ),
        ]
    )
    # [
    #     dash_table.DataTable(
    #         id="fees-data",
    #         columns=[
    #             {"name": i, "id": i, "deletable": False, "selectable": True}
    #             for i in drift_market_summary.columns
    #         ],
    #         data=drift_market_summary.to_dict("records"),
    #         editable=True,
    #         # filter_action="native",
    #         # sort_action="native",
    #         # sort_mode="multi",
    #         # column_selectable="single",
    #         # row_selectable="multi",
    #         # row_deletable=True,
    #         selected_columns=[],
    #         selected_rows=[],
    #         page_action="native",
    #         page_current=0,
    #         page_size=8,
    #         export_format="csv",
    #     ),
    # ]


def make_mango_summary() -> html.Header:

    return html.Header()
