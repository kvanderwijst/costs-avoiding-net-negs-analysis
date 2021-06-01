import numpy as np
from .data import PARAMS


def calc_total_net_negs(selection):
    unique_years = selection["year"].unique()

    net_negative_emissions = selection[["year", "global_emissions"] + PARAMS].copy()
    net_negative_emissions["global_emissions"] = net_negative_emissions[
        "global_emissions"
    ].clip(upper=0)

    new_years = np.linspace(unique_years[0], unique_years[-1], 200)
    finer_interpolation = lambda sub_df: np.trapz(
        np.clip(
            np.interp(new_years, sub_df["year"], sub_df["global_emissions"]), None, 0
        ),
        new_years,
    )

    # Group each scenario and perform linear integration (trapezoid summing)
    # Note that this overestimates the total negative emissions due to the clipping
    total_net_negs = net_negative_emissions.groupby(PARAMS).apply(finer_interpolation)
    # Transform multi-index Series to dataframe, and rename column to better name
    total_net_negs = total_net_negs.reset_index().rename(columns={0: "total_net_negs"})

    return total_net_negs


def _apply_temperatures(sub_df):
    series = sub_df[PARAMS].iloc[0]
    series["peak temp"] = sub_df["temperature"].max()
    series["2100 temp"] = sub_df.set_index("year").loc[2100]["temperature"]
    series["cumulative_emissions"] = sub_df.set_index("year").loc[2100][
        "cumulative_emissions"
    ]
    return series


def calc_temperatures(selection):
    return selection.groupby("ID").apply(_apply_temperatures).reset_index()
