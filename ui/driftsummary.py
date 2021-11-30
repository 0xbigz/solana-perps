import dash
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

sys.path.append("drift-py/")
from drift.drift import Drift, load_config, MARKET_INDEX_TO_PERP


def drift_py():
    USER_AUTHORITY = ""
    drift = Drift(USER_AUTHORITY)
    asyncio.run(drift.load())
    return drift


def drift_history_df(drift):
    history_df = asyncio.run(drift.load_history_df())
    return history_df
    # print(history_df.keys())


def drift_market_summary_df(drift):
    drift_market_summary = drift.market_summary()
    drift_market_summary.columns = drift_market_summary.columns.astype(str)
    drift_market_summary = drift_market_summary
    drift_market_summary = (
        drift_market_summary.drop(["oracle", "market_name", "initialized"], axis=0)
        .reset_index()
        .round(4)
    )
    drift_market_summary.columns = ["FIELD", "SOL-PERP", "BTC-PERP", "ETH-PERP"]
    return drift_market_summary


import dash_core_components as dcc
import dash_html_components as html

drift = drift_py()
history_df = drift_history_df(drift)
drift_market_summary = drift_market_summary_df(drift)


def make_ts():
    trdf = history_df["trade"].copy().sort_index()
    trdf["user_authority"] = trdf["user_authority"].astype(str)
    duration = trdf["fee"].index[-1] - trdf["fee"].index[0]
    duration = duration.seconds / 60 / 60
    print(int(duration * 100) / 100, "hours")

    for x in ["fee", "quote_asset_amount"]:
        trdf[x] /= 1e6
        trdf[x] = trdf[x].round(2)
    for x in ["base_asset_amount"]:
        trdf[x] /= 1e13
    for x in ["mark_price_after", "mark_price_before", "oracle_price"]:
        trdf[x] /= 1e10

    # show volume of traders in 1024 most recent trades
    toshow = (
        trdf.groupby(["user_authority", "market_index"])[
            ["base_asset_amount", "quote_asset_amount", "fee"]
        ]
        .sum()
        .sort_values("fee", ascending=False)
    )
    # calculate interpolated daily fee spend
    toshow["hourly_avg_fee"] = (toshow["fee"] / duration).round(2)

    return toshow.reset_index()


def make_funding_figs():
    frfull = history_df["fundingRate"].sort_index()
    figs = []
    for marketIndex in frfull.market_index.unique():
        fr = frfull[frfull["market_index"] == marketIndex]
        (fr[["oracle_price_twap", "mark_price_twap"]] / 1e10).replace(
            0, np.nan
        ).dropna().plot()
        fr_hand = (
            fr[["oracle_price_twap", "mark_price_twap"]].diff(axis=1) / 1e10
        ).iloc[:, -1].replace(0, np.nan) / 24
        fr_prot = (
            (
                fr[["cumulative_funding_rate_long", "cumulative_funding_rate_short"]]
                / 1e14
            )
            .replace(0, np.nan)
            .diff()
        )
        dfplt = pd.concat([fr_hand, fr_prot], axis=1)
        dfplt = (
            (dfplt * 100)
            .mul(1 / (fr["oracle_price_twap"] / 1e10), axis=0)
            .dropna()
            .tail(7 * 24)
        )

        dfplt = dfplt.rename(
            {
                "cumulative_funding_rate_long": "long_funding_rate",
                "cumulative_funding_rate_short": "short_funding_rate",
                "mark_price_twap": "balanced_funding",
            },
            axis=1,
        )
        figs.append(
            dfplt.plot(title=MARKET_INDEX_TO_PERP[marketIndex] + " funding rate %")
        )
    return figs


def make_deposit_fig():
    deposits = history_df["deposit"].loc["2021":]
    d = deposits.direction[0]
    assert "deposit" in str(d).lower()
    deposit_ts = (
        deposits.apply(
            lambda x: x["amount"] * -1 if x["direction"] != d else x["amount"], axis=1
        )
        / 1e6
    )
    fig = deposit_ts.sort_index().cumsum().plot(title="recent deposits/withdraws")
    return fig


def make_drift_summary() -> html.Header:
    """
    Returns a HTML Header element for the application Header.
    :return: HTML Header
    """

    lead_trade_table = make_ts()
    figs = make_funding_figs()
    user_summary_df = drift.user_summary()

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
        [html.H4("Markets Summary")]
        + [
            dash_table.DataTable(
                id="fees-data",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in drift_market_summary.columns
                ],
                data=drift_market_summary.to_dict("records"),
                editable=True,
                # filter_action="native",
                # sort_action="native",
                # sort_mode="multi",
                # column_selectable="single",
                # row_selectable="multi",
                # row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=8,
                export_format="csv",
            ),
            html.H4("Recent Trader Summary"),
            dash_table.DataTable(
                id="lead_trade_table",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in lead_trade_table.columns
                ],
                style_data={
                    "whiteSpace": "normal",
                    "height": "auto",
                    "lineHeight": "15px",
                },
                data=lead_trade_table.to_dict("records"),
                # editable=True,
                filter_action="native",
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
                export_format="csv",
            ),
            html.H4(
                "Recent cumulative deposits (note: total deposits are likely greater)"
            ),
            dcc.Graph(figure=make_deposit_fig()),
        ]
        + [html.H4("Hourly funding rates")]
        + [dcc.Graph(figure=figX) for figX in figs]
        + [
            html.H4("Trader Live to Date Performance"),
            dash_table.DataTable(
                id="trader_live_to_date",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in user_summary_df.columns
                ],
                style_data={
                    "whiteSpace": "normal",
                    "height": "auto",
                    "lineHeight": "15px",
                },
                data=user_summary_df.to_dict("records"),
                # editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                # column_selectable="single",
                # row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
                export_format="csv",
            ),
        ]
    )
