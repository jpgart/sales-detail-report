# Documentación de Escala de Colores - Cost Consistency Report

## Tabla: Charge Breakdown & Comparisons

### Columnas de Desviación: "vs Exporter" y "vs Global"

Las columnas de desviación utilizan un sistema de colores basado en los porcentajes de diferencia para facilitar la identificación visual de las variaciones en los costos:

#### Escala de Colores:

La escala se basa en el **valor absoluto** de la desviación, por lo que tanto valores positivos como negativos en el mismo rango tendrán el mismo color.

1. **Verde (`text-green-600`)**:
   - **Rango**: ≤ 15% de desviación absoluta
   - **Ejemplos**: -10.5%, +8.2%, -15.0%, +14.9%
   - **Significado**: Desviación aceptable/normal
   - **Código de color**: Verde (#059669)

2. **Amarillo (`text-yellow-600`)**:
   - **Rango**: > 15% y ≤ 30% de desviación absoluta
   - **Ejemplos**: -16.8%, +25.9%, -28.6%, +19.1%
   - **Significado**: Desviación moderada que requiere atención
   - **Código de color**: Amarillo (#D97706)

3. **Rojo (`text-red-600`)**:
   - **Rango**: > 30% de desviación absoluta
   - **Ejemplos**: -45.2%, +35.7%, -50.0%, +42.1%
   - **Significado**: Desviación alta que requiere investigación
   - **Código de color**: Rojo (#DC2626)

#### Formato de Valores:

- **Positivos**: Se muestran con signo "+" (ej: +25.3%)
- **Negativos**: Se muestran con signo "-" (ej: -18.7%)
- **Precisión**: Un decimal después del punto

#### Lógica de Aplicación:

```javascript
const getDeviationColor = (deviation) => {
  const absDeviation = Math.abs(deviation); // Usa valor absoluto
  if (absDeviation > 30) return 'text-red-600';     // Rojo: > 30%
  if (absDeviation > 15) return 'text-yellow-600';  // Amarillo: 15-30%
  return 'text-green-600';                          // Verde: ≤ 15%
};
```

#### **Nota Importante sobre Colores:**
- **Los colores se asignan basándose en el valor absoluto de la desviación**
- **Tanto -16.8% como +25.9% aparecen en amarillo** porque ambos están en el rango > 15% y ≤ 30%
- **Tanto -28.6% como +19.1% aparecen en amarillo** porque ambos están en el rango > 15% y ≤ 30%
- **El signo (+ o -) solo indica la dirección de la desviación, no la severidad del color**

#### Interpretación:

- **Verde**: Los costos están dentro del rango esperado (desviación ≤ 15%)
- **Amarillo**: Los costos muestran una variación moderada que podría indicar una oportunidad de optimización (15-30%)
- **Rojo**: Los costos están significativamente fuera del rango normal y requieren análisis inmediato (> 30%)

#### **Ejemplos de Comportamiento:**
- `-16.8%` y `+25.9%` → **Ambos amarillos** (16.8% y 25.9% están entre 15-30%)
- `-28.6%` y `+19.1%` → **Ambos amarillos** (28.6% y 19.1% están entre 15-30%)
- `-10.5%` y `+8.2%` → **Ambos verdes** (10.5% y 8.2% están ≤ 15%)
- `-45.2%` y `+35.7%` → **Ambos rojos** (45.2% y 35.7% están > 30%)

### Formatos Monetarios:

- **Amount**: $X,XXX (sin decimales)
- **Exporter Avg**: $X,XXX (sin decimales)
- **Global Avg**: $X,XXX (sin decimales)

Ejemplo: $1,250 en lugar de $1,250.00

---

**Fecha de documentación**: $(date)
**Versión del sistema**: 3.0.0
**Componente**: CostConsistencyReport.jsx
