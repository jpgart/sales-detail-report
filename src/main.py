import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

from data_processing import process_sales_data
from analysis import (
    rename_columns_for_readability,
    # 1. Initial Stock Analysis
    analyze_initial_stock_by_lotid,
    analyze_initial_stock_summary,
    # 2. Sales Analysis
    analyze_sales_detail_by_lotid_and_exporter,
    analyze_sales_summary_by_exporter,
    analyze_odd_retailers,
    # 3. Inventory Analysis
    analyze_inventory_by_exporter_fifo,
    analyze_inventory_summary_by_exporter,
    # 5. Financial Summary
    calculate_lot_summary_with_exporter,
    # 6. Charge and Deductions Analysis
    charges_stddev_consistency
)
from qc import run_quality_control_checks
from config import (
    EXPORTER_MAPPINGS,
    EXPORTER_COUNTRY_MAP,
    GRAPE_VARIETIES_SET,
    VARIETY_NORMALIZATION_MAP,
    ALL_EXPORTER_NAMES_AND_TAGS,
    PACKAGING_DETAIL_PATTERNS,
    PACKAGING_STYLE_KEYWORDS,
    SPECIFIC_LOTID_EXPORTER_MAP,
    SHEET_DESCRIPTIONS,
    AGROLATINA_SPECIFIC_CHARGES
)
from utils import export_to_excel, generate_data_analysis_blueprint_v8, generate_qc_report_markdown
from column_name_map import normalize_dataframe_columns

SCRIPT_VERSION = "8.6"

# --- Create timestamped output directory for this run ---
from datetime import datetime
BASE_REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')
if not os.path.exists(BASE_REPORTS_DIR):
    os.makedirs(BASE_REPORTS_DIR)
RUN_TIMESTAMP = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
RUN_REPORTS_DIR = os.path.join(BASE_REPORTS_DIR, RUN_TIMESTAMP)
os.makedirs(RUN_REPORTS_DIR, exist_ok=True)

from analysis import charge_summary_new
def main():
    input_file_path = '/Users/jp/Documents/Famus 3.0/famus-report-analysis/data/JP Famus Report Original 05.15.25 - FAMOUS LOT DETAIL REPORT SA GRAPES 24-25.csv'
    is_excel_file = input_file_path.lower().endswith(('.xlsx', '.xls'))

    print(f"--- Main execution starting for Famus Extract V{SCRIPT_VERSION} ---")

    processed_data = process_sales_data(
        input_file_path,
        EXPORTER_MAPPINGS,
        EXPORTER_COUNTRY_MAP,
        GRAPE_VARIETIES_SET,
        VARIETY_NORMALIZATION_MAP,
        ALL_EXPORTER_NAMES_AND_TAGS,
        PACKAGING_DETAIL_PATTERNS,
        PACKAGING_STYLE_KEYWORDS,
        SPECIFIC_LOTID_EXPORTER_MAP,
        is_excel=is_excel_file,
        sheet_name=0
    )

    processed_data = normalize_dataframe_columns(processed_data)

    if processed_data is not None:
        print("Data processed successfully.")

        seasons_to_process = processed_data['Season'].dropna().unique()
        seasons_to_process = [s for s in seasons_to_process if s not in ["Undefined Season", "Invalid Date Format"]]

        # (Eliminado: reporte all-seasons de desempeño de retailers)

        for season_name in seasons_to_process:
            print(f"\n--- Processing data for Season: {season_name} ---")
            df_season = processed_data[processed_data['Season'] == season_name].copy()
            if df_season.empty:
                print(f"No data for season {season_name}, skipping report generation for this season.")
                continue

            # Ensure output directory for this season's CSVs exists
            season_csv_output_dir = os.path.join(RUN_REPORTS_DIR, f"CSV_Report_{season_name}")
            os.makedirs(season_csv_output_dir, exist_ok=True)

            excel_sheets_season = {}

            # 1. Initial Stock Analysis by Lotid
            excel_sheets_season["Processed_Data"] = rename_columns_for_readability(df_season.copy())
            initial_stock_all = analyze_initial_stock_by_lotid(df_season)
            excel_sheets_season["Initial_Stock_All"] = initial_stock_all

            # 1.1 Initial Stock Summary by Exporter
            initial_stock_summary = analyze_initial_stock_summary(df_season)
            excel_sheets_season["Initial_Stock_Summary"] = initial_stock_summary

            # 2. Sales Analysis by Lotid
            sales_detail = analyze_sales_detail_by_lotid_and_exporter(df_season)
            excel_sheets_season["Sales_Detail_By_Lotid"] = sales_detail

            # 2.1 Sales Summary by Exporter
            sales_summary_exporter = analyze_sales_summary_by_exporter(df_season)
            excel_sheets_season["Sales_Summary_By_Exporter"] = sales_summary_exporter


            # 2.2 Retailer Performance Detailed (ELIMINADO: toda la información relevante está en Sales_Detail_By_Lotid)
            # (Eliminado: analyze_retailer_performance_detailed y reportes Retailer_Perf_Season/AllTime)

            # 2.3 Odd Retailers Analysis
            odd_retailers = analyze_odd_retailers(df_season)
            excel_sheets_season["Odd_Retailers"] = odd_retailers

            # 3. Inventory Analysis By Exporter FIFO
            resumen_fifo = analyze_inventory_by_exporter_fifo(df_season)
            excel_sheets_season["Inventory_By_Exporter_FIFO"] = resumen_fifo

            # 3.1 Inventory Summary by Exporter
            inventory_summary_exporter = analyze_inventory_summary_by_exporter(df_season)
            excel_sheets_season["Inventory_Summary_By_Exporter"] = inventory_summary_exporter

            # 3.2 Virtual Inventory Analysis (NUEVO)
            from analysis import create_virtual_inventory_df, analyze_inventory
            df_virtual_inventory = create_virtual_inventory_df(initial_stock_all, sales_detail)
            excel_sheets_season["Virtual_Inventory_Transactions"] = df_virtual_inventory

            # Análisis del inventario virtual: resumen de inventario actual por Lotid/Exporter
            virtual_inventory_results = analyze_inventory(df_virtual_inventory)
            # El resumen principal es el inventario actual por Lotid/Exporter
            df_virtual_current = virtual_inventory_results.get('current_inventory')
            if df_virtual_current is not None and not df_virtual_current.empty:
                excel_sheets_season["Virtual_Inventory_Current_Summary"] = df_virtual_current

            # 4. Deductions Analysis by Exporter
            # (Eliminado: Deduc_Summary_Sales y analyze_deductions_exporter_view)
            # (Eliminado: Pivoted_Deduc y analyze_deductions_by_category_per_lot)

            # 5. Financial Summary By Exporter
            lot_financial_summary_all_season, lot_financial_by_exporter = calculate_lot_summary_with_exporter(df_season)
            excel_sheets_season["Lot_Financial_Sum_All"] = lot_financial_summary_all_season
            # Add one sheet per exporter
            for sheet_name, df_exp in lot_financial_by_exporter.items():
                excel_sheets_season[sheet_name] = df_exp

            # 6. Charge and Deductions Analysis
            # (Eliminado: analyze_charge_summary, commission_stddev_consistency)
            # 6.5. Charge Summary New (agrupado y costo por caja)
            charge_summary_new_df = charge_summary_new(df_season)
            excel_sheets_season["Charge_Summary_New"] = charge_summary_new_df
            # Also export to CSV
            if charge_summary_new_df is not None and not charge_summary_new_df.empty:
                charge_summary_new_csv = os.path.join(season_csv_output_dir, "Charge_Summary_New.csv")
                charge_summary_new_df.to_csv(charge_summary_new_csv, index=False, encoding='utf-8-sig')

            # Consistencia de cargos sobre charge_summary_new
            charges_consistency = charges_stddev_consistency(charge_summary_new_df)
            # Convertir a DataFrame para exportar (resumen por cargo)
            charges_consistency_summary = pd.DataFrame([
                {
                    'Charge': k,
                    'Stddev': v['std_overall'],
                    'Mean': v['mean'],
                    'CV': v['cv']
                } for k, v in charges_consistency.items()
            ])
            excel_sheets_season["Charges_Stddev_Consistency"] = charges_consistency_summary

            # --- Add descriptions for new sheets if not present ---
            if "Sales_Stddev_Consistency" not in SHEET_DESCRIPTIONS:
                SHEET_DESCRIPTIONS["Sales_Stddev_Consistency"] = (
                    "Sales Stddev Consistency: For each combination of Variety, Packaging Style, and Size, analyzes the distribution of 'Price Four Star' across retailers. Calculates stddev, mean, coefficient of variation (CV), and marks as consistent/inconsistent. Includes barplot and boxplot visualizations in the output directory."
                )
            # Add description for each exporter sheet
            for sheet_name in lot_financial_by_exporter:
                if sheet_name not in SHEET_DESCRIPTIONS:
                    exporter = sheet_name.replace("Lot_Financial_Sum_", "").replace("_", " ")
                    SHEET_DESCRIPTIONS[sheet_name] = f"Lot Financial Summary for Exporter: {exporter}. Same columns as Lot_Financial_Sum_All, but filtered for this exporter only."
            if "Virtual_Inventory_Transactions" not in SHEET_DESCRIPTIONS:
                SHEET_DESCRIPTIONS["Virtual_Inventory_Transactions"] = (
                    "Virtual Inventory Transactions: All transactional inventory movements (entries and sales) merged for each Lotid and Exporter. Includes running inventory balance, days in inventory, and product details. Useful for tracing inventory flow and validating stock calculations."
                )
            if "Virtual_Inventory_Current_Summary" not in SHEET_DESCRIPTIONS:
                SHEET_DESCRIPTIONS["Virtual_Inventory_Current_Summary"] = (
                    "Virtual Inventory Current Summary: Current inventory per Lotid and Exporter, including inventory balance, last movement date, days in inventory, variety, and packaging style. Shows only the latest state for each Lotid/Exporter."
                )
            if "Charges_Stddev_Consistency" not in SHEET_DESCRIPTIONS:
                SHEET_DESCRIPTIONS["Charges_Stddev_Consistency"] = (
                    "Charges Stddev Consistency: Analyzes the standard deviation and coefficient of variation (CV) of charges for each exporter. Identifies inconsistent charges that may require further investigation."
                )

            # --- Export CSVs ---
            print(f"\n--- Exporting Individual CSV files for Season: {season_name} ---")
            season_csv_output_dir = os.path.join(RUN_REPORTS_DIR, f"CSV_Report_{season_name.replace(' ', '_')}")
            if not os.path.exists(season_csv_output_dir):
                os.makedirs(season_csv_output_dir)
            for sheet_key, df_csv in excel_sheets_season.items():
                if df_csv is not None and not df_csv.empty:
                    safe_csv_name = "".join(c if c.isalnum() else "_" for c in sheet_key)[:50]
                    csv_filepath = os.path.join(season_csv_output_dir, f"{safe_csv_name}.csv")
                    try:
                        df_csv.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
                        print(f"CSV saved: {csv_filepath}")
                    except Exception as e:
                        print(f"Error saving CSV {csv_filepath}: {e}")

            # --- Export Excel ---
            excel_output_filename_season = os.path.join(RUN_REPORTS_DIR, f"sales_analysis_report_{season_name.replace(' ', '_')}.xlsx")
            export_to_excel(excel_sheets_season, SHEET_DESCRIPTIONS, excel_output_filename_season)

            # --- Export CSVs ---
            print(f"\n--- Exporting Individual CSV files for Season: {season_name} ---")
            season_csv_output_dir = os.path.join(RUN_REPORTS_DIR, f"CSV_Report_{season_name.replace(' ', '_')}")
            if not os.path.exists(season_csv_output_dir):
                os.makedirs(season_csv_output_dir)
            for sheet_key, df_csv in excel_sheets_season.items():
                if df_csv is not None and not df_csv.empty:
                    safe_csv_name = "".join(c if c.isalnum() else "_" for c in sheet_key)[:50]
                    csv_filepath = os.path.join(season_csv_output_dir, f"{safe_csv_name}.csv")
                    try:
                        df_csv.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
                        print(f"CSV saved: {csv_filepath}")
                    except Exception as e:
                        print(f"Error saving CSV {csv_filepath}: {e}")

            # --- Run QC checks and generate Markdown QC report ---
            passed_qc, failed_issues, qc_all_messages = run_quality_control_checks(season_name, excel_sheets_season, df_season)
            generate_qc_report_markdown(season_name, passed_qc, failed_issues, qc_all_messages, RUN_REPORTS_DIR)

        # --- Generate documentation blueprint ---
        generate_data_analysis_blueprint_v8(RUN_REPORTS_DIR, script_version=SCRIPT_VERSION)
        print(f"\nAll processing complete. Results saved in: {RUN_REPORTS_DIR}")
    else:
        print("Data processing failed. Please check your input file.")

if __name__ == "__main__":
    main()
