# Proceso de Auditoría y Control de Consistencia - Famus Report Analysis

## 1. Archivo original
- **Archivo:** `JP Famus Report Original 05.15.25 - FAMOUS LOT DETAIL REPORT SA GRAPES 24-25.csv`
- **Filas:** 77,328
- **Columnas:** 35
- **Columnas principales:** `lotid`, `trxtype`, `recvqnt`, `invcqnt`, `rcptqnt`, `saleamt`, `chgqnt`, `chgamt`, `invcicqnt`, `pricepercase`, etc.
- **Suma de columnas numéricas clave:**
  - `recvqnt`: 5,245,230
  - `invcqnt`: 11,254,810
  - `rcptqnt`: 4,951,203
  - `saleamt`: 131,680,425.38
  - `chgamt`: 58,933,417.35
  - `invcicqnt`: 5,187,015
- **Notas:**
  - No hay pérdida de filas ni alteración de totales en el archivo base.

## 2. Proceso de transformación inicial (`process_sales_data`)
- **Filas procesadas:** 77,328 (idéntico al original)
- **Columnas procesadas:** 48 (se agregan columnas de ingeniería y normalización)
- **Columnas nuevas relevantes:**
  - `Pricepercase Cleaned`, `Exporter Clean`, `Exporter Country`, `Variety`, `Packaging Style`, `Packaging Detail`, `Retailer Name`, `Season`, `Price Per Case Invc`, `Price Per Case Rcpt`, `Is Advance`, `Is Produce Pay Commission`, `Is Retailer Commission`, etc.
- **Suma de columnas numéricas clave (idénticas al original):**
  - `Recvqnt`: 5,245,230
  - `Invcqnt`: 11,254,810
  - `Rcptqnt`: 4,951,203
  - `Saleamt`: 131,680,425.38
  - `Chgamt`: 58,933,417.35
  - `Invcicqnt`: 5,187,015
- **Notas:**
  - No se pierden filas ni se alteran los totales de las columnas numéricas principales.
  - Las columnas agregadas son de ingeniería y no afectan los datos originales.
  - La normalización de nombres de columnas y la creación de nuevas variables es correcta.

## 3. Validación de consistencia por temporada (main.py)
- **Archivos resultantes:**
  - `Processed_Data.csv` para 2023-2024 y 2024-2025
- **Chequeo de sumas:**
  - La suma de filas de ambos archivos: **77,328** (igual al archivo original)
  - Las sumas de columnas numéricas clave (`Recvqnt`, `Invcqnt`, `Rcptqnt`, `Saleamt`, `Chgamt`, `Invcicqnt`, etc.) coinciden exactamente con el archivo original.
- **Conclusión:**
  - El procesamiento y partición por temporada en main.py es correcto y no hay pérdida ni duplicación de datos en los archivos resultantes de cada temporada. La suma de ambos cubre el 100% del archivo original.

---


## 4. Cambios recientes y auditoría de consistencia (junio 2025)

- **Eliminación de reportes y funciones de desempeño de retailers:**
  - Se eliminaron los reportes `Retailer_Perf_Season` y `Retailer_Perf_All` y todas sus dependencias del código (`main.py`, `analysis.py`, `qc.py`, `utils.py`, `config.py`, `reporting.py`, `scripts/sumar_reportes_temporadas.py`).
  - Toda la información relevante de desempeño de retailers ahora se obtiene desde `Sales_Detail_By_Lotid`, que contiene el detalle de ventas por lote, exportador y retailer, con criterios de filtrado y agrupación estandarizados.

- **Auditoría de consistencia automatizada:**
  - El script `scripts/sumar_reportes_temporadas.py` fue actualizado para eliminar referencias a reportes de retailers y auditar únicamente los reportes relevantes (`Processed_Data.csv`, `All_Charges_Deductions.csv`, `Initial_Stock_All.csv`, `Lot_Financial_Sum_All.csv`, `Sales_Detail_By_Lotid.csv`).
  - El script compara sumas totales y agrupadas de columnas clave (cantidades y montos de ventas, stock, deducciones) entre los reportes generados y el archivo procesado, asegurando que no haya duplicación, pérdida ni propagación indebida de datos.
  - Se validó que las sumas de ventas y stock sean idénticas entre los reportes y el archivo original, tanto a nivel total como por lote/exportador.

- **Criterios estándar de filtrado y agrupación:**
  - Todos los reportes relevantes (ventas, inventario, deducciones, resumen financiero) utilizan los mismos criterios de filtrado y agrupación: por `Season`, `Lotid` y `Exporter Clean`.
  - Esto asegura que los reportes sean consistentes y comparables entre sí y con el archivo original.

- **Resultados de la auditoría:**
  - No se detectaron discrepancias significativas en sumas ni estructura entre el archivo original y los reportes generados.
  - Las sumas de ventas (`Invcicqnt`/`Sale Quantity`), montos (`Saleamt`/`Sales Amount`), stock inicial (`Recvqnt`/`Initial Stock`) y deducciones (`Chgamt`) coinciden exactamente entre los reportes y el archivo base.
  - No hay duplicación ni pérdida de datos en el flujo de procesamiento.
  - Las advertencias menores sobre columnas faltantes en algunos reportes financieros no afectan la integridad de la auditoría principal.

- **Procedimiento automatizable para futuras auditorías:**
  1. Ejecutar el flujo principal (`python3 src/main.py`) para generar los reportes por temporada.
  2. Ejecutar el script de auditoría (`python3 scripts/sumar_reportes_temporadas.py`).
  3. Verificar que las sumas y estructura de los reportes coincidan con el archivo original y entre sí, según la salida del script.
  4. Documentar cualquier discrepancia detectada y su causa.

---

**Este archivo documenta el procedimiento y hallazgos de la auditoría de consistencia de datos de ventas Famus.**
