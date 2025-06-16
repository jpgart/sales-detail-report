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
  // Paleta personalizada
  const kpis = [
    { label: 'Total Sales', value: `$${totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })}`, color: 'bg-[#3d5a80] text-white' },
    { label: 'Total Quantity', value: formatNumber(totalQty), color: 'bg-[#98c1d9] text-[#293241]' },
    { label: 'Avg. Four Star Price', value: formatNumber(avgPrice, true), color: 'bg-[#e0fbfc] text-[#293241]' },
    { label: 'Retailers', value: uniqueRetailers, color: 'bg-[#ee6c4d] text-white' },
    { label: 'Exporters', value: uniqueExporters, color: 'bg-[#293241] text-white' },
    { label: 'Varieties', value: uniqueVarieties, color: 'bg-[#98c1d9] text-[#293241]' },
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

// Índice de navegación mejorado con paleta
const navColors = ["bg-[#3d5a80] text-white","bg-[#98c1d9] text-[#293241]","bg-[#e0fbfc] text-[#293241]","bg-[#ee6c4d] text-white","bg-[#293241] text-white"];
const SectionIndex = ({ refs }) => (
  <nav className="my-8 flex flex-wrap gap-4 text-lg font-bold justify-center">
    {Object.entries(refs).map(([k, ref], i) => (
      <button
        key={k}
        onClick={() => ref.current.scrollIntoView({ behavior: 'smooth' })}
        className={`px-4 py-2 rounded transition ${navColors[i % navColors.length]}`}
      >
        {k.replace('KPIs', 'Scorecards')
          .replace('Heatmap Retailer vs Variety', 'Heatmap: Retailer vs Variety')
          .replace('Heatmap Exporter vs Retailer', 'Pivot Table: Exporter vs Retailer')
          .replace('Ranking Retailers', 'Top Retailers by Sales')
          .replace('Ranking Exporters', 'Top Exporters by Sales')
          .replace('Exporter Comparator', 'Exporter Comparator')
          .replace('Price History Retailer', 'Price History (Retailer)')
          .replace('Price History Exporter', 'Price History (Exporter)')
          .replace('Parte 1: Filtros y Gráficos', 'Part 1: Filters and Main Charts')
          .replace('Parte 2: Sales by Variety', 'Part 2: Sales by Variety')
          .replace('Parte 3: Sales Timeline', 'Part 3: Sales Timeline')
          .replace('Parte 4: Price Alerts', 'Part 4: Price Alerts')}
      </button>
    ))}
  </nav>
);

const SalesDetailReport = () => {
  const [salesData, setSalesData] = useState([]);
  const [exporter, setExporter] = useState('All');
  const [retailer, setRetailer] = useState('All');
  const [variety, setVariety] = useState('All');
  const [size, setSize] = useState('All');

  // Refs para navegación
  const refs = {
    'KPIs': useRef(),
    'Heatmap Retailer vs Variety': useRef(),
    'Heatmap Exporter vs Retailer': useRef(),
    'Ranking Retailers': useRef(),
    'Ranking Exporters': useRef(),
    'Exporter Comparator': useRef(),
    'Price History Retailer': useRef(),
    'Price History Exporter': useRef(),
    'Parte 1: Filtros y Gráficos': useRef(),
    'Parte 2: Sales by Variety': useRef(),
    'Parte 3: Sales Timeline': useRef(),
    'Parte 4: Price Alerts': useRef(),
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
    <div className="p-4 space-y-16">
      <h1 className="text-4xl font-extrabold text-center mb-8" style={{ color: '#EE6C4D' }}>Sales Detail Report</h1>
      <div className="mb-6">
        <label className="block mb-2 font-semibold text-lg">Upload Sales_Detail_By_Lotid.csv</label>
        <input type="file" accept=".csv" onChange={handleFile} className="border p-2 rounded" />
      </div>
      <SectionIndex refs={refs} />
      <div ref={refs['KPIs']}><KPICards data={salesData} /></div>
      <div ref={refs['Heatmap Retailer vs Variety']}><Heatmap data={salesData} rowKey="Retailer Name" colKey="Variety" valueKey="Price Four Star" agg="avg" title="Heatmap: Retailer vs Variety (Avg Price)" /></div>
      <div ref={refs['Heatmap Exporter vs Retailer']}><Heatmap data={salesData} rowKey="Exporter Clean" colKey="Retailer Name" valueKey="Sales Amount" agg="sum" title="Heatmap: Exporter vs Retailer (Sales Amount)" /></div>
      <div ref={refs['Ranking Retailers']}><RankingBar data={salesData} groupKey="Retailer Name" valueKey="Sales Amount" title="Top Retailers by Sales" /></div>
      <div ref={refs['Ranking Exporters']}><RankingBar data={salesData} groupKey="Exporter Clean" valueKey="Sales Amount" title="Top Exporters by Sales" /></div>
      <div ref={refs['Exporter Comparator']}><ExporterComparator data={salesData} exporters={exporters} /></div>
      <div ref={refs['Price History Retailer']}><PriceHistory data={salesData} groupKey="Retailer Name" /></div>
      <div ref={refs['Price History Exporter']}><PriceHistory data={salesData} groupKey="Exporter Clean" /></div>
      <div ref={refs['Parte 1: Filtros y Gráficos']}>
        {/* Parte 1: Filtros Exporter, Retailer, Variety, Size + gráfico, tabla y pie */}
        <section>
          <h2 className="text-xl font-bold mb-2">Sales by Retailer/Exporter/Variety/Size</h2>
          <div className="flex gap-4 mb-2 flex-wrap">
            <select value={exporter} onChange={e => setExporter(e.target.value)} className="border p-1 rounded">
              {exporters.map(e => <option key={e}>{e}</option>)}
            </select>
            <select value={retailer} onChange={e => setRetailer(e.target.value)} className="border p-1 rounded">
              {retailers.map(r => <option key={r}>{r}</option>)}
            </select>
            <select value={variety} onChange={e => setVariety(e.target.value)} className="border p-1 rounded">
              {varieties.map(v => <option key={v}>{v}</option>)}
            </select>
            <select value={size} onChange={e => setSize(e.target.value)} className="border p-1 rounded">
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
      <div ref={refs['Parte 2: Sales by Variety']}>
        {/* Parte 2: Sales by Variety */}
        <section>
          <h2 className="text-xl font-bold mb-2">Sales by Variety</h2>
          <Bar data={getVarietyChartData(salesData)} options={chartOptions} />
        </section>
      </div>
      <div ref={refs['Parte 3: Sales Timeline']}>
        {/* Parte 3: Sales Timeline */}
        <section>
          <h2 className="text-xl font-bold mb-2">Sales Timeline</h2>
          <Line data={getTimelineChartData(salesData)} options={chartOptions} />
        </section>
      </div>
      <div ref={refs['Parte 4: Price Alerts']}>
        {/* Parte 4: Price Alerts con filtro Variety */}
        <section>
          <h2 className="text-xl font-bold mb-2">Price Alerts by Variety</h2>
          <div className="flex gap-4 mb-2">
            <select value={variety} onChange={e => setVariety(e.target.value)} className="border p-1 rounded">
              {varieties.map(v => <option key={v}>{v}</option>)}
            </select>
          </div>
          <PriceAlerts data={filterData(salesData, { Variety: variety })} threshold={0.15} />
        </section>
      </div>
    </div>
  );
};

export default SalesDetailReport;
