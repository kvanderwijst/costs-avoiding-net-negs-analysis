import numpy as np
from plotly.subplots import make_subplots

from .netnegs import calc_total_net_negs
from .data import select, COSTS_GAMMA, DAMAGE_COEFFS, PARAMS
from .plotparams import COLORS_PBL
from .fig2 import calc_NPV


def add_scatter_traces(
    fig, facet_param, facet_values, x_param, y_param, column, df, row=1, dash="solid",
):

    for i, facet_value in enumerate(facet_values):
        sub_df = df[(df[facet_param] == facet_value) & ~(df[column].isna())]

        for j, (param2, sub_df2) in enumerate(sub_df.groupby(y_param)):
            fig.add_scatter(
                x=sub_df2[x_param].astype(float),
                y=sub_df2[column],
                mode="lines",
                line_color=COLORS_PBL[j],
                line_dash=dash,
                name="{:.1%}".format(param2),
                showlegend=i == 0,
                legendgroup=param2,
                row=row,
                col=i + 1,
            )


def create_fig(selection):

    total_net_negs_fig2 = calc_total_net_negs(select(selection, with_overshoot=True))
    return _create_fig_general(total_net_negs_fig2)


def create_fig_costs(selection, sdr):
    NPV_differences = selection.groupby("ID").apply(calc_NPV, sdr)
    NPV_differences = (
        NPV_differences.set_index(PARAMS)["NPV costs/GDP"]
        .unstack("minlevel")
        .reset_index()
    )
    diff = NPV_differences["0 GtCO2/yr"] / NPV_differences["-20 GtCO2/yr"] - 1
    NPV_differences["diff"] = diff
    fig = _create_fig_general(
        NPV_differences,
        False,
        "diff",
        False,
        "Extra costs from avoiding net negative emissions:",
    )

    delta_y = diff.max() - diff.min()
    yrange = [diff.min() - 0.07 * delta_y, diff.max() + 0.07 * delta_y]

    if diff.min() < 0.02:
        fig.add_shape(
            type="line", xref="paper", yref="y3", x0=1.01, x1=1.01, y0=yrange[0], y1=0
        ).add_annotation(
            xref="paper",
            yref="y3",
            x=1.01,
            y=yrange[0] / 2,
            text=" Benefits of<br> net negs<br> after 2100",
            ax=20,
            ay=0,
            xanchor="left",
            align="left",
        )
    fig.update_yaxes(title="", tickformat="+%", range=yrange)

    return fig


def _create_fig_general(
    df,
    withsecondary=True,
    variable="total_net_negs",
    fix_yrange=True,
    title="Total net negative emissions:",
):

    fig = make_subplots(
        1,
        3,
        shared_yaxes=True,
        specs=[[{}, {}, {"secondary_y": withsecondary}]],
        horizontal_spacing=0.04,
        vertical_spacing=0.2,
        subplot_titles=[
            "{}<br><br>Abat. cost level: <b>{}</b>".format(
                title.ljust(180) if i == 1 else "", val
            )
            for i, val in enumerate(["5th perc.", "median", "95th perc."])
        ],
    )

    fig.update_annotations(font_size=14)

    add_scatter_traces(
        fig,
        "gamma",
        [COSTS_GAMMA["p05"], COSTS_GAMMA["p50"], COSTS_GAMMA["p95"]],
        "damage_coeff",
        "PRTP",
        variable,
        df,
        row=1,
    )

    x_range = [float(DAMAGE_COEFFS[0]) - 0.00157, float(DAMAGE_COEFFS[-1]) + 0.00157]
    if fix_yrange:
        for i in range(3):
            fig.add_shape(
                type="line",
                x0=x_range[0],
                x1=x_range[1],
                y0=0,
                y1=0,
                xref=f"x{i+1}",
                yref=f"y{i+1}",
            )

    fig.update_xaxes(
        tickmode="array",
        tickvals=df["damage_coeff"].unique(),
        ticktext=["DICE", " ", "Howard<br>Total", " ", " ", " ", "Burke<br>(LR)"],
        tickangle=0,
        ticks="outside",
        range=x_range,
        title="Damage coefficient",
        title_standoff=7,
    )

    y_row2_range = [-598.8, 50.0]

    if withsecondary:
        fig.add_scatter(
            x=[None], y=[None], showlegend=False, row=1, col=3, secondary_y=True
        )

    if fix_yrange:
        y_row2_ticks = np.arange(int(y_row2_range[0] / 100) * 100, 100, 100)
        fig.update_yaxes(
            range=y_row2_range, tickmode="array", tickvals=y_row2_ticks, row=1
        )
    if withsecondary:
        fig.update_yaxes(
            ticktext=["{:.2f}°C".format(t) for t in np.abs(y_row2_ticks) * 0.00062],
            title="Temperature overshoot",
            title_standoff=0,
            secondary_y=True,
        )

    fig.update_layout(
        margin={"l": 50, "r": 30, "t": 80, "b": 60},
        yaxis1={"title": "GtCO<sub>2</sub>", "title_standoff": 5},
        height=380,
        width=900,
        legend={"y": 0.48, "title": "PRTP:", "tracegroupgap": 3},
    )

    return fig
