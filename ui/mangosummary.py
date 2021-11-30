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


def stream_pyth(market="BTC/USDC"):
    # Load the market
    stub = context.market_lookup.find_by_symbol(market)
    market = mango.ensure_market_loaded(context, stub)

    pyth = mango.create_oracle_provider(context, "pyth")
    pyth_mkt = pyth.oracle_for_market(context, market)
    return pyth_mkt


def load_mango_data(market="SOL-PERP"):
    # Create a 'devnet' Context
    context = mango.ContextBuilder.build(cluster_name="mainnet")

    # # Load the market
    # stub = context.market_lookup.find_by_symbol(market)
    # market = mango.ensure_market_loaded(context, stub)
    # market_operations = mango.create_market_operations(
    #     context, wallet, account, market, dry_run=False
    # )
    # ob = market_operations.load_orderbook()

    # bb = ob.asks[0]
    # return (bb.price, bb.quantity)


import dash_core_components as dcc
import dash_html_components as html


pyth_loader = stream_pyth()


def make_pyth_summary() -> html.Header:
    pythprice = pyth_loader.fetch_price(context)
    pythstr = ": {:.2f} ± {:.2f}".format(
        float(pythprice.mid_price), float(pythprice.confidence)
    )

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
