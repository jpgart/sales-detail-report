import React, { useState, useMemo, useRef } from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import 'chart.js/auto';
import Papa from 'papaparse';
import { Chart as ChartJS } from 'chart.js/auto';

// Utilidades para filtrar y agrupar datos
const getUnique = (data, key) => [...new Set(data.map(item => item[key]))];

const filterData = (data, filters) => {
  return data.filter(row => {
    return Object.entries(filters).every(([key, value]) =>
      value === 'All' || row[key] === value
    );
  });
};

const groupBy = (data, keys) => {
  return data.reduce((acc, row) => {
    const groupKey = keys.map(k => row[k]).join('-');
    if (!acc[groupKey]) acc[groupKey] = [];
    acc[groupKey].push(row);
    return acc;
  }, {});
};

// Formateo de números
const formatNumber = (num, isMoney = false) => {
  if (num === undefined || num === null || isNaN(num)) return '';
  const n = Number(num);
  return isMoney ? `$${n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : n.toLocaleString('en-US');
};

// Gráfico combinado con doble eje Y
const getChartData = (data, xKey, barKey, lineKey) => {
  const labels = getUnique(data, xKey);
  const barData = labels.map(label => {
    const rows = data.filter(row => row[xKey] === label);
    return rows.reduce((sum, r) => sum + Number(r[barKey] || 0), 0);
  });
  const lineData = labels.map(label => {
    const rows = data.filter(row => row[xKey] === label);
    const vals = rows.map(r => Number(r[lineKey] || 0)).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  });
  return {
    labels,
    datasets: [
      {
        type: 'bar',
        label: barKey,
        data: barData,
        backgroundColor: 'rgba(59,130,246,0.5)',
        yAxisID: 'y',
      },
      {
        type: 'line',
        label: 'Four Star Price Avg',
        data: lineData,
        borderColor: 'rgba(16,185,129,1)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };
};

// KPICards: tarjetas de KPIs grandes, centradas y filtrables por Exporter
const KPICards = ({ data }) => {
  const [selectedExporter, setSelectedExporter] = React.useState('All');
  const exporters = ['All', ...Array.from(new Set(data.map(r => r['Exporter Clean'])).values()).filter(Boolean)];
  const filtered = selectedExporter === 'All' ? data : data.filter(r => r['Exporter Clean'] === selectedExporter);
  // Cálculos de KPIs
  const totalSales = filtered.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
  const totalQty = filtered.reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0);
  const avgPrice = filtered.length ? filtered.map(r => Number(r['Price Four Star'] || 0)).filter(Boolean).reduce((a, b) => a + b, 0) / filtered.filter(r => Number(r['Price Four Star'])).length : 0;
  const uniqueRetailers = new Set(filtered.map(r => r['Retailer Name'])).size;
  const uniqueExporters = new Set(filtered.map(r => r['Exporter Clean'])).size;
  const uniqueVarieties = new Set(filtered.map(r => r['Variety'])).size;
  if (!data.length) return null;
  // Paleta unificada: todos los KPIs con mismo fondo y letras
  const kpis = [
    { label: 'Total Sales', value: `$${totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })}`, color: 'bg-[#E0FBFC] text-[#3D5A80]' },
    { label: 'Total Quantity', value: formatNumber(totalQty), color: 'bg-[#E0FBFC] text-[#3D5A80]' },
    { label: 'Avg. Four Star Price', value: formatNumber(avgPrice, true), color: 'bg-[#E0FBFC] text-[#3D5A80]' },
    { label: 'Retailers', value: uniqueRetailers, color: 'bg-[#E0FBFC] text-[#3D5A80]' },
    { label: 'Exporters', value: uniqueExporters, color: 'bg-[#E0FBFC] text-[#3D5A80]' },
    { label: 'Varieties', value: uniqueVarieties, color: 'bg-[#E0FBFC] text-[#3D5A80]' },
  ];
  return (
    <div className="flex flex-col items-center my-10">
      <div className="mb-6 flex flex-row items-center gap-3">
        <span className="font-semibold text-lg">Exporter:</span>
        <select value={selectedExporter} onChange={e => setSelectedExporter(e.target.value)} className="border p-2 rounded text-lg">
          {exporters.map(e => <option key={e}>{e}</option>)}
        </select>
      </div>
      <div className="flex flex-wrap justify-center gap-10">
        {kpis.map(kpi => (
          <div key={kpi.label} className={`w-56 h-32 rounded-2xl shadow-2xl flex flex-col items-center justify-center text-2xl font-bold ${kpi.color} transition-transform hover:scale-105`}>
            <div className="text-4xl mb-1 text-center truncate" style={{fontSize:'2.2rem', lineHeight:'2.5rem'}}>{kpi.value}</div>
            <div className="text-base font-medium tracking-wide text-center whitespace-nowrap">{kpi.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Key Market Insights Component with Collapsible Sections
const KeyMarketInsights = ({ data }) => {
  const [expandedSections, setExpandedSections] = useState({
    leadership: false,
    risks: false,
    premium: false,
    commodity: false,
    coverage: false
  });

  const toggleSection = (sectionName) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionName]: !prev[sectionName]
    }));
  };

  // Generate insights categorized by section
  const generateCategorizedInsights = () => {
    const allExporters = getUnique(data, 'Exporter Clean').filter(Boolean);
    const allRetailers = getUnique(data, 'Retailer Name').filter(Boolean);
    
    const categorized = {
      leadership: [],
      risks: [],
      premium: [],
      commodity: [],
      coverage: []
    };

    if (!data.length) return categorized;

    // Calculate analysis data
    const exportersAnalysis = allExporters.map(exporter => {
      const exporterData = data.filter(d => d['Exporter Clean'] === exporter);
      const totalSales = exporterData.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
      const retailers = getUnique(exporterData, 'Retailer Name').filter(Boolean);
      
      const retailerStats = retailers.map(retailer => {
        const retailerData = exporterData.filter(d => d['Retailer Name'] === retailer);
        const sales = retailerData.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
        const avgPrice = retailerData.length 
          ? retailerData.map(r => Number(r['Price Four Star'] || 0)).filter(Boolean).reduce((a, b) => a + b, 0) / retailerData.filter(r => Number(r['Price Four Star'])).length
          : 0;
        
        return {
          retailer,
          sales,
          avgPrice,
          percentage: totalSales ? (sales / totalSales * 100) : 0
        };
      }).sort((a, b) => b.sales - a.sales);

      return { exporter, totalSales, topRetailers: retailerStats.slice(0, 5) };
    }).sort((a, b) => b.totalSales - a.totalSales);

    // 🥇 LEADERSHIP INSIGHTS
    if (exportersAnalysis.length > 0) {
      const marketLeader = exportersAnalysis[0];
      const totalMarketSales = data.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
      const leaderShare = totalMarketSales ? (marketLeader.totalSales / totalMarketSales * 100) : 0;
      
      categorized.leadership.push(`${marketLeader.exporter} leads the market with ${leaderShare.toFixed(1)}% of total sales ($${marketLeader.totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })})`);
      
      // Top performers concentration
      const top3Share = exportersAnalysis.slice(0, 3).reduce((sum, e) => sum + e.totalSales, 0);
      const top3Percentage = totalMarketSales ? (top3Share / totalMarketSales * 100) : 0;
      if (top3Percentage > 60) {
        categorized.leadership.push(`Market concentration: Top 3 exporters control ${top3Percentage.toFixed(1)}% of total sales`);
      }
    }

    // Retailer demand leadership
    const retailerDemand = allRetailers.map(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const totalVolume = retailerData.reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0);
      return { retailer, totalVolume };
    }).sort((a, b) => b.totalVolume - a.totalVolume);
    
    if (retailerDemand[0]) {
      const totalVolume = retailerDemand.reduce((sum, r) => sum + r.totalVolume, 0);
      const topRetailerShare = totalVolume ? (retailerDemand[0].totalVolume / totalVolume * 100) : 0;
      categorized.leadership.push(`${retailerDemand[0].retailer} represents the largest share of demand with ${topRetailerShare.toFixed(1)}% of total volume`);
    }

    // ⚠️ RISKS & CONCENTRATION
    exportersAnalysis.forEach(exporterData => {
      if (exporterData.topRetailers && exporterData.topRetailers.length > 0) {
        const topRetailer = exporterData.topRetailers[0];
        if (topRetailer.percentage > 60) {
          categorized.risks.push(`${exporterData.exporter} has high dependency risk: ${topRetailer.percentage.toFixed(1)}% of sales from ${topRetailer.retailer}`);
        }
      }
    });

    // Retailer dependency on exporters
    allRetailers.forEach(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const exporterSales = allExporters.map(exporter => {
        const exporterData = retailerData.filter(d => d['Exporter Clean'] === exporter);
        const sales = exporterData.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
        return { exporter, sales };
      }).filter(e => e.sales > 0).sort((a, b) => b.sales - a.sales);
      
      if (exporterSales.length > 0) {
        const totalRetailerSales = exporterSales.reduce((sum, e) => sum + e.sales, 0);
        const topExporterShare = totalRetailerSales ? (exporterSales[0].sales / totalRetailerSales * 100) : 0;
        if (topExporterShare > 60) {
          categorized.risks.push(`${retailer} depends heavily on ${exporterSales[0].exporter} for ${topExporterShare.toFixed(1)}% of purchases`);
        }
      }
    });

    // 💰 PREMIUM POSITIONING
    const allPrices = data.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
    const avgMarketPrice = allPrices.length ? allPrices.reduce((a, b) => a + b, 0) / allPrices.length : 0;
    
    // Premium exporters (>$25)
    exportersAnalysis.forEach(exporterData => {
      if (exporterData.topRetailers && exporterData.topRetailers.length > 0) {
        const avgExporterPrice = exporterData.topRetailers.reduce((sum, r) => sum + r.avgPrice, 0) / exporterData.topRetailers.length;
        if (avgExporterPrice > 25) {
          categorized.premium.push(`${exporterData.exporter} maintains premium pricing at $${avgExporterPrice.toFixed(2)} average`);
        }
      }
    });

    // Premium retailers (above market average)
    allRetailers.forEach(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const retailerPrices = retailerData.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
      if (retailerPrices.length > 0) {
        const avgRetailerPrice = retailerPrices.reduce((a, b) => a + b, 0) / retailerPrices.length;
        if (avgRetailerPrice > avgMarketPrice * 1.2) { // 20% above market
          categorized.premium.push(`${retailer} pays premium prices ($${avgRetailerPrice.toFixed(2)}) indicating high-value positioning`);
        }
      }
    });

    // Premium varieties
    const varieties = getUnique(data, 'Variety').filter(Boolean);
    const varietyPrices = varieties.map(variety => {
      const varietyData = data.filter(d => d['Variety'] === variety);
      const prices = varietyData.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
      const avgPrice = prices.length ? prices.reduce((a, b) => a + b, 0) / prices.length : 0;
      return { variety, avgPrice };
    }).sort((a, b) => b.avgPrice - a.avgPrice);
    
    if (varietyPrices[0] && varietyPrices[0].avgPrice > 0) {
      categorized.premium.push(`${varietyPrices[0].variety} commands highest pricing at $${varietyPrices[0].avgPrice.toFixed(2)} average`);
    }

    // 📉 COMMODITY PATTERNS
    // Low price exporters
    exportersAnalysis.forEach(exporterData => {
      if (exporterData.topRetailers && exporterData.topRetailers.length > 0) {
        const avgExporterPrice = exporterData.topRetailers.reduce((sum, r) => sum + r.avgPrice, 0) / exporterData.topRetailers.length;
        if (avgExporterPrice < avgMarketPrice * 0.8 && avgExporterPrice > 0) { // 20% below market
          categorized.commodity.push(`${exporterData.exporter} focuses on commodity pricing at $${avgExporterPrice.toFixed(2)} average`);
        }
      }
    });

    // Low price retailers (≤$10)
    allRetailers.forEach(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const retailerPrices = retailerData.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
      if (retailerPrices.length > 0) {
        const avgRetailerPrice = retailerPrices.reduce((a, b) => a + b, 0) / retailerPrices.length;
        if (avgRetailerPrice <= 10) {
          categorized.commodity.push(`${retailer} pursues volume strategy with low prices ($${avgRetailerPrice.toFixed(2)} average)`);
        }
      }
    });

    // 📦 VOLUME & COVERAGE
    // Exporter market reach
    exportersAnalysis.forEach(exporterData => {
      const exporterRetailers = getUnique(data.filter(d => d['Exporter Clean'] === exporterData.exporter), 'Retailer Name').filter(Boolean);
      if (exporterRetailers.length >= 5) {
        categorized.coverage.push(`${exporterData.exporter} has broad reach, selling to ${exporterRetailers.length} unique retailers`);
      }
    });

    // Retailer diversification
    allRetailers.forEach(retailer => {
      const retailerExporters = getUnique(data.filter(d => d['Retailer Name'] === retailer), 'Exporter Clean').filter(Boolean);
      if (retailerExporters.length >= 3) {
        categorized.coverage.push(`${retailer} diversifies supply across ${retailerExporters.length} different exporters`);
      }
    });

    return categorized;
  };

  const categorizedInsights = generateCategorizedInsights();
  
  if (!data.length) return null;

  return (
    <div className="my-8 bg-[#F9F6F4] rounded-2xl p-6 shadow-md border border-[#98C1D9]">
      <h3 className="text-2xl font-bold mb-6 text-[#293241]">🔍 Key Market Insights</h3>
      
      {/* 🥇 Market Share & Leadership */}
      <div className="mb-4">
        <button 
          onClick={() => toggleSection('leadership')}
          className="w-full text-left flex items-center justify-between p-3 bg-[#E0FBFC] rounded-lg hover:bg-[#D4F1F4] transition-colors"
        >
          <h4 className="text-lg font-bold text-[#3D5A80]">🥇 Market Share & Leadership</h4>
          <span className="text-[#3D5A80]">{expandedSections.leadership ? '▼' : '▶'}</span>
        </button>
        {expandedSections.leadership && (
          <div className="mt-2 pl-4">
            <ul className="space-y-1">
              {categorizedInsights.leadership.map((insight, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-[#EE6C4D] mr-2">•</span>
                  <span className="text-[#293241]">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* ⚠️ Dependency & Concentration Risks */}
      <div className="mb-4">
        <button 
          onClick={() => toggleSection('risks')}
          className="w-full text-left flex items-center justify-between p-3 bg-[#FEE2E2] rounded-lg hover:bg-[#FECACA] transition-colors"
        >
          <h4 className="text-lg font-bold text-[#991B1B]">⚠️ Dependency & Concentration Risks</h4>
          <span className="text-[#991B1B]">{expandedSections.risks ? '▼' : '▶'}</span>
        </button>
        {expandedSections.risks && (
          <div className="mt-2 pl-4">
            <ul className="space-y-1">
              {categorizedInsights.risks.map((insight, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-[#DC2626] mr-2">•</span>
                  <span className="text-[#293241]">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 💰 Premium Price Positioning */}
      <div className="mb-4">
        <button 
          onClick={() => toggleSection('premium')}
          className="w-full text-left flex items-center justify-between p-3 bg-[#F0FDF4] rounded-lg hover:bg-[#DCFCE7] transition-colors"
        >
          <h4 className="text-lg font-bold text-[#166534]">💰 Premium Price Positioning</h4>
          <span className="text-[#166534]">{expandedSections.premium ? '▼' : '▶'}</span>
        </button>
        {expandedSections.premium && (
          <div className="mt-2 pl-4">
            <ul className="space-y-1">
              {categorizedInsights.premium.map((insight, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-[#059669] mr-2">•</span>
                  <span className="text-[#293241]">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 📉 Low Price / Commodity Patterns */}
      <div className="mb-4">
        <button 
          onClick={() => toggleSection('commodity')}
          className="w-full text-left flex items-center justify-between p-3 bg-[#FEF3C7] rounded-lg hover:bg-[#FDE68A] transition-colors"
        >
          <h4 className="text-lg font-bold text-[#92400E]">📉 Low Price / Commodity Patterns</h4>
          <span className="text-[#92400E]">{expandedSections.commodity ? '▼' : '▶'}</span>
        </button>
        {expandedSections.commodity && (
          <div className="mt-2 pl-4">
            <ul className="space-y-1">
              {categorizedInsights.commodity.map((insight, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-[#D97706] mr-2">•</span>
                  <span className="text-[#293241]">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 📦 Volume & Coverage */}
      <div className="mb-4">
        <button 
          onClick={() => toggleSection('coverage')}
          className="w-full text-left flex items-center justify-between p-3 bg-[#F3E8FF] rounded-lg hover:bg-[#E9D5FF] transition-colors"
        >
          <h4 className="text-lg font-bold text-[#6B21A8]">📦 Volume & Coverage</h4>
          <span className="text-[#6B21A8]">{expandedSections.coverage ? '▼' : '▶'}</span>
        </button>
        {expandedSections.coverage && (
          <div className="mt-2 pl-4">
            <ul className="space-y-1">
              {categorizedInsights.coverage.map((insight, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-[#7C3AED] mr-2">•</span>
                  <span className="text-[#293241]">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

// Pie chart data util
const getPieData = (data, labelKey, valueKey) => {
  const labels = getUnique(data, labelKey);
  const values = labels.map(label => {
    const rows = data.filter(row => row[labelKey] === label);
    return rows.reduce((sum, r) => sum + Number(r[valueKey] || 0), 0);
  });
  const total = values.reduce((a, b) => a + b, 0);
  return {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: [
          '#60a5fa', '#64748b', '#34d399', '#475569', '#a78bfa', '#f472b6', '#facc15', '#38bdf8', '#fca5a5', '#a3e635',
        ],
        // Mostrar porcentaje en tooltip
        datalabels: {
          display: true,
          color: '#222',
          font: { weight: 'bold', size: 16 },
          formatter: (value, ctx) => {
            const percent = total ? (value / total * 100) : 0;
            return percent > 2 ? percent.toFixed(1) + '%' : '';
          },
        },
      },
    ],
  };
};

// Opciones de gráfico globales
const chartOptions = {
  responsive: true,
  interaction: { mode: 'index', intersect: false },
  plugins: { legend: { position: 'top' } },
  scales: {
    y: {
      type: 'linear',
      position: 'left',
      title: { display: true, text: 'Sale Quantity' },
      beginAtZero: true,
    },
    y1: {
      type: 'linear',
      position: 'right',
      title: { display: true, text: 'Four Star Price Avg' },
      grid: { drawOnChartArea: false },
      beginAtZero: true,
    },
  },
};

// Gráfico por variedad
const getVarietyChartData = (data) => {
  const labels = getUnique(data, 'Variety');
  const barData = labels.map(label => {
    const rows = data.filter(row => row['Variety'] === label);
    return rows.reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0);
  });
  const lineData = labels.map(label => {
    const rows = data.filter(row => row['Variety'] === label);
    const vals = rows.map(r => Number(r['Price Four Star'] || 0)).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  });
  return {
    labels,
    datasets: [
      {
        type: 'bar',
        label: 'Sale Quantity',
        data: barData,
        backgroundColor: 'rgba(59,130,246,0.5)',
        yAxisID: 'y',
      },
      {
        type: 'line',
        label: 'Four Star Price Avg',
        data: lineData,
        borderColor: 'rgba(16,185,129,1)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };
};

// Visualización temporal (línea de tiempo)
const getTimelineChartData = (data) => {
  // Agrupar por fecha
  const dateKey = 'Sale Date';
  const labels = getUnique(data, dateKey).sort();
  const barData = labels.map(label => {
    const rows = data.filter(row => row[dateKey] === label);
    return rows.reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0);
  });
  const lineData = labels.map(label => {
    const rows = data.filter(row => row[dateKey] === label);
    const vals = rows.map(r => Number(r['Price Four Star'] || 0)).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  });
  return {
    labels,
    datasets: [
      {
        type: 'bar',
        label: 'Sale Quantity',
        data: barData,
        backgroundColor: 'rgba(59,130,246,0.5)',
        yAxisID: 'y',
      },
      {
        type: 'line',
        label: 'Four Star Price Avg',
        data: lineData,
        borderColor: 'rgba(16,185,129,1)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };
};

// Módulo de alertas por diferencia de precio
const PriceAlerts = ({ data, threshold = 0.15 }) => {
  if (!data.length) return null;
  const globalAvg = useMemo(() => {
    const vals = data.map(r => Number(r['Price Four Star'])).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  }, [data]);
  const alerts = useMemo(() => {
    const byRetailer = groupBy(data, ['Retailer Name']);
    return Object.entries(byRetailer).map(([retailer, rows]) => {
      const avg = rows.map(r => Number(r['Price Four Star'])).filter(Boolean);
      const avgVal = avg.length ? avg.reduce((a, b) => a + b, 0) / avg.length : 0;
      const diff = Math.abs(avgVal - globalAvg) / (globalAvg || 1);
      return { retailer, avg: avgVal, diff };
    }).filter(a => a.diff > threshold).sort((a, b) => b.diff - a.diff);
  }, [data, globalAvg, threshold]);
  if (!alerts.length) return null;
  return (
    <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4">
      <strong>Price Alerts:</strong>
      <ul className="list-disc ml-6">
        {alerts.map(a => (
          <li key={a.retailer}>
            {a.retailer}: {formatNumber(a.avg, true)} ({(a.diff * 100).toFixed(1)}% diff from avg)
          </li>
        ))}
      </ul>
    </div>
  );
};

// Tabla ordenable y con ajuste de ancho de columnas
const columns = [
  { key: 'Exporter Clean', label: 'Exporter', width: 120 },
  { key: 'Retailer Name', label: 'Retailer', width: 140 },
  { key: 'Variety', label: 'Variety', width: 120 },
  { key: 'Size', label: 'Size', width: 80 },
  { key: 'Sale Quantity', label: 'Sale Quantity', isNumber: true, width: 120 },
  { key: 'Sales Amount', label: 'Sales Amount', isNumber: true, isMoney: true, width: 120 },
  { key: 'Price Four Star', label: 'Four Star Price Avg', isNumber: true, isMoney: true, isAvg: true, width: 140 },
];

const SortableTable = ({ data }) => {
  const [sortCol, setSortCol] = useState('');
  const [sortDir, setSortDir] = useState('asc');
  const [colWidths, setColWidths] = useState(columns.map(c => c.width || 120));

  const handleResize = (idx, e) => {
    const startX = e.clientX;
    const startWidth = colWidths[idx];
    const onMouseMove = moveEvent => {
      const newWidths = [...colWidths];
      newWidths[idx] = Math.max(60, startWidth + moveEvent.clientX - startX);
      setColWidths(newWidths);
    };
    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  const sorted = useMemo(() => {
    if (!sortCol) return data.slice(0, 20);
    const col = columns.find(c => c.key === sortCol);
    const sortedData = [...data].sort((a, b) => {
      let aVal = a[sortCol], bVal = b[sortCol];
      if (col?.isNumber) {
        aVal = Number(aVal) || 0;
        bVal = Number(bVal) || 0;
      } else {
        aVal = aVal || '';
        bVal = bVal || '';
      }
      if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return sortedData.slice(0, 20);
  }, [data, sortCol, sortDir]);

  // Calcular promedio para Four Star Price
  const avgPrice = arr => {
    const vals = arr.map(r => Number(r['Price Four Star'])).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-xs text-center">
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th
                key={col.key}
                style={{ width: colWidths[idx], minWidth: 60, position: 'relative' }}
                className="px-2 py-1 font-bold bg-gray-100 cursor-pointer select-none group"
                onClick={() => {
                  if (sortCol === col.key) setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
                  else { setSortCol(col.key); setSortDir('asc'); }
                }}
              >
                {col.label} {sortCol === col.key ? (sortDir === 'asc' ? '▲' : '▼') : ''}
                <span
                  style={{ position: 'absolute', right: 0, top: 0, height: '100%', width: 8, cursor: 'col-resize', zIndex: 10 }}
                  onMouseDown={e => { e.stopPropagation(); handleResize(idx, e); }}
                  className="inline-block align-middle group-hover:bg-blue-200"
                />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row, i) => (
            <tr key={i} className="border-b">
              {columns.map((col, idx) => (
                <td key={col.key} className="px-2 py-1">
                  {col.isAvg
                    ? formatNumber(avgPrice([row]), col.isMoney)
                    : col.isNumber
                      ? formatNumber(row[col.key], col.isMoney)
                      : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Tabla interactiva con filtros rápidos
const FilterableTable = ({ data }) => {
  const [filters, setFilters] = useState(columns.map(() => ''));
  const filtered = useMemo(() => {
    return data.filter(row =>
      columns.every((col, idx) =>
        !filters[idx] || String(row[col.key] || '').toLowerCase().includes(filters[idx].toLowerCase())
      )
    );
  }, [data, filters]);
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-xs text-center">
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th key={col.key} className="px-2 py-1 font-bold bg-gray-100">
                <div>{col.label}</div>
                <input
                  className="w-full border rounded text-xs px-1 mt-1"
                  value={filters[idx]}
                  onChange={e => {
                    const newFilters = [...filters];
                    newFilters[idx] = e.target.value;
                    setFilters(newFilters);
                  }}
                  placeholder="Filter..."
                />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filtered.slice(0, 15).map((row, i) => (
            <tr key={i} className="border-b">
              {columns.map((col, idx) => (
                <td key={col.key} className="px-2 py-1">
                  {col.isAvg
                    ? formatNumber(row[col.key], col.isMoney)
                    : col.isNumber
                      ? formatNumber(row[col.key], col.isMoney)
                      : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Heatmap util (azul oscuro a blanco a rojo oscuro)
const getHeatmapMatrix = (data, rowKey, colKey, valueKey, agg = 'avg', rowFilter = 'All', colFilter = 'All', rowSort = 'desc', colSort = 'asc') => {
  let rows = getUnique(data, rowKey);
  let cols = getUnique(data, colKey);
  if (rowFilter !== 'All') rows = rows.filter(r => r === rowFilter);
  if (colFilter !== 'All') cols = cols.filter(c => c === colFilter);
  if (rowSort === 'desc') rows = [...rows].sort().reverse();
  else rows = [...rows].sort();
  cols = [...cols].sort(); // Siempre ascendente para columnas
  const matrix = rows.map(row =>
    cols.map(col => {
      const filtered = data.filter(d => d[rowKey] === row && d[colKey] === col);
      const vals = filtered.map(d => Number(d[valueKey])).filter(Boolean);
      if (!vals.length) return null;
      if (agg === 'sum') return vals.reduce((a, b) => a + b, 0);
      return vals.reduce((a, b) => a + b, 0) / vals.length;
    })
  );
  return { rows, cols, matrix };
};
// Heatmap: regla de colores personalizada
const getHeatColor = (val, min, max) => {
  if (val === null) return '#f3f4f6';
  if (val < 0) return '#ee6c4d';
  if (max === min) return '#e0fbfc';
  const percent = (val - min) / (max - min + 0.0001);
  if (percent > 0.85) return '#3d5a80';
  if (percent > 0.5) return '#98c1d9';
  if (percent > 0.01) return '#e0fbfc';
  return '#e0fbfc';
};
const Heatmap = ({ data, rowKey, colKey, valueKey, agg, title }) => {
  const [rowFilter, setRowFilter] = useState('All');
  const [rowSort, setRowSort] = useState('desc');
  const [colSort, setColSort] = useState(title.includes('Retailer vs Variety') ? 'desc' : 'asc');
  const { rows, cols, matrix } = getHeatmapMatrix(data, rowKey, colKey, valueKey, agg, rowFilter, 'All', rowSort, colSort);
  const max = Math.max(...matrix.flat().filter(v => v !== null));
  const min = Math.min(...matrix.flat().filter(v => v !== null));
  const allRows = getUnique(data, rowKey);
  return (
    <div className="overflow-x-auto my-8">
      <h3 className="font-bold mb-2 text-lg">{title}</h3>
      <div className="flex gap-2 mb-2 flex-wrap">
        <span>Row:</span>
        <select value={rowFilter} onChange={e => setRowFilter(e.target.value)} className="border p-1 rounded">
          <option>All</option>
          {allRows.map(r => <option key={r}>{r}</option>)}
        </select>
        <button onClick={() => setRowSort(rowSort === 'asc' ? 'desc' : 'asc')} className="border px-2 rounded">Sort {rowSort === 'asc' ? '▲' : '▼'}</button>
        {title.includes('Retailer vs Variety') && (
          <>
            <span>Col:</span>
            <button onClick={() => setColSort(colSort === 'asc' ? 'desc' : 'asc')} className="border px-2 rounded">Sort {colSort === 'asc' ? '▲' : '▼'}</button>
          </>
        )}
      </div>
      <table className="border text-xs">
        <thead>
          <tr>
            <th className="bg-gray-100 px-2 py-1">{rowKey} \ {colKey}</th>
            {cols.map(col => <th key={col} className="bg-gray-100 px-2 py-1">{col}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row}>
              <td className="font-bold bg-gray-100 px-2 py-1">{row}</td>
              {cols.map((col, j) => {
                const val = matrix[i][j];
                let cellValue = val;
                if (title.includes('Exporter vs Retailer') && val !== null) cellValue = `$${Math.round(val).toLocaleString('en-US')}`;
                else if (valueKey.includes('Price') && val !== null) cellValue = formatNumber(val, true);
                else if (val !== null) cellValue = formatNumber(val);
                return <td key={col} style={{background:getHeatColor(val,min,max), color:'#222'}} className="px-2 py-1 font-semibold">{val !== null ? cellValue : '-'}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Ranking horizontal con selección múltiple para top 20
const RankingBar = ({ data, groupKey, valueKey, title }) => {
  const [selected, setSelected] = useState([0,1]);
  const groups = getUnique(data, groupKey);
  const ranked = groups.map(g => {
    const vals = data.filter(d => d[groupKey] === g).map(d => Number(d[valueKey])).filter(Boolean);
    return { key: g, value: vals.length ? vals.reduce((a, b) => a + b, 0) : 0 };
  }).sort((a, b) => b.value - a.value).slice(0, 20);
  const handleSelect = e => {
    const options = Array.from(e.target.options);
    setSelected(options.filter(o => o.selected).map(o => Number(o.value)));
  };
  return (
    <div className="my-8">
      <h3 className="font-bold mb-2">{title}</h3>
      <div className="mb-2 flex gap-2 items-center">
        <span>Selecciona posiciones (Ctrl/Cmd para múltiple):</span>
        <select multiple value={selected} onChange={handleSelect} className="border p-1 rounded h-32">
          {ranked.map((r, idx) => <option key={r.key} value={idx}>{`#${idx+1} - ${r.key}`}</option>)}
        </select>
      </div>
      <Bar data={{
        labels: selected.map(i => ranked[i]?.key),
        datasets: [{ label: valueKey, data: selected.map(i => ranked[i]?.value), backgroundColor: '#3d5a80' }],
      }} options={{ indexAxis: 'y', plugins: { legend: { display: false } } }} />
    </div>
  );
};

// ExporterComparator: usar colores opacos/translúcidos
const ExporterComparator = ({ data, exporters }) => {
  const [exp1, setExp1] = useState(exporters[0] || '');
  const [exp2, setExp2] = useState(exporters[1] || '');
  const data1 = data.filter(d => d['Exporter Clean'] === exp1);
  const data2 = data.filter(d => d['Exporter Clean'] === exp2);
  const labels = getUnique([...data1, ...data2], 'Retailer Name');
  const barData1 = labels.map(label => data1.filter(r => r['Retailer Name'] === label).reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0));
  const barData2 = labels.map(label => data2.filter(r => r['Retailer Name'] === label).reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0));
  const lineData1 = labels.map(label => {
    const vals = data1.filter(r => r['Retailer Name'] === label).map(r => Number(r['Price Four Star'] || 0)).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  });
  const lineData2 = labels.map(label => {
    const vals = data2.filter(r => r['Retailer Name'] === label).map(r => Number(r['Price Four Star'] || 0)).filter(Boolean);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  });
  return (
    <div className="my-8">
      <h3 className="font-bold mb-2 text-lg">Exporter Comparator</h3>
      <div className="flex gap-4 mb-2">
        <select value={exp1} onChange={e => setExp1(e.target.value)} className="border p-1 rounded">{exporters.map(e => <option key={e}>{e}</option>)}</select>
        <select value={exp2} onChange={e => setExp2(e.target.value)} className="border p-1 rounded">{exporters.map(e => <option key={e}>{e}</option>)}</select>
      </div>
      <div className="w-full max-w-4xl mx-auto">
        <Bar data={{
          labels,
          datasets: [
            { type: 'bar', label: `Sale Quantity: ${exp1}`, data: barData1, backgroundColor: 'rgba(152,193,217,0.5)', yAxisID: 'y' },
            { type: 'bar', label: `Sale Quantity: ${exp2}`, data: barData2, backgroundColor: 'rgba(238,108,77,0.5)', yAxisID: 'y' },
            { type: 'line', label: `Four Star Price Avg: ${exp1}`, data: lineData1, borderColor: 'rgba(152,193,217,1)', borderWidth: 2, fill: false, tension: 0.4, yAxisID: 'y1' },
            { type: 'line', label: `Four Star Price Avg: ${exp2}`, data: lineData2, borderColor: 'rgba(238,108,77,1)', borderWidth: 2, fill: false, tension: 0.4, yAxisID: 'y1' },
          ]
        }} options={chartOptions} />
      </div>
    </div>
  );
};

// Exportar tabla a CSV
const exportToCSV = (data, filename = 'export.csv') => {
  const csv = [columns.map(c => c.label).join(',')].concat(
    data.map(row => columns.map(c => row[c.key]).join(','))
  ).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

// Historial de precios por Retailer/Exportador
const PriceHistory = ({ data, groupKey }) => {
  const groups = getUnique(data, groupKey);
  const [selected, setSelected] = useState(groups[0] || '');
  const filtered = data.filter(d => d[groupKey] === selected);
  return (
    <div className="my-4">
      <h3 className="font-bold mb-2">Price History ({groupKey})</h3>
      <select value={selected} onChange={e => setSelected(e.target.value)} className="border p-1 rounded mb-2">{groups.map(g => <option key={g}>{g}</option>)}</select>
      <Line data={getTimelineChartData(filtered)} options={chartOptions} />
    </div>
  );
};

// Índice de navegación unificado con fondo #98C1D9 y letras #3D5A80
const SectionIndex = ({ refs }) => (
  <nav className="my-8 flex flex-wrap gap-4 text-lg font-bold justify-center">
    {Object.entries(refs).map(([k, ref], i) => (
      <button
        key={k}
        onClick={() => ref.current.scrollIntoView({ behavior: 'smooth' })}
        className="px-4 py-2 rounded transition bg-[#98C1D9] text-[#3D5A80] hover:bg-[#7DB0D1]"
      >
        {k.replace('KPIs', 'KPIs')
          .replace('Key Insights', 'Key Insights')
          .replace('Exporter Comparator', 'Exporter Comparator')
          .replace('Sales by Variety', 'Sales by Variety')
          .replace('Sales Timeline', 'Sales Timeline')
          .replace('Price History Retailer', 'Price History (Retailer)')
          .replace('Price History Exporter', 'Price History (Exporter)')
          .replace('Heatmap Retailer vs Variety', 'Heatmap: Retailer / Variety')
          .replace('Heatmap Exporter vs Retailer', 'Heatmap: Exporter / Retailer')
          .replace('Exporter-Retailer Analysis', 'Top 5 Analysis')
          .replace('Ranking Retailers', 'Top Retailers by Sales')
          .replace('Ranking Exporters', 'Top Exporters by Sales')
          .replace('Sales by Retailer/Exporter/Variety/Size', 'Filtered Sales Analysis')
          .replace('Price Alerts by Variety', 'Price Alerts')}
      </button>
    ))}
  </nav>
);

// Automatic Analysis: Top 5 Retailers per Exporter with Insights
const ExporterRetailerAnalysis = ({ data }) => {
  // Calculate top retailers per exporter
  const getTopRetailersPerExporter = () => {
    const exporters = getUnique(data, 'Exporter Clean').filter(Boolean);
    
    return exporters.map(exporter => {
      const exporterData = data.filter(d => d['Exporter Clean'] === exporter);
      const retailers = getUnique(exporterData, 'Retailer Name').filter(Boolean);
      
      // Calculate TOTAL sales for the exporter (all retailers)
      const exporterTotalSales = exporterData.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
      
      const allRetailerStats = retailers.map(retailer => {
        const retailerData = exporterData.filter(d => d['Retailer Name'] === retailer);
        const totalSales = retailerData.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
        const totalQuantity = retailerData.reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0);
        const avgPrice = retailerData.length 
          ? retailerData.map(r => Number(r['Price Four Star'] || 0)).filter(Boolean).reduce((a, b) => a + b, 0) / retailerData.filter(r => Number(r['Price Four Star'])).length
          : 0;
        const varietyCount = new Set(retailerData.map(r => r['Variety'])).size;
        
        return {
          retailer,
          totalSales,
          totalQuantity,
          avgPrice,
          varietyCount,
          percentage: exporterTotalSales ? (totalSales / exporterTotalSales * 100) : 0
        };
      }).sort((a, b) => b.totalSales - a.totalSales);
      
      const topRetailers = allRetailerStats.slice(0, 5);
      
      // Filter worst retailers to only include those with sales > $1
      const validWorstRetailers = allRetailerStats.filter(retailer => retailer.totalSales > 1);
      const worstRetailers = validWorstRetailers.slice(-5).reverse(); // Get last 5 and reverse to show worst first
      
      // Get odd retailers (sales amount <= $0)
      const oddRetailers = allRetailerStats.filter(retailer => retailer.totalSales <= 0);
      
      return { exporter, topRetailers, worstRetailers, oddRetailers, totalSales: exporterTotalSales };
    }).sort((a, b) => b.totalSales - a.totalSales);
  };

  // Generate automatic insights
  const generateInsights = (analysisData) => {
    const insights = [];
    
    // Check if we have data
    if (!analysisData || analysisData.length === 0) {
      insights.push('No data available for analysis. Please upload a CSV file to see insights.');
      return insights;
    }
    
    // Calculate market totals
    const totalMarketSales = analysisData.reduce((sum, e) => sum + e.totalSales, 0);
    const allRetailers = getUnique(data, 'Retailer Name').filter(Boolean);
    const allExporters = getUnique(data, 'Exporter Clean').filter(Boolean);
    
    // 🥇 MARKET SHARE & LEADERSHIP
    insights.push('🥇 Market Share & Leadership');
    
    const topExporter = analysisData[0];
    if (topExporter && topExporter.exporter) {
      const marketShare = totalMarketSales ? (topExporter.totalSales / totalMarketSales * 100) : 0;
      insights.push(`Market Leader: ${topExporter.exporter} dominates with ${marketShare.toFixed(1)}% market share ($${topExporter.totalSales.toLocaleString()})`);
    }
    
    // Top 3 Exporters concentration
    const top3Sales = analysisData.slice(0, 3).reduce((sum, e) => sum + e.totalSales, 0);
    const top3Concentration = totalMarketSales ? (top3Sales / totalMarketSales * 100) : 0;
    insights.push(`Top 3 Exporters account for ${top3Concentration.toFixed(1)}% of total sales → ${top3Concentration > 70 ? 'high market concentration' : 'moderate market concentration'}`);
    
    // Largest retailer by demand
    const retailerDemand = allRetailers.map(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const totalVolume = retailerData.reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0);
      return { retailer, totalVolume };
    }).sort((a, b) => b.totalVolume - a.totalVolume);
    
    if (retailerDemand[0]) {
      const totalVolume = retailerDemand.reduce((sum, r) => sum + r.totalVolume, 0);
      const topRetailerShare = totalVolume ? (retailerDemand[0].totalVolume / totalVolume * 100) : 0;
      insights.push(`${retailerDemand[0].retailer} represents the largest share of demand, receiving ${topRetailerShare.toFixed(1)}% of total volume`);
    }
    
    // Retailers that buy from 75%+ of exporters (market knowledge)
    const retailersWithBroadCoverage = allRetailers.filter(retailer => {
      const retailerExporters = getUnique(data.filter(d => d['Retailer Name'] === retailer), 'Exporter Clean').filter(Boolean);
      return retailerExporters.length >= (allExporters.length * 0.75);
    });
    retailersWithBroadCoverage.forEach(retailer => {
      const exporterCount = getUnique(data.filter(d => d['Retailer Name'] === retailer), 'Exporter Clean').filter(Boolean).length;
      insights.push(`${retailer} has broad market knowledge, sourcing from ${exporterCount}/${allExporters.length} exporters (${((exporterCount/allExporters.length)*100).toFixed(0)}%)`);
    });
    
    insights.push(''); // Empty line separator
    
    // ⚠️ DEPENDENCY & CONCENTRATION RISKS
    insights.push('⚠️ Dependency & Concentration Risks');
    
    // High concentration exporters (>60%)
    const highConcentrationExporters = analysisData.filter(exporterData => {
      if (!exporterData.topRetailers || exporterData.topRetailers.length === 0) return false;
      return exporterData.topRetailers[0].percentage > 60;
    });
    
    highConcentrationExporters.forEach(exporterData => {
      const topRetailer = exporterData.topRetailers[0];
      insights.push(`${exporterData.exporter} has more than 60% of sales concentrated in ${topRetailer.retailer} (${topRetailer.percentage.toFixed(1)}%) → high dependency risk`);
    });
    
    // Retailer dependency on exporters
    allRetailers.forEach(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const exporterSales = allExporters.map(exporter => {
        const exporterData = retailerData.filter(d => d['Exporter Clean'] === exporter);
        const sales = exporterData.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
        return { exporter, sales };
      }).filter(e => e.sales > 0).sort((a, b) => b.sales - a.sales);
      
      if (exporterSales.length > 0) {
        const totalRetailerSales = exporterSales.reduce((sum, e) => sum + e.sales, 0);
        const topExporterShare = totalRetailerSales ? (exporterSales[0].sales / totalRetailerSales * 100) : 0;
        if (topExporterShare > 60) {
          insights.push(`${retailer} depends mainly on ${exporterSales[0].exporter}, sourcing ${topExporterShare.toFixed(1)}% of purchases from them`);
        }
      }
    });
    
    insights.push(''); // Empty line separator
    
    // 💰 PREMIUM PRICE POSITIONING
    insights.push('💰 Premium Price Positioning');
    
    // Premium exporters (>$25)
    analysisData.forEach(exporterData => {
      if (!exporterData || !exporterData.topRetailers || exporterData.topRetailers.length === 0) return;
      const avgExporterPrice = exporterData.topRetailers.reduce((sum, r) => sum + r.avgPrice, 0) / exporterData.topRetailers.length;
      if (avgExporterPrice > 25) {
        insights.push(`${exporterData.exporter} maintains a high average price ($${avgExporterPrice.toFixed(2)}) compared to peers`);
      }
    });
    
    // Premium retailers (above average price)
    const allPrices = data.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
    const avgMarketPrice = allPrices.length ? allPrices.reduce((a, b) => a + b, 0) / allPrices.length : 0;
    
    allRetailers.forEach(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const retailerPrices = retailerData.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
      if (retailerPrices.length > 0) {
        const avgRetailerPrice = retailerPrices.reduce((a, b) => a + b, 0) / retailerPrices.length;
        if (avgRetailerPrice > avgMarketPrice * 1.2) { // 20% above market
          insights.push(`${retailer} pays above-average prices ($${avgRetailerPrice.toFixed(2)}) → indicates premium relationship`);
        }
      }
    });
    
    // Premium varieties
    const varieties = getUnique(data, 'Variety').filter(Boolean);
    const varietyPrices = varieties.map(variety => {
      const varietyData = data.filter(d => d['Variety'] === variety);
      const prices = varietyData.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
      const avgPrice = prices.length ? prices.reduce((a, b) => a + b, 0) / prices.length : 0;
      return { variety, avgPrice };
    }).sort((a, b) => b.avgPrice - a.avgPrice);
    
    if (varietyPrices[0] && varietyPrices[0].avgPrice > 0) {
      insights.push(`${varietyPrices[0].variety} commands the highest average price ($${varietyPrices[0].avgPrice.toFixed(2)}) → premium variety positioning`);
    }
    
    insights.push(''); // Empty line separator
    
    // 📉 LOW PRICE / COMMODITY PATTERNS
    insights.push('📉 Low Price / Commodity Patterns');
    
    // Low price exporters
    analysisData.forEach(exporterData => {
      if (!exporterData || !exporterData.topRetailers || exporterData.topRetailers.length === 0) return;
      const avgExporterPrice = exporterData.topRetailers.reduce((sum, r) => sum + r.avgPrice, 0) / exporterData.topRetailers.length;
      if (avgExporterPrice < avgMarketPrice * 0.8 && avgExporterPrice > 0) { // 20% below market
        insights.push(`${exporterData.exporter} has below-average prices ($${avgExporterPrice.toFixed(2)}), indicating possible commodity positioning`);
      }
    });
    
    // Low price retailers (≤$10)
    allRetailers.forEach(retailer => {
      const retailerData = data.filter(d => d['Retailer Name'] === retailer);
      const retailerPrices = retailerData.map(r => Number(r['Price Four Star'] || 0)).filter(p => p > 0);
      if (retailerPrices.length > 0) {
        const avgRetailerPrice = retailerPrices.reduce((a, b) => a + b, 0) / retailerPrices.length;
        if (avgRetailerPrice <= 10) {
          insights.push(`${retailer} consistently buys at lower prices ($${avgRetailerPrice.toFixed(2)}) → volume-focused approach`);
        }
      }
    });
    
    insights.push(''); // Empty line separator
    
    // 📦 VOLUME & COVERAGE
    insights.push('📦 Volume & Coverage');
    
    // Exporter market reach
    analysisData.forEach(exporterData => {
      const exporterRetailers = getUnique(data.filter(d => d['Exporter Clean'] === exporterData.exporter), 'Retailer Name').filter(Boolean);
      if (exporterRetailers.length >= 5) { // Threshold for "high reach"
        insights.push(`${exporterData.exporter} sold to ${exporterRetailers.length} unique retailers, indicating ${exporterRetailers.length >= 10 ? 'high' : 'moderate'} market reach`);
      }
    });
    
    // Retailer diversification
    allRetailers.forEach(retailer => {
      const retailerExporters = getUnique(data.filter(d => d['Retailer Name'] === retailer), 'Exporter Clean').filter(Boolean);
      if (retailerExporters.length >= 3) { // Threshold for "diversification"
        insights.push(`${retailer} sourced from ${retailerExporters.length} different exporters, indicating ${retailerExporters.length >= 5 ? 'high' : 'moderate'} diversification`);
      }
    });
    
    return insights;
  };

  const analysisData = getTopRetailersPerExporter();
  const insights = generateInsights(analysisData);
  
  if (!data.length) return null;

  return (
    <div className="my-8 bg-[#F9F6F4] rounded-2xl p-6 shadow-md border border-[#98C1D9]">
      <h3 className="text-2xl font-bold mb-6 text-[#293241]">� Exporter-Retailer Analysis</h3>
      
      {analysisData.map(exporterData => (
        <div key={exporterData.exporter} className="mb-8 border-b border-gray-200 pb-6 last:border-b-0">
          <div className="bg-[#E0FBFC] p-4 rounded-lg mb-4">
            <h4 className="text-xl font-bold text-[#3D5A80] mb-2">{exporterData.exporter}</h4>
            <p className="text-[#293241]">Total Sales: <span className="font-bold">${exporterData.totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span></p>
          </div>
          
          {/* Top 5 Retailers - Full Width */}
          <div className="mb-6">
            <h5 className="text-lg font-bold text-[#293241] mb-3 text-green-800">🥇 Top 5 Retailers</h5>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border border-gray-300">
                <thead className="bg-[#98C1D9] text-[#3D5A80]">
                  <tr>
                    <th className="border px-2 py-1 text-left">#</th>
                    <th className="border px-2 py-1 text-left">Retailer</th>
                    <th className="border px-2 py-1 text-right">Sales Amount</th>
                    <th className="border px-2 py-1 text-right">% of Exporter</th>
                    <th className="border px-2 py-1 text-right">Avg Price</th>
                  </tr>
                </thead>
                <tbody>
                  {exporterData.topRetailers.map((retailer, idx) => (
                    <tr key={retailer.retailer} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="border px-2 py-1 font-bold">{idx + 1}</td>
                      <td className="border px-2 py-1">{retailer.retailer}</td>
                      <td className="border px-2 py-1 text-right font-semibold">${retailer.totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
                      <td className="border px-2 py-1 text-right text-blue-700 font-bold">{retailer.percentage.toFixed(1)}%</td>
                      <td className="border px-2 py-1 text-right">{formatNumber(retailer.avgPrice, true)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Bottom Row: Worst 5 (Left) and Odd Retailers (Right) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Worst 5 Retailers */}
            <div>
              <h5 className="text-lg font-bold text-[#293241] mb-3 text-red-800">📉 Worst 5 Retailers</h5>
              <p className="text-xs text-gray-600 mb-2">(Sales Amount greater than $1)</p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border border-gray-300">
                  <thead className="bg-[#FEE2E2] text-[#991B1B]">
                    <tr>
                      <th className="border px-2 py-1 text-left">Retailer</th>
                      <th className="border px-2 py-1 text-right">Sales Amount</th>
                      <th className="border px-2 py-1 text-right">% of Exporter</th>
                      <th className="border px-2 py-1 text-right">Avg Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {exporterData.worstRetailers.map((retailer, idx) => (
                      <tr key={retailer.retailer} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="border px-2 py-1">{retailer.retailer}</td>
                        <td className="border px-2 py-1 text-right font-semibold">${retailer.totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
                        <td className="border px-2 py-1 text-right text-red-700 font-bold">{retailer.percentage.toFixed(1)}%</td>
                        <td className="border px-2 py-1 text-right">{formatNumber(retailer.avgPrice, true)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Odd Retailers */}
            <div>
              <h5 className="text-lg font-bold text-[#293241] mb-3 text-orange-800">🔍 Odd Retailers</h5>
              <p className="text-xs text-gray-600 mb-2">(Sales Amount ≤ $0)</p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border border-gray-300">
                  <thead className="bg-[#FEF3C7] text-[#92400E]">
                    <tr>
                      <th className="border px-2 py-1 text-left">Retailer</th>
                      <th className="border px-2 py-1 text-right">Sales Amount</th>
                      <th className="border px-2 py-1 text-right">% of Exporter</th>
                      <th className="border px-2 py-1 text-right">Avg Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {exporterData.oddRetailers.length > 0 ? (
                      exporterData.oddRetailers.map((retailer, idx) => (
                        <tr key={retailer.retailer} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="border px-2 py-1">{retailer.retailer}</td>
                          <td className="border px-2 py-1 text-right font-semibold">${retailer.totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })}</td>
                          <td className="border px-2 py-1 text-right text-orange-700 font-bold">{retailer.percentage.toFixed(1)}%</td>
                          <td className="border px-2 py-1 text-right">{formatNumber(retailer.avgPrice, true)}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="4" className="border px-2 py-3 text-center text-gray-500 italic">No odd retailers found</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Gráfico combinado de KPIs clave
const CombinedKPIChart = ({ data, exporterFilter }) => {
  const filteredData = exporterFilter === 'All' ? data : data.filter(d => d['Exporter Clean'] === exporterFilter);
  const totalSales = filteredData.reduce((sum, r) => sum + Number(r['Sales Amount'] || 0), 0);
  const totalQuantity = filteredData.reduce((sum, r) => sum + Number(r['Sale Quantity'] || 0), 0);
  const avgPrice = filteredData.length ? filteredData.map(r => Number(r['Price Four Star'] || 0)).filter(Boolean).reduce((a, b) => a + b, 0) / filteredData.filter(r => Number(r['Price Four Star'])).length : 0;

  const chartData = {
    labels: ['Total Sales', 'Total Quantity', 'Avg. Four Star Price'],
    datasets: [
      {
        label: 'Exporter Performance',
        data: [totalSales, totalQuantity, avgPrice],
        backgroundColor: ['#60a5fa', '#34d399', '#f472b6'],
        borderColor: ['#3b82f6', '#10b981', '#ec4899'],
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: (tooltipItem) => {
            const value = tooltipItem.raw;
            return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
          },
        },
      },
    },
  };

  return (
    <div className="my-8">
      <h3 className="font-bold mb-4 text-lg">📊 Combined KPI Chart</h3>
      <Bar data={chartData} options={chartOptions} />
    </div>
  );
};

const SalesDetailReport = () => {
  const [salesData, setSalesData] = useState([]);
  const [exporter, setExporter] = useState('All');
  const [retailer, setRetailer] = useState('All');
  const [variety, setVariety] = useState('All');
  const [size, setSize] = useState('All');

  // Refs para navegación - nuevo orden
  const refs = {
    'KPIs': useRef(),
    'Key Insights': useRef(),
    'Exporter Comparator': useRef(),
    'Sales by Variety': useRef(),
    'Sales Timeline': useRef(),
    'Price History Retailer': useRef(),
    'Price History Exporter': useRef(),
    'Heatmap Retailer vs Variety': useRef(),
    'Heatmap Exporter vs Retailer': useRef(),
    'Exporter-Retailer Analysis': useRef(),
    'Ranking Retailers': useRef(),
    'Ranking Exporters': useRef(),
    'Sales by Retailer/Exporter/Variety/Size': useRef(),
    'Price Alerts by Variety': useRef(),
  };

  // Carga de archivo CSV
  const handleFile = e => {
    const file = e.target.files[0];
    if (!file) return;
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: results => setSalesData(results.data),
    });
  };

  // Filtros disponibles
  const exporters = useMemo(() => ['All', ...getUnique(salesData, 'Exporter Clean')], [salesData]);
  const retailers = useMemo(() => ['All', ...getUnique(salesData, 'Retailer Name')], [salesData]);
  const varieties = useMemo(() => ['All', ...getUnique(salesData, 'Variety')], [salesData]);
  const sizes = useMemo(() => ['All', ...getUnique(salesData, 'Size')], [salesData]);

  // Filtro principal parte 1
  const filtered = useMemo(() => filterData(salesData, {
    'Exporter Clean': exporter,
    'Retailer Name': retailer,
    'Variety': variety,
    'Size': size
  }), [salesData, exporter, retailer, variety, size]);

  // Agrupación para la sección 4 (solo para la 1ra hoja)
  const grouped = useMemo(() => groupBy(filtered, ['Variety', 'Packaging Style', 'Size']), [filtered]);

  return (
    <div className="min-h-screen bg-[#F9F6F4] w-full m-0 p-0">
      <div className="p-6 space-y-16 w-full max-w-none m-0">
        <h1 className="text-4xl font-extrabold text-center mb-8 text-[#EE6C4D]">Sales Detail Report</h1>
        <div className="mb-6">
          <label className="block mb-2 font-semibold text-lg text-[#3D5A80]">Upload Sales_Detail_By_Lotid.csv</label>
          <input type="file" accept=".csv" onChange={handleFile} className="border p-2 rounded border-[#98C1D9] bg-white" />
        </div>
        
        {/* 1. Indices */}
        <SectionIndex refs={refs} />
        
        {/* 2. KPIs */}
        <div ref={refs['KPIs']}><KPICards data={salesData} /></div>
        
        {/* 3. Key Insights */}
        <div ref={refs['Key Insights']}><KeyMarketInsights data={salesData} /></div>
        
        {/* 4. Exporter-Retailer Analysis */}
        <div ref={refs['Exporter-Retailer Analysis']}><ExporterRetailerAnalysis data={salesData} /></div>
        
        {/* 5. Exporter Comparator */}
        <div ref={refs['Exporter Comparator']}><ExporterComparator data={salesData} exporters={exporters} /></div>
        
        {/* 6. Sales by Variety */}
        <div ref={refs['Sales by Variety']}>
          <section className="bg-[#F9F6F4] rounded-2xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-2 text-[#293241]">Sales by Variety</h2>
            <Bar data={getVarietyChartData(salesData)} options={chartOptions} />
          </section>
        </div>
        
        {/* 7. Sales Timeline */}
        <div ref={refs['Sales Timeline']}>
          <section className="bg-[#F9F6F4] rounded-2xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-2 text-[#293241]">Sales Timeline</h2>
            <Line data={getTimelineChartData(salesData)} options={chartOptions} />
          </section>
        </div>
        
        {/* 8. Price History (Retailer Name) */}
        <div ref={refs['Price History Retailer']}><PriceHistory data={salesData} groupKey="Retailer Name" /></div>
        
        {/* 9. Price History (Exporter Clean) */}
        <div ref={refs['Price History Exporter']}><PriceHistory data={salesData} groupKey="Exporter Clean" /></div>
        
        {/* 10. Heatmap: Retailer vs Variety (Avg Price) */}
        <div ref={refs['Heatmap Retailer vs Variety']}><Heatmap data={salesData} rowKey="Retailer Name" colKey="Variety" valueKey="Price Four Star" agg="avg" title="Heatmap: Retailer vs Variety (Avg Price)" /></div>
        
        {/* 11. Heatmap: Exporter vs Retailer (Sales Amount) */}
        <div ref={refs['Heatmap Exporter vs Retailer']}><Heatmap data={salesData} rowKey="Exporter Clean" colKey="Retailer Name" valueKey="Sales Amount" agg="sum" title="Heatmap: Exporter vs Retailer (Sales Amount)" /></div>
        
        {/* 12. Top Retailers by Sales */}
        <div ref={refs['Ranking Retailers']}><RankingBar data={salesData} groupKey="Retailer Name" valueKey="Sales Amount" title="Top Retailers by Sales" /></div>
        
        {/* 13. Top Exporters by Sales */}
        <div ref={refs['Ranking Exporters']}><RankingBar data={salesData} groupKey="Exporter Clean" valueKey="Sales Amount" title="Top Exporters by Sales" /></div>
        
        {/* 14. Sales by Retailer/Exporter/Variety/Size */}
        <div ref={refs['Sales by Retailer/Exporter/Variety/Size']}>
          <section className="bg-[#F9F6F4] rounded-2xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-2 text-[#293241]">Sales by Retailer/Exporter/Variety/Size</h2>
            <div className="flex gap-4 mb-2 flex-wrap">
              <select value={exporter} onChange={e => setExporter(e.target.value)} className="border p-1 rounded border-[#98C1D9]">
                {exporters.map(e => <option key={e}>{e}</option>)}
              </select>
              <select value={retailer} onChange={e => setRetailer(e.target.value)} className="border p-1 rounded border-[#98C1D9]">
                {retailers.map(r => <option key={r}>{r}</option>)}
              </select>
              <select value={variety} onChange={e => setVariety(e.target.value)} className="border p-1 rounded border-[#98C1D9]">
                {varieties.map(v => <option key={v}>{v}</option>)}
              </select>
              <select value={size} onChange={e => setSize(e.target.value)} className="border p-1 rounded border-[#98C1D9]">
                {sizes.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <Bar data={getChartData(filtered, 'Retailer Name', 'Sale Quantity', 'Price Four Star')} options={chartOptions} />
            <SortableTable data={filtered} />
            <div className="w-[420px] mx-auto my-4">
              <Pie data={getPieData(filtered, 'Retailer Name', 'Sales Amount')} options={{ plugins: { legend: { position: 'bottom' }, datalabels: { display: true } }, aspectRatio: 1 }} />
            </div>
          </section>
        </div>
        
        {/* 15. Price Alerts by Variety */}
        <div ref={refs['Price Alerts by Variety']}>
          <section className="bg-[#F9F6F4] rounded-2xl p-6 shadow-md">
            <h2 className="text-xl font-bold mb-2 text-[#293241]">Price Alerts by Variety</h2>
            <div className="flex gap-4 mb-2">
              <select value={variety} onChange={e => setVariety(e.target.value)} className="border p-1 rounded border-[#98C1D9]">
                {varieties.map(v => <option key={v}>{v}</option>)}
              </select>
            </div>
            <PriceAlerts data={filterData(salesData, { Variety: variety })} threshold={0.15} />
          </section>
        </div>
      </div>
    </div>
  );
};

export default SalesDetailReport;
