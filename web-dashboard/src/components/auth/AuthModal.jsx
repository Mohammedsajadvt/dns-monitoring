import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  ShieldAlert,
  Lock,
  Mail,
  User,
  Eye,
  EyeOff,
  AlertCircle,
} from 'lucide-react';
import {
  loginUser,
  registerUser,
  clearAuthError,
} from '../../store/slices/authSlice';
import { addToast } from '../../store/slices/uiSlice';

export default function AuthModal({ isOpen, onClose, isRequired = false }) {
  const dispatch = useDispatch();
  const { isLoading, error } = useSelector((state) => state.auth);

  const [tab, setTab] = useState('login'); // 'login' | 'register'
  const [showPassword, setShowPassword] = useState(false);

  // Login Form
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register Form
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirm, setRegConfirm] = useState('');
  const [localError, setLocalError] = useState('');

  if (!isOpen && !isRequired) return null;

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    dispatch(clearAuthError());

    try {
      await dispatch(
        loginUser({ email: loginEmail, password: loginPassword })
      ).unwrap();
      dispatch(
        addToast({
          message: 'Welcome back! Signed in successfully.',
          type: 'success',
        })
      );
      if (onClose) onClose();
    } catch (err) {
      // Error handled by redux
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');
    dispatch(clearAuthError());

    if (regPassword !== regConfirm) {
      setLocalError('Passwords do not match');
      return;
    }
    if (regPassword.length < 6) {
      setLocalError('Password must be at least 6 characters');
      return;
    }

    try {
      await dispatch(
        registerUser({
          fullName: regName,
          email: regEmail,
          password: regPassword,
        })
      ).unwrap();
      dispatch(
        addToast({
          message: 'Admin account created successfully!',
          type: 'success',
        })
      );
      if (onClose) onClose();
    } catch (err) {
      // Error handled by redux
    }
  };

  const displayError = localError || error;

  return (
    <div className={`modal-overlay active`}>
      <div
        className="modal-content"
        style={{
          width: '460px',
          padding: '30px',
          background: 'var(--bg-secondary)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(6, 182, 212, 0.1)',
        }}
      >
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '16px' }}>
          <div
            style={{
              width: '54px',
              height: '54px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 8px 24px rgba(6, 182, 212, 0.35)',
              color: '#fff',
              marginBottom: '10px',
            }}
          >
            <ShieldAlert size={28} />
          </div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, letterSpacing: '-0.5px' }}>
            NetSentry Authentication
          </h2>
          <span
            style={{
              fontSize: '0.7rem',
              fontWeight: 700,
              letterSpacing: '1.2px',
              color: 'var(--accent-cyan)',
            }}
          >
            DNS CYBER INTELLIGENCE ACCESS
          </span>
        </div>

        {/* Tab switcher */}
        <div
          style={{
            display: 'flex',
            background: 'var(--bg-surface)',
            borderRadius: '10px',
            padding: '4px',
            gap: '4px',
            marginBottom: '16px',
          }}
        >
          <button
            type="button"
            onClick={() => {
              setTab('login');
              setLocalError('');
              dispatch(clearAuthError());
            }}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: '8px',
              border: 'none',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: tab === 'login' ? 'var(--accent-cyan)' : 'transparent',
              color: tab === 'login' ? '#000' : 'var(--text-secondary)',
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setTab('register');
              setLocalError('');
              dispatch(clearAuthError());
            }}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: '8px',
              border: 'none',
              fontWeight: 700,
              fontSize: '0.82rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: tab === 'register' ? 'var(--accent-purple)' : 'transparent',
              color: tab === 'register' ? '#fff' : 'var(--text-secondary)',
            }}
          >
            Create Account
          </button>
        </div>

        {/* Error notification */}
        {displayError && (
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              borderRadius: '8px',
              padding: '10px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              color: '#fca5a5',
              fontSize: '0.82rem',
              marginBottom: '14px',
            }}
          >
            <AlertCircle size={16} color="#ef4444" style={{ flexShrink: 0 }} />
            <span>{displayError}</span>
          </div>
        )}

        {/* Login Tab */}
        {tab === 'login' ? (
          <form onSubmit={handleLoginSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div className="form-group">
              <label>Email Address</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="email"
                  placeholder="admin@domain.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                  style={{ paddingLeft: '38px', width: '100%' }}
                />
                <Mail
                  size={16}
                  color="var(--accent-cyan)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  style={{ paddingLeft: '38px', paddingRight: '38px', width: '100%' }}
                />
                <Lock
                  size={16}
                  color="var(--accent-cyan)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: 'var(--text-muted)',
                  }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{ height: '44px', marginTop: '6px' }}
            >
              {isLoading ? 'Authenticating...' : 'Sign In Securely'}
            </button>
          </form>
        ) : (
          /* Register Tab */
          <form onSubmit={handleRegisterSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div className="form-group">
              <label>Full Name</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  placeholder="e.g. Sajad Admin"
                  value={regName}
                  onChange={(e) => setRegName(e.target.value)}
                  required
                  style={{ paddingLeft: '38px', width: '100%' }}
                />
                <User
                  size={16}
                  color="var(--accent-purple)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Email Address</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="email"
                  placeholder="admin@domain.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  required
                  style={{ paddingLeft: '38px', width: '100%' }}
                />
                <Mail
                  size={16}
                  color="var(--accent-purple)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Create strong password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  required
                  style={{ paddingLeft: '38px', width: '100%' }}
                />
                <Lock
                  size={16}
                  color="var(--accent-purple)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Confirm password"
                  value={regConfirm}
                  onChange={(e) => setRegConfirm(e.target.value)}
                  required
                  style={{ paddingLeft: '38px', width: '100%' }}
                />
                <Lock
                  size={16}
                  color="var(--accent-purple)"
                  style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary"
              style={{
                height: '44px',
                background: 'var(--accent-purple)',
                color: '#fff',
                marginTop: '6px',
              }}
            >
              {isLoading ? 'Creating Account...' : 'Create Admin Account'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
