# --- CLEAN VERSION: Only the refactored, Jinja2-based reporting module ---
"""
HTML Reporting Module
---------------------
This module provides functions to generate interactive HTML reports from DataFrames using Jinja2 templates.
All code, comments, and column names are in English for consistency.
"""

import os
import pandas as pd
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Optional

# Constants for report paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_BASE_DIR = os.path.join(BASE_DIR, 'data', 'html data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
HTML_REPORTS_DIR = os.path.join(REPORTS_DIR, 'html_reports')
ASSETS_DIR = os.path.join(REPORTS_DIR, 'assets')

## Eliminada función load_retailer_data y dependencias de Retailer_Perf_Season

def get_dropdown_options(df: pd.DataFrame) -> dict:
    """
    Returns unique dropdown options for variety and packaging style.
    Args:
        df (pd.DataFrame): Retailer DataFrame.
    Returns:
        dict: Dropdown options.
    """
    varieties = ['All'] + sorted(df['Variety'].dropna().unique().tolist())
    pack_styles = ['All'] + sorted(df['Packaging Style'].dropna().unique().tolist())
    return {
        'varieties': varieties,
        'pack_styles': pack_styles
    }

def format_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formats columns for display: thousands separator and currency.
    Args:
        df (pd.DataFrame): DataFrame to format.
    Returns:
        pd.DataFrame: Formatted DataFrame.
    """
    df = df.copy()
    # Format 'Total Cases Sold Invc' with thousands separator
    df['Total Cases Sold Invc'] = df['Total Cases Sold Invc'].apply(
        lambda x: '{:,.0f}'.format(x) if pd.notnull(x) else ''
    )
    # Format 'Avg Price Per Case Invc' as currency with $ and comma decimal
    df['Avg Price Per Case Invc'] = df['Avg Price Per Case Invc'].apply(
        lambda x: f"${x:,.2f}".replace('.', ',') if pd.notnull(x) else ''
    )
    return df

def render_html_report(df: pd.DataFrame, dropdowns: dict, output_filename: Optional[str] = None):
    """
    Renders the interactive HTML report using Jinja2 template.
    Args:
        df (pd.DataFrame): Data to visualize.
        dropdowns (dict): Dropdown options.
        output_filename (str): Output HTML filename (optional).
    """
    # Prepare data for JS
    data_for_js = df.to_dict(orient='records')
    data_js = json.dumps(data_for_js)

    # Set up Jinja2 environment
    template_dir = os.path.join(BASE_DIR, 'src', 'templates')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('retailer_sales.html')

    html = template.render(
        varieties=dropdowns['varieties'],
        pack_styles=dropdowns['pack_styles'],
        data_js=data_js
    )

    # Output path
    if not output_filename:
        output_filename = os.path.join(HTML_REPORTS_DIR, 'retailer_sales.html')
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Interactive HTML report saved at {output_filename}")

def retailer_sales(season: str):
    """
    Generates the retailer sales HTML report for a given season.
    Args:
        season (str): Season string, e.g. '2024-2025'.
    """
    raise NotImplementedError("El reporte de desempeño de retailers ha sido eliminado. Utilice Sales_Detail_By_Lotid para análisis de ventas por retailer.")






