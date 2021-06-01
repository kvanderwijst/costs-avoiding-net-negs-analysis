from plotly.subplots import make_subplots

from .colorutils import lighten_hex
from .plotparams import PRTP_COLORS
from .npv import NPV
from .data import select


def create_fig(selection, sdr):
    fig1c = make_subplots(subplot_titles=["<b>c.</b> Abatement and damage costs"])

    for i, r in enumerate(selection["PRTP"].unique()):

        selection_with_netnegs = select(selection, with_overshoot=True, prtp=r)
        selection_without_netnegs = select(selection, with_overshoot=False, prtp=r)

        costs_with_netnegs = [
            NPV(selection_with_netnegs, var, sdr)
            for var in ["damage_costs", "abatement_costs", "GDP_gross"]
        ]
        costs_without_netnegs = [
            NPV(selection_without_netnegs, var, sdr)
            for var in ["damage_costs", "abatement_costs", "GDP_gross"]
        ]
        baseline_GDP_NPV = 0  # TODO

        use_baseline_GDP = False

        if use_baseline_GDP:
            GDP_NPV_with = GDP_NPV_without = baseline_GDP_NPV
            raise NotImplementedError("Baseline GDP not implemented")
        else:
            GDP_NPV_with = costs_with_netnegs[2]
            GDP_NPV_without = costs_without_netnegs[2]

        costs_with_netnegs = [
            costs_with_netnegs[0] / GDP_NPV_with,
            costs_with_netnegs[1] / GDP_NPV_with,
        ]
        costs_without_netnegs = [
            costs_without_netnegs[0] / GDP_NPV_without,
            costs_without_netnegs[1] / GDP_NPV_without,
        ]

        shift_0 = costs_without_netnegs[0] / costs_with_netnegs[0] - 1
        shift_1 = costs_without_netnegs[1] / costs_with_netnegs[1] - 1
        shift_total = sum(costs_without_netnegs) / sum(costs_with_netnegs) - 1

        color_0 = lighten_hex(PRTP_COLORS[r], 0.2, -0.15)
        color_1 = PRTP_COLORS[r]

        n = 2
        width = 0.6
        x_left, x_right = i * n, i * n + 1

        x_values = [
            ["<br>PRTP: {:.1%}".format(r)] * 2,
            ["<b>With</b><br>net negs", "<b>Without</b><br>net negs"],
        ]

        fig1c.add_bar(
            x=x_values,
            y=[costs_with_netnegs[0], costs_without_netnegs[0]],
            marker_color=color_0,
            marker_line_width=2,
            width=width,
            showlegend=False,
        )
        fig1c.add_bar(
            x=x_values,
            y=[costs_with_netnegs[1], costs_without_netnegs[1]],
            marker_color=color_1,
            marker_line_width=2,
            width=width,
            showlegend=False,
        )

        add_line = lambda y0, y1: fig1c.add_shape(
            type="line",
            x0=x_left + 0.5 * width - 0.02,
            x1=x_right - 0.5 * width + 0.02,
            y0=y0,
            y1=y1,
            xref="x",
            yref="y",
            line_color="#777",
            line_width=2,
            name="r={:.1%}".format(r),
        )

        pad = 0.0004
        add_line(pad, pad)
        add_line(costs_with_netnegs[0], costs_without_netnegs[0])
        add_line(sum(costs_with_netnegs) - pad, sum(costs_without_netnegs) - pad)

        fig1c.add_annotation(
            x=x_right,
            y=sum(costs_without_netnegs),
            text="Total: {:+.0%}".format(shift_total),
            font_color="black",
            showarrow=False,
            yshift=12,
        )

        fig1c.add_annotation(
            x=x_right,
            y=sum(costs_without_netnegs),
            text="{:+.0%}".format(shift_1),
            font_color="white",
            showarrow=False,
            yshift=-10,
        )

        fig1c.add_annotation(
            x=x_right,
            y=costs_without_netnegs[0],
            text="{:+.0%}".format(shift_0),
            font_color="white",
            showarrow=False,
            yshift=12,
        )

        fig1c.add_scatter(
            x=[None],
            y=[None],
            name="<br><b>PRTP={:.1%}:</b>".format(r),
            line_color="rgba(0,0,0,0)",
        )
        fig1c.add_bar(x=[None], y=[None], name="Abatement costs", marker_color=color_1)
        fig1c.add_bar(x=[None], y=[None], name="Damage costs", marker_color=color_0)

    fig1c.update_layout(
        barmode="relative",
        margin={"l": 50, "r": 30, "t": 50, "b": 60},
        height=400,
        width=900,
        #     xaxis={
        #         'range': [-0.7, 3*n-0.5],
        #         'tickmode': 'array',
        #         'tickvals': np.concatenate([[i*n, i*n+1] for i in range(3)]),
        #         'ticktext': [f'<b>{name}</b><br>net negs' for name in ['With', 'Without']] * 3
        #     },
        yaxis={
            "title": "NPV total costs<br>(2020-2100, share of baseline GDP)",
            "tickformat": ",.1%",
        },
        legend={"y": 0.1},
    )

    return fig1c
