from typing import List, Optional
import numpy as np
import pwlf
import pandas as pd


def process_regression_indicator(filepath: str, x_label: str, y_label: str, slope_indices: List[int]) \
        -> List[Optional[float]]:
    """
    Calculates any of the regression-based indicators, namely the Rate of Change indicators, ERT indicators and Critical
     value indicators

    :param filepath: the path to the csv file which the regression will be built on
    :param x_label: the name of the column in the csv file denoting the change in time
    :param y_label: the name of the column in the csv file denoting the data
    :param slope_indices: the slopes to return. zero-based
    :return: the values of the slopes at the slope-indices given, and the coordinates of the knee point
    """
    df = pd.read_csv(filepath, engine='c', encoding="utf-8-sig")
    if len(df.index) == 0:
        return [None] * (len(slope_indices) + 2)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(axis=0, how='any', inplace=True)
    x = df[x_label]
    y = df[y_label]

    regression_model = pwlf.PiecewiseLinFit(x, y)
    slopes = __linear_slopes(regression_model)
    knee_x, knee_y = __knee_point(regression_model)

    return [float(i) for i in slopes[slope_indices]] + [knee_x, knee_y]

def __linear_slopes(regression_model: pwlf.PiecewiseLinFit) -> np.ndarray[np.float64]:
    """
    Calculates the slopes of the lines of a two-piecewise linear regression

    :param regression_model: a regression model of the type PiecewiseLinFit of pwlf
    :return: slopes of the lines of a two-piecewise linear regression
    """
    _ = regression_model.fit(2)
    slopes = regression_model.calc_slopes()
    return slopes

def __knee_point(regression_model: pwlf.PiecewiseLinFit) -> (float, float):
    """
    Calculates the coordinates of the knee point of a two-piecewise linear regression
    :param regression_model: a regression model of the type PiecewiseLinFit of pwlf
    :return: the x- and y-coordinates of the knee point
    """
    knee_point = regression_model.fit(2)
    x = knee_point[1]
    y = (regression_model.predict(x))[0]
    return x, y

