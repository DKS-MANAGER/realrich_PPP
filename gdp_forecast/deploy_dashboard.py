import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px # type: ignore
import pandas as pd
import os
from plotly.graph_objects import Figure # type: ignore

# Files
FORECAST_FILE = "forecasts/gdp_forecast_2026_2030_top50.csv"
HISTORY_FILE = "data/wbdata_gdp_2010_2025.csv"

# Load Data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not os.path.exists(FORECAST_FILE) or not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(), pd.DataFrame()
        
    df_forecast = pd.read_csv(FORECAST_FILE) # type: ignore
    df_history = pd.read_csv(HISTORY_FILE) # type: ignore
    
    # Standardize columns
    df_history['type'] = 'History'
    df_history.rename(columns={'GDP': 'gdp'}, inplace=True)
    df_history['year'] = pd.to_datetime(df_history['date']).dt.year
    
    df_forecast['type'] = 'Forecast'
    df_forecast.rename(columns={'forecast_mean': 'gdp'}, inplace=True)
    
    # Combine for plotting (common columns: country, year, gdp, type)
    common_cols = ['country', 'year', 'gdp', 'type']
    
    df_combined = pd.concat([
        df_history[common_cols],
        df_forecast[common_cols]
    ])
    
    return df_combined, df_forecast

df_combined, df_forecast = load_data()

# Initialize App
app = dash.Dash(__name__)

if df_combined.empty:
    app.layout = html.Div([
        html.H1("GDP Forecast Dashboard"),
        html.Div("Data not found. Please run main_forecast.py first.")
    ])
else:
    # Get available countries
    unique_countries = sorted(df_combined['country'].unique())
    
    app.layout = html.Div([
        html.H1("Global GDP Forecast (2026-2030)", style={'textAlign': 'center'}),
        
        # Country Selector
        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': c, 'value': c} for c in unique_countries],
                value=unique_countries[0] if unique_countries else None,
                clearable=False
            )
        ], style={'width': '50%', 'margin': 'auto'}),
        
        # Main Graph
        dcc.Graph(id='gdp-trend-graph'),
        
        # Rankings Table Section
        html.H3("Projected Top Economies (2030)", style={'textAlign': 'center', 'marginTop': '40px'}),
        html.Div(id='ranking-table-container', style={'width': '80%', 'margin': 'auto'})
    ])

    @app.callback(
        Output('gdp-trend-graph', 'figure'),
        [Input('country-dropdown', 'value')]
    )
    def update_graph(selected_country: str) -> Figure:
        filtered_df = df_combined[df_combined['country'] == selected_country]
        
        fig = px.line(filtered_df, x='year', y='gdp', color='type', 
                      title=f"GDP Forecast for {selected_country}",
                      markers=True)
        
        fig.update_layout(yaxis_title="GDP (Current US$)")
        return fig

    @app.callback(
        Output('ranking-table-container', 'children'),
        [Input('country-dropdown', 'value')] # Trigger update on load essentially
    )
    def update_ranking(_):
        # Filter for max year
        max_year = df_forecast['year'].max()
        ranking_df = df_forecast[df_forecast['year'] == max_year].copy()
        ranking_df = ranking_df.sort_values('gdp', ascending=False).head(20)
        
        ranking_df['gdp_trillions'] = (ranking_df['gdp'] / 1e12).map('{:,.2f} T'.format)
        
        # Simple HTML Table
        header = [
            html.Thead(
                html.Tr([html.Th("Rank"), html.Th("Country"), html.Th(f"GDP ({max_year})")])
            )
        ]
        
        rows = []
        for i, row in enumerate(ranking_df.itertuples()):
            rows.append(
                html.Tr([
                    html.Td(i+1),
                    html.Td(row.country),
                    html.Td(row.gdp_trillions)
                ])
            )
            
        body = [html.Tbody(rows)]
        
        return html.Table(header + body, className='table', style={'width': '100%', 'border': '1px solid black', 'borderCollapse': 'collapse', 'textAlign': 'center'})

if __name__ == '__main__':
    print("Starting Dashboard on http://127.0.0.1:8050/")
    app.run_server(debug=True)
    """
    # Jupyter Notebook Conversion Guide

    To run this dashboard inside a Jupyter Notebook (Google Colab, VS Code Notebooks, or JupyterLab):

    1. **Install Dependencies:**
        Run this in a cell first:
        ```python
        !pip install dash pandas plotly jupyter-dash
        ```

    2. **Refactor Execution Code:**
        Replace the `app.run_server` block with the code below. Specifically, `JupyterDash` (or the generic Dash app passing a specific mode) is needed to render inline.
    """

    # NOTE: In a real .ipynb file, you would run this in a new cell.
    # For modern Dash versions (v2.11+), no special 'JupyterDash' library is needed, 
    # you can just run it with the debug=True or use 'inline'.

    if __name__ == '__main__':
         # 'inline' mode allows the dashboard to appear directly in the notebook cell.
         # Other options: 'external' (opens in new tab), 'jupyterlab'
         app.run(debug=True, jupyter_mode='inline') 