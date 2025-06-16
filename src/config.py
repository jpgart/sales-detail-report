# --- Configuration & Mappings ---
EXPORTER_MAPPINGS = {
    "Agrolatina": ["AGROLATINA", "AGRIOLATINA", "AGROALATINA", "AGROALTINA", "AGROLATIN", "AGROLATINAS", "AGROLATINS", "AGROLATOINA", "AGROLATRINA", "AGROLTINA", "AROLATINA"],
    "Quintay": ["QUINTAY", "QUI", "QUITAY", "QUNITAY"],
    "Rio King": ["RIO KING", "RK"],
    "ELC": ["ELC"],
    "AGL": ["AGL"],
    "ECO": ["ECO"],
    "Del Monte": ["DEL MONTE", "OTPU6375068 - DEL MONTE"],
    "VIDEXPORT": ["VIDEXPORT"],
    "MDT": ["MDT"],
    "Agrovita": ["AGROVITA"],
    "SAFCO PERU": ["SAFCO PERU"],
    "BORQUEZ": ["BORQUEZ"]
}

EXPORTER_COUNTRY_MAP = {
    "Quintay": "Chile", "Rio King": "Chile", "ELC": "Chile", "MDT": "Chile",
    "Agrovita": "Chile", "Del Monte": "Chile",
    "Agrolatina": "Peru", "AGL": "Peru", "ECO": "Peru", "SAFCO PERU": "Peru",
    "BORQUEZ": "Mexico", "VIDEXPORT": "Mexico"
}

ALL_EXPORTER_NAMES_AND_TAGS = set()
for correct_name, misspellings_list in EXPORTER_MAPPINGS.items():
    ALL_EXPORTER_NAMES_AND_TAGS.add(correct_name.upper())
    for m in misspellings_list:
        ALL_EXPORTER_NAMES_AND_TAGS.add(m.upper())

GRAPE_VARIETIES_LIST_FROM_USER = [
    "AUTUMN CRISP", "TIMCO", "SWEET GLOBE", "CANDY SNAP", "ALLISON", "IVORY",
    "COTTON CANDY", "CANDY DREAMS", "SWEET FAVORS", "JACK SALUTE", "TIMCO CLAM",
    "SWEET CELEB", "SWEETIES", "SWEET SAPPHIRE", "AUTUMN ROYAL", "THOMPSON",
    "CRIMSON", "RED GLOBE", "MELODY", "RED SDLS", "FLAME", "TIMPSON",
    "TAWNY", "EARLY SWEET", "BI-COLOR", "CANDY HEARTS", "GREAT GREEN",
    "GREEN SEEDLESS", "HONEY POP", "KRISSY", "PASSION FIRE", "PASSION FIRE-ORG",
    "SUGAR CRISP", "SUGAR DROP", "SUGAR DROP - ORG", "SUMMER ROYAL", "SWEETCELEBRATION"
]
GRAPE_VARIETIES_SET = {variety.upper() for variety in GRAPE_VARIETIES_LIST_FROM_USER}
VARIETY_NORMALIZATION_MAP = {
    "SWEET CELEB": "SWEETCELEBRATION", "THOMPSON": "THOMPSON SDLS", "TIMCO CLAM": "TIMCO"
}

PACKAGING_DETAIL_PATTERNS = {
    "CLAM 6PK - #2": r"CLAM\s*6PK\s*-\s*#2", "CLAM 6PK - #3": r"CLAM\s*6PK\s*-\s*#3",
    "CLAM 8PK - #2": r"CLAM\s*8PK\s*-\s*#2", "CLAM 8PK - #3": r"CLAM\s*8PK\s*-\s*#3",
    "BAG 16#BAG": r"BAG\s*16#BAG", "BAG 18#POUCH": r"BAG\s*18#POUCH",
    "BAG 18#CLEAR": r"BAG\s*18#CLEAR"
}
PACKAGING_STYLE_KEYWORDS = { "Clam": ["CLAM", "CLAMSHELL"], "Bag": ["BAG", "POUCH"] }

SPECIFIC_LOTID_EXPORTER_MAP = {
    '24D6375068': 'Del Monte', '24E04178': 'VIDEXPORT', '24E04179': 'VIDEXPORT',
    '24E04196': 'VIDEXPORT', '24E04204': 'VIDEXPORT', '24E04205': 'VIDEXPORT',
    '24E04206': 'VIDEXPORT', '24E04207': 'VIDEXPORT'
}

AGROLATINA_SPECIFIC_CHARGES = [
    "RECORDER", "PACKING MATERIALS-OUTSIDE", "COMMISSION-FLAT",
    "COLD TREATMENT FEES", "COLD STORAGE FEES", "ASSESSMENTS",
    "AIR BAG", "ADVERTISMENT & PROMOTIONS", "INSPECTIONS"
]

SHEET_DESCRIPTIONS = {
    "Charge_Summary_New": "Charge Summary New: Grouped summary of charges/deductions by Lotid and Chargedescr, summing Chgamt and Chgqnt, obtaining the initial stock per Lotid and calculating the cost per box (Chgamt/Initial Stock). Exports the key columns for reporting and analysis.",
    "Sales_Stddev_Consistency": "Sales Stddev Consistency: For each combination of Variety, Packaging Style, and Size, analyzes the distribution of 'Price Four Star' across retailers. Calculates stddev, mean, coefficient of variation (CV), and marks as consistent/inconsistent. Includes barplot and boxplot visualizations in the output directory.",
    # New: Lot Financial Summary by Exporter (template, actual keys are Lot_Financial_Sum_{ExporterName})
    # These will be added dynamically in main.py, but you can add a template here for documentation:
    "Lot_Financial_Sum_{ExporterName}": "Lot Financial Summary for Exporter: {ExporterName}. Same columns as Lot_Financial_Sum_All, but filtered for this exporter only.",
    "Processed_Data": "This sheet contains the fully processed and cleaned sales and deduction data for the specified season. It includes all original columns plus engineered features like 'Exporter Clean', 'Exporter Country', normalized 'Variety', 'Packaging Style', 'Packaging Detail', 'Retailer Name', 'Season', and flags for 'Is Advance', 'Is Produce Pay Commission', and 'Is Retailer Commission'. This dataset serves as the foundation for all subsequent analysis sheets in this report.",
    "Initial_Stock_All": "Informe de stock inicial por 'Lotid'. Incluye todas las filas con 'Sourceidx'=1, mostrando 'Lotid', 'Exporter Clean', 'Stock Inicial' (Recvqnt) y 'Fecha' (Refdate).",
    "Initial_Stock_Summary": "Resumen de stock inicial por exportador: muestra el total de stock inicial y el número de contenedores (Lotid) por exportador para la temporada seleccionada.",  # ...otras hojas...  
    "Inventory_By_Exporter_FIFO": "Reporte de inventario agrupado por 'Exporter Clean', modelo FIFO. Muestra por exportador y 'Lotid': fecha de ingreso, stock inicial, total vendido, inventario actual y días en inventario (ordenado por más días en stock primero).",
    "Deduc_Summary": "Exporter View (Deduction Summary per Lot/Charge): Detalle de deducciones operativas (excluyendo anticipos y comisiones principales de ProducePay) para cada 'Lotid' en la temporada. Para cada 'Chargedescr', muestra el 'Total Deduction Amount', 'Total Cases Sold Lot' y 'Avg Deduction Per Case'.",
    "Deduc_Summary_Lotid": "Resumen de deducciones totales por 'Lotid' (suma de cajas, deducciones y promedio por caja).",
    "Lot_Financial_Sum_All": "Lot Financial Summary (All Exporters): Resumen financiero por 'Lotid' para la temporada, agregando todos los exportadores. Incluye: 'Lotid', 'Exporter Clean', 'Total Sales', 'Total Deductions Excl Advances', 'Total Advances', 'FOB Price' y 'Advance Pct Of FOB'.",
    "Lot_Financial_Sum": "Lot Financial Summary by Exporter: Igual que 'Lot_Financial_Sum_All' pero filtrado por exportador ('Exporter Clean').",
    "OceanFreight_Detail": "Detailed Ocean Freight Data: Lista todos los cargos de flete marítimo registrados para la temporada. Incluye 'Lotid', 'Exporter Clean', 'Exporter Country', 'Chargedescr', 'Ocean Freight Amount', 'Total Cases Sold Lot' y 'Ocean Freight Per Case'.",
    "OceanFreight_Sum": "Ocean Freight Summary (Chile vs. Peru): Compara el costo promedio de flete marítimo por caja ('Avg Ocean Freight Per Case') para exportadores de Chile y Perú.",
    # "Retailer_Perf_Season": "Retailer Performance (Current Season): ... (ELIMINADO)",
    # "Retailer_Perf_AllTime": "Retailer Performance (All Seasons Trend): ... (ELIMINADO)",
    "DeducConsist": "Deduction Consistency Analysis by Charge Type: Cada hoja prefijada 'DeducConsist_' compara el 'Avg Deduction Per Case' entre exportadores para ese cargo. Incluye estadísticas por exportador.",
    "Fixed_Var_Charges": "Fixed vs. Variable Charges Identification: Analiza las características de los cargos. Identifica 'Chargedescr' que ocurren con 'Chgamt' pero sin 'Chgqnt', lo que puede indicar costos fijos.",
    "Charge_Rate_Consist": "Charge Rate Consistency: Para cargos con cantidad ('Chgqnt') y monto ('Chgamt'), analiza la consistencia del rate ('Chgamt / Chgqnt'). Agrupa por 'Chargedescr' y 'Exporter Clean'.",
    "Fumigation_Analysis": "Fumigation Charge Analysis: Reporta cargos de 'FUMIGATION'. Lista cualquier caso donde se aplicó a exportadores no chilenos. Si no hay discrepancias, lo indica.",
    "Sales_Detail_Prices": "Sales Detail with Price per Case Metrics: Muestra líneas individuales de venta (trxtype=1) con precio por caja calculado ('Price Per Case Invc' y 'Price Per Case Rcpt').",
    "Odd_Retailers": "Odd Retailer Sales: Lista ventas (trxtype=1) donde hay retailer identificado y 'Invcicqnt' > 0, pero 'Saleamt' es cero o nulo. Agrupa por 'Exporter Clean', 'Retailer Name' y 'Lotid'.",
    "Commission_Analysis": "Commission Analysis Overview: Resumen de comisiones identificadas para la temporada, categorizando en 'Produce Pay Commission' (incluyendo 'Liquidation') y 'Retailer Commission'. Muestra 'Lotid', 'Exporter Clean', 'Chargedescr', 'Descr', 'Charge Amount', 'Charge Quantity' y 'Rate Per Case Chgqnt'.",
    "DQ_Deduc_NoSales": "Data Quality - Lots with Deductions but No Sales: Lista 'Lotid' con deducciones operativas pero sin ventas ('Total Cases Sold Lot' = 0). Incluye 'Exporter Clean', 'Chargedescr' y 'Total Deduction Amount'.",
    "DQ_Unknown_Exp": "Data Quality - Unknown Exporters: Lista 'Lotid' donde no se pudo identificar el exportador. Incluye el 'Lotdescr' original.",
    "RetailerSales": "Retailer Sales Summary by Exporter (Per Exporter Sheet): Una hoja por exportador ('RetailerSales_'). Muestra ventas por 'Retailer Name' para ese exportador. Incluye 'Exporter Clean', 'Total Cases Sold', 'Total Sales Amount' y 'Avg Price Per Case'.",
    "ChargesPerLot": "All Charges by Lot per Exporter (Per Exporter Sheet): Una hoja por exportador ('ChargesPerLot_'). Detalla todos los cargos (trxtype=2) para ese exportador. Filas: 'Lotid', columnas: 'Chargedescr', valores: suma de 'Chgamt'.",
    "Agrolatina_Specific_Charges": "Agrolatina Specific Charges Analysis: Hoja enfocada en cargos específicos de Agrolatina. Presenta estos cargos por 'Lotid' para revisión.",
    "Sales_Detail_By_Lotid": "Detalle de ventas por 'Lotid': muestra cada transacción de venta con 'Exporter Clean', 'Lotid', 'Variety', 'Packaging Style', 'Fecha Ingreso', 'Stock Inicial', 'Fecha Venta', 'Retailer Name', 'Cajas Vendidas' y 'Días en Inventario'.",
    "Fix_Rate_Consistency": "Fixed Rate Consistency: Analiza todos los cargos o descuentos donde 'Chgamt' > 0 y 'Chgqnt' = 0. Agrupa por 'Exporter Clean' y 'Chargedescr', mostrando el monto total y el número de ocurrencias. Permite identificar cargos fijos por lote/exportador.",
    "Variable_Rate_Consistency": "Variable Rate Consistency: Analiza todos los cargos o descuentos donde 'Chgamt' > 0 y 'Chgqnt' != 0. Usa 'Recvqnt' desde el modelo FIFO para calcular el costo por caja ('Chgamt / Recvqnt') y agrupa por 'Exporter Clean' y 'Chargedescr'. Permite revisar la consistencia de cargos variables por caja.",
}

