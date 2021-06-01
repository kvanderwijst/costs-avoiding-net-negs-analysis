import numpy as np


def NPV(sub_df, column, r):
    values = sub_df[column].values
    years = sub_df["year"].values
    output = np.exp(-float(r) * (years - years[0])) * values
    return np.trapz(output, x=years)
