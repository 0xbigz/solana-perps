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
                    html.Div(
                        [
                            html.Img(
                                src="https://pbs.twimg.com/profile_banners/1388194344390119426/1637877290/1500x500",
                                style={
                                    "max-height": "50px",
                                    "max-width": "12%",
                                    # "width": "4%",
                                    # "float": "left",
                                    "position": "relative",
                                    "padding-bottom": 10,
                                    "padding-bottom": 40,
                                    "padding-right": 10,
                                },
                            ),
                            html.Img(
                                src="assets/platyperpstext.png",
                                style={
                                    "height": "100px",
                                },
                            ),
                            html.Img(
                                src="https://pbs.twimg.com/profile_banners/1388194344390119426/1637877290/1500x500",
                                style={
                                    "max-height": "50px",
                                    "max-width": "12%",
                                    # "width": "4%",
                                    # "float": "left",
                                    "position": "relative",
                                    "padding-bottom": 10,
                                    "padding-bottom": 40,
                                    "padding-right": 10,
                                    "transform": "scaleX(-1)",
                                },
                            ),
                        ],
                        style={
                            "margin": "auto",
                            "text-align": "center",
                        },
                    )
                ],
                href="https://twitter.com/bigz_Pubkey",
            ),
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
                                "Mango",
                                href="/mango",
                                className="tab",
                                id="tab-mango",
                            ),
                            dcc.Link(
                                "FAQ",
                                href="/faq",
                                className="tab",
                                id="tab-faq",
                            ),
                            dcc.Link(
                                "Resources",
                                href="/resources",
                                className="tab",
                                id="tab-resources",
                            ),
                        ],
                        className="row all-tabs",
                    ),
                ],
                style={
                    "text-align": "center",
                },
            ),
        ]
    )
