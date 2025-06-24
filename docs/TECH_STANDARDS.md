# 📊 Technical Standards for Reports - Famus Workflow

## 🎯 Official Technology Stack

This document establishes the standard technology stack for **all reports** created in the Famus workflow.

### 🔧 **Frontend Framework**
- **React 18.0+** - Core framework
- **JavaScript (JSX)** - Development language
- **Hooks**: useState, useMemo, useRef, useEffect

### 📈 **Charting Library**
- **Chart.js 4.5+** - Base charting library
- **react-chartjs-2 5.3+** - Official React wrapper
- **chartjs-plugin-zoom 2.2+** - Interactive zoom and pan functionality
- **Supported types**: Bar, Line, Pie, Donut, Scatter
- **Features**: Dual Y-axis, custom tooltips, interactive legends, zoom/pan

### 📋 **Table Library**
- **Native HTML Tables** with React
- **Required functionality**:
  - Column sorting
  - Dynamic filtering
  - Column resizing
  - Pagination (when necessary)
- **Implementation**: Custom components, no external dependencies

### 🎨 **Styling Framework**
- **Tailwind CSS 3.0+** - Primary framework
- **PostCSS + Autoprefixer** - CSS processing
- **Responsive design** - Mobile-first approach
- **Standard color palette**:
  - Primary: `#EE6C4D` (Famus Orange)
  - Secondary: `#3D5A80` (Famus Navy)
  - Accent: `#98C1D9` (Famus Blue)
  - Background: `#F9F6F4` (Famus Cream)

### 🎨 **Key Market Insights Color Palette**
**Standard color scheme for collapsible insight sections with visual hierarchy:**

- **Leadership/Market Share**: `#3D5A80` (Dark blue - authority)
- **Risks/Dependencies**: `#6B8B9E` (Medium blue-gray - caution)
- **Premium Positioning**: `#98C1D9` (Light blue - premium)
- **Commodity/Low Price**: `#BEE0EB` (Very light blue - volume)
- **Volume/Coverage**: `#E0FBFC` (Lightest blue - broad reach)

**Features:**
- Consistent visual hierarchy across all reports
- White content areas with matching borders
- Maximum height: `max-h-60` (15rem) with vertical scroll
- Typography: `text-sm leading-relaxed` for readability
- Color utility: `/src/utils/colorPalette.js`

### 📊 **Data Handling**
- **Papa Parse 5.5+** - For CSV parsing (development)
- **Embedded data** - For production (security)
- **Native JavaScript** - Data manipulation
- **Data structure**: JSON arrays with normalized objects

### 🛠️ **Build & Development**
- **Webpack 5.0+** - Primary bundler
- **Babel** - ES6+ and JSX transpiler
- **webpack-dev-server** - Development server
- **HTML Webpack Plugin** - Automatic HTML generation

### 🚀 **Deployment**
- **GitHub Pages** - Default static hosting
- **Clean repository** - No CSV files in production
- **Optimized bundle** - Compression and minification

## 📁 **Standard Project Structure**

```
project-name/
├── src/
│   ├── data/
│   │   └── embeddedData.js
│   └── components/ (optional)
├── dist/ (generated)
├── public/
│   └── assets/
├── package.json
├── webpack.config.js
├── tailwind.config.js
├── index.html
├── index.jsx (entry point)
├── ReportComponent.jsx (main component)
├── .gitignore
└── README.md
```

## 🔒 **Security Standards**

### Embedded Data (MANDATORY):
1. Convert CSV to embedded JavaScript
2. Include conversion script (excluded from repo)
3. Update .gitignore to exclude CSVs
4. No data download endpoints

### .gitignore Configuration:
```
node_modules/
dist/
.DS_Store
*.log
.cache/
*.csv
**/convertCsvToData.js
```

## 📦 **Standard Dependencies**

### Production Dependencies:
```json
{
  "chart.js": "^4.5.0",
  "chartjs-plugin-zoom": "^2.2.0",
  "react": "^18.0.0",
  "react-chartjs-2": "^5.3.0",
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
  "csv-loader": "^3.0.5",
  "gh-pages": "^6.0.0",
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

## 🎯 **Required Standard Components**

### 1. KPI Cards
- Main metrics in visual cards
- Consistent icons and colors
- Standardized number formatting

### 2. Interactive Charts
- Bar, line, and pie charts
- Informative tooltips
- Clickable legends
- Zoom and pan functionality

### 3. Dynamic Filters
- Dropdowns for main categories
- Real-time filtering
- Filter reset functionality

### 4. Data Tables
- Column sorting
- Search/filtering
- Consistent number formatting

### 5. Section Navigation
- Table of contents
- Automatic scrolling
- Navigation references

## 📋 **Quality Checklist**

### Before Deploy:
- [ ] Data embedded correctly
- [ ] CSV excluded from repository
- [ ] Successful build without errors
- [ ] Responsive design verified
- [ ] Colors and fonts consistent
- [ ] Filter functionality tested
- [ ] GitHub Pages configured
- [ ] README updated
- [ ] .gitignore configured

### Performance:
- [ ] Bundle size optimized
- [ ] Lazy loading implemented (if applicable)
- [ ] Images optimized
- [ ] CSS minified

## 🔄 **Development Workflow**

1. **Setup**: Clone template with standard stack
2. **Development**: Use CSV data for testing
3. **Conversion**: Embed data for production
4. **Testing**: Verify complete functionality
5. **Deploy**: GitHub Pages with optimized files
6. **Documentation**: README with instructions

## 🎨 **Design System**

### Color Palette:
```css
:root {
  --famus-orange: #EE6C4D;
  --famus-navy: #3D5A80;
  --famus-blue: #98C1D9;
  --famus-cream: #F9F6F4;
}
```

### Typography:
- **Headers**: Font weight 700, Navy color
- **Body**: Font weight 400, Navy color
- **Captions**: Font weight 300, Gray color

### Interactive Elements:
- **Hover effects**: Subtle color transitions
- **Active states**: Clear visual feedback
- **Loading states**: Spinner with brand colors

## � **Chart Configuration Standards**

### Default Chart Options:
```javascript
const defaultChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    tooltip: {
      backgroundColor: '#3D5A80',
      titleColor: '#F9F6F4',
      bodyColor: '#F9F6F4',
    },
    zoom: {
      zoom: {
        wheel: {
          enabled: true,
        },
        pinch: {
          enabled: true
        },
        mode: 'xy',
      },
      pan: {
        enabled: true,
        mode: 'xy',
      }
    }
  }
};
```

## 📚 **Technical References**

- **React**: https://react.dev/
- **Chart.js**: https://www.chartjs.org/
- **ChartJS Zoom Plugin**: https://www.chartjs.org/chartjs-plugin-zoom/
- **Tailwind CSS**: https://tailwindcss.com/
- **Webpack**: https://webpack.js.org/

---

**Version**: 2.0  
**Date**: June 19, 2025  
**Base Project**: Famus-HTML-Reports  
**Maintainer**: JP

> This standard ensures consistency, quality, and security across all reports in the Famus workflow.

## ✅ **Famus Cream Background Standard Applied**

**Date**: 2025-06-19

### Background Color Consistency Updates:

1. **Sales Detail Report** (`SalesDetailReport.jsx`):
   - **Fixed**: KPISection background changed from `bg-gray-50` to `bg-[#F9F6F4]` (Famus Cream)
   - **Status**: ✅ Consistent with brand standards

2. **Cost Consistency Report** (`CostConsistencyReport.jsx`):
   - **Verified**: Uses `bg-famus-cream` in main container and `bg-transparent` in KPISection
   - **Status**: ✅ Already correct (transparent allows main background to show)

3. **Profitability Report** (`ProfitabilityReport.jsx`):
   - **Added**: Main container now uses `bg-[#F9F6F4]` (Famus Cream)
   - **Kept**: KPISection with `bg-transparent` to maintain consistency
   - **Status**: ✅ Now consistent with other reports

### Standard Applied:
- **Main containers**: Use Famus Cream `#F9F6F4` or `bg-[#F9F6F4]`
- **KPISection components**: Use `bg-transparent` when main container has Famus Cream, or `bg-[#F9F6F4]` when main container is neutral
- **Result**: All three reports now have consistent Famus Cream backgrounds for all KPI sections

### Files Modified:
- `/src/components/reports/SalesDetailReport.jsx` - KPISection background update
- `/src/components/reports/ProfitabilityReport.jsx` - Main container background added

### Verification:
- ✅ Application builds successfully
- ✅ No compilation errors
- ✅ Visual consistency achieved across all reports
- ✅ Brand standard (Famus Cream) applied uniformly
