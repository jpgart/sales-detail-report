import os
import sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, 'src'))
from analysis import charge_summary_new, calculate_lot_summary_with_exporter
import pandas as pd

# Configuración de rutas
R23 = os.path.join(BASE, 'reports/2025-06-12_10-23-16/CSV_Report_2023-2024')
R24 = os.path.join(BASE, 'reports/2025-06-12_10-23-16/CSV_Report_2024-2025')

def safe_sum(df, col):
    import numpy as np
    if col not in df.columns:
        return None
    # Limpieza para columnas numéricas con formato string, comas, $ y vacíos
    serie = df[col]
    if serie.dtype == object:
        # Eliminar comillas, comas, $, espacios y convertir a float
        serie = serie.astype(str).str.replace('"', '', regex=False)
        serie = serie.str.replace(',', '', regex=False)
        serie = serie.str.replace('$', '', regex=False)
        serie = serie.str.replace(' ', '', regex=False)
        serie = serie.replace({'': np.nan, 'nan': np.nan, 'None': np.nan})
        try:
            serie = serie.astype(float)
        except Exception:
            # Si falla, devolver None para indicar error de formato
            return None
    return serie.sum(skipna=True)

def check_and_print(label, val1, val2, ref=None, tol=1e-2):
    print(f"  {label}: {val1} | {val2}", end='')
    if ref is not None:
        print(f" | Ref: {ref}", end='')
        if abs((val1 or 0) - (ref or 0)) > tol or abs((val2 or 0) - (ref or 0)) > tol:
            print("  <-- DISCREPANCIA")
        else:
            print("  (OK)")
    else:
        if val1 == val2:
            print("  (OK)")
        else:
            print("  <-- DISCREPANCIA")

def auditar_temporada(ruta, temporada):
    print(f"\n---\nTEMPORADA: {temporada}\n---")

    # Cargar archivos
    p = lambda f: os.path.join(ruta, f)
    archivos = {}
    for nombre in [
        'Processed_Data.csv',
        'All_Charges_Deductions.csv',
        'Initial_Stock_All.csv',
        'Lot_Financial_Sum_All.csv',
        'Sales_Detail_By_Lotid.csv'
    ]:
        try:
            archivos[nombre] = pd.read_csv(p(nombre))
        except Exception as e:
            print(f"[ERROR] No se pudo cargar {nombre}: {e}")
            archivos[nombre] = None
    df_proc = archivos['Processed_Data.csv']
    df_chg = archivos['All_Charges_Deductions.csv']
    df_stock = archivos['Initial_Stock_All.csv']
    df_lotfin = archivos['Lot_Financial_Sum_All.csv']
    df_sales = archivos['Sales_Detail_By_Lotid.csv']

    # --- Nueva lógica: aplicar charge_summary_new y calculate_lot_summary_with_exporter ---
    if df_proc is not None:
        # Normalizar columnas si es necesario
        try:
            resumen_lotes, _ = calculate_lot_summary_with_exporter(df_proc)
        except Exception as e:
            print(f"[ERROR] No se pudo calcular el resumen financiero con la nueva lógica: {e}")
            resumen_lotes = None
    else:
        resumen_lotes = None

    # --- Validación de totales ---
    if df_lotfin is not None and resumen_lotes is not None:
        print("\nValidación de totales Lot_Financial_Sum_All vs Nueva Lógica:")
        cols_validar = [
            'Total Deductions', 'COMMISSION', 'Advances', 'FOB Liq', '% Commission', 'Advance Pct Of FOB'
        ]
        for col in cols_validar:
            val1 = safe_sum(df_lotfin, col)
            val2 = safe_sum(resumen_lotes, col)
            check_and_print(col, val1, val2)
    else:
        print("[ADVERTENCIA] No se pudo validar totales: faltan datos de Lot_Financial_Sum_All o resumen_lotes.")

    # Validar presencia de columnas clave solo en los reportes relevantes
    columnas_clave = ['Lotid', 'Exporter Clean']
    archivos_relevantes = [
        'Processed_Data.csv',
        'All_Charges_Deductions.csv',
        'Initial_Stock_All.csv',
        'Lot_Financial_Sum_All.csv',
        'Sales_Detail_By_Lotid.csv'
    ]
    for nombre in archivos_relevantes:
        df = archivos[nombre]
        if df is not None:
            faltantes = [col for col in columnas_clave if col not in df.columns]
            if faltantes:
                print(f"[ADVERTENCIA] El archivo {nombre} NO contiene las columnas clave: {faltantes}")
            else:
                print(f"[OK] {nombre} contiene columnas clave {columnas_clave}")

    def safe_group_sum(df, col, group_cols=None):
        import numpy as np
        if df is None or col not in df.columns:
            return None
        serie = df[col]
        if serie.dtype == object:
            serie = serie.astype(str).str.replace('"', '', regex=False)
            serie = serie.str.replace(',', '', regex=False)
            serie = serie.str.replace('$', '', regex=False)
            serie = serie.str.replace(' ', '', regex=False)
            serie = serie.replace({'': np.nan, 'nan': np.nan, 'None': np.nan})
            try:
                serie = serie.astype(float)
            except Exception:
                return None
        # Agrupación flexible
        if group_cols is None:
            group_cols = ['Lotid', 'Exporter Clean'] if 'Exporter Clean' in df.columns else ['Lotid']
        # Solo usar columnas que existan
        group_cols = [c for c in group_cols if c in df.columns]
        if not group_cols:
            return serie.sum(skipna=True)
        return df.assign(_val=serie).groupby(group_cols)['_val'].sum().sum(skipna=True)



    # --- FILTROS para comparación justa ---
    # Filtro para stock inicial: Sourceidx == 1, Recvqnt > 0, Exporter Clean != 'Todos'
    if df_proc is not None:
        df_proc_stock = df_proc.copy()
        if 'Sourceidx' in df_proc_stock.columns and 'Recvqnt' in df_proc_stock.columns and 'Exporter Clean' in df_proc_stock.columns:
            df_proc_stock = df_proc_stock[(df_proc_stock['Sourceidx'] == 1) & (df_proc_stock['Recvqnt'] > 0) & (df_proc_stock['Exporter Clean'].fillna('') != 'Todos')]
    else:
        df_proc_stock = None

    # Filtro para deducciones: Trxtype == 2, Chgamt > 0, Is Advance == False, Is Produce Pay Commission == False
    if df_proc is not None:
        df_proc_deduc = df_proc.copy()
        for col in ['Trxtype', 'Chgamt', 'Is Advance', 'Is Produce Pay Commission']:
            if col not in df_proc_deduc.columns:
                df_proc_deduc = None
                break
        if df_proc_deduc is not None:
            df_proc_deduc = df_proc_deduc[(df_proc_deduc['Trxtype'] == 2)
                                          & (df_proc_deduc['Chgamt'] > 0)
                                          & (df_proc_deduc['Is Advance'] == False)
                                          & (df_proc_deduc['Is Produce Pay Commission'] == False)]
    else:
        df_proc_deduc = None

    # 1. All_Charges_Deductions.csv vs Processed_Data.csv (filtrado)
    print("\nAll_Charges_Deductions.csv vs Processed_Data.csv (filtrado):")
    print("  Suma total:")
    check_and_print('Chgamt', safe_sum(df_chg, 'Chgamt'), safe_sum(df_proc_deduc, 'Chgamt'))
    check_and_print('Chgqnt', safe_sum(df_chg, 'Chgqnt'), safe_sum(df_proc_deduc, 'Chgqnt'))
    check_and_print('Initial Stock vs Recvqnt', safe_sum(df_chg, 'Initial Stock'), safe_sum(df_proc_stock, 'Recvqnt'))
    print("  Suma agrupada por Lotid, Exporter Clean, Exporter Country, Chargedescr:")
    group_fields = ['Lotid', 'Exporter Clean', 'Exporter Country', 'Chargedescr']
    check_and_print('Chgamt', safe_group_sum(df_chg, 'Chgamt', group_fields), safe_group_sum(df_proc_deduc, 'Chgamt', group_fields))
    check_and_print('Chgqnt', safe_group_sum(df_chg, 'Chgqnt', group_fields), safe_group_sum(df_proc_deduc, 'Chgqnt', group_fields))
    check_and_print('Initial Stock vs Recvqnt', safe_group_sum(df_chg, 'Initial Stock', group_fields), safe_group_sum(df_proc_stock, 'Recvqnt', group_fields))

    # 2. Initial_Stock_All.csv vs Processed_Data.csv (filtrado)
    print("\nInitial_Stock_All.csv vs Processed_Data.csv (filtrado):")
    print("  Suma total:")
    check_and_print('Initial Stock vs Recvqnt', safe_sum(df_stock, 'Initial Stock'), safe_sum(df_proc_stock, 'Recvqnt'))
    print("  Suma agrupada por Lotid (sin duplicados):")
    check_and_print('Initial Stock vs Recvqnt', safe_group_sum(df_stock, 'Initial Stock'), safe_group_sum(df_proc_stock, 'Recvqnt'))

    # 3. Lot_Financial_Sum_All.csv, Sales_Detail_By_Lotid.csv, Processed_Data.csv
    print("\nVentas (deben ser iguales en todos los reportes):")
    print("  Suma total:")
    qty_lotfin = safe_sum(df_lotfin, 'Sales Quantity')
    qty_sales = safe_sum(df_sales, 'Sale Quantity')
    qty_proc = safe_sum(df_proc, 'Invcicqnt')
    check_and_print('Sales Quantity (Lot_Financial_Sum_All)', qty_lotfin, qty_proc)
    check_and_print('Sales Quantity (Sales_Detail_By_Lotid)', qty_sales, qty_proc)

    amt_lotfin = safe_sum(df_lotfin, 'Sales Amount')
    amt_sales = safe_sum(df_sales, 'Sales Amount')
    amt_proc = safe_sum(df_proc, 'Saleamt')
    check_and_print('Sales Amount (Lot_Financial_Sum_All)', amt_lotfin, amt_proc)
    check_and_print('Sales Amount (Sales_Detail_By_Lotid)', amt_sales, amt_proc)
    print("  Suma agrupada por Lotid (sin duplicados):")
    qty_lotfin_g = safe_group_sum(df_lotfin, 'Sales Quantity')
    qty_sales_g = safe_group_sum(df_sales, 'Sale Quantity')
    qty_proc_g = safe_group_sum(df_proc, 'Invcicqnt')
    check_and_print('Sales Quantity (Lot_Financial_Sum_All)', qty_lotfin_g, qty_proc_g)
    check_and_print('Sales Quantity (Sales_Detail_By_Lotid)', qty_sales_g, qty_proc_g)

    amt_lotfin_g = safe_group_sum(df_lotfin, 'Sales Amount')
    amt_sales_g = safe_group_sum(df_sales, 'Sales Amount')
    amt_proc_g = safe_group_sum(df_proc, 'Saleamt')
    check_and_print('Sales Amount (Lot_Financial_Sum_All)', amt_lotfin_g, amt_proc_g)
    check_and_print('Sales Amount (Sales_Detail_By_Lotid)', amt_sales_g, amt_proc_g)

if __name__ == "__main__":
    auditar_temporada(R23, '2023-2024')
    auditar_temporada(R24, '2024-2025')
    print("\nComparar estos totales con el archivo original para validar integridad.")
