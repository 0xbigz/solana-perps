import dash_core_components as dcc
import dash_html_components as html


def make_footer() -> html.Footer:
    """
    Returns a HTML Header element for the application Header.
    :return: HTML Header
    """
    return html.Footer(
        children=[
            html.H5("FAQ"),
            html.H3("Why are prices different between DEXs?"),
            html.P(
                "perpetual swaps aren't fungible. you cant take a position on one protocol and bring it to another. so the accessibility (drift on closed mainnet) + incentive structures(drift hourly funding rates vs mango continuous) + exchange risk (drift vAMM vs mango clob) will bring prices in line."
            ),
            html.P(
                "prices are currently `last trade`, mango's bid/ask price could be different."
            ),
            html.H3("Where does the data come from?"),
            html.Span(
                [
                    html.P(
                        "A mix of on-chain inspection / api requests. The project is written in python and is "
                    ),
                    html.A(
                        "open sourced",
                        "https://github.com/0xbigz/solana-perps",
                        href="https://github.com/0xbigz/solana-perps",
                        target="_",
                    ),
                    html.P("feel free to submit a pull request or make a request"),
                ]
            ),
            html.H3("Why make this?"),
            html.Span("bigz likes data and wanted to share :D"),
            html.H3("When funding comparison/strategy explanation?"),
            html.P("soon (tm)"),
        ]
    )


def make_resources() -> html.Footer:
    return html.Footer(
        children=[
            html.H5("Resources"),
            html.H4("readings"),
            html.A(
                "Drift litepaper",
                href="https://docs.drift.trade/technical-litepaper",
            ),
            html.Br(),
            html.A(
                "Mango litepaper",
                href="https://docs.mango.markets/litepaper",
            ),
            html.Br(),
            html.A(
                "deep dive Drift explainer (wip)",
                href="https://foregoing-script-fd0.notion.site/Drift-s-dAMM-ff154003aedb4efa83d6e7f4440cd4ab",
            ),
            html.Br(),
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
            ),
        ]
    )
