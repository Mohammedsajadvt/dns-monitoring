import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { X } from 'lucide-react';
import { closeEditModal, updateDevice } from '../../store/slices/devicesSlice';
import { addToast } from '../../store/slices/uiSlice';

export default function EditDeviceModal() {
  const dispatch = useDispatch();
  const { isModalOpen, selectedDevice } = useSelector((state) => state.devices);
  const [friendlyName, setFriendlyName] = useState('');
  const [deviceType, setDeviceType] = useState('unknown');

  useEffect(() => {
    if (selectedDevice) {
      setFriendlyName(selectedDevice.friendly_name || selectedDevice.hostname || '');
      setDeviceType(selectedDevice.device_type || 'unknown');
    }
  }, [selectedDevice]);

  if (!isModalOpen || !selectedDevice) return null;

  const handleSave = async () => {
    try {
      await dispatch(
        updateDevice({
          networkId: selectedDevice.network_id,
          ip: selectedDevice.ip,
          friendlyName,
          deviceType,
        })
      ).unwrap();

      dispatch(
        addToast({
          message: 'Device details updated successfully',
          type: 'success',
        })
      );
    } catch (e) {
      dispatch(
        addToast({
          message: 'Failed to update device: ' + e,
          type: 'threat',
        })
      );
    }
  };

  return (
    <div className={`modal-overlay ${isModalOpen ? 'active' : ''}`}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Edit Device Alias & Type</h3>
          <button
            onClick={() => dispatch(closeEditModal())}
            className="btn-icon"
          >
            <X size={20} />
          </button>
        </div>

        <div className="form-group">
          <label>IP Address</label>
          <input
            type="text"
            className="mono"
            value={selectedDevice.ip}
            disabled
            style={{ opacity: 0.7 }}
          />
        </div>

        <div className="form-group">
          <label>MAC Address</label>
          <input
            type="text"
            className="mono"
            value={selectedDevice.mac}
            disabled
            style={{ opacity: 0.7 }}
          />
        </div>

        <div className="form-group">
          <label>Friendly Name / Owner Alias</label>
          <input
            type="text"
            placeholder="e.g. Sajad's iPhone 15 Pro"
            value={friendlyName}
            onChange={(e) => setFriendlyName(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Device Category</label>
          <select
            value={deviceType}
            onChange={(e) => setDeviceType(e.target.value)}
          >
            <option value="phone">Phone / Mobile</option>
            <option value="laptop">Laptop / Workstation</option>
            <option value="smart_tv">Smart TV / Streaming</option>
            <option value="iot">Smart Home IoT</option>
            <option value="router">Router / Gateway</option>
            <option value="unknown">Unknown Device</option>
          </select>
        </div>

        <div className="modal-actions">
          <button
            onClick={() => dispatch(closeEditModal())}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button onClick={handleSave} className="btn-primary">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
