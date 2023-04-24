"""
This module generates a Treemap chart using Plotly in Python.

It reads data from an Excel file, maps color codes to color text,
and creates a Treemap chart with labels and text labels
at the center of each rectangle block. The generated chart is saved as a PNG image file.

Example usage:
    res = TreemapChartView()
    result = res.generate_chart()
    print(result)
"""

import plotly.express as px
import plotly.io as pio
import pandas as pd

class TreemapChartView:
    """
    Class to generate Treemap chart using Plotly.
    """
    def generate_chart(self):
        """
        Generate Treemap chart using Plotly.

        Reads data from an Excel file, maps color codes to color text,
        and creates a Treemap chart with labels and text labels
        at the center of each rectangle block. The generated chart is saved as a PNG image file.

        Returns:
            str: A string indicating the result of chart generation.
        """
        try:
            # Define the data as a DataFrame
            excel_file_path = 'Heat_map.xls.xls'
            dataframe = pd.read_excel(excel_file_path, skiprows=1, usecols="A:C").dropna()
            # Convert DataFrame to dictionary
            data = dataframe.to_dict(orient='list')
            color_codes = {
                "Light green": "#90EE90",
                "Dark Green": "#70ad46",
                "One level below dark green": "#a9d08f",
                "One Level Above Light Green": "#c1e6bf",
                "Two level above Light green": "#d6edcc",
                "Two level above Light  green": "#d6edcc",
                "Two level below dark green": "#8ca16e",
                "Above Light Green": "#e2efdb",
                "White": "#FFFFFF"
            }
            data['color']= [color_codes[color_name] for color_name in data
            ['Average Team Expertise (1 - 5)']]
            data_frame = pd.DataFrame(data)
            data_frame = data_frame.rename(columns=
                                           {'Average Team Expertise (1 - 5)': 'Color',
                                            'Existing Team Members Proficient with this area': 'Values'})
            # Create the Treemap chart using plotly.express
            fig = px.treemap(data_frame, path=['Area'], values='Values',
                             color='Color', color_discrete_map=color_codes,
                             hover_data={'Values': True},
                             labels={'Values': 'Expertise Level'},
                             title='Expertise Levels by Area', branchvalues='total')
            fig.update_traces(textfont={'size': 14},
                              textposition='middle center',
                              textfont_color='black',
                              texttemplate='%{label}(%{value})')
            # Save the Treemap chart as PNG image
            #fig.show()
            pio.write_image(fig, 'treemap_chart.png', width=2000, height=1200)

            return "Chart Generated"
        except FileNotFoundError as error:
            # Catch specific exception for file not found error
            return f"File not found: {error}"


if __name__ == "__main__":
    res = TreemapChartView()
    t = res.generate_chart()
    print(t)
