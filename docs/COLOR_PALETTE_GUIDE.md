# Key Market Insights Color Palette - Usage Guide

## Overview
Este documento explica cómo implementar correctamente la paleta de colores estándar para secciones de "Key Market Insights" en los reportes de Famus.

## Paleta de Colores

### 🥇 Leadership/Market Share - `#3D5A80`
- **Uso**: Información sobre liderazgo de mercado, cuota de mercado, participantes principales
- **Color de fondo**: `#3D5A80` (dark blue)
- **Color de hover**: `#2E4B6B` 
- **Texto del botón**: `white`
- **Ejemplo**: "Market leader analysis", "Top exporters by volume"

### ⚠️ Risks/Dependencies - `#6B8B9E`  
- **Uso**: Riesgos de concentración, dependencias, alertas de mercado
- **Color de fondo**: `#6B8B9E` (medium blue-gray)
- **Color de hover**: `#5A7A8C`
- **Texto del botón**: `white`
- **Ejemplo**: "High customer concentration", "Supply chain dependencies"

### 💰 Premium Positioning - `#98C1D9`
- **Uso**: Análisis de posicionamiento premium, precios altos, valor agregado
- **Color de fondo**: `#98C1D9` (light blue)
- **Color de hover**: `#86B4D1`
- **Texto del botón**: `white`
- **Ejemplo**: "Premium pricing strategies", "High-value products"

### 📉 Commodity/Low Price - `#BEE0EB`
- **Uso**: Estrategias de bajo precio, productos commodity, mercado masivo
- **Color de fondo**: `#BEE0EB` (very light blue)
- **Color de hover**: `#AAD8E3`
- **Texto del botón**: `#293241` (dark text for better contrast)
- **Ejemplo**: "Low-price competition", "Commodity market patterns"

### 📦 Volume/Coverage - `#E0FBFC`
- **Uso**: Análisis de volumen, cobertura de mercado, alcance geográfico
- **Color de fondo**: `#E0FBFC` (lightest blue)
- **Color de hover**: `#D1F4F7`
- **Texto del botón**: `#293241` (dark text for better contrast)
- **Ejemplo**: "Market coverage analysis", "Volume distribution"

## Implementación

### 1. Importar la utilidad de colores
```javascript
import { getInsightColors, INSIGHT_SECTION_CLASSES } from '@utils/colorPalette';
```

### 2. Estructura HTML estándar
```jsx
{/* Ejemplo: Sección de Liderazgo */}
<div className="mb-4">
  <button 
    onClick={() => toggleSection('leadership')}
    className="w-full text-left flex items-center justify-between p-3 bg-[#3D5A80] rounded-lg hover:bg-[#2E4B6B] transition-colors"
  >
    <h4 className="text-lg font-bold text-white">🥇 Market Share & Leadership</h4>
    <span className="text-white">{expandedSections.leadership ? '▼' : '▶'}</span>
  </button>
  {expandedSections.leadership && (
    <div className="mt-2 p-4 bg-white rounded-lg border-2 border-[#3D5A80] max-h-60 overflow-y-auto">
      <ul className="space-y-2">
        {insights.leadership.map((insight, idx) => (
          <li key={idx} className="flex items-start">
            <span className="text-[#3D5A80] mr-2 font-bold">•</span>
            <span className="text-[#293241] text-sm leading-relaxed">{insight}</span>
          </li>
        ))}
      </ul>
    </div>
  )}
</div>
```

### 3. Características del área de contenido
- **Fondo blanco** (`bg-white`) para máximo contraste
- **Borde de 2px** que coincide con el color del botón
- **Altura máxima** (`max-h-60`) equivalente a 15rem
- **Scroll vertical** (`overflow-y-auto`) cuando el contenido excede la altura
- **Padding interno** (`p-4`) para espaciado cómodo
- **Espaciado entre elementos** (`space-y-2`) para buena legibilidad

### 4. Tipografía estándar
- **Viñetas**: Color que coincide con el tema de la sección, peso `font-bold`
- **Texto del contenido**: `text-[#293241] text-sm leading-relaxed`
- **Espaciado de línea relajado** para facilitar la lectura

## Consideraciones de Diseño

### Accesibilidad
- Contraste mínimo WCAG AA cumplido en todas las combinaciones
- Textos legibles en todos los fondos de color
- Indicadores visuales claros para estado expandido/colapsado

### Consistencia Visual
- Misma estructura y altura en todas las secciones
- Transiciones suaves (`transition-colors`) 
- Jerarquía visual clara de más oscuro (leadership) a más claro (coverage)

### Responsive Design
- Funciona correctamente en dispositivos móviles
- El scroll vertical se adapta al contenido disponible
- Los botones mantienen usabilidad en pantallas táctiles

## Archivos Relacionados
- `/src/utils/colorPalette.js` - Configuración de colores y utilidades
- `/src/utils/index.js` - Exportaciones centralizadas
- `/docs/TECH_STANDARDS.md` - Estándares técnicos del proyecto
