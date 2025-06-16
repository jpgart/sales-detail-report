(deductions) o cargos (charges) son las siguientes:

1. analyze_deductions_by_category_per_lot
Analiza deducciones por categoría para cada lote.
Usa columnas como 'Chargedescr' y 'Chgamt'.

¿Cómo obtiene "Total Cases Sold Lot"?
Generalmente, esta función pivotea los cargos/deducciones por categoría y lote, pero no calcula explícitamente "Total Cases Sold Lot". Si lo incluye, suele venir de un merge previo o de un DataFrame externo.
¿Puede haber inconsistencias?
Sí, si el DataFrame de entrada no tiene la columna correctamente calculada o sincronizada con el reporte de ventas.

2. analyze_deductions_exporter_view
Analiza deducciones por exportador (excluyendo anticipos).
Calcula deducciones, promedios por caja y totales.

¿Cómo obtiene "Total Cases Sold Lot"?
Calcula Total Cases Sold Lot así:|
  lot_cases_sold = df[df['Trxtype'] == 1].groupby('Lotid')['Invcicqnt'].sum().reset_index(name='Total Cases Sold Lot')
Es decir, suma todas las ventas (Trxtype==1) por Lotid.
¿Puede haber inconsistencias?
Si en otros lugares se filtra distinto (por ejemplo, usando también Sourceidx==5 o excluyendo ciertos retailers), puede haber diferencias.


3. analyze_deduction_consistency_by_charge
Analiza la consistencia de deducciones por tipo de cargo.
Agrupa por 'Chargedescr' y exportador.

¿Cómo obtiene "Total Cases Sold Lot"?
No calcula explícitamente "Total Cases Sold Lot". Analiza cargos usando 'Chgqnt' y 'Chgamt'.
¿Puede haber inconsistencias?
Si se usa 'Chgqnt' como proxy de cajas vendidas, puede diferir del cálculo estándar de ventas.

4. analyze_deductions_summary_by_lotid
Resume deducciones por lote y exportador.
Calcula totales y promedios por caja.

¿Cómo obtiene "Total Cases Sold Lot"?
No calcula "Total Cases Sold Lot". Calcula tasas usando 'Chgamt' / 'Chgqnt'.
¿Puede haber inconsistencias?
Sí, si 'Chgqnt' no representa exactamente las cajas vendidas reales.

5. analyze_charges_by_lot_per_exporter
Analiza cargos por lote y exportador.
Usa pivot table para mostrar cargos por tipo ('Chargedescr').

¿Cómo obtiene "Total Cases Sold Lot"?
No calcula "Total Cases Sold Lot". Se enfoca en cargos de fumigación y compara montos y cantidades.
¿Puede haber inconsistencias?
Si compara contra ventas, debe asegurarse de usar el mismo criterio de cajas vendidas.

--------
6. analyze_fixed_vs_variable_charges
Analiza si los cargos son fijos o variables.
Usa 'Chargedescr', 'Chgqnt', 'Chgamt'.

¿Cómo obtiene "Total Cases Sold Lot"?
No calcula "Total Cases Sold Lot" directamente, pero puede usar 'Chgqnt' para calcular tasas por caja.
¿Puede haber inconsistencias?
Sí, si 'Chgqnt' no es igual al total de ventas reales.

7. analyze_charge_rate_consistency
Analiza la consistencia de la tasa de cargos (chgamt/chgqnt).
Agrupa por tipo de cargo y exportador.

¿Cómo obtiene "Total Cases Sold Lot"?
No calcula "Total Cases Sold Lot". Se enfoca en cargos específicos por tipo.
¿Puede haber inconsistencias?
Si se requiere comparar cargos con ventas, debe alinearse con el cálculo estándar.

8. analyze_fumigation_charges
Analiza cargos de fumigación.
Busca 'FUMIGATION' en 'Chargedescr'.

¿Cómo obtiene "Total Cases Sold Lot"?
No calcula "Total Cases Sold Lot". Solo pivotea cargos por lote y tipo.
¿Puede haber inconsistencias?
Sí, si se requiere comparar cargos con ventas, debe agregarse el cálculo estándar.

9. analyze_commissions_overview
Analiza cargos de comisiones (ProducePay, Retailer).
Usa 'Chargedescr', 'Chgamt', 'Chgqnt'.

¿Cómo obtiene "Total Cases Sold Lot"?
Usa la columna 'Total Cases Sold Lot' del DataFrame de entrada, que debe estar previamente calculada.
¿Puede haber inconsistencias?
Sí, si el DataFrame de entrada no tiene la columna calculada de forma consistente con los reportes de ventas.

10. analyze_agrolatina_specific_charges
Analiza cargos específicos para Agrolatina.
Filtra por exportador y tipo de cargo.
Resumen:

¿Cómo obtiene "Total Cases Sold Lot"?
Calcula así:|
group = deduc_summary_df.groupby(['Lotid', 'Exporter Clean'], as_index=False).agg({
    'Total Cases Sold Lot': 'sum',
    ...
})
Depende de que la columna 'Total Cases Sold Lot' ya esté correctamente calculada en el DataFrame de entrada.
¿Puede haber inconsistencias?
Sí, si el origen de la columna no es consistente con el reporte de ventas.


""" ## Nuevas hojas de análisis agregadas

- **Fix_Rate_Consistency**: Analiza todos los cargos/descuentos fijos (Chgamt > 0 y Chgqnt = 0) agrupando por exportador y tipo de cargo.
- **Variable_Rate_Consistency**: Analiza todos los cargos/descuentos variables (Chgamt > 0 y Chgqnt != 0) usando Recvqnt del modelo FIFO para calcular el costo por caja, agrupando por exportador y tipo de cargo.
"""
