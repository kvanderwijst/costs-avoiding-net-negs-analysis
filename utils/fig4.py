from plotly.subplots import make_subplots

from .netnegs import calc_total_net_negs, calc_temperatures
from .data import COSTS_GAMMA, DAMAGE_COEFFS, PARAMS
from .plotparams import PRTP_COLORS


def create_fig(selection):

    netnegs_irrivers_cb = calc_total_net_negs(selection)
    netnegs_irrivers_cb["effective_carbonbudget"] = (
        600
        + (1 - netnegs_irrivers_cb["perc_reversible"])
        * netnegs_irrivers_cb["total_net_negs"]
    )
    netnegs_irrivers_cb["below_budget"] = (
        netnegs_irrivers_cb["effective_carbonbudget"] - 600
    )
    netnegs_irrivers_cb["perc_irreversible"] = (
        1 - netnegs_irrivers_cb["perc_reversible"]
    )

    temperatures = calc_temperatures(selection)

    netnegs_irrivers_cb = netnegs_irrivers_cb.merge(temperatures, on=PARAMS)

    fig = make_subplots(
        1,
        2,
        subplot_titles=(
            "<b>a.</b> Total net negative emissions",
            "<b>b.</b> Cumulative emissions 2020-2100",
            # "<b>b.</b> Temperature in 2100",
        ),
        horizontal_spacing=0.09,
    )

    cost_level = "p50"

    for i, var in enumerate(["total_net_negs", "cumulative_emissions"]):
        for damage_i, dash in [(0, "dash"), (2, "solid"), (-1, "dot")]:
            for prtp in [0.001, 0.015, 0.03]:
                sub_df = netnegs_irrivers_cb[
                    (netnegs_irrivers_cb["gamma"] == COSTS_GAMMA[cost_level])
                    & (netnegs_irrivers_cb["PRTP"] == prtp)
                    & (netnegs_irrivers_cb["damage_coeff"] == DAMAGE_COEFFS[damage_i])
                ]
                fig.add_scatter(
                    x=sub_df["perc_irreversible"],
                    y=sub_df[var],
                    line={"color": PRTP_COLORS[prtp], "dash": dash},
                    showlegend=i == 0 and dash == "solid",
                    name="{:.1%}".format(prtp),
                    mode="lines",
                    col=i + 1,
                    row=1,
                )

    (
        fig.add_scatter(
            x=[None],
            y=[None],
            mode="lines",
            line={"color": "rgba(0,0,0,0)"},
            legendgroup="1",
            name="",
        )
        .add_scatter(
            x=[None],
            y=[None],
            mode="lines",
            line={"color": "black", "dash": "dash"},
            legendgroup="1",
            name="DICE damages",
        )
        .add_scatter(
            x=[None],
            y=[None],
            mode="lines",
            line={"color": "black", "dash": "solid"},
            legendgroup="1",
            name="Howard Total damages",
        )
        .add_scatter(
            x=[None],
            y=[None],
            mode="lines",
            line={"color": "black", "dash": "dot"},
            legendgroup="1",
            name="Burke (LR) damages",
        )
        .add_annotation(
            x=0.33,
            y=220,
            text="Target not binding",
            row=1,
            col=2,
            ax=30,
            ay=50,
            arrowwidth=1.5,
            arrowsize=1,
            arrowhead=2,
        )
        .update_xaxes(tickformat="%", title="Perc. irreversible", dtick=0.25)
        .update_yaxes(title="GtCO<sub>2</sub>", title_standoff=0, col=1)
        .update_yaxes(title="GtCO<sub>2</sub>", title_standoff=0, col=2)
        # .update_yaxes(ticksuffix="°C", title_standoff=0, col=2)
        # .update_yaxes(col=2, range=range_y2)
        # .update_yaxes(
        #     title="% of carbon budget",
        #     tickformat="%",
        #     range=range_y2 / 600,
        #     secondary_y=True,
        #     showgrid=False,
        #     col=1
        # )
        .update_layout(
            legend={"title": "PRTP:", "y": 0.5, "x": 1.05, "tracegroupgap": 3},
            # yaxis2={"matches": "y"},
            width=900,
            height=300,
            margin={"t": 40, "r": 0, "b": 20, "l": 60},
        )
    )

    return fig
