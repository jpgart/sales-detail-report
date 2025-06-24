# 🚀 Template de Proyecto para Reportes Famus

## Comandos de Setup Rápido

```bash
# 1. Crear nuevo proyecto
mkdir new-report-name
cd new-report-name

# 2. Inicializar proyecto
npm init -y

# 3. Instalar dependencias estándar
npm install chart.js@^4.0.0 react@^18.0.0 react-chartjs-2@^5.0.0 react-dom@^18.0.0

# 4. Instalar dev dependencies
npm install -D @babel/core@^7.27.4 @babel/preset-env@^7.27.2 @babel/preset-react@^7.27.1 autoprefixer@^10.0.0 babel-loader@^10.0.0 css-loader@^7.1.2 html-webpack-plugin@^5.6.3 papaparse@^5.5.3 postcss@^8.0.0 postcss-loader@^8.1.1 style-loader@^4.0.0 tailwindcss@^3.0.0 webpack@^5.99.9 webpack-cli@^6.0.1 webpack-dev-server@^5.2.2

# 5. Configurar Tailwind
npx tailwindcss init

# 6. Crear estructura de archivos
mkdir src src/data public
```

## Scripts package.json Estándar

```json
{
  "scripts": {
    "start": "webpack serve --mode development --open",
    "build": "webpack --mode production",
    "dev": "webpack serve --mode development"
  }
}
```

## Archivos de Configuración Base

### webpack.config.js
```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './index.jsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
    clean: true,
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-react', '@babel/preset-env'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './index.html',
    }),
  ],
  devServer: {
    static: path.join(__dirname, 'dist'),
    compress: true,
    port: 8080,
    open: true,
  },
};
```

### tailwind.config.js
```javascript
module.exports = {
  content: [
    "./*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'famus-orange': '#EE6C4D',
        'famus-navy': '#3D5A80',
        'famus-blue': '#98C1D9',
        'famus-cream': '#F9F6F4',
      }
    },
  },
  plugins: [],
};
```

### .gitignore
```
node_modules/
dist/
.DS_Store
*.log
.cache/
*.csv
**/convertCsvToData.js
```

### index.html base
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Famus Report</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
```

### index.css base
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}
```

## Comando de Copia Rápida desde Template

```bash
# Copiar estructura desde proyecto base
cp -r /path/to/famus-report-analysis/reports/html_reports/sales-report-v2-final/* ./
rm -rf node_modules dist .git src/data/salesDataEmbedded.js
```

## Checklist de Nuevo Proyecto

- [ ] Estructura de carpetas creada
- [ ] Dependencies instaladas
- [ ] Webpack configurado
- [ ] Tailwind inicializado
- [ ] Colores Famus en config
- [ ] .gitignore configurado
- [ ] Scripts npm configurados
- [ ] Primer build exitoso
- [ ] Git inicializado
- [ ] README creado

## Conversión CSV a Datos Embebidos

```javascript
// Script convertCsvToData.js (mantener fuera del repo)
const fs = require('fs');

function convertCsvToJs(csvPath, outputPath) {
  const csvContent = fs.readFileSync(csvPath, 'utf-8');
  const lines = csvContent.split('\n');
  const headers = lines[0].split(',');
  
  const data = lines.slice(1)
    .filter(line => line.trim())
    .map(line => {
      const values = line.split(',');
      const row = {};
      headers.forEach((header, index) => {
        row[header.trim()] = values[index]?.trim() || '';
      });
      return row;
    });

  const jsContent = `export const reportData = ${JSON.stringify(data, null, 2)};
export const getReportData = () => reportData;
export const getDataSummary = () => ({
  totalRecords: reportData.length,
  // Agregar más metadata según necesidades
});`;

  fs.writeFileSync(outputPath, jsContent);
  console.log(`✅ Converted ${data.length} records to ${outputPath}`);
}
```

---

**Template actualizado**: 18 de junio de 2025  
**Base**: Famus Sales Detail Report v2
