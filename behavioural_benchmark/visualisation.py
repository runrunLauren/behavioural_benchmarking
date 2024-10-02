from typing import List, Dict
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns

class Visualisation:
    def __init__(self, data: pd.DataFrame, identifier_header="metaheuristic"):
        self.data = data
        self.identifier_header = identifier_header

    def cartesian_visualisation(
            self,
            columns: List[str],
            filters: Dict[str, List[str]],
            exclude_outliers: bool = True,
            normalise: bool = True
    ):
        assert len(columns) > 0
        prepped_data = self.__prep_data__(columns, filters, exclude_outliers, normalise)
        if len(columns) == 3:
            self.__visualise_3d__(prepped_data, column_1=columns[0], column_2=columns[1], column_3=columns[2])
        elif len(columns) == 2:
            self.__visualise_2d__(prepped_data, column_1=columns[0], column_2=columns[1])
        elif len(columns) == 1:
            self.__visualise_1d__(prepped_data, columns[0])
        else:
            print("This style of visualisation is only available for up to three columns")

    def venn_diagram_visualisation(self):
        print("todo")

    def __prep_data__(
            self,
            columns: List[str],
            filters: Dict[str, List[str]],
            exclude_outliers: bool,
            normalise: bool
    ) -> pd.DataFrame:
        """
        Takes the given data, and return prepped data. Prepped data only contains the identifier header column, and the
         columns that are going to be visualised, and have been filtered. Optionally prepped data is normalised and
         excludes outliers.

        :param columns: the columns to prep and return
        :param filters: a dictionary containing columns, and the acceptable values in those columns
        :param exclude_outliers: whether to include outliers in the prepped data
        :param normalise: whether to normalise the prepped data
        """
        filtered_data = self.data
        for column, values in filters.items():
            filtered_data = filtered_data[filtered_data[column].isin(values)]

        prepped_data = filtered_data[[self.identifier_header] + columns]
        if exclude_outliers:
            for col in columns:
                Q1 = prepped_data[col].quantile(0.25)
                Q3 = prepped_data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                prepped_data = prepped_data[(prepped_data[col] >= lower_bound) & (prepped_data[col] <= upper_bound)]

        if normalise:
            for col in columns:
                scaler = MinMaxScaler()
                prepped_data[[col]] = scaler.fit_transform(prepped_data[[col]])

        return prepped_data

    def __visualise_1d__(self, data: pd.DataFrame, column: str):
        sns.histplot(x=column, data=data, hue=self.identifier_header, element='poly')

    def __visualise_2d__(self, data:pd.DataFrame, column_1: str, column_2: str):
        print("todo")

    def __visualise_3d__(self, data: pd.DataFrame, column_1: str, column_2: str, column_3: str):
        print("todo")

