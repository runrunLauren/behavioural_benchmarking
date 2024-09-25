import numpy as np
import pandas as pd

def explore_percent(filepath: str):
    """
    Takes the diversity csv data, calculates the XPL% for every iteration, and then calculates the mean XPL%

    :param filepath: the path to the csv file which contains the diversity data
    :return: the mean XPL% as per the diversity data
    """
    df = pd.read_csv(filepath, engine='c', encoding="utf-8-sig")
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(axis=0, how='any', inplace=True)

    div_max = max(df['diversity'])
    df['xpl_percent'] = df['diversity'] / div_max * 100
    return df['xpl_percent'].mean()

def infeasible_percent(filepath: str):
    """
    Takes the F% (calculated while running experiments) and returns the mean

    :param filepath: the path to the csv file which contains the F%
    :return: the mean F%
    """
    df = pd.read_csv(filepath, engine='c', encoding="utf-8-sig")
    return df['f_percent'].mean()


