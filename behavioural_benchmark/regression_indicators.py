from typing import List

import numpy as np
import pwlf
import pandas as pd


def linear_slopes(regression_model: pwlf.PiecewiseLinFit) -> np.ndarray[np.float64]:
    """
    Calculates the slopes of the lines of a two-piecewise linear regression

    :param regression_model: a regression model of the type PiecewiseLinFit of pwlf
    :return: slopes of the lines of a two-piecewise linear regression
    """
    _ = regression_model.fit(2)
    slopes = regression_model.calc_slopes()
    return slopes

def process_regression_indicator(filepath: str, x_label: str, y_label: str, slope_indices: List[int]) \
        -> np.ndarray[np.float64]:
    """
    Calculates any of the regression-based indicators, namely DRoC, CRoC, ARoC-A, ARoC-B, LRoC-A, and LRoC-B.

    :param filepath: the path to the csv file which the regression will be built on
    :param x_label: the name of the column in the csv file denoting the change in time
    :param y_label: the name of the column in the csv file denoting the data
    :param slope_indices: the slopes to return. zero-based
    :return: the values of the slopes at the slope-indices given
    """
    df = pd.read_csv(filepath, engine='c', encoding="utf-8-sig")
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(axis=0, how='any', inplace=True)
    x = df[x_label]
    y = df[y_label]

    regression_model = pwlf.PiecewiseLinFit(x, y)
    slopes = linear_slopes(regression_model)

    return slopes[slope_indices]



