"""
### La función analyze_inventory_by_exporter_fifo tiene la misión de crear un reporte de movimiento de inventario: Entradas y ventas de los distintos lotid, para poder analzar y sacar conclusiones como la siguientes: 
- A: a cuantos retailers distintos en promedio se vende cada Lotid
- B: Dias de inventario promedio por Variety """


1. analyze_deductions_by_category_per_lot
Analiza deducciones por categoría para cada lote.
Usa columnas como 'Chargedescr' y 'Chgamt'.

2. analyze_deductions_exporter_view
Analiza deducciones por exportador (excluyendo anticipos).
Calcula deducciones, promedios por caja y totales.

3. analyze_deduction_consistency_by_charge
Analiza la consistencia de deducciones por tipo de cargo.
Agrupa por 'Chargedescr' y exportador.

4. analyze_deductions_summary_by_lotid
Resume deducciones por lote y exportador.
Calcula totales y promedios por caja.

5. analyze_charges_by_lot_per_exporter
Analiza cargos por lote y exportador.
Usa pivot table para mostrar cargos por tipo ('Chargedescr').

6. analyze_fixed_vs_variable_charges
Analiza si los cargos son fijos o variables.
Usa 'Chargedescr', 'Chgqnt', 'Chgamt'.

7. analyze_charge_rate_consistency
Analiza la consistencia de la tasa de cargos (chgamt/chgqnt).
Agrupa por tipo de cargo y exportador.

8. analyze_fumigation_charges
Analiza cargos de fumigación.
Busca 'FUMIGATION' en 'Chargedescr'.

9. analyze_commissions_overview
Analiza cargos de comisiones (ProducePay, Retailer).
Usa 'Chargedescr', 'Chgamt', 'Chgqnt'.

10. analyze_agrolatina_specific_charges
Analiza cargos específicos para Agrolatina.
Filtra por exportador y tipo de cargo.
