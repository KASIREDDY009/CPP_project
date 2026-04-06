import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import api from '../api';

function EditItem() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    category: 'Other',
    quantity: 1,
    unit: 'pcs',
    expiry_date: '',
    image_url: '',
  });
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  const categories = ['Fruit', 'Vegetable', 'Dairy', 'Meat', 'Bakery', 'Beverage', 'Snack', 'Grain', 'Other'];
  const units = ['pcs', 'kg', 'g', 'L', 'ml', 'dozen', 'pack', 'bottle', 'can', 'box'];

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const res = await api.get('/items');
        const item = (res.data.items || []).find((i) => i.id === id);
        if (item) {
          setForm({
            name: item.name || '',
            category: item.category || 'Other',
            quantity: item.quantity || 1,
            unit: item.unit || 'pcs',
            expiry_date: item.expiry_date || '',
            image_url: item.image_url || '',
          });
        } else {
          toast.error('Item not found');
          navigate('/pantry');
        }
      } catch (err) {
        toast.error('Failed to load item');
      } finally {
        setFetching(false);
      }
    };
    fetchItem();
  }, [id, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      toast.error('Item name is required');
      return;
    }
    setLoading(true);
    try {
      await api.put(`/items/${id}`, form);
      toast.success('Item updated!');
      navigate('/pantry');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update item');
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return <div className="flex justify-center items-center h-64"><p className="text-gray-500">Loading...</p></div>;
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Edit Item</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
        {form.image_url && (
          <img src={form.image_url} alt={form.name} className="w-32 h-32 object-cover rounded-md" />
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Item Name *</label>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
          <select
            name="category"
            value={form.category}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
            <input
              type="number"
              name="quantity"
              value={form.quantity}
              onChange={handleChange}
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
            <select
              name="unit"
              value={form.unit}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              {units.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
          <input
            type="date"
            name="expiry_date"
            value={form.expiry_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'Updating...' : 'Update Item'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/pantry')}
            className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default EditItem;
