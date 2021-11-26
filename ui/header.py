import dash_core_components as dcc
import dash_html_components as html


def make_header() -> html.Header:
    """
    Returns a HTML Header element for the application Header.
    :return: HTML Header
    """
    return html.Header(
        children=[
            # Icon and title container
            # html.Div(
            #     className="dash-title-container",
            #     children=[
            #         html.Img(className="dash-icon", src="assets/img/ship-1.svg"),
            #         html.H1(className="dash-title", children=["Dash ports analytics"]),
            #     ],
            # ),
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
                    dcc.Tabs(
                        id="navigation-tabs",
                        value="tab-port-map",
                        children=[
                            dcc.Tab(
                                label="Price",
                                value="tab-port-map",
                                className="dash-tab",
                                selected_className="dash-tab-selected",
                            ),
                            dcc.Tab(
                                label="Funding",
                                value="tab-port-stats",
                                className="dash-tab",
                                selected_className="dash-tab-selected",
                                disabled=True,
                            ),
                            dcc.Tab(
                                label="Users",
                                value="tab-port-compare",
                                className="dash-tab",
                                selected_className="dash-tab-selected",
                                disabled=True,
                            ),
                        ],
                    ),
                    # TODO Dario - remove below button
                    # html.Button(id='btn-sidebar-request-port', className='btn-sidebar-request-port', children=[strings.BTN_REQUEST_PORT])
                ]
            ),
        ]
    )
