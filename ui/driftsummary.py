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

# import dash_bootstrap_components as dbc

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
    drift_market_summary.columns = ["FIELD"]+list(MARKET_INDEX_TO_PERP.values())
    return drift_market_summary


import dash_core_components as dcc
import dash_html_components as html


def make_ts(history_df):
    trdf = history_df["trade"].copy().sort_index()
    trdf["user_authority"] = trdf["user_authority"].astype(str)
    duration = trdf["fee"].index[-1] - trdf["fee"].index[0]
    duration = duration.seconds / 60 / 60
    # print(int(duration * 100) / 100, "hours")

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


def make_funding_figs(history_df):
    dfs_to_plt = {}

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
        if (
            dfplt["long_funding_rate"] - dfplt["short_funding_rate"]
        ).abs().sum() <= 1e-6:
            dfplt = dfplt.drop(["short_funding_rate", "long_funding_rate"], axis=1)

        dfs_to_plt[MARKET_INDEX_TO_PERP[marketIndex]] = dfplt.resample("1H").bfill()

    thefig = pd.concat(dfs_to_plt, axis=1)
    thefig.columns = [str(x) for x in thefig.columns]
    figs = [thefig.plot()]
    funding_stats = thefig.tail(24).agg(["mean", "std", "sum"])
    funding_stats = funding_stats.round(5).reset_index()
    last_funding_stats = thefig.tail(1)
    return (figs, funding_stats, last_funding_stats)


def make_deposit_fig(history_df):
    deposits = history_df["deposit"].loc["2021":]
    d = deposits.direction[0]
    assert "deposit" in str(d).lower()
    deposit_ts = (
        deposits.apply(
            lambda x: x["amount"] * -1 if x["direction"] != d else x["amount"], axis=1
        )
        / 1e6
    )
    fig = deposit_ts.sort_index().cumsum().plot()
    return fig


def make_curve_history_df(history_df):
    curvedffull = history_df["curve"].copy().sort_index(ascending=False).reset_index()
    print(curvedffull.columns)

    cost_col = ["total_fee", "total_fee_minus_distributions", "adjustment_cost"]
    peg_col = ["peg_multiplier_before", "peg_multiplier_after"]
    k_col = ["sqrt_k_before", "sqrt_k_after"]
    dd = curvedffull[
        ["ts", "market_index", "open_interest"] + peg_col + k_col + cost_col
    ]

    for col in cost_col:
        dd[col] /= 1e6
        dd[col] = dd[col].round(2)

    for col in k_col:
        dd[col] /= 1e13
        dd[col] = dd[col].round(5)

    for col in peg_col:
        dd[col] /= 1e3
        dd[col] = dd[col].round(3)

    return dd


# for marketIndex in curvedffull.market_index.unique():
#     curvedf = curvedffull[curvedffull.market_index == marketIndex]
#     print(curvedf.columns)
#     cdf = curvedf[['total_fee', 'total_fee_minus_distributions','adjustment_cost']]/1e6
#     fig = cdf.plot(title=MARKET_INDEX_TO_PERP[marketIndex])
#     fig.show()

# card = dbc.Card(
#     dbc.CardBody(
#         [
#             html.H4("Title", id="card-title"),
#             html.H2("100", id="card-value"),
#             html.P("Description", id="card-description"),
#         ]
#     )
# )


def make_drift_summary(drift) -> html.Header:
    """
    Returns a HTML Header element for the application Header.
    :return: HTML Header
    """
    maintenant = datetime.datetime.utcnow()

    history_df = drift_history_df(drift)

    lead_trade_table = make_ts(history_df)
    xx = make_funding_figs(history_df)
    figs = xx[0]
    funding_stats = xx[1]
    last_funding_stats = xx[2].reset_index()
    deposit_fig = make_deposit_fig(history_df)
    curve_df = make_curve_history_df(history_df)

    user_summary_df = drift.user_summary()
    drift_market_summary = drift_market_summary_df(drift)

    drift_m_sum = drift.market_summary().T
    fee_pool_balance = (
        drift_m_sum["total_fee_minus_distributions"] - drift_m_sum["total_fee"] / 2
    )
    drift_fund_rate = (
        (drift_m_sum["last_mark_price_twap"] - drift_m_sum["last_oracle_price_twap"])
    ) / 24
    # drift_fund_rate_pct = drift_fund_rate  / drift_m_sum['last_oracle_price_twap']
    est_fee_pool_funding_revenue = drift_m_sum["base_asset_amount"] * drift_fund_rate
    fee_pool_df = pd.concat(
        {
            "fee_pool": fee_pool_balance,
            "next_est_funding_revenue": est_fee_pool_funding_revenue,
            "last_ts": drift_m_sum["last_mark_price_twap_ts"],
        },
        axis=1,
    ).T.reset_index()
    fee_pool_df.columns = ["FIELD"]+list(MARKET_INDEX_TO_PERP.values())

    fee_pool_df = fee_pool_df.round(2)

    est_next_funding = (
        (
            drift_market_summary.set_index("FIELD").T["last_mark_price_twap"]
            - drift_market_summary.set_index("FIELD").T["last_oracle_price_twap"]
        )
        / drift_market_summary.set_index("FIELD").T["last_oracle_price_twap"]
    ) / 24

    return html.Header(
        children=[
            html.H4("Markets Summary"),
            dash_table.DataTable(
                id="fees-data",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in drift_market_summary.columns
                ],
                data=drift_market_summary.to_dict("records"),
                editable=False,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
                export_format="csv",
            ),
            dash_table.DataTable(
                id="fee-pool",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in fee_pool_df.columns
                ],
                data=fee_pool_df.to_dict("records"),
                editable=False,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10,
                export_format="csv",
            ),
            html.H4("Recent Trader Volume Summary"),
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
            html.H4("Hourly funding rates"),
            html.H5("Last Funding Update"),
            dash_table.DataTable(
                id="last-funding-data",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in last_funding_stats.columns
                ],
                data=last_funding_stats.to_dict("records"),
                editable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=8,
                export_format="csv",
            ),
            html.H5("24h Aggregate Funding Statistics"),
            # pd.DataFrame(est_next_funding).to_html(),
            dash_table.DataTable(
                id="funding-data",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in funding_stats.columns
                ],
                data=funding_stats.to_dict("records"),
                editable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=8,
                export_format="csv",
            ),
            html.Div([dcc.Graph(figure=figX) for figX in figs]),
            html.H4("Trader Leaderboard"),
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
            html.H4("Recent Curve History"),
            dash_table.DataTable(
                id="fees-data",
                columns=[
                    {"name": i, "id": i, "deletable": False, "selectable": True}
                    for i in curve_df.columns
                ],
                data=curve_df.to_dict("records"),
                editable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=8,
                export_format="csv",
                # style_table={
                #     "width": "50%",
                # },
            ),
            html.H4("Recent cumulative deposits (note: total deposits greater)"),
            dcc.Graph(figure=deposit_fig),
        ]
    )
