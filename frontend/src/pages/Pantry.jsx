import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../api';

function Pantry() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState('');
  const [filterCategory, setFilterCategory] = useState('All');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const res = await api.get('/items');
      setItems(res.data.items || []);
    } catch (err) {
      toast.error('Failed to load items');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    try {
      await api.delete(`/items/${id}`);
      toast.success('Item deleted');
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      toast.error('Failed to delete item');
    }
  };

  const getExpiryStatus = (expiryDate) => {
    if (!expiryDate) return 'none';
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const exp = new Date(expiryDate);
    const diff = (exp - today) / (1000 * 60 * 60 * 24);
    if (diff < 0) return 'expired';
    if (diff <= 3) return 'expiring';
    return 'fresh';
  };

  const statusColors = {
    expired: 'bg-red-50 border-red-200',
    expiring: 'bg-yellow-50 border-yellow-200',
    fresh: 'bg-white border-gray-200',
    none: 'bg-white border-gray-200',
  };

  const statusBadge = {
    expired: <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">Expired</span>,
    expiring: <span className="text-xs bg-yellow-100 text-yellow-600 px-2 py-0.5 rounded-full">Expiring Soon</span>,
    fresh: null,
    none: null,
  };

  const categories = ['All', ...new Set(items.map((i) => i.category))];

  const filtered = items.filter((item) => {
    const matchSearch = item.name.toLowerCase().includes(search.toLowerCase());
    const matchCategory = filterCategory === 'All' || item.category === filterCategory;
    return matchSearch && matchCategory;
  });

  if (loading) {
    return <div className="flex justify-center items-center h-64"><p className="text-gray-500">Loading...</p></div>;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">My Pantry</h1>
        <Link to="/add-item" className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm">
          + Add Item
        </Link>
      </div>

      {/* Search & Filter */}
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          placeholder="Search items..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {/* Items */}
      {filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          {items.length === 0 ? (
            <p>Your pantry is empty. <Link to="/add-item" className="text-green-600 hover:underline">Add your first item!</Link></p>
          ) : (
            <p>No items match your search.</p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => {
            const status = getExpiryStatus(item.expiry_date);
            return (
              <div key={item.id} className={`rounded-lg shadow-sm border p-4 ${statusColors[status]}`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-800">{item.name}</h3>
                    <p className="text-sm text-gray-500">{item.category}</p>
                  </div>
                  {statusBadge[status]}
                </div>
                {item.image_url && (
                  <img src={item.image_url} alt={item.name} className="w-full h-32 object-cover rounded-md mb-2" />
                )}
                <div className="flex justify-between items-center text-sm text-gray-600 mb-3">
                  <span>{item.quantity} {item.unit}</span>
                  {item.expiry_date && <span>Expires: {item.expiry_date}</span>}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => navigate(`/edit-item/${item.id}`)}
                    className="flex-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(item.id, item.name)}
                    className="flex-1 px-3 py-1.5 text-sm bg-red-50 text-red-600 rounded-md hover:bg-red-100"
                  >
                    Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Pantry;
