import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setActivePanel } from '../redux/slices/appSlice';

const Sidebar = () => {
  const dispatch = useDispatch();
  const activePanel = useSelector((state) => state.app.activePanel);

  const menuItems = [
    { id: 'chat', icon: '💬', label: 'Chat' },
    { id: 'memory', icon: '🧠', label: 'Memory' },
    { id: 'context', icon: '🔄', label: 'Context' },
    { id: 'update', icon: '⬆️', label: 'Updates' },
    { id: 'security', icon: '🔒', label: 'Security' },
    { id: 'logs', icon: '📋', label: 'Logs' },
    { id: 'settings', icon: '⚙️', label: 'Settings' },
  ];

  const handlePanelChange = (panelId) => {
    dispatch(setActivePanel(panelId));
  };

  return (
    <aside className="jarvis-sidebar w-64 bg-opacity-80 backdrop-blur-md border-r border-opacity-20 border-white flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-opacity-20 border-white">
        <div className="text-2xl font-bold text-center">JARVIS</div>
        <div className="text-sm text-center opacity-70">AI Assistant</div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-2 px-2">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => handlePanelChange(item.id)}
                className={`w-full flex items-center px-4 py-3 rounded-lg transition-all duration-300 ${
                  activePanel === item.id
                    ? 'bg-primary bg-opacity-20 text-primary'
                    : 'hover:bg-white hover:bg-opacity-10'
                }`}
              >
                <span className="text-xl mr-3">{item.icon}</span>
                <span>{item.label}</span>
                {item.id === 'update' && (
                  <span className="ml-auto bg-primary text-xs px-2 py-1 rounded-full">1</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Quick Controls */}
      <div className="p-4 border-t border-opacity-20 border-white">
        <button className="jarvis-button w-full mb-2 flex items-center justify-center">
          <span className="mr-2">🎤</span> Voice Mode
        </button>
        <button className="jarvis-button w-full bg-opacity-50 flex items-center justify-center">
          <span className="mr-2">🔄</span> Restart Jarvis
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;