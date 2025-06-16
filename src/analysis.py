import pandas as pd
import re
from datetime import datetime
import numpy as np
from column_name_map import normalize_dataframe_columns

# --- Utility: Rename columns for readability ---
def rename_columns_for_readability(df):
    if df is None or df.empty:
        return df
    new_cols = {}
    for col in df.columns:
        temp_col = str(col).replace('_', ' ')
        temp_col = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", temp_col)
        temp_col = re.sub(r"([A-Z])([A-Z][a-z])", r"\1 \2", temp_col)
        temp_col = ' '.join(temp_col.split())
        new_cols[col] = temp_col.title()
    return df.rename(columns=new_cols)

# 1. Initial Stock Analysis
# Initial Stock Movements by Lotid
def analyze_initial_stock_by_lotid(df):
    """
    Devuelve los movimientos de stock inicial por Lotid y Exporter Clean, filtrando por temporada si la columna 'Season' está presente en el DataFrame global.
    Estandariza la agrupación y filtrado para asegurar consistencia en todos los reportes.
    """
    df = normalize_dataframe_columns(df)
    if df is None or df.empty:
        return pd.DataFrame()
    required_cols = ['Lotid', 'Exporter Clean', 'Recvqnt', 'Refdate', 'Variety', 'Sourceidx']
    if not all(col in df.columns for col in required_cols):
        print("Missing Columns for initial stock analysis.")
        return pd.DataFrame()
    # Filtrado por temporada si existe la columna 'Season' y hay un único valor
    if 'Season' in df.columns:
        seasons = df['Season'].dropna().unique()
        if len(seasons) == 1:
            df = df[df['Season'] == seasons[0]]
    # Solo incluir filas válidas
    filtered = df[(df['Sourceidx'] == 1) & (df['Recvqnt'] > 0)].copy()
    filtered = filtered[filtered['Exporter Clean'].fillna('') != 'Todos']
    filtered = filtered[['Lotid', 'Exporter Clean', 'Recvqnt', 'Refdate', 'Variety']]
    filtered = filtered.rename(columns={
        'Recvqnt': 'Initial Stock',
        'Refdate': 'Entry Date'
    })
    filtered = filtered.sort_values(['Exporter Clean', 'Lotid', 'Entry Date'])
    filtered['Entry Date'] = pd.to_datetime(filtered['Entry Date'], errors='coerce').dt.strftime('%m/%d/%Y')
    return rename_columns_for_readability(filtered.reset_index(drop=True))

# 1.1. Report: Initial Stock by Exporter Summary
def analyze_initial_stock_summary(df):
    """
    Initial stock summary by exporter.
    """
    initial_stock = analyze_initial_stock_by_lotid(df)
    if initial_stock is None or initial_stock.empty:
        return pd.DataFrame()
    stock_summary = initial_stock.groupby('Exporter Clean').agg(
        Initial_Stock=('Initial Stock', 'sum'),
        Containers=('Lotid', 'nunique')
    ).reset_index()
    return rename_columns_for_readability(stock_summary)

# 2. Sales Analysis
# 2. Sales Movements by Lotid and Exporter
def analyze_sales_detail_by_lotid_and_exporter(df):
    """
    Returns all sales movements (one row per sale) by Lotid and Exporter,
    with formatted columns and calculated price columns.
    We will use 
    sales_detail = analyze_sales_detail_by_lotid_and_exporter(df_season) 
    for all sales related data
    """
    """
    Devuelve todos los movimientos de venta por Lotid y Exporter Clean, filtrando por temporada si la columna 'Season' está presente y es única.
    Estandariza la agrupación y filtrado para asegurar consistencia en todos los reportes.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    df = normalize_dataframe_columns(df)
    df = df.rename(columns={c: c.strip() for c in df.columns})
    # Filtrado por temporada si existe la columna 'Season' y hay un único valor
    if 'Season' in df.columns:
        seasons = df['Season'].dropna().unique()
        if len(seasons) == 1:
            df = df[df['Season'] == seasons[0]]
    sales = df[
        (df['Trxtype'] == 1) &
        (df['Sourceidx'] == 5) &
        (df['Invcicqnt'] > 0) &
        (df['Retailer Name'] != "N/A")
    ].copy()
    sales = sales[sales['Exporter Clean'].fillna('') != 'Todos']
    # Rename columns for output, incluyendo 'Price Per Case Invc' a 'Sale Price Calc'
    sales = sales.rename(columns={
        'Refdate': 'Sale Date',
        'Invcicqnt': 'Sale Quantity',
        'Saleamt': 'Sales Amount',
        'Price Per Case Invc': 'Sale Price Calc',
        'Pricepercase Cleaned': 'Price Four Star',
        'Gradeinvc': 'Size'
    })

    required_columns = [
        'Exporter Clean', 'Lotid', 'Retailer Name', 'Sale Date',
        'Sale Quantity', 'Sales Amount', 'Sale Price Calc', 'Variety',
        'Price Four Star', 'Packaging Style', 'Packaging Detail', 'Size', 'Exporter Country'
    ]
    for col in required_columns:
        if col not in sales.columns:
            sales[col] = np.nan

    # Format columns
    sales['Sale Date'] = pd.to_datetime(sales['Sale Date'], errors='coerce').dt.strftime('%m/%d/%Y')
    # Export as numbers, not formatted strings
    sales['Sale Quantity'] = pd.to_numeric(sales['Sale Quantity'], errors='coerce')
    sales['Sales Amount'] = pd.to_numeric(sales['Sales Amount'], errors='coerce')
    sales['Sale Price Calc'] = pd.to_numeric(sales['Sale Price Calc'], errors='coerce')
    sales['Price Four Star'] = pd.to_numeric(sales['Price Four Star'], errors='coerce')
    sales['Size'] = sales['Size'].apply(lambda x: str(x) if pd.notnull(x) else "")

    # Calculate Price Difference: Price Four Star - Sale Price Calc (both as float)
    def calc_price_diff(row):
        try:
            pfs = float(str(row['Price Four Star']).replace('$', '').replace(',', ''))
            spc = float(str(row['Sale Price Calc']).replace('$', '').replace(',', ''))
            return pfs - spc if pd.notnull(pfs) and pd.notnull(spc) else np.nan
        except Exception:
            return np.nan

    sales['Price Difference'] = sales.apply(calc_price_diff, axis=1)

    # Final columns order
    final_columns = [
        'Exporter Clean', 'Lotid', 'Retailer Name', 'Sale Date',
        'Sale Quantity', 'Sales Amount', 'Price Four Star', 'Sale Price Calc',
        'Price Difference', 'Variety', 'Packaging Style', 'Packaging Detail', 'Size', 'Exporter Country',
    ]
    sales = sales[final_columns].sort_values(['Exporter Clean', 'Lotid', 'Sale Date'])

    return rename_columns_for_readability(sales.reset_index(drop=True))

# 2.1. Report: Sales by Exporter Summary (no retailer breakdown)
def analyze_sales_summary_by_exporter(df):
    """
    Returns a summary of sales by exporter, using the detailed sales DataFrame.
    """
    sales_detail = analyze_sales_detail_by_lotid_and_exporter(df)
    if sales_detail is None or sales_detail.empty:
        return pd.DataFrame()
    # Convert columns back to numeric for aggregation (robust to already-numeric columns)
    if sales_detail['Sale Quantity'].dtype == object:
        sales_detail['Sale Quantity'] = pd.to_numeric(sales_detail['Sale Quantity'].str.replace(',', ''), errors='coerce')
    else:
        sales_detail['Sale Quantity'] = pd.to_numeric(sales_detail['Sale Quantity'], errors='coerce')

    if sales_detail['Sales Amount'].dtype == object:
        sales_detail['Sales Amount'] = pd.to_numeric(sales_detail['Sales Amount'].str.replace('$', '').replace(',', '', regex=True), errors='coerce')
    else:
        sales_detail['Sales Amount'] = pd.to_numeric(sales_detail['Sales Amount'], errors='coerce')

    if sales_detail['Sale Price Calc'].dtype == object:
        sales_detail['Sale Price Calc'] = pd.to_numeric(sales_detail['Sale Price Calc'].str.replace('$', '').replace(',', '', regex=True), errors='coerce')
    else:
        sales_detail['Sale Price Calc'] = pd.to_numeric(sales_detail['Sale Price Calc'], errors='coerce')
    summary = sales_detail.groupby('Exporter Clean').agg(
        Total_Sale_Quantity=('Sale Quantity', 'sum'),
        Total_Sales_Amount=('Sales Amount', 'sum'),
        Avg_Sale_Price_Calc=('Sale Price Calc', 'mean')
    ).reset_index()
    # Export as numbers, not formatted strings
    return rename_columns_for_readability(summary)

# Different df for Sales Summary by Exporter


# 2.3. Odd Retailers Analysis
def analyze_odd_retailers(df):
    print("\n--- Analyzing Odd Retailer Sales ---")
    if df is None or df.empty:
        print("Cannot analyze odd retailers: DataFrame is None or empty."); return pd.DataFrame()
    df = normalize_dataframe_columns(df)
    required_cols = ['Exporter Clean', 'Retailer Name', 'Trxtype', 'Invcicqnt', 'Saleamt', 'Lotid']
    if not all(col in df.columns for col in required_cols):
        print("Odd retailer analysis cannot proceed: Missing columns."); return pd.DataFrame()
    odd_sales = df[(df['Trxtype'] == 1) & (df['Invcicqnt'] != 0) & (df['Saleamt'].fillna(0) == 0) & (df['Retailer Name'] != "N/A") & (df['Retailer Name'] != "N/A (Likely Product/Exporter Info)")].copy()
    if odd_sales.empty:
        print("No 'odd retailer' sales found."); return pd.DataFrame()
    odd_retailer_summary = odd_sales.groupby(['Exporter Clean', 'Retailer Name', 'Lotid']).agg(Total_Cases_Odd_Sale=('Invcicqnt', 'sum'), Total_Amount_Odd_Sale=('Saleamt', 'sum')).reset_index()
    print(f"Found {len(odd_retailer_summary)} instances of 'odd retailer' sales.")
    return rename_columns_for_readability(odd_retailer_summary)

# 3. Inventory Analysis
# Inventory Analysis By Exporter
def analyze_inventory_by_exporter_fifo(df):
    """
    Returns a detailed DataFrame with all initial stock entries and sales movements by Lotid,
    showing each movement, current inventory, and weighted days in inventory.
    Uses consistent column names and structure as analyze_sales_detail_by_lotid_and_exporter and analyze_initial_stock_by_lotid.
    """
    if df is None or df.empty:
        print("Cannot analyze inventory: DataFrame is None or empty.")
        return pd.DataFrame()
    df = normalize_dataframe_columns(df)

    # 1. Initial Stock Movements
    initial_stock = df[
        (df['Sourceidx'] == 1) & (df['Recvqnt'] > 0)
    ][['Exporter Clean', 'Lotid', 'Recvqnt', 'Refdate', 'Variety', 'Packaging Style']].copy()
    initial_stock = initial_stock.rename(columns={
        'Recvqnt': 'Initial Stock',
        'Refdate': 'Entry Date'
    })
    initial_stock['Sale Quantity'] = np.nan
    initial_stock['Sale Date'] = np.nan
    initial_stock['Retailer Name'] = np.nan
    initial_stock['Sales Amount'] = np.nan

    # 2. Sales Movements
    sales = df[
        (df['Trxtype'] == 1) &
        (df['Sourceidx'] == 5) &
        (df['Invcicqnt'] > 0)
    ][['Exporter Clean', 'Lotid', 'Invcicqnt', 'Refdate', 'Variety', 'Retailer Name', 'Saleamt', 'Packaging Style']].copy()
    sales = sales.rename(columns={
        'Invcicqnt': 'Sale Quantity',
        'Refdate': 'Sale Date',
        'Saleamt': 'Sales Amount'
    })
    sales['Initial Stock'] = np.nan
    sales['Entry Date'] = np.nan

    # 3. Unify columns
    final_columns = [
        'Exporter Clean', 'Lotid', 'Entry Date', 'Initial Stock',
        'Sale Date', 'Sale Quantity', 'Variety', 'Retailer Name', 'Sales Amount', 'Packaging Style'
    ]
    initial_stock = initial_stock[final_columns]
    sales = sales[final_columns]

    # 4. Concatenate all movements
    movements = pd.concat([initial_stock, sales], ignore_index=True, sort=False)

    # 5. Calculate current inventory per Lotid
    inventory = movements.groupby('Lotid').agg({
        'Initial Stock': 'sum',
        'Sale Quantity': 'sum'
    }).reset_index()
    inventory['Current Inventory'] = inventory['Initial Stock'] - inventory['Sale Quantity']
    inventory = inventory[['Lotid', 'Current Inventory']]

    # 6. Calculate Weighted Days In Inventory per Lotid
    days_inventory = []
    for lotid, group in movements.groupby('Lotid'):
        initial_lot = initial_stock[initial_stock['Lotid'] == lotid]
        sales_lot = sales[sales['Lotid'] == lotid]
        # Weighted entry date
        if not initial_lot.empty:
            entry_date_weighted = np.average(
                pd.to_datetime(initial_lot['Entry Date']).astype(np.int64),
                weights=initial_lot['Initial Stock']
            )
            entry_date_weighted = pd.to_datetime(entry_date_weighted)
        else:
            entry_date_weighted = pd.NaT
        # Weighted sale date
        if not sales_lot.empty:
            sale_date_weighted = np.average(
                pd.to_datetime(sales_lot['Sale Date']).astype(np.int64),
                weights=sales_lot['Sale Quantity']
            )
            sale_date_weighted = pd.to_datetime(sale_date_weighted)
        else:
            sale_date_weighted = pd.NaT
        if pd.notnull(entry_date_weighted) and pd.notnull(sale_date_weighted):
            days = (sale_date_weighted - entry_date_weighted).days
        else:
            days = np.nan
        days_inventory.append({'Lotid': lotid, 'Weighted Days In Inventory': days})
    days_inventory = pd.DataFrame(days_inventory)

    # 7. Merge inventory and days in inventory
    movements = movements.merge(inventory, on='Lotid', how='left')
    movements = movements.merge(days_inventory, on='Lotid', how='left')

    # 8. Format dates
    movements['Entry Date'] = pd.to_datetime(movements['Entry Date'], errors='coerce').dt.strftime('%m/%d/%Y')
    movements['Sale Date'] = pd.to_datetime(movements['Sale Date'], errors='coerce').dt.strftime('%m/%d/%Y')

    # 9. Reorder columns
    final_columns = [
        'Exporter Clean', 'Lotid', 'Entry Date', 'Initial Stock',
        'Sale Date', 'Sale Quantity', 'Variety', 'Retailer Name', 'Sales Amount',
        'Packaging Style', 'Current Inventory', 'Weighted Days In Inventory'
    ]
    movements = movements[final_columns]
    movements = movements.sort_values(['Exporter Clean', 'Lotid', 'Entry Date', 'Sale Date'])

    # Export as numbers, not formatted strings

    return movements.reset_index(drop=True)

# 3.1. Report: Inventory By Exporter Summary
def analyze_inventory_summary_by_exporter(df_season):
    """
    Analyzes inventory by exporter using FIFO method.
    Returns a summary DataFrame with Initial Stock, Sale Quantity, Current Inventory, and Calculated Inventory.
    """
    if df_season is None or df_season.empty:
        print("Cannot analyze inventory summary: DataFrame is None or empty.")
        return pd.DataFrame()
    df_season = normalize_dataframe_columns(df_season)
    # Analyze inventory by exporter using FIFO  
    inventory_summary = analyze_inventory_by_exporter_fifo(df_season)
    for col in ['Initial Stock', 'Sale Quantity', 'Current Inventory']:
        if col in inventory_summary.columns:
            inventory_summary[col] = (
                inventory_summary[col]
                .replace('', np.nan)
                .replace(',', '', regex=True)
                .astype(float)
            )   
    inventory_summary = inventory_summary.groupby('Exporter Clean').agg({
        'Initial Stock': 'sum',
        'Sale Quantity': 'sum',
        'Current Inventory': 'sum'
    }).reset_index()
    inventory_summary['Calculated Inventory'] = inventory_summary['Initial Stock'] - inventory_summary['Sale Quantity']
    cols = ['Exporter Clean', 'Initial Stock', 'Sale Quantity', 'Calculated Inventory', 'Current Inventory']
    inventory_summary = inventory_summary[cols]
    return rename_columns_for_readability(inventory_summary)

# ChatGPT Inventory
# 3.2. Virtual Inventory Analysis
# initial_stock (output of analyze_initial_stock_by_lotid(df_season))
# sales_detail (output of analyze_sales_detail_by_lotid_and_exporter(df_season))

# Create the virtual inventory DataFrame
def create_virtual_inventory_df(initial_stock, sales_detail):
    """
    Merges initial stock and sales details into a single transactional inventory DataFrame.
    Calculates inventory balance, days in inventory, and unifies all information by Exporter and Lotid.
     - initial_stock: DataFrame from analyze_initial_stock_by_lotid
        - sales_detail: DataFrame from analyze_sales_detail_by_lotid_and_exporter
    Returns:
        DataFrame with columns: Exporter, Lotid, Date, Movement, Quantity, Inventory Balance, 
        Days In Inventory, Variety, Packaging Style,
    """
    # 1. Prepare entries DataFrame (initial stock)
    entries = initial_stock.rename(columns={
        'Exporter Clean': 'Exporter',
        'Initial Stock': 'Quantity',
        'Entry Date': 'Date',
        'Variety': 'Variety',
        'Packaging Style': 'Packaging Style',
        'Lotid': 'Lotid'
    }).copy()
    entries['Movement'] = 'Entry'
    entries['Quantity'] = entries['Quantity'].astype(float)
    
    # 2. Prepare sales DataFrame (stock out)
    sales = sales_detail.rename(columns={
        'Exporter Clean': 'Exporter',
        'Sale Quantity': 'Quantity',
        'Sale Date': 'Date',
        'Variety': 'Variety',
        'Packaging Style': 'Packaging Style',
        'Lotid': 'Lotid'
    }).copy()
    sales['Movement'] = 'Sale'
    # Remove commas and convert sale quantities to negative numbers
    sales['Quantity'] = sales['Quantity'].replace({',': ''}, regex=True).astype(float) * -1

    # 3. Merge entries and sales
    df_all = pd.concat([entries, sales], ignore_index=True)
    # Convert date column to datetime
    df_all['Date'] = pd.to_datetime(df_all['Date'], errors='coerce')
    # Sort by Exporter, Lotid, Date, and Movement
    df_all = df_all.sort_values(['Exporter', 'Lotid', 'Date', 'Movement'], ascending=[True, True, True, True])
    
    # 4. Calculate running inventory balance per Lotid/Exporter
    df_all['Inventory Balance'] = df_all.groupby(['Exporter', 'Lotid'])['Quantity'].cumsum()
    
    # 5. Calculate days in inventory (since first entry for each Lotid)
    df_all['First Entry Date'] = df_all.groupby(['Exporter', 'Lotid'])['Date'].transform('min')
    df_all['Days In Inventory'] = (df_all['Date'] - df_all['First Entry Date']).dt.days
    
    # 6. Forward and backward fill missing Variety and Packaging Style
    df_all['Variety'] = df_all.groupby(['Exporter', 'Lotid'])['Variety'].ffill().bfill()
    df_all['Packaging Style'] = df_all.groupby(['Exporter', 'Lotid'])['Packaging Style'].ffill().bfill()
    
    # Format date as MM/DD/YYYY
    df_all['Date'] = df_all['Date'].dt.strftime('%m/%d/%Y')
    
    # 7. Select and reorder columns
    df_all = df_all[[
        'Exporter', 'Lotid', 'Date', 'Movement', 'Quantity', 'Inventory Balance',
        'Days In Inventory', 'Variety', 'Packaging Style'
    ]].reset_index(drop=True)
    return df_all

# 3.3 Analyze Virtual Inventory
def analyze_inventory(df_inventory):
    """
    Analyzes the transactional inventory DataFrame.
    Returns:
      - Current inventory per Lotid and Exporter (including inventory age)
      - Average number of entries per Lotid
      - Average number of sales per Lotid
      - Sales ratio (sold vs initial stock) per Lotid
    """
    results = {}

    # A. Current inventory (latest row for each Lotid/Exporter)
    last_balances = df_inventory.sort_values('Date').groupby(['Exporter', 'Lotid']).tail(1)
    results['current_inventory'] = last_balances[['Exporter', 'Lotid', 'Inventory Balance', 'Date', 'Days In Inventory', 'Variety', 'Packaging Style']].sort_values(['Exporter', 'Lotid'])

    # B. Average entries per Lotid
    entries = df_inventory[df_inventory['Movement'] == 'Entry']
    avg_entries = entries.groupby(['Exporter', 'Lotid']).size().groupby('Lotid').mean()
    results['avg_entries_per_lotid'] = avg_entries

    # C. Average sales per Lotid
    sales = df_inventory[df_inventory['Movement'] == 'Sale']
    avg_sales = sales.groupby(['Exporter', 'Lotid']).size().groupby('Lotid').mean()
    results['avg_sales_per_lotid'] = avg_sales

    # D. Sales ratio (total sales vs total entries per Lotid)
    total_entries = entries.groupby(['Exporter', 'Lotid'])['Quantity'].sum().abs()
    total_sales = sales.groupby(['Exporter', 'Lotid'])['Quantity'].sum().abs()
    sales_ratio = (total_sales / total_entries).fillna(0)
    results['sales_ratio_per_lotid'] = sales_ratio

    return results

# 4 Deductions Analysis
# 4.1. Deductions Analysis Against Sales 
def analyze_deductions_exporter_view(df, sales_detail):
    print("\n--- Analyzing Deductions (Exporter View - excluding Advances) ---")
    if df is None or df.empty:
        print("Cannot analyze exporter deductions: DataFrame is None or empty."); return pd.DataFrame()
    df = normalize_dataframe_columns(df)
    # Filtrado por temporada si existe la columna 'Season' y hay un único valor
    if 'Season' in df.columns:
        seasons = df['Season'].dropna().unique()
        if len(seasons) == 1:
            df = df[df['Season'] == seasons[0]]
    if not all(col in df.columns for col in ['Lotid', 'Exporter Clean', 'Trxtype', 'Chargedescr', 'Chgamt', 'Invcicqnt', 'Is Advance', 'Is Produce Pay Commission']):
        print("Exporter deduction analysis cannot proceed: Missing columns."); return pd.DataFrame()
    deductions_df = df[(df['Trxtype'] == 2) & (df['Chgamt'] > 0) & (df['Is Advance'] == False) & (((df['Is Produce Pay Commission'] == False) | (df['Chgamt'] > 0)))].copy()
    if deductions_df.empty:
        print("No relevant deduction entries found for Exporter View."); return pd.DataFrame()
    # Sales detail should be provided as a separate DataFrame from analyze_sales_detail_by_lotid_and_exporter
    sales_detail = sales_detail.copy()
    if 'Season' in sales_detail.columns:
        seasons = sales_detail['Season'].dropna().unique()
        if len(seasons) == 1:
            sales_detail = sales_detail[sales_detail['Season'] == seasons[0]]
    if sales_detail['Sale Quantity'].dtype == object:
        sales_detail['Sale Quantity'] = pd.to_numeric(sales_detail['Sale Quantity'].str.replace(',', ''), errors='coerce')
    else:
        sales_detail['Sale Quantity'] = pd.to_numeric(sales_detail['Sale Quantity'], errors='coerce')

    if sales_detail['Sales Amount'].dtype == object:
        sales_detail['Sales Amount'] = pd.to_numeric(sales_detail['Sales Amount'].str.replace('$', '').replace(',', '', regex=True), errors='coerce')
    else:
        sales_detail['Sales Amount'] = pd.to_numeric(sales_detail['Sales Amount'], errors='coerce')

    if sales_detail['Sale Price Calc'].dtype == object:
        sales_detail['Sale Price Calc'] = pd.to_numeric(sales_detail['Sale Price Calc'].str.replace('$', '').replace(',', '', regex=True), errors='coerce')
    else:
        sales_detail['Sale Price Calc'] = pd.to_numeric(sales_detail['Sale Price Calc'], errors='coerce')
    total_sold = sales_detail.groupby(['Lotid', 'Exporter Clean'])['Sale Quantity'].sum().reset_index()
    total_sold = total_sold.rename(columns={'Sale Quantity': 'Total Sold'})
    deductions_df = pd.merge(deductions_df, total_sold, on=['Lotid', 'Exporter Clean'], how='left')
    deductions_df['Total Sold'] = deductions_df['Total Sold'].fillna(0)
    lot_deductions_summary = deductions_df.groupby(['Lotid', 'Exporter Clean', 'Chargedescr', 'Total Sold'])['Chgamt'].sum().reset_index()
    lot_deductions_summary.rename(columns={'Chgamt': 'Total Deduction Amount'}, inplace=True)
    lot_deductions_summary['Avg Deduction Per Case'] = np.where(
        lot_deductions_summary['Total Sold'] > 0,
        lot_deductions_summary['Total Deduction Amount'] / lot_deductions_summary['Total Sold'],
        np.nan
    )
    print("Deduction analysis (Exporter View) numeric complete.")
    return rename_columns_for_readability(lot_deductions_summary)

# 4.2. Pivoted Deduction by Lotid
def analyze_deductions_by_category_per_lot(df):
    print("\n--- Analyzing Deductions by Category per Lot ---")
    if df is None or df.empty:
        print("Cannot analyze deductions: DataFrame is None or empty."); return pd.DataFrame()
    df = normalize_dataframe_columns(df)
    # Filtrado por temporada si existe la columna 'Season' y hay un único valor
    if 'Season' in df.columns:
        seasons = df['Season'].dropna().unique()
        if len(seasons) == 1:
            df = df[df['Season'] == seasons[0]]
    if not all(col in df.columns for col in ['Lotid', 'Exporter Clean', 'Trxtype', 'Chargedescr', 'Chgamt', 'Is Advance', 'Is Produce Pay Commission']):
        print("Deduction category analysis cannot proceed: Missing columns."); return pd.DataFrame()
    deductions_to_pivot = df[(df['Trxtype'] == 2) & (df['Is Advance'] == False) & (((df['Is Produce Pay Commission'] == False) | (df['Chgamt'] > 0)) & (df['Chgamt'] > 0))].copy()
    if deductions_to_pivot.empty:
        print("No relevant deduction entries to pivot."); return pd.DataFrame()
    pivot_table = pd.pivot_table(deductions_to_pivot, index=['Lotid', 'Exporter Clean'], columns='Chargedescr', values='Chgamt', aggfunc='sum', fill_value=0).reset_index()
    print("Deduction analysis (Category per Lot) complete.")
    return rename_columns_for_readability(pivot_table)

# 4.3. Deductions Analysis Against Initial Stock
# This function analyzes deductions against initial stock, consolidating by Lotid, Exporter Clean, Exporter Country, and Chargedescr.
# It calculates total deduction amounts, total deduction quantities, total initial stock per Lotid, and cost per case.
def analyze_deductions_initial_stock(
    df, 
    country_filter=None
):
    """
    Returns a consolidated DataFrame with all deductions (trxtype==2 and chgamt>0)
    by Lotid, Exporter Clean, Exporter Country, and Chargedescr, including:
      - Total deduction amount and quantity
      - Total initial stock per Lotid (sum of all initial stock entries for each Lotid)
      - Cost per case (deduction/initial stock)
    Ready to export to CSV/Excel.
    """
    df = normalize_dataframe_columns(df)
    # Filtrado por temporada si existe la columna 'Season' y hay un único valor
    if 'Season' in df.columns:
        seasons = df['Season'].dropna().unique()
        if len(seasons) == 1:
            df = df[df['Season'] == seasons[0]]
    # 1. Get total initial stock per Lotid (sum for each Lotid)
    initial_stock_df = analyze_initial_stock_by_lotid(df)
    if initial_stock_df is None or initial_stock_df.empty or 'Initial Stock' not in initial_stock_df.columns:
        print("No initial stock data found.")
        return pd.DataFrame()
    if 'Initial Stock' in initial_stock_df.columns:
        total_initial_stock = initial_stock_df.groupby('Lotid', as_index=False)['Initial Stock'].sum()
        total_initial_stock = total_initial_stock.rename(columns={"Initial Stock": "Total Initial Stock"})
    else:
        print("Warning: 'Initial Stock' column not found in initial_stock_df. Returning empty DataFrame.")
        return pd.DataFrame()

    # 2. Filter relevant deductions
    deductions = df[
        (df['Trxtype'] == 2) &
        (df['Chgamt'] > 0) &
        (df['Chargedescr'].notna())
    ].copy()
    if deductions.empty:
        print("No deduction entries found.")
        return pd.DataFrame()

    # 3. Group by Lotid, Exporter Clean, Exporter Country, Chargedescr
    deductions_grouped = deductions.groupby(
        ['Lotid', 'Exporter Clean', 'Exporter Country', 'Chargedescr']
    ).agg(
        Total_Deduction_Amount=('Chgamt', 'sum'),
        Total_Deduction_Quantity=('Chgqnt', 'sum')
    ).reset_index()

    # 4. Merge with total initial stock per Lotid
    merged = deductions_grouped.merge(
        total_initial_stock,
        on='Lotid',
        how='left'
    )

    # 5. Cost per case (handle division by zero)
    merged['Cost Per Case'] = merged.apply(
        lambda row: row['Total_Deduction_Amount'] / row['Total Initial Stock'] if row['Total Initial Stock'] and row['Total Initial Stock'] > 0 else 0, axis=1
    )

    # 6. Filter by country if needed
    if country_filter:
        merged = merged[merged['Exporter Country'].isin(country_filter)]

    # 7. Order columns for export
    cols_export = [
        'Lotid', 'Exporter Clean', 'Exporter Country', 'Chargedescr',
        'Total_Deduction_Amount', 'Total_Deduction_Quantity', 'Total Initial Stock', 'Cost Per Case'
    ]
    merged = merged[cols_export]

    return merged

# 5 Financial Summary
# 5.1. Financial Summary By Exporter
# Esta función calcula el resumen financiero para cada lote, incluyendo ventas, deducciones, anticipos y FOB, sin formateo de números.
def calculate_lot_summary_with_exporter(df):
    """
    Calculates the financial summary for each lot and exporter, including:
      - Sales Quantity (cases sold)
      - Sales Amount (total sales, numeric)
      - Total Deductions (all deductions except COMMISSION and GROWER ADVANCES, from charge_summary_new)
      - COMMISSION (from charge_summary_new)
      - Advances (GROWER ADVANCES, from charge_summary_new)
      - FOB Liq (Sales Amount - Total Deductions - COMMISSION)
      - FOB per Case (FOB Liq / Sales Quantity)
      - Advance Pct Of FOB (Advances / FOB Liq)
      - % Commission (COMMISSION / (Sales Amount - Total Deductions))
    Columns: Exporter Clean, Lotid, Sales Quantity, Sales Amount, Total Deductions, COMMISSION, FOB Liq, FOB per Case, Advances, Advance Pct Of FOB, % Commission
    """
    print("\n--- Calculating Lot Financial Summary with Exporter (new logic) ---")
    if df is None or df.empty:
        print("Cannot calculate lot summary: DataFrame is None or empty.")
        return pd.DataFrame(), {}
    required_summary_cols = [
        'Lotid', 'Exporter Clean', 'Trxtype', 'Saleamt', 'Chgamt', 'Is Advance',
        'Is Produce Pay Commission', 'Chargedescr', 'Sourceidx', 'Invcicqnt', 'Retailer Name'
    ]
    if not all(col in df.columns for col in required_summary_cols):
        print("Cannot calculate lot summary: Missing one or more required columns.")
        return pd.DataFrame(), {}

    # --- SALES ---
    sales_df = df[
        (df['Trxtype'] == 1) &
        (df['Sourceidx'] == 5) &
        (df['Invcicqnt'] > 0) &
        (df['Retailer Name'] != "N/A")
    ]
    sales_per_lot = sales_df.groupby(['Lotid', 'Exporter Clean'])['Saleamt'].sum()
    sales_quantity_per_lot = sales_df.groupby(['Lotid', 'Exporter Clean'])['Invcicqnt'].sum()

    # --- CHARGES SUMMARY ---
    # Import charge_summary_new here to avoid circular import
    from analysis import charge_summary_new
    charges_df = charge_summary_new(df)
    # Total Deductions: all except COMMISSION and GROWER ADVANCES
    mask_ded = (~charges_df['Chargedescr'].str.upper().isin(['COMMISSION', 'GROWER ADVANCES']))
    total_deductions = charges_df[mask_ded].groupby(['Lotid', 'Exporter Clean'])['Chgamt'].sum()
    # COMMISSION only
    commission = charges_df[charges_df['Chargedescr'].str.upper() == 'COMMISSION'].groupby(['Lotid', 'Exporter Clean'])['Chgamt'].sum()
    # Advances (GROWER ADVANCES)
    advances = charges_df[charges_df['Chargedescr'].str.upper() == 'GROWER ADVANCES'].groupby(['Lotid', 'Exporter Clean'])['Chgamt'].sum()

    # --- BUILD SUMMARY ---
    summary_df = pd.DataFrame({
        'Sales Amount': sales_per_lot,
        'Sales Quantity': sales_quantity_per_lot,
        'Total Deductions': total_deductions,
        'COMMISSION': commission,
        'Advances': advances
    }).fillna(0)

    # --- FOB Liq ---
    summary_df['FOB Liq'] = summary_df['Sales Amount'] - summary_df['Total Deductions'] - summary_df['COMMISSION']
    # --- FOB per Case ---
    summary_df['FOB per Case'] = summary_df.apply(
        lambda row: row['FOB Liq'] / row['Sales Quantity'] if row['Sales Quantity'] > 0 else np.nan,
        axis=1
    )
    # --- Advance Pct Of FOB ---
    summary_df['Advance Pct Of FOB'] = summary_df.apply(
        lambda row: (row['Advances'] / row['FOB Liq']) * 100 if row['FOB Liq'] != 0 else 0,
        axis=1
    )
    # --- % Commission ---
    summary_df['% Commission'] = summary_df.apply(
        lambda row: (row['COMMISSION'] / (row['Sales Amount'] - row['Total Deductions'])) * 100 if (row['Sales Amount'] - row['Total Deductions']) != 0 else 0,
        axis=1
    )

    summary_df = summary_df.reset_index()

    # --- Final columns order ---
    final_columns = [
        'Exporter Clean', 'Lotid', 'Sales Quantity', 'Sales Amount',
        'Total Deductions', 'COMMISSION', 'FOB Liq', 'FOB per Case', 'Advances', 'Advance Pct Of FOB', '% Commission'
    ]
    summary_df = summary_df[final_columns]

    # --- Also create a summary per exporter ---
    exporter_summaries = {}
    for exporter in summary_df['Exporter Clean'].unique():
        df_exp = summary_df[summary_df['Exporter Clean'] == exporter].copy()
        exporter_summaries[f"Lot_Financial_Sum_{exporter.replace(' ', '_')}"] = df_exp.reset_index(drop=True)

    print("Lot financial summary with exporter calculation complete.")
    return summary_df, exporter_summaries

# 6.4. Sales Stddev Consistency Analysis
def sales_stddev_consistency(sales_detail, output_dir=None, season_name=None, stddev_threshold=0.10):
    """
    For each combination of Variety + Packaging Style + Size, analyzes the distribution of 'Price Four Star' across retailers.
    Calculates stddev, mean, CV (coefficient of variation) and marks as consistent/inconsistent.
    Returns a DataFrame and saves barplot/boxplot if output_dir is provided.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    if sales_detail is None or sales_detail.empty:
        return pd.DataFrame()
    df = sales_detail.copy()
    group_cols = ['Variety', 'Packaging Style', 'Size']
    results = []
    for name, group in df.groupby(group_cols):
        # Only consider if there are at least 2 retailers
        if group['Retailer Name'].nunique() < 2:
            continue
        prices = group[['Retailer Name', 'Price Four Star']].dropna()
        if prices.empty:
            continue
        std = prices.groupby('Retailer Name')['Price Four Star'].mean().std()
        mean = prices['Price Four Star'].mean()
        cv = std / mean if mean and not pd.isna(mean) and mean != 0 else None
        results.append({
            'Variety': name[0],
            'Packaging Style': name[1],
            'Size': name[2],
            'Stddev': std,
            'Mean': mean,
            'CV': cv,
            'N Retailers': group['Retailer Name'].nunique(),
            'Consistent': 'Consistent' if cv is not None and cv <= stddev_threshold else 'Inconsistent'
        })
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values(['Variety', 'Packaging Style', 'Size']).reset_index(drop=True)
    # --- Visualizations ---
    if output_dir is not None and not result_df.empty:
        os.makedirs(output_dir, exist_ok=True)
        # Barplot
        plt.figure(figsize=(14, 6))
        sns.barplot(data=result_df, x='Variety', y='Stddev', hue='Consistent', dodge=False, palette={'Consistent': 'green', 'Inconsistent': 'red'})
        plt.axhline(stddev_threshold, color='blue', linestyle='--', label=f'Threshold ({stddev_threshold})')
        plt.title(f'Stddev Consistency of Sales Price by Variety/Packaging/Size{f" - {season_name}" if season_name else ""}')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        barplot_path = os.path.join(output_dir, f'sales_stddev_consistency_barplot_{season_name or "summary"}.png')
        plt.tight_layout()
        plt.savefig(barplot_path)
        plt.close()
        # Boxplot
        plt.figure(figsize=(14, 6))
        sns.boxplot(data=df, x='Variety', y='Price Four Star', hue='Packaging Style')
        plt.title(f'Sales Price Distribution by Variety/Packaging/Size{f" - {season_name}" if season_name else ""}')
        plt.xticks(rotation=45, ha='right')
        boxplot_path = os.path.join(output_dir, f'sales_stddev_consistency_boxplot_{season_name or "summary"}.png')
        plt.tight_layout()
        plt.savefig(boxplot_path)
        plt.close()
    return result_df

# 6 Charge and Deductions Analysis
# Charge Summary Analysis V4
# Eliminar: analyze_charge_summary

# 6.1. Consistencia de stddev para cargos usando charge_summary_new
# Ahora revisa la consistencia de todos los cargos en la columna Chargedescr del DataFrame de charge_summary_new, sin excepciones.
def charges_stddev_consistency(df):
    """
    Para cada cargo/deducción en 'Chargedescr' de charge_summary_new,
    calcula la desviación estándar, media y coeficiente de variación (CV) de 'Cost per Box'
    a nivel Exporter, Country, Season y global.
    """
    if df is None or df.empty:
        return {}
    df = normalize_dataframe_columns(df)
    result = {}
    for charge in df['Chargedescr'].dropna().unique():
        df_charge = df[df['Chargedescr'] == charge]
        if df_charge.empty:
            continue
        std_by_exporter = df_charge.groupby('Exporter Clean')['Cost per Box'].std().rename('Std_Exporter').reset_index()
        std_by_country = df_charge.groupby('Exporter Country')['Cost per Box'].std().rename('Std_Country').reset_index()
        std_by_season = df_charge.groupby('Season')['Cost per Box'].std().rename('Std_Season').reset_index() if 'Season' in df_charge.columns else pd.DataFrame()
        std_overall = df_charge['Cost per Box'].std()
        mean = df_charge['Cost per Box'].mean()
        cv = std_overall / mean if mean and not pd.isna(mean) and mean != 0 else None
        result[charge] = {
            'std_by_exporter': std_by_exporter,
            'std_by_country': std_by_country,
            'std_by_season': std_by_season,
            'std_overall': std_overall,
            'mean': mean,
            'cv': cv
        }
    return result

def charge_summary_new(df):
    """
    Agrupa por Lotid y Chargedescr, suma Chgamt y Chgqnt, obtiene el stock inicial por Lotid y calcula el costo por caja.
    Exporta las columnas clave: Lotid, Chargedescr, Chgamt, Chgqnt, Initial Stock, Cost per Box, Exporter Clean, Exporter Country, Season.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    df = normalize_dataframe_columns(df)
    # Asegurar que existan las columnas necesarias
    required_cols = ['Lotid', 'Chargedescr', 'Chgamt', 'Chgqnt', 'Exporter Clean', 'Exporter Country', 'Season']
    for col in required_cols:
        if col not in df.columns:
            print(f"[charge_summary_new] Falta columna: {col}")
            return pd.DataFrame()
    # Stock inicial por Lotid
    initial_stock = df.groupby('Lotid', as_index=False)['Recvqnt'].sum().rename(columns={'Recvqnt': 'Initial Stock'})
    # Agrupar cargos
    charges = df.groupby(['Lotid', 'Chargedescr', 'Exporter Clean', 'Exporter Country', 'Season'], as_index=False).agg({
        'Chgamt': 'sum',
        'Chgqnt': 'sum'
    })
    # Unir con stock inicial
    charges = charges.merge(initial_stock, on='Lotid', how='left')
    charges['Cost per Box'] = charges.apply(
        lambda row: row['Chgamt'] / row['Initial Stock'] if row['Initial Stock'] and row['Initial Stock'] > 0 else None,
        axis=1
    )
    # Ordenar columnas
    cols = ['Lotid', 'Chargedescr', 'Chgamt', 'Chgqnt', 'Initial Stock', 'Cost per Box', 'Exporter Clean', 'Exporter Country', 'Season']
    charges = charges[cols]
    return charges