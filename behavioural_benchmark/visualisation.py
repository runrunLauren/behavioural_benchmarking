from typing import List, Dict
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial import ConvexHull, HalfspaceIntersection
from shapely import Polygon
from matplotlib_venn import venn2, venn3
import seaborn as sns
sns.set_style("white")


class Visualisation:
    def __init__(self, data: pd.DataFrame, identifier_header="metaheuristic"):
        self.data = data
        self.identifier_header = identifier_header

    def visualise(
            self,
            visualisation_type: str,
            columns: List[str],
            filters: Dict[str, List[str]],
            exclude_outliers: bool = True,
            normalise: bool = True
    ):
        assert len(columns) > 0
        prepped_data = self.__prep_data__(columns, filters, exclude_outliers, normalise)
        if visualisation_type == 'kde':
            if len(columns) == 2:
                self.__kde_visualise_2d__(prepped_data, column_1=columns[0], column_2=columns[1])
            elif len(columns) == 1:
                self.__kde_visualise_1d__(prepped_data, columns[0])
            else:
                print("This style of visualisation is only available for up to two columns")
        elif visualisation_type == 'polyhedron':
            if len(columns) != 2:
                print("This style of visualisation is only available for two columns")
                return
            self.__polyhedron_visualisation__(prepped_data, columns)
        elif visualisation_type == 'venn':
            if len(filters[self.identifier_header]) >= 2:
                self.__venn_diagram_visualisation__(prepped_data, columns)
            else:
                print("This style of visualisation requires at least two identifiers.")
        else:
            print("Available visualisation types: 'kde', 'polyhedron', 'venn'")

    def __labeled_polyhedrons_and_halfspaces__(self, data: pd.DataFrame, columns: List[str]):
        labeled_convex_hulls_and_halfspaces = []
        for identifier in data[self.identifier_header].unique():
            convex_hull = ConvexHull(data[data[self.identifier_header] == identifier][columns])
            labeled_convex_hulls_and_halfspaces.append((
                identifier,
                convex_hull,
                np.hstack((convex_hull.equations[:, :-1], convex_hull.equations[:, -1][:, np.newaxis]))
            ))
        return labeled_convex_hulls_and_halfspaces

    @staticmethod
    def __combined_hull__(halfspaces, interior_point):
        try:
            hs_intersection = HalfspaceIntersection(halfspaces, interior_point)
            combined_hull = ConvexHull(hs_intersection.intersections)
        except ValueError:
            # If there is an error in constructing the HalfspaceIntersection, they do not overlap
            combined_hull = None
        return combined_hull

    def __polyhedron_visualisation__(self, data: pd.DataFrame, columns: List[str]):
        labeled_convex_hulls_and_halfspaces = self.__labeled_polyhedrons_and_halfspaces__(data, columns)
        all_halfspaces = np.vstack([tup[2] for tup in labeled_convex_hulls_and_halfspaces])
        intersect_hull = self.__combined_hull__(all_halfspaces, np.mean(data[columns], axis=0))

        if intersect_hull is not None:
            polyhedron = Polygon(intersect_hull.points[intersect_hull.vertices])
            x, y = polyhedron.exterior.xy
            plt.fill(x, y, label='Intersection')
        for tup in labeled_convex_hulls_and_halfspaces:
            label, convex_hull = tup[0], tup[1]
            polyhedron = Polygon(convex_hull.points[convex_hull.vertices])
            x, y = polyhedron.exterior.xy
            plt.plot(x, y, label=label)
        plt.legend()
        plt.show()

    def __venn_diagram_visualisation__(self, data: pd.DataFrame, columns: List[str]):
        labeled_convex_hulls_and_halfspaces = self.__labeled_polyhedrons_and_halfspaces__(data, columns)
        all_halfspaces = np.vstack([tup[2] for tup in labeled_convex_hulls_and_halfspaces])
        intersect_hull = self.__combined_hull__(all_halfspaces, np.mean(data[columns], axis=0))

        volumes = [x[1].volume for x in labeled_convex_hulls_and_halfspaces]
        labels = [x[0] for x in labeled_convex_hulls_and_halfspaces]
        intersect_volume = intersect_hull.volume
        total_volume = sum(volumes) - intersect_volume

        overlap_percentage = intersect_volume / total_volume * 100
        percentages = [v / total_volume * 100 for v in volumes]

        # Draw the Venn diagram
        percentages.append(overlap_percentage)
        venn2(subsets=percentages, set_labels=labels, subset_label_formatter=lambda x: f"{x:.2f}%")

        # Add title and display the plot
        plt.title(f'Venn Diagram with {overlap_percentage:.2f}% Overlap')
        plt.show()

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

    def __kde_visualise_1d__(self, data: pd.DataFrame, column: str):
        fig, ax = plt.subplots()
        sns.kdeplot(x=column, data=data, hue=self.identifier_header, ax=ax, legend=False, fill=True, linewidth=0)
        sns.rugplot(x=column, data=data, hue=self.identifier_header, ax=ax, legend=True, height=0.1)
        ax.set_yticks([])
        ax.set_ylabel('')
        plt.show()

    def __kde_visualise_2d__(self, data:pd.DataFrame, column_1: str, column_2: str):
        fig, ax = plt.subplots()
        sns.kdeplot(x=column_1, y=column_2, data=data, hue=self.identifier_header, fill=True, alpha=.3, ax=ax,
                    bw_adjust=1, levels=2)
        sns.scatterplot(x='col_1', y='col_2', data=data, hue='metaheuristic', ax=ax)
        plt.show()

