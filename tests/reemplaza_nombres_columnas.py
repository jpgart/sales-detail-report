import os
import re

# Diccionario de reemplazos: clave = nombre incorrecto, valor = nombre correcto
REEMPLAZOS = {
    "Exporter Clean": "Exporter Clean",
    "Retailer Name": "Retailer Name",
    "Packaging Style": "Packaging Style",
    "Packaging Detail": "Packaging Detail",
    "Is Advance": "Is Advance",
    "Is Produce Pay Commission": "Is Produce Pay Commission",
    "Is Retailer Commission": "Is Retailer Commission",
    "Exporter Country": "Exporter Country",
    "Chargedescr": "Chargedescr",  # ya correcto, pero por si acaso
    "Lotid": "Lotid",
    "Lotdescr": "Lotdescr",
    "Recvqnt": "Recvqnt",
    "Refdate": "Refdate",
    "Variety": "Variety",
    "Season": "Season",
    "Invcicqnt": "Invcicqnt",
    "Saleamt": "Saleamt",
    "Trxtype": "Trxtype",
    "Sourceidx": "Sourceidx",
    "Rcptqnt": "Rcptqnt",
    "Chgamt": "Chgamt",
    "Chgqnt": "Chgqnt",
    "Invcqnt": "Invcqnt",
    "Pricepercase": "Pricepercase",
    "Pricepercase Cleaned": "Pricepercase Cleaned",
    "Price Per Case Invc": "Price Per Case Invc",
    "Price Per Case Rcpt": "Price Per Case Rcpt",
    "Total Cases Sold Lot": "Total Cases Sold Lot",
    "Total Deduction Amount": "Total Deduction Amount",
    "Avg Deduction Per Case": "Avg Deduction Per Case",
    "Total Sales": "Total Sales",
    "Total Deductions Excl Advances": "Total Deductions Excl Advances",
    "Total Advances": "Total Advances",
    "FOB Price": "FOB Price",
    "Advance Pct Of FOB": "Advance Pct Of FOB",
    "Ocean Freight Amount": "Ocean Freight Amount",
    "Ocean Freight Per Case": "Ocean Freight Per Case",
    "Retailer_Perf_Season": "Retailer_Perf_Season",
    "Retailer_Perf_AllTime": "Retailer_Perf_AllTime",
    "Odd_Retailers": "Odd_Retailers",
    "Fixed_Var_Charges": "Fixed_Var_Charges",
    "Charge_Rate_Consist": "Charge_Rate_Consist",
    "Fumigation_Analysis": "Fumigation_Analysis",
    "Commission_Analysis": "Commission_Analysis",
    "Sales_Detail_By_Lotid": "Sales_Detail_By_Lotid",
    "DQ_Deduc_NoSales": "DQ_Deduc_NoSales",
    "DQ_Unknown_Exp": "DQ_Unknown_Exp",
    "Agrolatina_Specific_Charges": "Agrolatina_Specific_Charges",
    "RetailerSales_": "RetailerSales_",
    "ChargesPerLot_": "ChargesPerLot_",
    "Lot_Financial_Sum_All": "Lot_Financial_Sum_All",
    "Lot_Financial_Sum": "Lot_Financial_Sum",
    "Deduc_Summary": "Deduc_Summary",
    "Deduc_Summary_Lotid": "Deduc_Summary_Lotid",
    "Pivoted_Deduc": "Pivoted_Deduc",
    "Initial_Stock_By_Lotid": "Initial_Stock_By_Lotid",
    "Inventory_By_Exporter_FIFO": "Inventory_By_Exporter_FIFO",
}

# Carpeta raíz del proyecto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def reemplazar_en_archivo(filepath, reemplazos):
    try:
        with open(filepath, encoding='utf-8') as f:
            contenido = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, encoding='latin-1') as f:
                contenido = f.read()
        except Exception as e:
            print(f"Archivo omitido por error de codificación: {filepath} ({e})")
            return
    original = contenido
    for viejo, nuevo in reemplazos.items():
        contenido = re.sub(rf"(['\[\"]){viejo}(['\"\]])", rf"\1{nuevo}\2", contenido)
    if contenido != original:
        with open(filepath, "w", encoding='utf-8') as f:
            f.write(contenido)
        print(f"Reemplazos aplicados en: {filepath}")

def buscar_y_reemplazar(root_dir, reemplazos):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                reemplazar_en_archivo(filepath, reemplazos)

if __name__ == "__main__":
    buscar_y_reemplazar(ROOT_DIR, REEMPLAZOS)
    print("Reemplazos completados en todos los archivos .py del workspace.")