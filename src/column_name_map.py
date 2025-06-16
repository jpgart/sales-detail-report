def rename_columns_for_readability(df):
    """
    Convierte nombres_de_columnas o camelCase a 'Title Case With Spaces'.
    Si la columna ya es legible, la deja igual.
    """
    import re
    def prettify(col):
        # Si ya tiene espacios y mayúsculas, la dejamos
        if ' ' in col and col[0].isupper():
            return col
        # Si es todo mayúsculas, lo dejamos
        if col.isupper():
            return col
        # Si es snake_case o camelCase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', col)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        s3 = s2.replace('_', ' ')
        return s3.strip().title()
    df = df.copy()
    df.columns = [prettify(col) for col in df.columns]
    return df
COLUMN_NAME_MAP = {
    # Variantes para cada columna relevante (sin espacios, con guion bajo, todo minúscula, etc.)
    "lotid": "Lotid",
    "lot_id": "Lotid",
    "lotdescr": "Lotdescr",
    "lot_description": "Lotdescr",
    "lotdescription": "Lotdescr",
    "lotclosedate": "Lotclosedate",
    "lothistflag": "Lothistflag",
    "trxtype": "Trxtype",
    "trx_type": "Trxtype",
    "chargeorderby": "Chargeorderby",
    "charge_order_by": "Chargeorderby",
    "chargeid": "Chargeid",
    "charge_id": "Chargeid",
    "chargedescr": "Chargedescr",
    "charge_descr": "Chargedescr",
    "chargeratetype": "Chargeratetype",
    "charge_rate_type": "Chargeratetype",
    "sourceidx": "Sourceidx",
    "source_idx": "Sourceidx",
    "refdate": "Refdate",
    "ref_date": "Refdate",
    "ref": "Ref",
    "descr": "Descr",
    "garunidx": "Garunidx",
    "recvqnt": "Recvqnt",
    "recv_qnt": "Recvqnt",
    "issueqnt": "Issueqnt",
    "issue_qnt": "Issueqnt",
    "invcqnt": "Invcqnt",
    "invc_qnt": "Invcqnt",
    "rcptqnt": "Rcptqnt",
    "rcpt_qnt": "Rcptqnt",
    "saleamt": "Saleamt",
    "sale_amt": "Saleamt",
    "chgqnt": "Chgqnt",
    "chg_qnt": "Chgqnt",
    "chgamt": "Chgamt",
    "chg_amt": "Chgamt",
    "gwrproductdescr": "Gwrproductdescr",
    "gwr_product_descr": "Gwrproductdescr",
    "cmtyinvc": "Cmtyinvc",
    "vrtyinvc": "Vrtyinvc",
    "styleorderby": "Styleorderby",
    "gradeinvc": "Gradeinvc",
    "sizeorderby": "Sizeorderby",
    "uom": "Uom",
    "fcchargeidx": "Fcchargeidx",
    "invcicqnt": "Invcicqnt",
    "invc_icqnt": "Invcqnt",
    "astitle": "Astitle",
    "ascompanyname": "Ascompanyname",
    "reportdate": "Reportdate",
    "reportdate1": "Reportdate.1",
    "report_date_1": "Reportdate.1",
    "pricepercase": "Pricepercase",
    "price_per_case": "Pricepercase",
    "pricepercasecleaned": "Pricepercase Cleaned",
    "price_per_case_cleaned": "Pricepercase Cleaned",
    "exporterclean": "Exporter Clean",
    "exporter_clean": "Exporter Clean",
    "exporter": "Exporter Clean",
    "exportercountry": "Exporter Country",
    "exporter_country": "Exporter Country",
    "variety": "Variety",
    "packagingstyle": "Packaging Style",
    "packaging_style": "Packaging Style",
    "packagingdetail": "Packaging Detail",
    "packaging_detail": "Packaging Detail",
    "retailername": "Retailer Name",
    "retailer_name": "Retailer Name",
    "season": "Season",
    "pricepercaseinvc": "Price Per Case Invc",
    "price_per_case_invc": "Price Per Case Invc",
    "pricepercasercpt": "Price Per Case Rcpt",
    "price_per_case_rcpt": "Price Per Case Rcpt",
    "isadvance": "Is Advance",
    "is_advance": "Is Advance",
    "isproducepaycommission": "Is Produce Pay Commission",
    "is_produce_pay_commission": "Is Produce Pay Commission",
    "isretailercommission": "Is Retailer Commission",
    "is_retailer_commission": "Is Retailer Commission",
}

def normalize_column(col):
    key = col.lower().replace(" ", "").replace("_", "")
    return COLUMN_NAME_MAP.get(key, col)

def normalize_dataframe_columns(df):
    df = df.copy()
    df.columns = [normalize_column(col) for col in df.columns]
    return df