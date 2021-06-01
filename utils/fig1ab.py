import numpy as np
from plotly.subplots import make_subplots

from .netnegs import calc_total_net_negs
from .plotparams import PRTP_COLORS, LINE_DASH


def create_fig(selection):

    # Calculate total net neg
    total_net_negs = calc_total_net_negs(selection)

    fig = make_subplots(
        1,
        2,
        subplot_titles=("<b>a.</b> Emission paths", "<b>b.</b> Overshoot"),
        column_widths=[0.7, 0.3],
        specs=[[{}, {"secondary_y": True}]],
        horizontal_spacing=0.12,
    )

    for i, ((r, minEmissions), sub_df) in enumerate(
        selection.groupby(["PRTP", "minlevel"])
    ):
        # Show baseline emissions:
        # if i == 0:
        #     fig.add_scatter(
        #         x=sub_df["year"],
        #         y=sub_df["baseline"],
        #         line={"color": "#BBB"},
        #         showlegend=False,
        #     )
        #     fig.add_annotation(
        #         x=2070,
        #         y=sub_df[sub_df["year"] == 2070]["baseline"].values[0],
        #         text="Baseline",
        #         font_color="#888",
        #         arrowcolor="#888",
        #         arrowhead=6,
        #         ax=0,
        #         ay=30,
        #     )
        fig.add_scatter(
            x=sub_df["year"],
            y=sub_df["global_emissions"],
            line={
                "color": PRTP_COLORS[r],
                "dash": LINE_DASH[minEmissions],
                "simplify": False,
            },
            name="{}, {}".format(r, minEmissions),
            mode="lines",
            showlegend=False,
            row=1,
            col=1,
        )

    fig.add_bar(
        x=["{}%".format(r * 100) for r in total_net_negs["PRTP"]],
        y=total_net_negs["total_net_negs"],
        marker_color=[PRTP_COLORS[r] for r in total_net_negs["PRTP"]],
        width=0.7,
        showlegend=False,
        row=1,
        col=2,
    )

    fig.add_shape(type="line", x0=-1, x1=3, y0=0, y1=0, xref="x2", yref="y2")

    ## Add legends
    for r in selection["PRTP"].unique():
        fig.add_scatter(
            x=[None],
            y=[None],
            mode="lines",
            line_color=PRTP_COLORS[r],
            name="PRTP: {:.1%}".format(r),
        )
    fig.add_scatter(
        x=[None],
        y=[None],
        mode="lines",
        line_color="black",
        name="<b>With</b> net negs",
    )
    fig.add_scatter(
        x=[None],
        y=[None],
        mode="lines",
        line_color="black",
        line_dash="dot",
        name="<b>Without</b> net negs",
    )

    ## Add temperature overshoot (secondary) y-axis
    yaxis2_range = [np.min(total_net_negs["total_net_negs"]) * 1.05, 25]

    fig.add_scatter(
        x=[None], y=[None], showlegend=False, row=1, col=2, secondary_y=True
    )
    yaxis2_ticks = np.arange(int(yaxis2_range[0] / 100) * 100, 100, 100)
    fig.update_yaxes(
        range=yaxis2_range, tickmode="array", tickvals=yaxis2_ticks, row=1, col=2
    )
    fig.update_yaxes(
        ticktext=["{:.2f}°C".format(t) for t in np.abs(yaxis2_ticks) * 0.00062],
        title="Temperature overshoot",
        title_standoff=0,
        row=1,
        col=2,
        secondary_y=True,
    )

    fig.update_layout(
        margin={"l": 50, "r": 30, "t": 50, "b": 60},
        height=380,
        width=900,
        yaxis1={"range": [-22, 38.80], "title": "GtCO<sub>2</sub>/year"},
        xaxis2={"type": "category", "title": "PRTP", "range": [-0.7, 2.7]},
        yaxis2={
            "title": "Total net negative emissions<br>GtCO<sub>2</sub> (2020-2100)"
        },
        legend={"orientation": "h", "x": -0.04},
    )
    fig.update_yaxes(title_standoff=0)
    return fig
