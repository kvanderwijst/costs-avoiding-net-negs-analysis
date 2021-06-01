"""
Import and join data from MIMOSA output files
"""

import os
from glob import glob
from typing import Iterable
import numpy as np
import pandas as pd

from .baselinegdp import GDP

META_COLUMNS = [
    "ID",
    "Experiment",
    "Variable",
    "Region",
    "carbonbudget",
    "minlevel",
    "inertia",
    "gamma",
    "PRTP",
    "damage_coeff",
    "perc_reversible",
    "TCRE",
]
PARAMS = ["damage_coeff", "TCRE", "gamma", "PRTP", "minlevel", "perc_reversible"]

COSTS_GAMMA = {
    "p05": "954.9608 USD2005/tCO2",
    "p50": "2442.3716 USD2005/tCO2",
    "p95": "5996.4614 USD2005/tCO2",
}

MINLEVEL_OVERSHOOT = {
    True: "-20 GtCO2/yr",
    False: "0 GtCO2/yr",
}

DAMAGE_COEFFS = np.linspace(0.00267, 0.0283483, 7).round(5).astype("str")

DEFAULT_TCRE = "0.62 delta_degC/(TtCO2)"


def read_single(filename):
    df = pd.read_csv(filename)
    return df[META_COLUMNS + [str(x) for x in range(2020, 2151)]]


def read_all(directory):
    filenames = glob(os.path.join(directory, "*.csv"))
    combined = pd.concat([read_single(filename) for filename in filenames])

    # Change several column types
    combined["damage_coeff"] = combined["damage_coeff"].round(5).astype(str)
    return combined


def to_long(wide_table):
    wide_table.loc[wide_table["Region"] == "WorldOrig", "Region"] = "Global"
    stacked = (
        wide_table.set_index(META_COLUMNS)
        .rename_axis("year", axis=1)
        .stack()
        .unstack("Variable")
        .reset_index()
        .sort_values(
            ["TCRE", "gamma", "perc_reversible", "PRTP", "damage_coeff", "minlevel"]
        )
    )
    stacked["year"] = stacked["year"].astype(int)

    # damage_costs are relative, transform to absolute
    stacked["damage_costs"] *= stacked["GDP_gross"]

    # Add column `total_costs` and `total_costs_relative`
    stacked["total_costs"] = stacked["abatement_costs"] + stacked["damage_costs"]
    stacked["total_costs_relative"] = stacked["total_costs"] / stacked["GDP_gross"]
    stacked["damage_costs_relative"] = stacked["damage_costs"] / stacked["GDP_gross"]
    stacked["abatement_costs_relative"] = (
        stacked["abatement_costs"] / stacked["GDP_gross"]
    )

    # Add column baseline GDP loss
    stacked["baseline_GDP"] = GDP(stacked["year"], "SSP2")
    stacked["baseline_GDP_loss"] = stacked["baseline_GDP"] - stacked["GDP_net"]
    return stacked


def select(
    df,
    cost_level=None,
    prtp=None,
    budget=None,
    with_overshoot=None,
    tcre=None,
    perc_reversible=None,
    damage_i=None,
    endyear=2150,
):
    return df[
        _select_single(df, "carbonbudget", budget)
        & _select_single(df, "TCRE", tcre)
        & _select_single(df, "gamma", COSTS_GAMMA.get(cost_level))
        & _select_single(df, "PRTP", prtp)
        & _select_single(df, "perc_reversible", perc_reversible)
        & _select_single(df, "minlevel", MINLEVEL_OVERSHOOT.get(with_overshoot))
        & _select_single(
            df,
            "damage_coeff",
            DAMAGE_COEFFS[damage_i] if damage_i is not None else None,
        )
        & (df["year"] <= endyear)
    ]


def _select_single(df, column, value):
    value_check = (
        (df[column].isin(value)) if _is_listy(value) else (df[column] == value)
    )
    none_check = value is None
    return value_check | none_check


def _is_listy(value):
    if isinstance(value, Iterable) and not isinstance(value, str):
        return True
    return False
