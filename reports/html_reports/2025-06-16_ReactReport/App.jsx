import React from 'react';
import SalesDetailReport from './SalesDetailReport';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="flex items-center bg-[#98C1D9] p-4">
        <img src="logo.png" alt="Logo" className="h-10 w-auto" />
      </header>
      <main className="max-w-6xl mx-auto py-8">
        <SalesDetailReport />
      </main>
    </div>
  );
}

export default App;
