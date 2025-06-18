# 📊 Estándar Técnico para Reportes - Famus Workflow

## 🎯 Stack Tecnológico Oficial

Este documento establece el stack tecnológico estándar para **todos los reportes** creados en el workflow de Famus.

### 🔧 **Frontend Framework**
- **React 18.0+** - Framework principal
- **JavaScript (JSX)** - Lenguaje de desarrollo
- **Hooks**: useState, useMemo, useRef, useEffect

### 📈 **Charting Library**
- **Chart.js 4.0+** - Librería de gráficos base
- **react-chartjs-2 5.0+** - Wrapper React oficial
- **Tipos soportados**: Bar, Line, Pie, Donut, Scatter
- **Características**: Doble eje Y, tooltips personalizados, leyendas interactivas

### 📋 **Table Library**
- **HTML Tables nativas** con React
- **Funcionalidades requeridas**:
  - Ordenamiento por columnas
  - Filtrado dinámico
  - Redimensionamiento de columnas
  - Paginación (cuando sea necesario)
- **Implementación**: Custom components, sin dependencias externas

### 🎨 **Styling Framework**
- **Tailwind CSS 3.0+** - Framework principal
- **PostCSS + Autoprefixer** - Procesamiento CSS
- **Diseño responsivo** - Mobile-first approach
- **Paleta de colores estándar**:
  - Primario: `#EE6C4D` (Orange)
  - Secundario: `#3D5A80` (Navy)
  - Accent: `#98C1D9` (Light Blue)
  - Background: `#F9F6F4` (Cream)

### 📊 **Data Handling**
- **Papa Parse 5.5+** - Para parsing CSV (desarrollo)
- **Datos embebidos** - Para producción (seguridad)
- **JavaScript nativo** - Manipulación de datos
- **Estructura de datos**: JSON arrays con objetos normalizados

### 🛠️ **Build & Development**
- **Webpack 5.0+** - Bundler principal
- **Babel** - Transpilador ES6+ y JSX
- **webpack-dev-server** - Servidor de desarrollo
- **HTML Webpack Plugin** - Generación HTML automática

### 🚀 **Deployment**
- **GitHub Pages** - Hosting estático predeterminado
- **Repositorio limpio** - Sin archivos CSV en producción
- **Bundle optimizado** - Compresión y minificación

## 📁 **Estructura de Proyecto Estándar**

```
project-name/
├── src/
│   ├── data/
│   │   └── embeddedData.js
│   └── components/ (opcional)
├── dist/ (generado)
├── public/
│   └── assets/
├── package.json
├── webpack.config.js
├── tailwind.config.js
├── index.html
├── index.jsx (punto de entrada)
├── ReportComponent.jsx (componente principal)
├── .gitignore
└── README.md
```

## 🔒 **Estándares de Seguridad**

### Datos Embebidos (OBLIGATORIO):
1. Convertir CSV a JavaScript embebido
2. Incluir script de conversión (excluido del repo)
3. Actualizar .gitignore para excluir CSVs
4. Sin endpoints de descarga de datos

### Configuración .gitignore:
```
node_modules/
dist/
.DS_Store
*.log
.cache/
*.csv
**/convertCsvToData.js
```

## 📦 **Dependencies Estándar**

### Production Dependencies:
```json
{
  "chart.js": "^4.0.0",
  "react": "^18.0.0",
  "react-chartjs-2": "^5.0.0",
  "react-dom": "^18.0.0"
}
```

### Development Dependencies:
```json
{
  "@babel/core": "^7.27.4",
  "@babel/preset-env": "^7.27.2",
  "@babel/preset-react": "^7.27.1",
  "autoprefixer": "^10.0.0",
  "babel-loader": "^10.0.0",
  "css-loader": "^7.1.2",
  "html-webpack-plugin": "^5.6.3",
  "papaparse": "^5.5.3",
  "postcss": "^8.0.0",
  "postcss-loader": "^8.1.1",
  "style-loader": "^4.0.0",
  "tailwindcss": "^3.0.0",
  "webpack": "^5.99.9",
  "webpack-cli": "^6.0.1",
  "webpack-dev-server": "^5.2.2"
}
```

## 🎯 **Componentes Estándar Requeridos**

### 1. KPI Cards
- Métricas principales en cards visuales
- Iconos y colores consistentes
- Formato de números estandarizado

### 2. Charts Interactivos
- Gráficos de barras, líneas y pie
- Tooltips informativos
- Leyendas clickeables

### 3. Filtros Dinámicos
- Dropdowns para categorías principales
- Filtrado en tiempo real
- Reset de filtros

### 4. Tablas de Datos
- Ordenamiento por columnas
- Búsqueda/filtrado
- Formato de números consistente

### 5. Navegación por Secciones
- Índice de contenidos
- Scroll automático
- Referencias de navegación

## 📋 **Checklist de Calidad**

### Antes del Deploy:
- [ ] Datos embebidos correctamente
- [ ] CSV excluido del repositorio
- [ ] Build exitoso sin errores
- [ ] Responsive design verificado
- [ ] Colores y fuentes consistentes
- [ ] Funcionalidad de filtros probada
- [ ] GitHub Pages configurado
- [ ] README actualizado
- [ ] .gitignore configurado

### Performance:
- [ ] Bundle size optimizado
- [ ] Lazy loading implementado (si aplica)
- [ ] Imágenes optimizadas
- [ ] CSS minificado

## 🔄 **Workflow de Desarrollo**

1. **Setup**: Clonar template con stack estándar
2. **Desarrollo**: Usar datos CSV para testing
3. **Conversión**: Embebber datos para producción
4. **Testing**: Verificar funcionalidad completa
5. **Deploy**: GitHub Pages con archivos optimizados
6. **Documentación**: README con instrucciones

## 📚 **Referencias Técnicas**

- **React**: https://react.dev/
- **Chart.js**: https://www.chartjs.org/
- **Tailwind CSS**: https://tailwindcss.com/
- **Webpack**: https://webpack.js.org/

---

**Versión**: 1.0  
**Fecha**: 18 de junio de 2025  
**Proyecto base**: Famus-Sales-Detail  
**Mantenedor**: JP

> Este estándar asegura consistencia, calidad y seguridad en todos los reportes del workflow Famus.
