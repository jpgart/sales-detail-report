# 📄 CSV INTEGRATION GUIDE - Manejo de Stock Inicial

**Archivo:** Guía específica para la integración de datos CSV en el sistema Famus  
**Fecha:** 19 de junio de 2025  
**Enfoque:** Initial_Stock_All.csv integration

---

## 🎯 **RESUMEN DE INTEGRACIÓN CSV**

### **Archivo Objetivo:**
- **Path:** `/public/data/Initial_Stock_All.csv`
- **Formato:** CSV con comas como separadores
- **Encoding:** UTF-8 con BOM
- **Registros:** 2,718 líneas de datos
- **Status:** ✅ **COMPLETAMENTE INTEGRADO**

### **Datos Cargados:**
- **Total Stock:** 2,122,368 cajas
- **Lotids Únicos:** 1,297 lotes
- **Exportadores:** 6 únicos
- **Variedades:** 24 tipos de uva

---

## 🔧 **FUNCIONES IMPLEMENTADAS**

### **1. Función Principal: `loadInitialStockFromCSV()`**

```javascript
export const loadInitialStockFromCSV = async () => {
  if (cachedInitialStockData) return cachedInitialStockData;
  
  try {
    const response = await fetch('/data/Initial_Stock_All.csv');
    const csvText = await response.text();
    
    // ⭐ CRÍTICO: Remove BOM if present
    const cleanCsvText = csvText.replace(/^\uFEFF/, '');
    
    // Parse CSV (comma separated)
    const lines = cleanCsvText.split('\n').filter(line => line.trim());
    const headers = lines[0].split(',').map(h => h.trim());
    
    const data = lines.slice(1).map(line => {
      const values = line.split(',');
      const row = {};
      
      headers.forEach((header, index) => {
        const value = values[index]?.trim();
        
        // Parse numeric fields
        if (header === 'Initial Stock') {
          row[header] = parseFloat(value) || 0;
        } else {
          row[header] = value || '';
        }
      });
      
      return row;
    }).filter(row => row.Lotid); // Filter out empty rows
    
    cachedInitialStockData = data;
    console.log(`✅ Loaded ${data.length} initial stock records from CSV`);
    
    return data;
  } catch (error) {
    console.error('❌ Error loading initial stock CSV:', error);
    throw error;
  }
};
```

**Puntos Críticos:**
- ✅ Manejo de BOM UTF-8: `csvText.replace(/^\uFEFF/, '')`
- ✅ Limpieza de headers: `.map(h => h.trim())`
- ✅ Parsing numérico seguro: `parseFloat(value) || 0`
- ✅ Filtrado de filas vacías: `.filter(row => row.Lotid)`
- ✅ Sistema de cache: `cachedInitialStockData`

### **2. Consolidación por Lotid: `getConsolidatedInitialStock()`**

```javascript
export const getConsolidatedInitialStock = async () => {
  if (cachedConsolidatedInitialStock) return cachedConsolidatedInitialStock;
  
  const stockData = await loadInitialStockFromCSV();
  const consolidated = {};
  
  stockData.forEach(record => {
    const lotid = record.Lotid;
    const stock = record['Initial Stock'] || 0;
    const exporter = record['Exporter Clean'] || 'Unknown';
    const variety = record.Variety || 'Unknown';
    const entryDate = record['Entry Date'] || '';
    
    if (!consolidated[lotid]) {
      consolidated[lotid] = {
        lotid,
        totalStock: 0,
        exporter,
        variety,
        entryDate,
        records: []
      };
    }
    
    consolidated[lotid].totalStock += stock;
    consolidated[lotid].records.push({
      stock,
      exporter,
      variety,
      entryDate
    });
  });
  
  cachedConsolidatedInitialStock = consolidated;
  console.log(`✅ Consolidated initial stock for ${Object.keys(consolidated).length} Lotids`);
  
  return consolidated;
};
```

**Funcionalidad:**
- ✅ Agrupa múltiples registros por Lotid
- ✅ Suma stock total por lote
- ✅ Preserva metadatos (exporter, variety, date)
- ✅ Mantiene histórico de registros individuales

### **3. Análisis Multidimensional: `getInitialStockAnalysis()`**

```javascript
export const getInitialStockAnalysis = async () => {
  const stockData = await loadInitialStockFromCSV();
  
  const analysis = {
    totalStock: 0,
    totalLotids: new Set(),
    totalRecords: stockData.length,
    byExporter: {},
    byVariety: {},
    byMonth: {},
    dateRange: { earliest: null, latest: null }
  };
  
  stockData.forEach(record => {
    const lotid = record.Lotid;
    const stock = record['Initial Stock'] || 0;
    const exporter = record['Exporter Clean'] || 'Unknown';
    const variety = record.Variety || 'Unknown';
    const entryDate = record['Entry Date'] || '';
    
    analysis.totalStock += stock;
    analysis.totalLotids.add(lotid);
    
    // Parse date for date range and monthly analysis
    let date = null;
    if (entryDate) {
      const [month, day, year] = entryDate.split('/');
      if (month && day && year) {
        date = new Date(year, month - 1, day);
        
        // Track date range
        if (!analysis.dateRange.earliest || date < analysis.dateRange.earliest) {
          analysis.dateRange.earliest = date;
        }
        if (!analysis.dateRange.latest || date > analysis.dateRange.latest) {
          analysis.dateRange.latest = date;
        }
      }
    }
    
    // By exporter analysis
    if (!analysis.byExporter[exporter]) {
      analysis.byExporter[exporter] = { 
        totalStock: 0, 
        lotids: new Set(), 
        varieties: new Set(),
        records: 0,
        avgStockPerLotid: 0
      };
    }
    analysis.byExporter[exporter].totalStock += stock;
    analysis.byExporter[exporter].lotids.add(lotid);
    analysis.byExporter[exporter].varieties.add(variety);
    analysis.byExporter[exporter].records += 1;
    
    // By variety analysis
    if (!analysis.byVariety[variety]) {
      analysis.byVariety[variety] = { 
        totalStock: 0, 
        lotids: new Set(), 
        exporters: new Set(),
        records: 0,
        avgStockPerLotid: 0
      };
    }
    analysis.byVariety[variety].totalStock += stock;
    analysis.byVariety[variety].lotids.add(lotid);
    analysis.byVariety[variety].exporters.add(exporter);
    analysis.byVariety[variety].records += 1;
    
    // By month analysis (if date is valid)
    if (date) {
      const monthKey = date.toISOString().slice(0, 7); // YYYY-MM
      if (!analysis.byMonth[monthKey]) {
        analysis.byMonth[monthKey] = { 
          totalStock: 0, 
          lotids: new Set(), 
          exporters: new Set(),
          varieties: new Set(),
          records: 0
        };
      }
      analysis.byMonth[monthKey].totalStock += stock;
      analysis.byMonth[monthKey].lotids.add(lotid);
      analysis.byMonth[monthKey].exporters.add(exporter);
      analysis.byMonth[monthKey].varieties.add(variety);
      analysis.byMonth[monthKey].records += 1;
    }
  });
  
  // Convert sets to counts/arrays and calculate averages
  Object.values(analysis.byExporter).forEach(data => {
    data.lotidCount = data.lotids.size;
    data.varietyCount = data.varieties.size;
    data.varieties = Array.from(data.varieties);
    data.avgStockPerLotid = data.lotidCount > 0 ? Math.round(data.totalStock / data.lotidCount) : 0;
  });
  
  Object.values(analysis.byVariety).forEach(data => {
    data.lotidCount = data.lotids.size;
    data.exporterCount = data.exporters.size;
    data.exporters = Array.from(data.exporters);
    data.avgStockPerLotid = data.lotidCount > 0 ? Math.round(data.totalStock / data.lotidCount) : 0;
  });
  
  Object.values(analysis.byMonth).forEach(data => {
    data.lotidCount = data.lotids.size;
    data.exporterCount = data.exporters.size;
    data.varietyCount = data.varieties.size;
    data.exporters = Array.from(data.exporters);
    data.varieties = Array.from(data.varieties);
  });
  
  analysis.totalLotids = analysis.totalLotids.size;
  
  return analysis;
};
```

**Dimensiones de Análisis:**
- ✅ **Por Exportador:** Stock, Lotids, variedades, promedios
- ✅ **Por Variedad:** Stock, Lotids, exportadores involucrados
- ✅ **Por Mes:** Distribución temporal del stock
- ✅ **Rangos de Fechas:** Earliest/latest entry dates
- ✅ **Totales Generales:** Stock total, Lotids únicos, registros

### **4. Funciones de Análisis Específico:**

```javascript
// Top variedades por volumen
export const getTopVarietiesByStock = async (limit = 10) => {
  const analysis = await getInitialStockAnalysis();
  
  return Object.entries(analysis.byVariety)
    .sort(([,a], [,b]) => b.totalStock - a.totalStock)
    .slice(0, limit)
    .map(([variety, data]) => ({
      variety,
      totalStock: data.totalStock,
      lotidCount: data.lotidCount,
      exporterCount: data.exporterCount,
      exporters: data.exporters,
      avgStockPerLotid: data.avgStockPerLotid
    }));
};

// Distribución mensual del stock
export const getStockDistributionByMonth = async () => {
  const analysis = await getInitialStockAnalysis();
  
  return Object.entries(analysis.byMonth)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, data]) => ({
      month,
      monthLabel: new Date(month + '-01').toLocaleDateString('en-US', { year: 'numeric', month: 'short' }),
      totalStock: data.totalStock,
      lotidCount: data.lotidCount,
      exporterCount: data.exporterCount,
      varietyCount: data.varietyCount,
      exporters: data.exporters,
      varieties: data.varieties
    }));
};

// Validación por exportador (con logging)
export const validateInitialStockByExporter = async () => {
  const analysis = await getInitialStockAnalysis();
  
  console.log('📊 Initial Stock by Exporter Validation:');
  Object.entries(analysis.byExporter)
    .sort(([,a], [,b]) => b.totalStock - a.totalStock)
    .forEach(([exporter, data]) => {
      console.log(`  ${exporter}: ${data.totalStock.toLocaleString()} boxes (${data.lotidCount} Lotids, ${data.varietyCount} varieties)`);
    });
  
  return analysis.byExporter;
};
```

---

## 🎨 **INTEGRACIÓN EN UI**

### **Componente: `AdvancedStockAnalysis`**

**Ubicación:** `src/components/reports/CostConsistencyReport.jsx`

```javascript
const AdvancedStockAnalysis = () => {
  const [stockAnalysis, setStockAnalysis] = useState(null);
  const [topVarieties, setTopVarieties] = useState([]);
  const [monthlyDistribution, setMonthlyDistribution] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStockAnalysis = async () => {
      try {
        setLoading(true);
        
        // Load all analysis data in parallel
        const [analysis, varieties, monthly] = await Promise.all([
          getInitialStockAnalysis(),
          getTopVarietiesByStock(8),
          getStockDistributionByMonth()
        ]);
        
        setStockAnalysis(analysis);
        setTopVarieties(varieties);
        setMonthlyDistribution(monthly);
        
        // Log validation data
        await validateInitialStockByExporter();
      } catch (error) {
        console.error('Error loading stock analysis:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStockAnalysis();
  }, []);

  // ... resto del componente con visualizaciones
};
```

**Elementos de UI Implementados:**
- ✅ **KPI Cards:** Total Stock, Lotids, Varieties, Avg per Lot
- ✅ **Top Varieties Chart:** Bar chart con las 8 variedades principales
- ✅ **Monthly Distribution:** Line chart de distribución temporal
- ✅ **Exporter Table:** Tabla detallada por exportador
- ✅ **Variety Details:** Tabla de variedades con métricas

---

## 🧪 **TESTING Y VALIDACIÓN**

### **Script de Prueba Independiente:**

```javascript
// test-csv.js (para verificación externa)
const fs = require('fs');
const path = require('path');

const csvPath = path.join(__dirname, 'public/data/Initial_Stock_All.csv');

console.log('🧪 Testing CSV File Loading...');
console.log('📁 File path:', csvPath);

// Check if file exists
if (!fs.existsSync(csvPath)) {
  console.error('❌ CSV file does not exist!');
  process.exit(1);
}

// Read file
const csvContent = fs.readFileSync(csvPath, 'utf8');

// Remove BOM if present
const cleanCsvContent = csvContent.replace(/^\uFEFF/, '');

const lines = cleanCsvContent.split('\n').filter(line => line.trim());

console.log('✅ File exists and loaded');
console.log('📊 Total lines:', lines.length);
console.log('📋 Headers:', lines[0]);
console.log('📝 First 5 data lines:');
lines.slice(1, 6).forEach((line, index) => {
  console.log(`  ${index + 1}: ${line}`);
});

// Parse and analyze data
const headers = lines[0].split(',').map(h => h.trim());
const data = lines.slice(1).map(line => {
  const values = line.split(',');
  const row = {};
  headers.forEach((header, index) => {
    const value = values[index]?.trim();
    if (header === 'Initial Stock') {
      row[header] = parseFloat(value) || 0;
    } else {
      row[header] = value || '';
    }
  });
  return row;
}).filter(row => row.Lotid);

console.log('\n📈 Data Analysis:');
console.log('📦 Total records:', data.length);
console.log('🏭 Unique exporters:', [...new Set(data.map(r => r['Exporter Clean']))].length);
console.log('📋 Unique Lotids:', [...new Set(data.map(r => r.Lotid))].length);
console.log('🌱 Unique varieties:', [...new Set(data.map(r => r.Variety))].length);

// Calculate total stock
const totalStock = data.reduce((sum, record) => sum + (record['Initial Stock'] || 0), 0);
console.log('📊 Total Initial Stock:', totalStock.toLocaleString(), 'boxes');

// Group by exporter
const byExporter = {};
data.forEach(record => {
  const exporter = record['Exporter Clean'] || 'Unknown';
  if (!byExporter[exporter]) {
    byExporter[exporter] = { 
      stock: 0, 
      records: 0, 
      lotids: new Set(),
      varieties: new Set()
    };
  }
  byExporter[exporter].stock += record['Initial Stock'] || 0;
  byExporter[exporter].records += 1;
  byExporter[exporter].lotids.add(record.Lotid);
  byExporter[exporter].varieties.add(record.Variety);
});

console.log('\n🏭 Stock by Exporter:');
Object.entries(byExporter)
  .sort(([,a], [,b]) => b.stock - a.stock)
  .forEach(([exporter, data]) => {
    console.log(`  ${exporter}: ${data.stock.toLocaleString()} boxes (${data.lotids.size} Lotids, ${data.varieties.size} varieties)`);
  });

console.log('\n✅ CSV test completed successfully!');
```

**Ejecutar:**
```bash
node test-csv.js
```

### **Resultados Esperados del Testing:**

```
✅ CSV test completed successfully!
📦 Total records: 2718
🏭 Unique exporters: 6
📋 Unique Lotids: 1297
🌱 Unique varieties: 24
📊 Total Initial Stock: 2,122,368 boxes

🏭 Stock by Exporter:
  Agrolatina: 1,781,565 boxes (1102 Lotids, 10 varieties)
  Quintay: 136,935 boxes (77 Lotids, 1 varieties)
  MDT: 106,351 boxes (61 Lotids, 11 varieties)
  Unknown Exporter: 65,600 boxes (41 Lotids, 6 varieties)
  Agrovita: 28,317 boxes (14 Lotids, 7 varieties)
  VIDEXPORT: 3,600 boxes (2 Lotids, 1 varieties)
```

---

## ⚠️ **PROBLEMAS COMUNES Y SOLUCIONES**

### **Problema 1: BOM UTF-8**
```
Error: Headers no reconocidos, parsing falla
Causa: Archivo tiene BOM (EF BB BF) al inicio
Solución: csvText.replace(/^\uFEFF/, '')
```

### **Problema 2: Headers con espacios**
```
Error: Columnas no matchean correctamente
Causa: Headers tienen espacios extra
Solución: .map(h => h.trim())
```

### **Problema 3: Números como strings**
```
Error: Cálculos matemáticos fallan
Causa: Stock viene como string "1234" en lugar de número
Solución: parseFloat(value) || 0
```

### **Problema 4: Filas vacías**
```
Error: Registros con Lotid undefined
Causa: Líneas vacías al final del CSV
Solución: .filter(row => row.Lotid)
```

### **Problema 5: Cache no se limpia**
```
Error: Cambios al CSV no se reflejan
Causa: Datos cacheados en memoria
Solución: clearAllCaches() o refresh completo
```

---

## 🚀 **COMANDOS ÚTILES**

### **Verificación de Archivos:**
```bash
# Verificar archivo existe
ls -la public/data/Initial_Stock_All.csv

# Ver primeras líneas
head -5 public/data/Initial_Stock_All.csv

# Contar líneas
wc -l public/data/Initial_Stock_All.csv

# Verificar encoding
file public/data/Initial_Stock_All.csv

# Verificar acceso desde servidor
curl -s http://localhost:3003/data/Initial_Stock_All.csv | head -5
```

### **Debug en Navegador:**
```javascript
// En consola del navegador (Cost Consistency Report abierto)

// Verificar cache
console.log('Cache status:', !!window.cachedInitialStockData);

// Limpiar cache y recargar
await clearAllCaches();
location.reload();

// Probar función individual
const stockData = await loadInitialStockFromCSV();
console.log('Raw data:', stockData.length, 'records');

// Probar consolidación
const consolidated = await getConsolidatedInitialStock();
console.log('Consolidated:', Object.keys(consolidated).length, 'Lotids');

// Probar análisis
const analysis = await getInitialStockAnalysis();
console.log('Analysis:', analysis);
```

---

## 📊 **FORMATO DEL CSV**

### **Headers Esperados:**
```
Lotid,Exporter Clean,Initial Stock,Entry Date,Variety
```

### **Formato de Datos:**
```
24A0005623,Agrolatina,240,03/13/2025,AUTUMN CRISP
24A0005623,Agrolatina,1360,03/13/2025,AUTUMN CRISP
24A0026441,Agrolatina,1120,03/03/2025,TIMCO
```

### **Tipos de Datos:**
- **Lotid:** String (ID único del lote)
- **Exporter Clean:** String (Nombre del exportador)
- **Initial Stock:** Number (Cantidad en cajas)
- **Entry Date:** String formato MM/DD/YYYY
- **Variety:** String (Tipo de uva)

---

## 🎯 **MÉTRICAS FINALES**

**Performance:**
- ✅ Carga inicial: ~2-3 segundos
- ✅ Análisis completo: ~1 segundo
- ✅ Cache hit: Instantáneo

**Datos Procesados:**
- ✅ 2,718 registros parseados
- ✅ 1,297 Lotids consolidados  
- ✅ 6 exportadores analizados
- ✅ 24 variedades categorizadas

**UI Actualizada:**
- ✅ KPIs con datos reales
- ✅ Gráficos dinámicos
- ✅ Tablas interactivas
- ✅ Loading states

---

**🎉 INTEGRACIÓN CSV COMPLETAMENTE EXITOSA 🎉**

*Este archivo documenta completamente la integración del CSV de Stock Inicial. Todos los componentes funcionan correctamente y los datos se cargan dinámicamente desde el archivo CSV real.*
