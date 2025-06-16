import pandas as pd
from analysis import (
    analyze_initial_stock_by_lotid,
    analyze_sales_detail_by_lotid_and_exporter,
    analyze_inventory_by_exporter_fifo,
    analyze_deductions_initial_stock,
    analyze_deductions_exporter_view
)

# Load your main DataFrame using the correct relative path
df = pd.read_csv('data/JP Famus Report Original 05.15.25 - FAMOUS LOT DETAIL REPORT SA GRAPES 24-25.csv')

# Filter Lotids for Agrovita
agrovita_lotids = df[df['Exporter Clean'] == 'Agrovita']['Lotid'].unique().tolist()

# 1. Initial Stock
initial_stock = analyze_initial_stock_by_lotid(df)
initial_stock = initial_stock[initial_stock['Lotid'].isin(agrovita_lotids)]

# 2. Sales Detail
sales_detail = analyze_sales_detail_by_lotid_and_exporter(df)
sales_detail = sales_detail[sales_detail['Lotid'].isin(agrovita_lotids)]

# 3. Inventory Movements
inventory_movements = analyze_inventory_by_exporter_fifo(df)
inventory_movements = inventory_movements[inventory_movements['Lotid'].isin(agrovita_lotids)]

# 4. Inventory Summary by Lotid
inventory_summary = inventory_movements.groupby('Lotid').agg(
    Initial_Stock=('Initial Stock', lambda x: pd.to_numeric(x, errors='coerce').sum()),
    Sales_Quantity=('Sale Quantity', lambda x: pd.to_numeric(x, errors='coerce').sum()),
    Current_Inventory=('Current Inventory', lambda x: pd.to_numeric(x, errors='coerce').max())
).reset_index()

# 5. Deductions vs Initial Stock
deductions_initial_stock = analyze_deductions_initial_stock(df)
deductions_initial_stock = deductions_initial_stock[deductions_initial_stock['Lotid'].isin(agrovita_lotids)]

# 6. Deductions vs Sales
deductions_sales = analyze_deductions_exporter_view(df, sales_detail)
deductions_sales = deductions_sales[deductions_sales['Lotid'].isin(agrovita_lotids)]

# 7. Export all to Excel in the reports folder
import os
reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
os.makedirs(reports_dir, exist_ok=True)
excel_path = os.path.join(reports_dir, 'Agrovita Report.xlsx')

with pd.ExcelWriter(excel_path) as writer:
    initial_stock.to_excel(writer, sheet_name='Initial Stock', index=False)
    sales_detail.to_excel(writer, sheet_name='Sales Detail', index=False)
    inventory_movements.to_excel(writer, sheet_name='Inventory Movements', index=False)
    inventory_summary.to_excel(writer, sheet_name='Inventory Summary', index=False)
    deductions_initial_stock.to_excel(writer, sheet_name='Deductions Initial Stock', index=False)
    deductions_sales.to_excel(writer, sheet_name='Deductions Sales', index=False)

print(f"Report generated: {excel_path}")