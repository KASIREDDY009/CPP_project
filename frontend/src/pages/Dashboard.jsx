import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../api';

function Dashboard() {
  const [stats, setStats] = useState({ total_items: 0, expiring_soon: 0, expired: 0, categories: {} });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await api.get('/dashboard');
      setStats(res.data);
    } catch (err) {
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckExpiry = async () => {
    try {
      const res = await api.post('/notifications/check');
      const { expiring, expired } = res.data;
      if (expiring.length === 0 && expired.length === 0) {
        toast.info('No items expiring soon!');
      } else {
        if (expired.length > 0) toast.warn(`Expired: ${expired.join(', ')}`);
        if (expiring.length > 0) toast.warn(`Expiring soon: ${expiring.join(', ')}`);
      }
    } catch (err) {
      toast.error('Failed to check expiry');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64"><p className="text-gray-500">Loading...</p></div>;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <div className="flex gap-3">
          <button
            onClick={handleCheckExpiry}
            className="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 text-sm"
          >
            Check Expiry Alerts
          </button>
          <Link to="/add-item" className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm">
            + Add Item
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-1">Total Items</p>
          <p className="text-3xl font-bold text-gray-800">{stats.total_items}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-yellow-200 p-6">
          <p className="text-sm text-yellow-600 mb-1">Expiring Soon</p>
          <p className="text-3xl font-bold text-yellow-600">{stats.expiring_soon}</p>
          <p className="text-xs text-gray-400 mt-1">Within 3 days</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-red-200 p-6">
          <p className="text-sm text-red-500 mb-1">Expired</p>
          <p className="text-3xl font-bold text-red-500">{stats.expired}</p>
        </div>
      </div>

      {/* Categories */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Items by Category</h2>
        {Object.keys(stats.categories).length === 0 ? (
          <p className="text-gray-400">No items yet. <Link to="/add-item" className="text-green-600 hover:underline">Add your first item!</Link></p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.categories).map(([cat, count]) => (
              <div key={cat} className="bg-gray-50 rounded-md p-3 text-center">
                <p className="text-sm text-gray-500">{cat}</p>
                <p className="text-xl font-semibold text-gray-700">{count}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
