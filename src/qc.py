from analysis import charge_summary_new
# Quality Control Module for Famus Report Analysis

"""
This module contains functions to perform quality control checks on the processed data and generated analysis results.
It ensures data integrity and consistency throughout the analysis process.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QCError(Exception):
    """Custom exception for quality control errors."""
    pass

def run_quality_control_checks(
    season_name: str,
    excel_sheets_data_dict: Dict[str, pd.DataFrame],
    df_full_processed_season_qc: pd.DataFrame,
    qc_report_path: Optional[Path] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Performs a series of quality control checks on the processed data and generated reports.
    
    Args:
        season_name: Name of the season being analyzed
        excel_sheets_data_dict: Dictionary containing all analysis DataFrames
        df_full_processed_season_qc: Full processed DataFrame for the season
        qc_report_path: Optional path to write QC report
        
    Returns:
        Tuple containing:
        - Boolean indicating if all checks passed
        - List of QC issues found
        - List of all QC log messages
        
    Raises:
        QCError: If critical QC checks fail
    """
    logger.info(f"Starting QC checks for season: {season_name}")
    passed_all_qc = True
    qc_issues_list = []
    qc_log_messages = []

    def qc_log(message: str, condition: bool, details: Optional[str] = None) -> None:
        """Helper function to log QC check results."""
        nonlocal passed_all_qc
        icon = "✅ PASSED:" if condition else "❌ FAILED:"
        full_message = f"{icon} {message}"
        logger.info(full_message)
        qc_log_messages.append(full_message)
        if not condition:
            passed_all_qc = False
            qc_issues_list.append(message)
            if details:
                qc_log_messages.append(details)

    try:
        # --- QC 1: FOB Price calculation matches for sample lot ---
        df_lot_fin_sum_all_qc = excel_sheets_data_dict.get("Lot_Financial_Sum_All")
        if df_lot_fin_sum_all_qc is not None and not df_lot_fin_sum_all_qc.empty:
            sample_row_fin = df_lot_fin_sum_all_qc.sample(min(1, len(df_lot_fin_sum_all_qc))).iloc[0]
            ts_col = 'Total Sales'
            td_col = 'Total Deductions Excl Advances'
            fob_col = 'FOB Price'
            if all(col in sample_row_fin for col in [ts_col, td_col, fob_col]):
                calculated_fob = sample_row_fin[ts_col] - sample_row_fin[td_col]
                qc_log(
                    f"FOB Price calculation matches for sample lot {sample_row_fin.get('Lotid', 'N/A')}",
                    abs(calculated_fob - sample_row_fin[fob_col]) < 0.01
                )
            else:
                msg = f"Missing columns for FOB Price check in Lot_Financial_Sum_All for {season_name}"
                qc_log(msg, False)

            # QC 2: No negative 'Total Advances'
            if 'Total Advances' in df_lot_fin_sum_all_qc.columns:
                qc_log(
                    "No negative 'Total Advances' in Lot_Financial_Sum_All",
                    bool((df_lot_fin_sum_all_qc['Total Advances'] >= 0).all())
                )
            else:
                msg = f"'Total Advances' column missing in Lot_Financial_Sum_All for {season_name}"
                qc_log(msg, False)

            # QC 3: No duplicate Lotid + Exporter Clean
            if all(col in df_lot_fin_sum_all_qc.columns for col in ['Lotid', 'Exporter Clean']):
                dups = df_lot_fin_sum_all_qc.duplicated(subset=['Lotid', 'Exporter Clean']).sum()
                qc_log(
                    f"No duplicate Lotid + Exporter Clean in Lot_Financial_Sum_All (Found: {dups})",
                    dups == 0
                )
            else:
                msg = f"Missing Lotid or Exporter Clean for duplicate check in Lot_Financial_Sum_All for {season_name}"
                qc_log(msg, False)
        else:
            info_msg = f"QC Info: Lot_Financial_Sum_All data not found or empty for {season_name}."
            logger.info(info_msg)
            qc_log_messages.append(info_msg)

        # --- QC 4 & 5: Totals Consistency (Retailer Performance) ---
        # Eliminado: ya no se generan reportes Retailer_Perf_Season ni dependencias.

        # --- QC Info: Number of lots with deductions but no sales ---
        df_dq_deduc_no_sales = excel_sheets_data_dict.get("DQ_Deduc_NoSales")
        if df_dq_deduc_no_sales is not None:
            info_msg = f"QC Info: Number of lots with deductions but no sales: {len(df_dq_deduc_no_sales)}"
            logger.info(info_msg)
            qc_log_messages.append(info_msg)

        # --- QC Info: Number of lots with unknown exporters ---
        df_dq_unknown_exp = excel_sheets_data_dict.get("DQ_Unknown_Exp")
        if df_dq_unknown_exp is not None:
            info_msg = f"QC Info: Number of lots with unknown exporters: {len(df_dq_unknown_exp)}"
            logger.info(info_msg)
            qc_log_messages.append(info_msg)

        # --- QC 6: Fumigation charges applied to non-Chilean exporters ---
        df_fumigation = excel_sheets_data_dict.get("Fumigation_Analysis")
        if df_fumigation is not None and not df_fumigation.empty:
            discrepancies = df_fumigation[
                (df_fumigation['Exporter Country'] != 'Chile')
            ]
            details_str = ""
            if not discrepancies.empty:
                details_str = "\n    Details of non-Chilean fumigation instances:\n"
                details_str += discrepancies[['Lotid', 'Exporter Clean', 'Exporter Country', 'Chargedescr', 'Chgamt']].to_string(index=False)
            qc_log(
                f"Fumigation charges applied to non-Chilean exporters: {len(discrepancies)} instances.",
                len(discrepancies) == 0,
                details=details_str
            )
        else:
            info_msg = f"QC Info: Fumigation_Analysis data not found or empty for {season_name}."
            logger.info(info_msg)
            qc_log_messages.append(info_msg)

        # --- QC 7: Total cases from Processed_Data vs Deduc_Summary are close ---
        df_processed_qc = excel_sheets_data_dict.get("Processed_Data")
        df_deduc_summary_qc = excel_sheets_data_dict.get("Deduc_Summary")
        
        # Type checking and validation
        if not isinstance(df_processed_qc, pd.DataFrame) or not isinstance(df_deduc_summary_qc, pd.DataFrame):
            info_msg = f"QC Info: Processed_Data or Deduc_Summary data not found or invalid type for {season_name}."
            logger.info(info_msg)
            qc_log_messages.append(info_msg)
            return passed_all_qc, qc_issues_list, qc_log_messages
            
        if df_processed_qc.empty or df_deduc_summary_qc.empty:
            info_msg = f"QC Info: Processed_Data or Deduc_Summary data is empty for {season_name}."
            logger.info(info_msg)
            qc_log_messages.append(info_msg)
            return passed_all_qc, qc_issues_list, qc_log_messages
            
        required_cols_processed = ['Invcicqnt', 'Trxtype']
        required_cols_deduc = ['Total Cases Sold Lot', 'Lotid']
        
        if not all(col in df_processed_qc.columns for col in required_cols_processed) or \
           not all(col in df_deduc_summary_qc.columns for col in required_cols_deduc):
            msg = f"Missing required columns for case count comparison in Processed_Data or Deduc_Summary for {season_name}"
            qc_log(msg, False)
            return passed_all_qc, qc_issues_list, qc_log_messages
            
        # At this point we know both DataFrames are valid and have required columns
        total_cases_from_processed = df_processed_qc[df_processed_qc['Trxtype'] == 1]['Invcicqnt'].sum()
        total_cases_from_deduc_summary = df_deduc_summary_qc.drop_duplicates(subset=['Lotid'])['Total Cases Sold Lot'].sum()
        qc_log(
            f"Total cases from Processed_Data ({total_cases_from_processed:,.0f}) vs Deduc_Summary ({total_cases_from_deduc_summary:,.0f}) are close.",
            abs(total_cases_from_processed - total_cases_from_deduc_summary) <= 1.0
        )

        # Generate QC report if path provided
        if qc_report_path:
            try:
                with open(qc_report_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Quality Control Report for {season_name}\n\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("## Summary of Checks\n\n")
                    for msg in qc_log_messages:
                        f.write(f"* {msg}\n")
                    f.write("\n---\n")
                    f.write("This report summarizes the quality control checks performed on the data and generated reports.\n")
                logger.info(f"Generated QC Report: {qc_report_path}")
            except Exception as e:
                logger.error(f"Error writing QC report: {e}")
                raise QCError(f"Failed to write QC report: {e}")

        logger.info(f"QC checks completed for season {season_name}")
        return passed_all_qc, qc_issues_list, qc_log_messages

    except Exception as e:
        logger.error(f"Error during QC checks: {e}")
        raise QCError(f"QC checks failed: {e}")