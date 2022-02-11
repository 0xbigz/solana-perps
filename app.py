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
        mango_luna_candles = requests.get(
            "https://event-history-api-candles.herokuapp.com/trades/address/BCJrpvsB2BJtqiDgKVC4N6gyX1y24Jz96C6wMraYmXss"
            ).json()["data"]
        mango_avax_candles = requests.get(
        'https://event-history-api-candles.herokuapp.com/trades/address/EAC7jtzsoQwCbXj1M3DapWrNLnc3MBwXAarvWDPr2ZV9'
        ).json()["data"]
        mango_bnb_candles = requests.get(
            'https://event-history-api-candles.herokuapp.com/trades/address/CqxX2QupYiYafBSbA519j4vRVxxecidbh2zwX66Lmqem'
        ).json()["data"]
        mango_srm_candles = requests.get(
            'https://event-history-api-candles.herokuapp.com/trades/address/4GkJj2znAr2pE2PBbak66E12zjCs2jkmeafiJwDVM9Au'
        ).json()["data"]
        mango_ada_candles = requests.get(
            'https://event-history-api-candles.herokuapp.com/trades/address/Bh9UENAncoTEwE7NDim8CdeM1GPvw6xAT4Sih2rKVmWB'
        ).json()["data"]
        mango_ftt_candles = requests.get(
            'https://event-history-api-candles.herokuapp.com/trades/address/AhgEayEGNw46ALHuC5ASsKyfsJzAm5JY8DWqpGMQhcGC'
        ).json()["data"]
        return [mango_sol_candles, mango_btc_candles, mango_eth_candles] \
        + [mango_luna_candles, mango_avax_candles, mango_bnb_candles]\
        + ([[{"price": np.nan, "time": np.nan}] * 2] * 3)\
        + [mango_ada_candles]\
        + ([[{"price": np.nan, "time": np.nan}] * 2] * 1)\
        + [mango_ftt_candles]\
        + [mango_srm_candles]
    except:
        return [[{"price": np.nan, "time": np.nan}] * 2] * 11


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
        return [mango_sol_candles, mango_btc_candles, mango_eth_candles]+[[{"markPrice": np.nan, "time": 0}] * 2] * 17
    except:
        return [[{"markPrice": np.nan, "time": 0}] * 2] * 15


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
        return [[{"afterPrice": np.nan, "ts": np.nan}] * 2] * 11



mango_v_drift = pd.DataFrame(
    [["loading..."] * 4] * 4,
    columns=["Protocol", "SOL", "BTC", "ETH"],
)
mango_v_drift["Protocol"] = pd.Series(["(FTX)", "Mango", "Drift", "Bonfida"])
ftx_funds = [{
    "success": False,
    "result": {
        "volume": np.nan,
        "nextFundingRate": np.nan,
        "nextFundingTime": "2021-12-03T21:00:00+00:00",
        "openInterest": np.nan,
    },
}]*5

dydx_data = {"markets":{"BTC-USD":{"market":"BTC-USD","status":"ONLINE","baseAsset":"BTC","quoteAsset":"USD","stepSize":"0.0001","tickSize":"1","indexPrice":"42968.3170","oraclePrice":"42922.8550","priceChange24H":"-1203.984000","nextFundingRate":"0.0000037402","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.001","type":"PERPETUAL","initialMarginFraction":"0.05","maintenanceMarginFraction":"0.03","volume24H":"1640902107.353700","trades24H":"198273","openInterest":"5439.2241","incrementalInitialMarginFraction":"0.01","incrementalPositionSize":"1.5","maxPositionSize":"170","baselinePositionSize":"9","assetResolution":"10000000000","syntheticAssetId":"0x4254432d3130000000000000000000"},"SUSHI-USD":{"market":"SUSHI-USD","status":"ONLINE","baseAsset":"SUSHI","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"4.3138","oraclePrice":"4.3110","priceChange24H":"-0.428218","nextFundingRate":"-0.0000052310","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3506719.908000","trades24H":"1828","openInterest":"3046758.4","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"10000","maxPositionSize":"491000","baselinePositionSize":"49200","assetResolution":"10000000","syntheticAssetId":"0x53555348492d370000000000000000"},"AVAX-USD":{"market":"AVAX-USD","status":"ONLINE","baseAsset":"AVAX","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"88.9606","oraclePrice":"88.9100","priceChange24H":"-0.359377","nextFundingRate":"0.0000111770","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"77383612.420000","trades24H":"21226","openInterest":"526110.3","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1800","maxPositionSize":"91000","baselinePositionSize":"9000","assetResolution":"10000000","syntheticAssetId":"0x415641582d37000000000000000000"},"1INCH-USD":{"market":"1INCH-USD","status":"ONLINE","baseAsset":"1INCH","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.7700","oraclePrice":"1.7675","priceChange24H":"-0.146723","nextFundingRate":"-0.0000463210","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3227348.146000","trades24H":"2211","openInterest":"6173663","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"35000","maxPositionSize":"1700000","baselinePositionSize":"170000","assetResolution":"10000000","syntheticAssetId":"0x31494e43482d370000000000000000"},"ETH-USD":{"market":"ETH-USD","status":"ONLINE","baseAsset":"ETH","quoteAsset":"USD","stepSize":"0.001","tickSize":"0.1","indexPrice":"3023.8912","oraclePrice":"3019.3671","priceChange24H":"-206.026197","nextFundingRate":"-0.0000115577","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.01","type":"PERPETUAL","initialMarginFraction":"0.05","maintenanceMarginFraction":"0.03","volume24H":"1357856566.385000","trades24H":"172305","openInterest":"88254.870","incrementalInitialMarginFraction":"0.01","incrementalPositionSize":"28","maxPositionSize":"2820","baselinePositionSize":"140","assetResolution":"1000000000","syntheticAssetId":"0x4554482d3900000000000000000000"},"XMR-USD":{"market":"XMR-USD","status":"ONLINE","baseAsset":"XMR","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"177.1264","oraclePrice":"176.7150","priceChange24H":"-8.281115","nextFundingRate":"-0.0000066527","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"1165485.516000","trades24H":"1225","openInterest":"23382.55","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"200","maxPositionSize":"6000","baselinePositionSize":"400","assetResolution":"100000000","syntheticAssetId":"0x584d522d3800000000000000000000"},"COMP-USD":{"market":"COMP-USD","status":"ONLINE","baseAsset":"COMP","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"131.2077","oraclePrice":"131.2000","priceChange24H":"-13.361681","nextFundingRate":"-0.0000062885","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4050490.079000","trades24H":"2469","openInterest":"65502.97","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"330","maxPositionSize":"16600","baselinePositionSize":"1700","assetResolution":"100000000","syntheticAssetId":"0x434f4d502d38000000000000000000"},"ALGO-USD":{"market":"ALGO-USD","status":"ONLINE","baseAsset":"ALGO","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"0.9551","oraclePrice":"0.9540","priceChange24H":"-0.076083","nextFundingRate":"-0.0000072367","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3987185.189000","trades24H":"3157","openInterest":"7702958","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"55000","maxPositionSize":"2700000","baselinePositionSize":"275000","assetResolution":"1000000","syntheticAssetId":"0x414c474f2d36000000000000000000"},"BCH-USD":{"market":"BCH-USD","status":"ONLINE","baseAsset":"BCH","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"333.8701","oraclePrice":"332.5600","priceChange24H":"-10.949868","nextFundingRate":"-0.0000058063","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"12794211.979000","trades24H":"3159","openInterest":"39548.67","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"170","maxPositionSize":"8300","baselinePositionSize":"840","assetResolution":"100000000","syntheticAssetId":"0x4243482d3800000000000000000000"},"CRV-USD":{"market":"CRV-USD","status":"ONLINE","baseAsset":"CRV","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"3.1460","oraclePrice":"3.1500","priceChange24H":"-0.325781","nextFundingRate":"-0.0000258473","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"11792139.878000","trades24H":"4266","openInterest":"9059504","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"37000","maxPositionSize":"1900000","baselinePositionSize":"190000","assetResolution":"1000000","syntheticAssetId":"0x4352562d3600000000000000000000"},"UNI-USD":{"market":"UNI-USD","status":"ONLINE","baseAsset":"UNI","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"11.2410","oraclePrice":"11.2600","priceChange24H":"-1.009000","nextFundingRate":"0.0000022992","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"5207393.784800","trades24H":"2928","openInterest":"1311918.6","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"4000","maxPositionSize":"210000","baselinePositionSize":"20800","assetResolution":"10000000","syntheticAssetId":"0x554e492d3700000000000000000000"},"MKR-USD":{"market":"MKR-USD","status":"ONLINE","baseAsset":"MKR","quoteAsset":"USD","stepSize":"0.001","tickSize":"1","indexPrice":"2073.8600","oraclePrice":"2074.2074","priceChange24H":"-166.270000","nextFundingRate":"0.0000125000","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.01","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4563864.002000","trades24H":"704","openInterest":"8164.437","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"40","maxPositionSize":"2000","baselinePositionSize":"200","assetResolution":"1000000000","syntheticAssetId":"0x4d4b522d3900000000000000000000"},"LTC-USD":{"market":"LTC-USD","status":"ONLINE","baseAsset":"LTC","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"131.7110","oraclePrice":"131.6400","priceChange24H":"-7.459234","nextFundingRate":"-0.0000227146","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"11217188.737000","trades24H":"3652","openInterest":"180424.74","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"560","maxPositionSize":"28000","baselinePositionSize":"2800","assetResolution":"100000000","syntheticAssetId":"0x4c54432d3800000000000000000000"},"EOS-USD":{"market":"EOS-USD","status":"ONLINE","baseAsset":"EOS","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"2.5220","oraclePrice":"2.5174","priceChange24H":"-0.147346","nextFundingRate":"0.0000057040","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3012338.275000","trades24H":"2513","openInterest":"6094188","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"22000","maxPositionSize":"1100000","baselinePositionSize":"110000","assetResolution":"1000000","syntheticAssetId":"0x454f532d3600000000000000000000"},"DOGE-USD":{"market":"DOGE-USD","status":"ONLINE","baseAsset":"DOGE","quoteAsset":"USD","stepSize":"10","tickSize":"0.0001","indexPrice":"0.1496","oraclePrice":"0.1497","priceChange24H":"-0.009766","nextFundingRate":"-0.0000114947","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"100","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"9073625.550000","trades24H":"3914","openInterest":"137332630","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"400000","maxPositionSize":"22000000","baselinePositionSize":"2180000","assetResolution":"100000","syntheticAssetId":"0x444f47452d35000000000000000000"},"ATOM-USD":{"market":"ATOM-USD","status":"ONLINE","baseAsset":"ATOM","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"28.4932","oraclePrice":"28.5340","priceChange24H":"-2.035984","nextFundingRate":"-0.0000487751","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"24370439.887000","trades24H":"9426","openInterest":"1104803.0","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3000","maxPositionSize":"158000","baselinePositionSize":"16000","assetResolution":"10000000","syntheticAssetId":"0x41544f4d2d37000000000000000000"},"ZRX-USD":{"market":"ZRX-USD","status":"ONLINE","baseAsset":"ZRX","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"0.6598","oraclePrice":"0.6592","priceChange24H":"-0.048451","nextFundingRate":"-0.0000070338","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"12594556.282000","trades24H":"4099","openInterest":"11586619","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"100000","maxPositionSize":"5000000","baselinePositionSize":"500000","assetResolution":"1000000","syntheticAssetId":"0x5a52582d3600000000000000000000"},"SOL-USD":{"market":"SOL-USD","status":"ONLINE","baseAsset":"SOL","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"104.7960","oraclePrice":"104.9100","priceChange24H":"-8.894022","nextFundingRate":"-0.0000309724","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"54186410.727700","trades24H":"18151","openInterest":"436082.0","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"700","maxPositionSize":"34900","baselinePositionSize":"3400","assetResolution":"10000000","syntheticAssetId":"0x534f4c2d3700000000000000000000"},"UMA-USD":{"market":"UMA-USD","status":"ONLINE","baseAsset":"UMA","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"6.1678","oraclePrice":"6.1647","priceChange24H":"-0.452454","nextFundingRate":"-0.0000293797","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4689780.373000","trades24H":"4477","openInterest":"281698.9","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1000","maxPositionSize":"30000","baselinePositionSize":"2000","assetResolution":"10000000","syntheticAssetId":"0x554d412d3700000000000000000000"},"AAVE-USD":{"market":"AAVE-USD","status":"ONLINE","baseAsset":"AAVE","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.01","indexPrice":"173.6709","oraclePrice":"173.2700","priceChange24H":"-13.491902","nextFundingRate":"-0.0000076472","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"6094287.667100","trades24H":"1984","openInterest":"87170.52","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"300","maxPositionSize":"17000","baselinePositionSize":"1700","assetResolution":"100000000","syntheticAssetId":"0x414156452d38000000000000000000"},"ADA-USD":{"market":"ADA-USD","status":"ONLINE","baseAsset":"ADA","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.1307","oraclePrice":"1.1290","priceChange24H":"-0.057525","nextFundingRate":"-0.0000056476","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"8670745.789000","trades24H":"3557","openInterest":"17945971","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"46000","maxPositionSize":"2300000","baselinePositionSize":"230000","assetResolution":"1000000","syntheticAssetId":"0x4144412d3600000000000000000000"},"SNX-USD":{"market":"SNX-USD","status":"ONLINE","baseAsset":"SNX","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"5.1717","oraclePrice":"5.1720","priceChange24H":"-0.623267","nextFundingRate":"0.0000052792","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4324102.723000","trades24H":"2399","openInterest":"2694507.9","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"11000","maxPositionSize":"520000","baselinePositionSize":"52000","assetResolution":"10000000","syntheticAssetId":"0x534e582d3700000000000000000000"},"FIL-USD":{"market":"FIL-USD","status":"ONLINE","baseAsset":"FIL","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"22.7821","oraclePrice":"22.7500","priceChange24H":"-1.163894","nextFundingRate":"-0.0000161504","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"6352160.834000","trades24H":"3903","openInterest":"478499.1","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1400","maxPositionSize":"68000","baselinePositionSize":"6800","assetResolution":"10000000","syntheticAssetId":"0x46494c2d3700000000000000000000"},"ZEC-USD":{"market":"ZEC-USD","status":"ONLINE","baseAsset":"ZEC","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"122.0400","oraclePrice":"121.7926","priceChange24H":"-4.200376","nextFundingRate":"0.0000006253","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3243018.921000","trades24H":"2368","openInterest":"55010.85","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"100","maxPositionSize":"3000","baselinePositionSize":"200","assetResolution":"100000000","syntheticAssetId":"0x5a45432d3800000000000000000000"},"YFI-USD":{"market":"YFI-USD","status":"ONLINE","baseAsset":"YFI","quoteAsset":"USD","stepSize":"0.0001","tickSize":"1","indexPrice":"24236.5076","oraclePrice":"24199.5000","priceChange24H":"-1797.362365","nextFundingRate":"-0.0000064895","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.001","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4466618.461300","trades24H":"2223","openInterest":"744.6725","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3","maxPositionSize":"140","baselinePositionSize":"14","assetResolution":"10000000000","syntheticAssetId":"0x5946492d3130000000000000000000"},"LINK-USD":{"market":"LINK-USD","status":"ONLINE","baseAsset":"LINK","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"17.2721","oraclePrice":"17.2700","priceChange24H":"-1.217733","nextFundingRate":"-0.0000145151","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"7246391.294400","trades24H":"3673","openInterest":"1087769.4","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3900","maxPositionSize":"200000","baselinePositionSize":"20000","assetResolution":"10000000","syntheticAssetId":"0x4c494e4b2d37000000000000000000"},"DOT-USD":{"market":"DOT-USD","status":"ONLINE","baseAsset":"DOT","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"20.2224","oraclePrice":"20.1624","priceChange24H":"-1.618407","nextFundingRate":"-0.0000241039","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"9136465.054000","trades24H":"6092","openInterest":"1561849.2","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"2900","maxPositionSize":"150000","baselinePositionSize":"14600","assetResolution":"10000000","syntheticAssetId":"0x444f542d3700000000000000000000"},"MATIC-USD":{"market":"MATIC-USD","status":"ONLINE","baseAsset":"MATIC","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.8393","oraclePrice":"1.8368","priceChange24H":"-0.188705","nextFundingRate":"-0.0000233629","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"36449333.021000","trades24H":"11703","openInterest":"18980542","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"80000","maxPositionSize":"4000000","baselinePositionSize":"410000","assetResolution":"1000000","syntheticAssetId":"0x4d415449432d360000000000000000"}}}

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

# import dash_bootstrap_components as dbc
app = dash.Dash(__name__)#, external_stylesheets=[dbc.themes.ZEPHYR])
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
    # drift_markets = {v: str(k) for k,v in driftsummary.MARKET_INDEX_TO_PERP.items()}
    ASSETS=[]
    for x in range(len(list(driftsummary.MARKET_INDEX_TO_PERP.values()))):
        ASSETS.append(driftsummary.MARKET_INDEX_TO_PERP[x].split('-')[0])
        #("SOL", "BTC", "ETH", "LUNA", "AVAX", "BNB", "MATIC")
    print(ASSETS)
    assert(ASSETS[0]=='SOL')

    EXTRAS = ['SRM']
    for extra in EXTRAS:
        ASSETS.append(extra)
    
    # import requests
    def load_mango_data(market="SOL-PERP"):
        # Find the addresses associated with the Perp market
        perp_stub = context.market_lookup.find_by_symbol("perp:" + market)
        # Load the rest of the on-chain metadata of the market
        perp_market = mango.ensure_market_loaded(context, perp_stub)
        # z = perp_market.fetch_funding(context)
        return perp_market
    

    mango_markets = {
        "BTC": "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        "SOL": "2TgaaVoHgnSeEtXvWTx13zQeTf4hYWAMEiMQdcG6EwHi",
        "ETH": "DVXWg6mfwFvHQbGyaHke4h3LE9pSkgbooDSDgA4JBC8d",
        "LUNA": "BCJrpvsB2BJtqiDgKVC4N6gyX1y24Jz96C6wMraYmXss",
        "AVAX": "EAC7jtzsoQwCbXj1M3DapWrNLnc3MBwXAarvWDPr2ZV9",
        "BNB": "CqxX2QupYiYafBSbA519j4vRVxxecidbh2zwX66Lmqem",
        'SRM': "4GkJj2znAr2pE2PBbak66E12zjCs2jkmeafiJwDVM9Au",
        'RAY': "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        'MNGO': "DtEcjPLyD4YtTBB4q8xwFZ9q49W89xZCZtJyrGebi5t8",
        'ADA': "Bh9UENAncoTEwE7NDim8CdeM1GPvw6xAT4Sih2rKVmWB",
        'FTT': "AhgEayEGNw46ALHuC5ASsKyfsJzAm5JY8DWqpGMQhcGC",
    }
    mango_fund_rate = [np.nan]*len(ASSETS)
    mango_oi = [np.nan]*len(ASSETS)
    try:
        for i,x in enumerate((ASSETS)):
            if x in mango_markets.keys():
                mfund = load_mango_data(x+"-PERP")
                if mfund is not None:
                    mango_fund_rate[i] = mfund.fetch_funding(context).rate
                    mango_oi[i] = mfund.fetch_funding(context).open_interest
    except:
        pass


    try:
        dydx_url = 'https://api.dydx.exchange/v3/markets'
        global dydx_data
        dydx_data = requests.get(dydx_url).json()
    except:
        dydx_data = {"markets":{"BTC-USD":{"market":"BTC-USD","status":"ONLINE","baseAsset":"BTC","quoteAsset":"USD","stepSize":"0.0001","tickSize":"1","indexPrice":"42968.3170","oraclePrice":"42922.8550","priceChange24H":"-1203.984000","nextFundingRate":"0.0000037402","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.001","type":"PERPETUAL","initialMarginFraction":"0.05","maintenanceMarginFraction":"0.03","volume24H":"1640902107.353700","trades24H":"198273","openInterest":"5439.2241","incrementalInitialMarginFraction":"0.01","incrementalPositionSize":"1.5","maxPositionSize":"170","baselinePositionSize":"9","assetResolution":"10000000000","syntheticAssetId":"0x4254432d3130000000000000000000"},"SUSHI-USD":{"market":"SUSHI-USD","status":"ONLINE","baseAsset":"SUSHI","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"4.3138","oraclePrice":"4.3110","priceChange24H":"-0.428218","nextFundingRate":"-0.0000052310","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3506719.908000","trades24H":"1828","openInterest":"3046758.4","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"10000","maxPositionSize":"491000","baselinePositionSize":"49200","assetResolution":"10000000","syntheticAssetId":"0x53555348492d370000000000000000"},"AVAX-USD":{"market":"AVAX-USD","status":"ONLINE","baseAsset":"AVAX","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"88.9606","oraclePrice":"88.9100","priceChange24H":"-0.359377","nextFundingRate":"0.0000111770","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"77383612.420000","trades24H":"21226","openInterest":"526110.3","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1800","maxPositionSize":"91000","baselinePositionSize":"9000","assetResolution":"10000000","syntheticAssetId":"0x415641582d37000000000000000000"},"1INCH-USD":{"market":"1INCH-USD","status":"ONLINE","baseAsset":"1INCH","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.7700","oraclePrice":"1.7675","priceChange24H":"-0.146723","nextFundingRate":"-0.0000463210","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3227348.146000","trades24H":"2211","openInterest":"6173663","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"35000","maxPositionSize":"1700000","baselinePositionSize":"170000","assetResolution":"10000000","syntheticAssetId":"0x31494e43482d370000000000000000"},"ETH-USD":{"market":"ETH-USD","status":"ONLINE","baseAsset":"ETH","quoteAsset":"USD","stepSize":"0.001","tickSize":"0.1","indexPrice":"3023.8912","oraclePrice":"3019.3671","priceChange24H":"-206.026197","nextFundingRate":"-0.0000115577","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.01","type":"PERPETUAL","initialMarginFraction":"0.05","maintenanceMarginFraction":"0.03","volume24H":"1357856566.385000","trades24H":"172305","openInterest":"88254.870","incrementalInitialMarginFraction":"0.01","incrementalPositionSize":"28","maxPositionSize":"2820","baselinePositionSize":"140","assetResolution":"1000000000","syntheticAssetId":"0x4554482d3900000000000000000000"},"XMR-USD":{"market":"XMR-USD","status":"ONLINE","baseAsset":"XMR","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"177.1264","oraclePrice":"176.7150","priceChange24H":"-8.281115","nextFundingRate":"-0.0000066527","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"1165485.516000","trades24H":"1225","openInterest":"23382.55","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"200","maxPositionSize":"6000","baselinePositionSize":"400","assetResolution":"100000000","syntheticAssetId":"0x584d522d3800000000000000000000"},"COMP-USD":{"market":"COMP-USD","status":"ONLINE","baseAsset":"COMP","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"131.2077","oraclePrice":"131.2000","priceChange24H":"-13.361681","nextFundingRate":"-0.0000062885","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4050490.079000","trades24H":"2469","openInterest":"65502.97","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"330","maxPositionSize":"16600","baselinePositionSize":"1700","assetResolution":"100000000","syntheticAssetId":"0x434f4d502d38000000000000000000"},"ALGO-USD":{"market":"ALGO-USD","status":"ONLINE","baseAsset":"ALGO","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"0.9551","oraclePrice":"0.9540","priceChange24H":"-0.076083","nextFundingRate":"-0.0000072367","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3987185.189000","trades24H":"3157","openInterest":"7702958","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"55000","maxPositionSize":"2700000","baselinePositionSize":"275000","assetResolution":"1000000","syntheticAssetId":"0x414c474f2d36000000000000000000"},"BCH-USD":{"market":"BCH-USD","status":"ONLINE","baseAsset":"BCH","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"333.8701","oraclePrice":"332.5600","priceChange24H":"-10.949868","nextFundingRate":"-0.0000058063","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"12794211.979000","trades24H":"3159","openInterest":"39548.67","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"170","maxPositionSize":"8300","baselinePositionSize":"840","assetResolution":"100000000","syntheticAssetId":"0x4243482d3800000000000000000000"},"CRV-USD":{"market":"CRV-USD","status":"ONLINE","baseAsset":"CRV","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"3.1460","oraclePrice":"3.1500","priceChange24H":"-0.325781","nextFundingRate":"-0.0000258473","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"11792139.878000","trades24H":"4266","openInterest":"9059504","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"37000","maxPositionSize":"1900000","baselinePositionSize":"190000","assetResolution":"1000000","syntheticAssetId":"0x4352562d3600000000000000000000"},"UNI-USD":{"market":"UNI-USD","status":"ONLINE","baseAsset":"UNI","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"11.2410","oraclePrice":"11.2600","priceChange24H":"-1.009000","nextFundingRate":"0.0000022992","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"5207393.784800","trades24H":"2928","openInterest":"1311918.6","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"4000","maxPositionSize":"210000","baselinePositionSize":"20800","assetResolution":"10000000","syntheticAssetId":"0x554e492d3700000000000000000000"},"MKR-USD":{"market":"MKR-USD","status":"ONLINE","baseAsset":"MKR","quoteAsset":"USD","stepSize":"0.001","tickSize":"1","indexPrice":"2073.8600","oraclePrice":"2074.2074","priceChange24H":"-166.270000","nextFundingRate":"0.0000125000","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.01","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4563864.002000","trades24H":"704","openInterest":"8164.437","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"40","maxPositionSize":"2000","baselinePositionSize":"200","assetResolution":"1000000000","syntheticAssetId":"0x4d4b522d3900000000000000000000"},"LTC-USD":{"market":"LTC-USD","status":"ONLINE","baseAsset":"LTC","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"131.7110","oraclePrice":"131.6400","priceChange24H":"-7.459234","nextFundingRate":"-0.0000227146","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"11217188.737000","trades24H":"3652","openInterest":"180424.74","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"560","maxPositionSize":"28000","baselinePositionSize":"2800","assetResolution":"100000000","syntheticAssetId":"0x4c54432d3800000000000000000000"},"EOS-USD":{"market":"EOS-USD","status":"ONLINE","baseAsset":"EOS","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"2.5220","oraclePrice":"2.5174","priceChange24H":"-0.147346","nextFundingRate":"0.0000057040","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3012338.275000","trades24H":"2513","openInterest":"6094188","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"22000","maxPositionSize":"1100000","baselinePositionSize":"110000","assetResolution":"1000000","syntheticAssetId":"0x454f532d3600000000000000000000"},"DOGE-USD":{"market":"DOGE-USD","status":"ONLINE","baseAsset":"DOGE","quoteAsset":"USD","stepSize":"10","tickSize":"0.0001","indexPrice":"0.1496","oraclePrice":"0.1497","priceChange24H":"-0.009766","nextFundingRate":"-0.0000114947","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"100","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"9073625.550000","trades24H":"3914","openInterest":"137332630","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"400000","maxPositionSize":"22000000","baselinePositionSize":"2180000","assetResolution":"100000","syntheticAssetId":"0x444f47452d35000000000000000000"},"ATOM-USD":{"market":"ATOM-USD","status":"ONLINE","baseAsset":"ATOM","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"28.4932","oraclePrice":"28.5340","priceChange24H":"-2.035984","nextFundingRate":"-0.0000487751","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"24370439.887000","trades24H":"9426","openInterest":"1104803.0","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3000","maxPositionSize":"158000","baselinePositionSize":"16000","assetResolution":"10000000","syntheticAssetId":"0x41544f4d2d37000000000000000000"},"ZRX-USD":{"market":"ZRX-USD","status":"ONLINE","baseAsset":"ZRX","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"0.6598","oraclePrice":"0.6592","priceChange24H":"-0.048451","nextFundingRate":"-0.0000070338","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"12594556.282000","trades24H":"4099","openInterest":"11586619","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"100000","maxPositionSize":"5000000","baselinePositionSize":"500000","assetResolution":"1000000","syntheticAssetId":"0x5a52582d3600000000000000000000"},"SOL-USD":{"market":"SOL-USD","status":"ONLINE","baseAsset":"SOL","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"104.7960","oraclePrice":"104.9100","priceChange24H":"-8.894022","nextFundingRate":"-0.0000309724","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"54186410.727700","trades24H":"18151","openInterest":"436082.0","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"700","maxPositionSize":"34900","baselinePositionSize":"3400","assetResolution":"10000000","syntheticAssetId":"0x534f4c2d3700000000000000000000"},"UMA-USD":{"market":"UMA-USD","status":"ONLINE","baseAsset":"UMA","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"6.1678","oraclePrice":"6.1647","priceChange24H":"-0.452454","nextFundingRate":"-0.0000293797","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4689780.373000","trades24H":"4477","openInterest":"281698.9","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1000","maxPositionSize":"30000","baselinePositionSize":"2000","assetResolution":"10000000","syntheticAssetId":"0x554d412d3700000000000000000000"},"AAVE-USD":{"market":"AAVE-USD","status":"ONLINE","baseAsset":"AAVE","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.01","indexPrice":"173.6709","oraclePrice":"173.2700","priceChange24H":"-13.491902","nextFundingRate":"-0.0000076472","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"6094287.667100","trades24H":"1984","openInterest":"87170.52","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"300","maxPositionSize":"17000","baselinePositionSize":"1700","assetResolution":"100000000","syntheticAssetId":"0x414156452d38000000000000000000"},"ADA-USD":{"market":"ADA-USD","status":"ONLINE","baseAsset":"ADA","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.1307","oraclePrice":"1.1290","priceChange24H":"-0.057525","nextFundingRate":"-0.0000056476","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"8670745.789000","trades24H":"3557","openInterest":"17945971","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"46000","maxPositionSize":"2300000","baselinePositionSize":"230000","assetResolution":"1000000","syntheticAssetId":"0x4144412d3600000000000000000000"},"SNX-USD":{"market":"SNX-USD","status":"ONLINE","baseAsset":"SNX","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"5.1717","oraclePrice":"5.1720","priceChange24H":"-0.623267","nextFundingRate":"0.0000052792","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4324102.723000","trades24H":"2399","openInterest":"2694507.9","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"11000","maxPositionSize":"520000","baselinePositionSize":"52000","assetResolution":"10000000","syntheticAssetId":"0x534e582d3700000000000000000000"},"FIL-USD":{"market":"FIL-USD","status":"ONLINE","baseAsset":"FIL","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"22.7821","oraclePrice":"22.7500","priceChange24H":"-1.163894","nextFundingRate":"-0.0000161504","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"6352160.834000","trades24H":"3903","openInterest":"478499.1","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"1400","maxPositionSize":"68000","baselinePositionSize":"6800","assetResolution":"10000000","syntheticAssetId":"0x46494c2d3700000000000000000000"},"ZEC-USD":{"market":"ZEC-USD","status":"ONLINE","baseAsset":"ZEC","quoteAsset":"USD","stepSize":"0.01","tickSize":"0.1","indexPrice":"122.0400","oraclePrice":"121.7926","priceChange24H":"-4.200376","nextFundingRate":"0.0000006253","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"3243018.921000","trades24H":"2368","openInterest":"55010.85","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"100","maxPositionSize":"3000","baselinePositionSize":"200","assetResolution":"100000000","syntheticAssetId":"0x5a45432d3800000000000000000000"},"YFI-USD":{"market":"YFI-USD","status":"ONLINE","baseAsset":"YFI","quoteAsset":"USD","stepSize":"0.0001","tickSize":"1","indexPrice":"24236.5076","oraclePrice":"24199.5000","priceChange24H":"-1797.362365","nextFundingRate":"-0.0000064895","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"0.001","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"4466618.461300","trades24H":"2223","openInterest":"744.6725","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3","maxPositionSize":"140","baselinePositionSize":"14","assetResolution":"10000000000","syntheticAssetId":"0x5946492d3130000000000000000000"},"LINK-USD":{"market":"LINK-USD","status":"ONLINE","baseAsset":"LINK","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.001","indexPrice":"17.2721","oraclePrice":"17.2700","priceChange24H":"-1.217733","nextFundingRate":"-0.0000145151","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"7246391.294400","trades24H":"3673","openInterest":"1087769.4","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"3900","maxPositionSize":"200000","baselinePositionSize":"20000","assetResolution":"10000000","syntheticAssetId":"0x4c494e4b2d37000000000000000000"},"DOT-USD":{"market":"DOT-USD","status":"ONLINE","baseAsset":"DOT","quoteAsset":"USD","stepSize":"0.1","tickSize":"0.01","indexPrice":"20.2224","oraclePrice":"20.1624","priceChange24H":"-1.618407","nextFundingRate":"-0.0000241039","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"1","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"9136465.054000","trades24H":"6092","openInterest":"1561849.2","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"2900","maxPositionSize":"150000","baselinePositionSize":"14600","assetResolution":"10000000","syntheticAssetId":"0x444f542d3700000000000000000000"},"MATIC-USD":{"market":"MATIC-USD","status":"ONLINE","baseAsset":"MATIC","quoteAsset":"USD","stepSize":"1","tickSize":"0.001","indexPrice":"1.8393","oraclePrice":"1.8368","priceChange24H":"-0.188705","nextFundingRate":"-0.0000233629","nextFundingAt":"2022-02-11T01:00:00.000Z","minOrderSize":"10","type":"PERPETUAL","initialMarginFraction":"0.10","maintenanceMarginFraction":"0.05","volume24H":"36449333.021000","trades24H":"11703","openInterest":"18980542","incrementalInitialMarginFraction":"0.02","incrementalPositionSize":"80000","maxPositionSize":"4000000","baselinePositionSize":"410000","assetResolution":"1000000","syntheticAssetId":"0x4d415449432d360000000000000000"}}}
        
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

    dydx_assets = list(dydx_data['markets'].keys())

    ftx_fund_rate = [z["result"]["nextFundingRate"] for z in ftx_funds]
    ftx_oi = [z["result"]["openInterest"] for z in ftx_funds]

    dydx_data_assets = [dydx_data['markets'][ast+'-USD'] if ast+'-USD' in dydx_data['markets'] else {} for ast in ASSETS ]

    dydx_fund_rate = [float(dydx_dat.get('nextFundingRate',np.nan)) for dydx_dat in dydx_data_assets]
    dydx_volume = [float(dydx_dat.get('volume24H',np.nan)) for dydx_dat in dydx_data_assets]
    dydx_oi = [float(dydx_dat.get('openInterest', np.nan)) for dydx_dat in dydx_data_assets]

    drift_m_sum = drift.market_summary().T
    drift_fund_rate = (
        (drift_m_sum["last_mark_price_twap"] - drift_m_sum["last_oracle_price_twap"])
        / drift_m_sum["last_oracle_price_twap"]
    ) / 24

    drift_oi = (drift_m_sum['base_asset_amount_long'] - drift_m_sum['base_asset_amount_short'])
    print('FUNDING_SCALE', FUNDING_SCALE)
    funding_rate_df = pd.concat(
        [pd.Series(ftx_fund_rate), pd.Series(dydx_fund_rate), pd.Series(mango_fund_rate), drift_fund_rate], axis=1
    ).T * FUNDING_SCALE
    funding_rate_df.index = ["(FTX)", "DYDX", "Mango", "Drift"]
    funding_rate_df.index.name = "Protocol"
    funding_rate_df.columns = ASSETS
    funding_rate_df = funding_rate_df * 100
    for col in funding_rate_df.columns:
        funding_rate_df[col] = funding_rate_df[col].map("{:,.5f}%".format).replace('nan%','')

    funding_rate_df = funding_rate_df.reset_index()

    # make volume table too
    bonfida_markets = {
        "BTC": "475P8ZX3NrzyEMJSFHt9KCMjPpWBWGa6oNxkWcwww2BR",
        "SOL": "jeVdn6rxFPLpCH9E6jmk39NTNx2zgTmKiVXBDiApXaV",
        "ETH": "3ds9ZtmQfHED17tXShfC1xEsZcfCvmT8huNG79wa4MHg",
    }

    drift_markets = {v: str(k) for k,v in driftsummary.MARKET_INDEX_TO_PERP.items()}
    try:
        fida_volume = [
            requests.get(
                "https://serum-api.bonfida.com/perps/volume?market=%s"
                % bonfida_markets[x]
            ).json()["data"]["volume"]
            for x in ("SOL", "BTC", "ETH")
        ]
    except:
        fida_volume = [np.nan] * len(ASSETS)

    mango_volume = [np.nan]*len(ASSETS)
    for i,x in enumerate(ASSETS):
        try:
            mango_volume[i] = requests.get(
                "https://event-history-api.herokuapp.com/stats/perps/%s"
                % mango_markets[x]
            ).json()["data"]["volume"] 
        except:
            pass
            
    drift_volume = [np.nan]*len(ASSETS)
    for i,x in enumerate(ASSETS):
        try:
            drift_volume[i] = requests.get(
            "https://mainnet-beta.api.drift.trade/stats/24HourVolume?marketIndex=%s"
            % drift_markets[x+'-PERP']
        ).json()["data"]["volume"]
        except:
            pass

    # ftx_volume = [z["result"]["volume"] for z in ftx_funds]
    ftx_volume = [z["result"]["volumeUsd24h"] for z in ftx_px]

    oi = pd.concat(
        [pd.Series(ftx_oi), pd.Series(dydx_oi), pd.Series(mango_oi), drift_oi], axis=1
    ).T
    oi.index = [
            "(FTX)",
            "DYDX",
            "Mango",
            "Drift"
        ]
    for col in oi.columns:
        oi[col] = oi[col].astype(float).map("{:,.1f}".format)
    oi = oi.reset_index().replace('nan','')
    oi.columns = ["Protocol"]+list(ASSETS)

    volumes = pd.DataFrame(
        [ftx_volume, dydx_volume, mango_volume, drift_volume, fida_volume],
        index=[
            "(FTX)",
            "DYDX",
            "Mango",
            "Drift",
            "Bonfida",
        ],
    )
    # volumes.iloc[[0], :] *= np.array([[140, 42000, 3600, 66, 84, 520, 2.13]])  # todo lol
    for col in volumes.columns:
        volumes[col] = volumes[col].astype(float).map("${:,.0f}".format).replace('$nan','')
    volumes = volumes.reset_index()
    volumes.columns = ["Protocol"]+list(ASSETS)
    # volumes

    return funding_rate_df, volumes, oi, ftx_px


drift = driftsummary.drift_py()

FUNDING_SCALE = 1
funding_table, volume_table, oi_table, ftx_px = make_funding_table()



mango_prices_full =  [[{"price": np.nan, "time": np.nan}] * 15]*15#get_mango_prices()
fida_prices_full =  [[{"markPrice": np.nan, "time": 0}] * 15]*15#get_fida_prices()
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
                            "max-width": "900px",
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
            html.Span([
            html.H6("1h Funding Rates", id="funding-rate-update-text"),
            html.Div(
                [
                    dcc.Dropdown(
                        id="dropdown2",
                        options=[
                            {"label": '1h', "value": 1},
                            {"label": '24h', "value": 24},
                            {"label": '7d', "value": 24*7},
                            {"label": 'APR', "value": 24*365},
                        ],
                        value=1,
                    ),
                ],
                style={"max-width": "100px", "margin": "auto", "text-align": "left"},
            ),
            ],
            style={'display':'inline'},
            ),
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
                    "max-width": "900px",
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
                    "max-width": "900px",
                    "margin": "auto",
                },
            ),
            html.Br(),
            html.H6("Open Interest"),
            html.Div(
                [
                    dash_table.DataTable(
                        id="oi_table",
                        columns=[
                            {
                                "name": i,
                                "id": i,
                                "deletable": True,
                                "selectable": True,
                            }
                            for i in oi_table.columns
                        ],
                        style_data={
                            "whiteSpace": "normal",
                            "height": "auto",
                            "lineHeight": "15px",
                        },
                        data=oi_table.to_dict("records"),
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
                    "max-width": "900px",
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
                            for i in list(driftsummary.MARKET_INDEX_TO_PERP.values())
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
        " | ",
        html.A(
            " drift-flat-data (csv)",
            href="https://flatgithub.com/0xbigz/drift-flat-data?filename=data%2Fliquidation_history.csv&sort=record_id%2Cdesc&stickyColumnName=ts",
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
    [dash.dependencies.Output("funding-rate-update-text", 'children')],
    [
        dash.dependencies.Input("dropdown2", "value")
    ],
)
def update_funding_scale(funding_scale):
    global FUNDING_SCALE
    FUNDING_SCALE = funding_scale
    funding_nom = {1: '1h',
                    24: '24h',
                    24*7: '7d',
                    24*365:'APR'}[funding_scale]

    return [(str(funding_nom)+' Funding Rate')]

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

    if (maintenant - maintenant_data).seconds > 60:
        get_new_data() # fire and forget async_foo()
    maintenant = datetime.datetime.utcnow()

    drift_prices_selected = None
    rr = None
    style = {"padding": "5px", "fontSize": "16px"}
    # coingeckp = get_coin_gecko()
    dds = {}
    ASSETS2 = list((driftsummary.MARKET_INDEX_TO_PERP).items())
    ASSETS2.append((len(ASSETS2), 'SRM')) #extras todo
    for key, valperp in ASSETS2:
        val = valperp.split('-')[0]
        # print(fida_prices_full, key)
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

        if len(drift_prices_full) > key:
            drift_prices = drift_prices_full[key]
        else:
            drift_prices = {'afterPrice':np.nan, 'ts':np.nan}

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
    ).reset_index().replace('$nan','')

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
    if lock == 1 and (now - maintenant_data).seconds < 60*5:
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

    f, v, o, fx = make_funding_table()
    global funding_table
    funding_table = f

    global volume_table
    volume_table = v
    # print(volume_table)

    global oi_table
    oi_table = o

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
