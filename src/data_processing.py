from analysis import charge_summary_new
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from utils import (
    clean_exporter_name,
    get_variety,
    extract_packaging_info,
    extract_retailer_name,
    define_season
)
from column_name_map import normalize_dataframe_columns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessingError(Exception):
    """Custom exception for data processing errors."""
    pass

def process_sales_data(
    file_path_to_load: Union[str, Path],
    exporter_mappings_dict: Dict[str, List[str]],
    exporter_country_m: Dict[str, str],
    grape_varieties_s: set,
    variety_norm_map: Dict[str, str],
    all_exporter_tags_s: set,
    pkg_detail_patterns: Dict[str, str],
    pkg_style_keywords: Dict[str, List[str]],
    specific_lotid_exporter_map: Dict[str, str],
    is_excel: bool = False,
    sheet_name: Union[int, str] = 0
) -> Optional[pd.DataFrame]:
    """
    Loads raw sales data, performs cleaning, and engineers new features.
    
    Args:
        file_path_to_load: Path to the input data file
        exporter_mappings_dict: Dictionary mapping correct exporter names to their variations
        exporter_country_m: Dictionary mapping exporters to their countries
        grape_varieties_s: Set of known grape varieties
        variety_norm_map: Dictionary for normalizing variety names
        all_exporter_tags_s: Set of all known exporter tags
        pkg_detail_patterns: Dictionary of packaging detail patterns
        pkg_style_keywords: Dictionary of packaging style keywords
        specific_lotid_exporter_map: Dictionary for lotid-specific exporter mappings
        is_excel: Whether the input file is Excel
        sheet_name: Sheet name or index for Excel files
        
    Returns:
        Processed DataFrame or None if processing fails
        
    Raises:
        DataProcessingError: If required columns are missing or data loading fails
    """
    logger.info(f"Attempting to load data from: {file_path_to_load}")
    try:
        df = pd.read_csv(file_path_to_load) if not is_excel else pd.read_excel(file_path_to_load, sheet_name=sheet_name)
        logger.info(f"Data loaded successfully from: {file_path_to_load}")
    except FileNotFoundError:
        logger.error(f"File not found at path: {file_path_to_load}")
        raise DataProcessingError(f"File not found: {file_path_to_load}")
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise DataProcessingError(f"Error loading data: {e}")

    df_processed = df.copy()
    logger.info("Starting Data Cleaning and Preprocessing...")

    # Normalize column names at the start
    df_processed = normalize_dataframe_columns(df_processed)

    required_cols = [
        'Lotid', 'Refdate', 'Reportdate', 'Lotdescr', 'Vrtyinvc', 'Descr', 'Trxtype',
        'Invcicqnt', 'Chgamt', 'Chargedescr', 'Saleamt', 'Pricepercase', 'Gwrproductdescr', 'Chgqnt', 'Rcptqnt'
    ]
    missing_cols = [col for col in required_cols if col not in df_processed.columns]
    if missing_cols:
        error_msg = f"Missing required columns: {', '.join(missing_cols)}"
        logger.error(error_msg)
        raise DataProcessingError(error_msg)

    # Convert date columns
    df_processed['Refdate'] = pd.to_datetime(df_processed['Refdate'], errors='coerce')
    
    # Convert numeric columns using vectorized operations
    numeric_cols = {
        'Pricepercase': 'Pricepercase Cleaned',
        'Invcicqnt': 'Invcicqnt',
        'Rcptqnt': 'Rcptqnt',
        'Saleamt': 'Saleamt',
        'Chgamt': 'Chgamt',
        'Chgqnt': 'Chgqnt'
    }
    
    for col, new_col in numeric_cols.items():
        if col == 'Pricepercase':
            df_processed[new_col] = pd.to_numeric(
                df_processed[col].astype(str).str.replace(r'[$,]', '', regex=True),
                errors='coerce'
            )
        else:
            df_processed[new_col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0)

    # Vectorized exporter cleaning
    df_processed['Exporter Clean'] = df_processed.apply(
        lambda row: clean_exporter_name(
            row['Lotdescr'], row['Lotid'], exporter_mappings_dict, specific_lotid_exporter_map
        ), axis=1
    )
    
    # Vectorized country mapping
    df_processed['Exporter Country'] = df_processed['Exporter Clean'].map(exporter_country_m).fillna("Unknown Country")
    
    # Vectorized variety extraction
    df_processed['Variety'] = df_processed.apply(
        lambda row: get_variety(
            row['Vrtyinvc'], row['Descr'], grape_varieties_s, all_exporter_tags_s, variety_norm_map
        ), axis=1
    )

    # Vectorized packaging info extraction
    packaging_info = df_processed.apply(
        lambda row: extract_packaging_info(
            row['Gwrproductdescr'], row['Pricepercase'], pkg_detail_patterns, pkg_style_keywords
        ), axis=1
    )
    df_processed['Packaging Style'] = [info[0] for info in packaging_info]
    df_processed['Packaging Detail'] = [info[1] for info in packaging_info]

    # Vectorized retailer name extraction
    df_processed['Retailer Name'] = df_processed.apply(
        lambda row: extract_retailer_name(
            row['Descr'], row['Trxtype'], row['Invcicqnt'], all_exporter_tags_s
        ), axis=1
    )
    
    # Vectorized season definition
    df_processed['Season'] = df_processed['Refdate'].apply(define_season)

    # Vectorized price calculations
    df_processed['Price Per Case Invc'] = np.where(
        df_processed['Invcicqnt'] != 0,
        df_processed['Saleamt'] / df_processed['Invcicqnt'],
        np.nan
    )
    df_processed['Price Per Case Rcpt'] = np.where(
        df_processed['Rcptqnt'] != 0,
        df_processed['Saleamt'] / df_processed['Rcptqnt'],
        np.nan
    )

    # Vectorized flag calculations
    chargedescr_str_upper = df_processed['Chargedescr'].fillna('').astype(str).str.upper()
    descr_str_upper = df_processed['Descr'].fillna('').astype(str).str.upper()

    df_processed['Is Advance'] = chargedescr_str_upper.str.contains("ADVANCE|ANTICIPO", na=False)
    
    # CORREGIDO: No usar pd.eval, usar expresión booleana estándar
    pp_comm_conditions = (
        (df_processed['Chgamt'] < 0) |
        (chargedescr_str_upper.str.contains('COMMISSION', na=False) &
         descr_str_upper.str.contains('LIQUIDATION', na=False)) |
        descr_str_upper.str.contains(r'\bPP\b', na=False, regex=True)
    )
    df_processed['Is Produce Pay Commission'] = pp_comm_conditions
    
    df_processed['Is Retailer Commission'] = (
        (df_processed['Trxtype'] == 2) &
        chargedescr_str_upper.str.contains("COMMISSION", na=False) &
        (~df_processed['Is Produce Pay Commission']) &
        (~df_processed['Is Advance'])
    )

    logger.info("Data processing complete.")
    return df_processed

