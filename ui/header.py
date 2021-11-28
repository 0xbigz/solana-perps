import dash_core_components as dcc
import dash_html_components as html


def make_header() -> html.Header:
    """
    Returns a HTML Header element for the application Header.
    :return: HTML Header
    """
    return html.Header(
        children=[
            html.A(
                [
                    html.Span(
                        [
                            html.Img(
                                src="https://pbs.twimg.com/profile_banners/1388194344390119426/1637877290/1500x500",
                                style={
                                    "height": "50px",
                                    # "width": "4%",
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
            html.H4("~comparing perpetual swap prices on Solana DEXs~"),
            html.H4("(updates every 10 seconds, please be patient with loads! 🐢 )"),
            # create navigator with buttons
            html.Nav(
                children=[
                    html.Div(
                        [
                            dcc.Link(
                                "Comparison",
                                href="/compare",
                                className="tab first",
                                id="tab-compare",
                            ),
                            dcc.Link(
                                "Drift",
                                href="/drift",
                                className="tab",
                                id="tab-drift",
                            ),
                            dcc.Link(
                                "More",
                                href="/more",
                                className="tab",
                                id="tab-more",
                            ),
                        ],
                        className="row all-tabs",
                    ),
                ]
            ),
        ]
    )
