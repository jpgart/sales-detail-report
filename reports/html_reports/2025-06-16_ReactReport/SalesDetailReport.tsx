// Versión TypeScript de SalesDetailReport, adaptada desde SalesDetailReport.jsx
// Mantiene toda la lógica, formato y avances visuales/funcionales
// Para usar en proyectos Vite + React + TypeScript

import React, { useState, useMemo, useRef } from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import 'chart.js/auto';
import Papa from 'papaparse';
import { Chart as ChartJS } from 'chart.js/auto';

// Tipos de datos
export interface SalesRow {
  [key: string]: string | number | undefined | null;
  'Exporter Clean'?: string;
  'Retailer Name'?: string;
  'Variety'?: string;
  'Size'?: string;
  'Sale Quantity'?: number | string;
  'Sales Amount'?: number | string;
  'Price Four Star'?: number | string;
  'Sale Date'?: string;
  'Packaging Style'?: string;
}

// Utilidades para filtrar y agrupar datos
const getUnique = (data: SalesRow[], key: string): string[] => [...new Set(data.map(item => String(item[key] ?? '')))].filter(Boolean);

const filterData = (data: SalesRow[], filters: Record<string, string>): SalesRow[] => {
  return data.filter(row => {
    return Object.entries(filters).every(([key, value]) =>
      value === 'All' || row[key] === value
    );
  });
};

const groupBy = (data: SalesRow[], keys: string[]): Record<string, SalesRow[]> => {
  return data.reduce((acc: Record<string, SalesRow[]>, row) => {
    const groupKey = keys.map(k => row[k]).join('-');
    if (!acc[groupKey]) acc[groupKey] = [];
    acc[groupKey].push(row);
    return acc;
  }, {});
};

// Formateo de números
const formatNumber = (num: any, isMoney = false): string => {
  if (num === undefined || num === null || isNaN(Number(num))) return '';
  const n = Number(num);
  return isMoney ? `$${n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : n.toLocaleString('en-US');
};

// KPICards: tarjetas de KPIs grandes, centradas y filtrables por Exporter
type KPICardsProps = { data: SalesRow[] };
const KPICards = ({ data }: KPICardsProps) => {
  const [selectedExporter, setSelectedExporter] = useState('All');
  const exporters = ['All', ...Array.from(new Set(data.map(r => r['Exporter Clean'])).values()).filter(Boolean) as string[]];
  const filtered = selectedExporter === 'All' ? data : data.filter(r => r['Exporter Clean'] === selectedExporter);
  // Paleta actualizada según Style-Report.md (ProducePay v2.0)
  const kpis = [
    { label: 'Total Sales', value: `$${totalSales.toLocaleString('en-US', { maximumFractionDigits: 0 })}`, color: 'bg-[#3D5A80] text-white' },
    { label: 'Total Quantity', value: formatNumber(totalQty), color: 'bg-[#98C1D9] text-[#293241]' },
    { label: 'Avg. Four Star Price', value: formatNumber(avgPrice, true), color: 'bg-[#E0FBFC] text-[#293241]' },
    { label: 'Retailers', value: uniqueRetailers, color: 'bg-[#EE6C4D] text-white' },
    { label: 'Exporters', value: uniqueExporters, color: 'bg-[#293241] text-white' },
    { label: 'Varieties', value: uniqueVarieties, color: 'bg-[#98C1D9] text-[#293241]' },
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
type PieData = {
  labels: string[];
  datasets: Array<{
    data: number[];
    backgroundColor: string[];
    datalabels?: any;
  }>;
};
const getPieData = (data: SalesRow[], labelKey: string, valueKey: string): PieData => {
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
        datalabels: {
          display: true,
          color: '#222',
          font: { weight: 'bold', size: 16 },
          formatter: (value: number, ctx: any) => {
            const percent = total ? (value / total * 100) : 0;
            return percent > 2 ? percent.toFixed(1) + '%' : '';
          },
        },
      },
    ],
  };
};

// Opciones de gráfico globales
type ChartOptions = {
  responsive: boolean;
  interaction: { mode: string; intersect: boolean };
  plugins: { legend: { position: string } };
  scales: any;
};
const chartOptions: ChartOptions = {
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

// Componente principal adaptado a TypeScript
const SalesDetailReport = () => {
  const [salesData, setSalesData] = useState<SalesRow[]>([]);
  const [exporter, setExporter] = useState('All');
  const [retailer, setRetailer] = useState('All');
  const [variety, setVariety] = useState('All');
  const [size, setSize] = useState('All');

  // Refs para navegación
  const refs: Record<string, React.RefObject<HTMLDivElement>> = {
    'KPIs': useRef<HTMLDivElement>(null),
    'Heatmap Retailer vs Variety': useRef<HTMLDivElement>(null),
    'Heatmap Exporter vs Retailer': useRef<HTMLDivElement>(null),
    'Ranking Retailers': useRef<HTMLDivElement>(null),
    'Ranking Exporters': useRef<HTMLDivElement>(null),
    'Exporter Comparator': useRef<HTMLDivElement>(null),
    'Price History Retailer': useRef<HTMLDivElement>(null),
    'Price History Exporter': useRef<HTMLDivElement>(null),
    'Parte 1: Filtros y Gráficos': useRef<HTMLDivElement>(null),
    'Parte 2: Sales by Variety': useRef<HTMLDivElement>(null),
    'Parte 3: Sales Timeline': useRef<HTMLDivElement>(null),
    'Parte 4: Price Alerts': useRef<HTMLDivElement>(null),
  };

  // Carga de archivo CSV
  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: results => setSalesData(results.data as SalesRow[]),
    });
  };

  // ...existing code...
};

export default SalesDetailReport;
