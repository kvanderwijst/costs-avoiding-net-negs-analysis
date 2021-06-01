import numpy as np


SSP_years = np.linspace(2010, 2100, 10)
extra_years = np.arange(2110, 2260, 10)
extended_years = np.concatenate([SSP_years, extra_years])

# To extrapolate: take growth rate 2090-2100, linearly bring it down to growth rate of 0 in 2150
def extrapolate(input, years, extra_years, stabilising_years=50):
    # First get final change rate
    change_rate = (input[-1] - input[-2]) / (years[-1] - years[-2])
    minmax = np.maximum if change_rate > 0 else np.minimum

    t_prev = years[-1]
    val_prev = input[-1]

    new_values = []

    for t in extra_years:
        change = minmax(
            0.0, change_rate - change_rate * (t_prev - 2100.0) / stabilising_years
        )
        val = val_prev + change * (t - t_prev)

        new_values.append(val)

        val_prev = val
        t_prev = t

    return np.concatenate([input, new_values])


GDP_data = {
    "SSP1": 1e-3
    * np.array(
        [
            68461.88281,
            101815.2969,
            155854.7969,
            223195.5,
            291301.4063,
            356291.4063,
            419291.1875,
            475419.1875,
            524875.8125,
            565389.625,
        ]
    ),
    "SSP2": 1e-3
    * np.array(
        [
            68461.88281,
            101602.2031,
            144812.9063,
            188496.5938,
            234213.4063,
            283250.5938,
            338902.5,
            399688.5938,
            466015.8125,
            538245.875,
        ]
    ),
    "SSP3": 1e-3
    * np.array(
        [
            68461.88281,
            100879.5,
            135704.5938,
            160926.5,
            180601,
            197332.2031,
            215508.2969,
            234786.4063,
            255673.7969,
            279511.1875,
        ]
    ),
    "SSP4": 1e-3
    * np.array(
        [
            68461.88281,
            103664.2969,
            147928.2969,
            191229.5,
            229272.7969,
            262242.4063,
            292255.1875,
            317266.6875,
            339481.8125,
            360479.5,
        ]
    ),
    "SSP5": 1e-3
    * np.array(
        [
            68461.88281,
            105689.8984,
            174702.2969,
            271955.0938,
            378443.0938,
            492278.5938,
            617695.3125,
            749892.8125,
            889666.3125,
            1034177.0,
        ]
    ),
}

GDP_extended = {
    SSP: extrapolate(data, SSP_years, extra_years) for SSP, data in GDP_data.items()
}
# go.Figure([go.Scatter(x=SSP_years, y=GDP_data['SSP3']),go.Scatter(x=extended_years, y=GDP_extended['SSP3'])]).show()


def GDP(year, SSP):
    return np.interp(year, extended_years, GDP_extended[SSP])

