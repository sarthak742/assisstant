import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setTheme } from '../redux/slices/appSlice';

const TopBar = () => {
  const dispatch = useDispatch();
  const { connectionStatus, theme } = useSelector((state) => state.app);
  const { currentVersion } = useSelector((state) => state.update);

  const handleThemeChange = (newTheme) => {
    dispatch(setTheme(newTheme));
  };

  // Connection status indicator
  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'bg-green-500';
      case 'connecting':
        return 'bg-yellow-500 animate-pulse';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="jarvis-topbar bg-opacity-80 backdrop-blur-md border-b border-opacity-20 border-white px-4 py-2 flex items-center justify-between">
      {/* Logo and Title */}
      <div className="flex items-center">
        <div className="text-2xl font-bold text-primary mr-2">JARVIS</div>
        <div className="text-sm opacity-70">AI Assistant</div>
      </div>

      {/* Center - Version Info */}
      <div className="flex items-center">
        <div className="text-sm opacity-70 mr-2">Version:</div>
        <div className="text-sm">{currentVersion || 'Loading...'}</div>
      </div>

      {/* Right - Connection Status and Theme Toggle */}
      <div className="flex items-center space-x-4">
        {/* Connection Status */}
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${getConnectionStatusColor()}`}></div>
          <span className="text-sm">{connectionStatus}</span>
        </div>

        {/* Theme Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleThemeChange('blue')}
            className={`w-6 h-6 rounded-full bg-blue-500 ${theme === 'blue' ? 'ring-2 ring-white' : ''}`}
            aria-label="Blue theme"
          ></button>
          <button
            onClick={() => handleThemeChange('teal')}
            className={`w-6 h-6 rounded-full bg-teal-500 ${theme === 'teal' ? 'ring-2 ring-white' : ''}`}
            aria-label="Teal theme"
          ></button>
          <button
            onClick={() => handleThemeChange('violet')}
            className={`w-6 h-6 rounded-full bg-violet-500 ${theme === 'violet' ? 'ring-2 ring-white' : ''}`}
            aria-label="Violet theme"
          ></button>
        </div>
      </div>
    </div>
  );
};

export default TopBar;