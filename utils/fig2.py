import plotly.express as px
from plotly.subplots import make_subplots

from .colorutils import lighten_hex, hex_to_rgba
from .npv import NPV
from .data import select, PARAMS
from .plotparams import COLORS_PBL


def calc_NPV(sub_df, sdr):
    series = sub_df[PARAMS].iloc[0]
    series["NPV total costs"] = NPV(sub_df, "total_costs", sdr)
    series["NPV GDP"] = NPV(sub_df, "GDP_gross", sdr)
    series["NPV costs/GDP"] = series["NPV total costs"] / series["NPV GDP"]
    series["NPV baseline loss/baseline GDP"] = NPV(
        sub_df, "baseline_GDP_loss", sdr
    ) / NPV(sub_df, "baseline_GDP", sdr)
    return series


def create_fig(selection, sdr, with_arrows=True):
    fillchars = 55
    fig = make_subplots(
        3,
        6,
        shared_yaxes=True,
        horizontal_spacing=0.01,
        vertical_spacing=0.1,
        column_widths=[4, 1] * 3,
        subplot_titles=[
            "<b>DICE</b> damages (low)<br>" + "PRTP: <b>0.1%</b>:".ljust(fillchars),
            "",
            "<b>Howard Total</b> damages (medium)<br> ",
            "",
            "<b>Burke (LR)</b> damages (high)<br> ",
            "",
            "PRTP: <b>1.5%</b>:".ljust(fillchars),
            "",
            "",
            "",
            "",
            "",
            "PRTP: <b>3%</b>:".ljust(fillchars),
            "",
            "",
            "",
            "",
            "",
        ],
    )

    fig.update_annotations(font_size=14)

    for i, damage_i in enumerate([0, 2, -1]):
        for j, PRTP in enumerate([0.001, 0.015, 0.03]):
            row = j + 1
            col = 2 * i + 1

            NPV_values = {}

            for with_overshoot, dash, color in [
                (True, "solid", COLORS_PBL[4]),  # px.colors.qualitative.Plotly[0]),
                (False, "dot", COLORS_PBL[3]),  # px.colors.qualitative.Plotly[1]),
            ]:
                subset = select(
                    selection,
                    damage_i=damage_i,
                    prtp=PRTP,
                    with_overshoot=with_overshoot,
                )
                for var, opacity, lighten in [
                    ("abatement_costs_relative", 0.33, 0.15),
                    ("damage_costs_relative", 0.66, 0),
                ]:
                    fig.add_scatter(
                        x=subset["year"],
                        y=subset[var],
                        line={"dash": dash, "color": lighten_hex(color, lighten)},
                        stackgroup=with_overshoot,
                        fillcolor=hex_to_rgba(color, opacity),
                        row=row,
                        col=col,
                        showlegend=i == 0 and j == 0,
                        name="Abatement costs"
                        if var.startswith("abatement")
                        else "Damage costs"
                        # name="<b>{}</b> net negs".format(
                        #     "With" if with_overshoot else "Without"
                        # ),
                    )
                NPV_values[with_overshoot] = calc_NPV(subset, sdr)
                if i == 0 and j == 0:
                    fig.add_scatter(
                        x=[None],
                        y=[None],
                        mode="lines",
                        line={"color": "rgba(0,0,0,0)"},
                        name="<br><b>{}</b> net negs:".format(
                            "With" if with_overshoot else "Without"
                        ),
                    )

            # Add bar chart for NPV difference
            NPV_diff = (
                NPV_values[False]["NPV costs/GDP"] / NPV_values[True]["NPV costs/GDP"]
                - 1
            )

            fig.add_bar(
                x=[""],
                y=[NPV_diff],
                row=row,
                col=col + 1,
                showlegend=False,
                marker_color="#BBB",
            )
            fig.add_shape(
                type="rect",
                row=row,
                col=col + 1,
                x0=-10,
                x1=10,
                y0=-10,
                y1=10,
                fillcolor="white",
                layer="below",
                line_color="rgba(0,0,0,0)",
            ).add_shape(
                type="line", x0=-10, x1=10, y0=0, y1=0, row=row, col=col + 1
            ).add_annotation(
                x=0,
                y=0,
                yshift=-2 if NPV_diff > 0 else 2,
                yanchor="top" if NPV_diff > 0 else "bottom",
                text="{:+.1%}<br>NPV".format(NPV_diff),
                showarrow=False,
                row=row,
                col=col + 1,
            )

    #### Explanation arrows
    arrow_style = dict(arrowhead=6, font_size=13, arrowwidth=2, arrowsize=1)
    arrow_params = dict(row=3, col=3, **arrow_style)
    if with_arrows:
        fig.add_annotation(
            x=2053,
            y=0.05,
            text="                   <b>Abatement costs</b>",
            ax=0 * 50,
            ay=50,
            **arrow_params
        )
        fig.add_annotation(
            x=2057,
            y=0.065,
            text="<b>Damage costs</b>       ",
            ax=0 * 20,
            ay=-35,
            **arrow_params
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.97,
            y=0.74,
            **arrow_style,
            ax=0,
            ay=25,
            text=" Benefits of net negs<br>after 2100",
            xanchor="left",
            yanchor="middle"
        )

    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.295,
        y=-0.03,
        **arrow_style,
        ax=0,
        ay=25,
        text=" <b>Extra total costs when avoiding net negs</b>",
        xanchor="left",
        yanchor="middle"
    )

    fig.update_layout(
        width=900,
        height=630,
        margin={"t": 60, "b": 60, "r": 30, "l": 30},
        legend_y=0.5,
    ).update_yaxes(matches="y1", tickformat="p", rangemode="nonnegative").update_yaxes(
        col=1, title={"text": "Costs (% GDP)", "standoff": 0}
    )

    for col in [2, 4, 6]:
        fig.update_yaxes(col=col, matches="y2", range=[-0.08, 0.3095])
        fig.update_xaxes(col=col, range=[-1, 1])
        fig.update_xaxes(col=col - 1, range=[2020, 2100])

    return fig
