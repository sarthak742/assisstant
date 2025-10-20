import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchContext, fetchRecentInteractions, clearMemory } from '../redux/slices/memorySlice';
import { checkForUpdates } from '../redux/slices/updateSlice';

const StatusPanel = () => {
  const dispatch = useDispatch();
  const activePanel = useSelector((state) => state.app.activePanel);
  const context = useSelector((state) => state.memory.context);
  const { currentVersion, latestVersion, updateAvailable, updateStatus } = useSelector((state) => state.update);
  const { securityLevel, privacySettings } = useSelector((state) => state.security);
  const logs = useSelector((state) => state.app.notifications);
  const { interactions, isLoading: memoryLoading, error: memoryError } = useSelector((state) => state.memory);

  // Fetch context data on mount
  useEffect(() => {
    dispatch(fetchContext());
  }, [dispatch]);

  const renderContextPanel = () => (
    <div className="animate-fade-in">
      <h3 className="text-lg font-medium mb-3">Active Context</h3>
      <div className="space-y-3">
        {Object.keys(context).length > 0 ? (
          Object.entries(context).map(([key, value]) => (
            <div key={key} className="bg-opacity-20 bg-white rounded-md p-3">
              <div className="text-sm font-medium text-primary mb-1">{key}</div>
              <div className="text-sm opacity-80">{typeof value === 'object' ? JSON.stringify(value) : value}</div>
            </div>
          ))
        ) : (
          <div className="text-center opacity-60 py-4">No active context data</div>
        )}
      </div>
    </div>
  );

  const renderUpdatePanel = () => (
    <div className="animate-fade-in">
      <h3 className="text-lg font-medium mb-3">System Updates</h3>
      
      <div className="bg-opacity-20 bg-white rounded-md p-3 mb-3">
        <div className="flex justify-between items-center mb-2">
          <div className="text-sm">Current Version</div>
          <div className="font-medium">{currentVersion || 'Unknown'}</div>
        </div>
        <div className="flex justify-between items-center">
          <div className="text-sm">Latest Version</div>
          <div className="font-medium">{latestVersion || 'Unknown'}</div>
        </div>
      </div>
      
      <div className="mb-4">
        {updateAvailable ? (
          <div className="bg-green-500 bg-opacity-20 text-green-400 rounded-md p-3 text-center">
            Update available! 
          </div>
        ) : (
          <div className="bg-opacity-20 bg-white rounded-md p-3 text-center opacity-60">
            System is up to date
          </div>
        )}
      </div>
      
      <button 
        className="jarvis-button w-full mb-2"
        onClick={() => dispatch(checkForUpdates())}
        disabled={updateStatus === 'checking'}
      >
        {updateStatus === 'checking' ? 'Checking...' : 'Check for Updates'}
      </button>
      
      {updateAvailable && (
        <button className="jarvis-button w-full bg-green-500">
          Install Update
        </button>
      )}
    </div>
  );

  const renderSecurityPanel = () => (
    <div className="animate-fade-in">
      <h3 className="text-lg font-medium mb-3">Security & Permissions</h3>
      
      <div className="bg-opacity-20 bg-white rounded-md p-3 mb-3">
        <div className="flex justify-between items-center mb-1">
          <div className="text-sm">Security Level</div>
          <div className="font-medium capitalize">{securityLevel}</div>
        </div>
        <div className="w-full bg-opacity-20 bg-white rounded-full h-1.5 mt-1">
          <div 
            className="bg-primary h-1.5 rounded-full" 
            style={{ 
              width: securityLevel === 'high' ? '100%' : securityLevel === 'standard' ? '66%' : '33%' 
            }}
          ></div>
        </div>
      </div>
      
      <div className="space-y-2 mb-4">
        <div className="text-sm font-medium mb-1">Privacy Settings</div>
        <div className="flex justify-between items-center text-sm">
          <div>Data Retention</div>
          <div>{privacySettings.dataRetention} days</div>
        </div>
        <div className="flex justify-between items-center text-sm">
          <div>Voice Data Storage</div>
          <div>{privacySettings.voiceDataStorage ? 'Enabled' : 'Disabled'}</div>
        </div>
        <div className="flex justify-between items-center text-sm">
          <div>Location Tracking</div>
          <div>{privacySettings.locationTracking ? 'Enabled' : 'Disabled'}</div>
        </div>
      </div>
      
      <button className="jarvis-button w-full">
        Manage Security Settings
      </button>
    </div>
  );

  const renderLogsPanel = () => (
    <div className="animate-fade-in">
      <h3 className="text-lg font-medium mb-3">System Logs</h3>
      
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {logs.length > 0 ? (
          logs.map((log) => (
            <div 
              key={log.id} 
              className={`p-2 rounded-md text-sm ${
                log.type === 'error' 
                  ? 'bg-red-500 bg-opacity-20 text-red-400' 
                  : log.type === 'warning'
                    ? 'bg-yellow-500 bg-opacity-20 text-yellow-400'
                    : 'bg-opacity-20 bg-white'
              }`}
            >
              <div className="flex justify-between items-center">
                <div className="font-medium">{log.type}</div>
                <div className="text-xs opacity-70">
                  {new Date(log.id).toLocaleTimeString()}
                </div>
              </div>
              <div className="mt-1">{log.message}</div>
            </div>
          ))
        ) : (
          <div className="text-center opacity-60 py-4">No logs to display</div>
        )}
      </div>
    </div>
  );

  const renderMemoryPanel = () => (
    <div className="animate-fade-in">
      <h3 className="text-lg font-medium mb-3">Recent Memory</h3>
      <div className="flex space-x-2 mb-3">
        <button
          className="jarvis-button"
          onClick={() => dispatch(fetchRecentInteractions(15))}
          disabled={memoryLoading}
        >
          {memoryLoading ? 'Loading...' : 'Refresh'}
        </button>
        <button
          className="jarvis-button bg-red-500"
          onClick={() => dispatch(clearMemory())}
        >
          Clear Memory
        </button>
      </div>
      {memoryError && (
        <div className="bg-red-500 bg-opacity-20 text-red-400 rounded-md p-2 mb-3 text-sm">
          {memoryError}
        </div>
      )}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {interactions && interactions.length > 0 ? (
          interactions.map((it, idx) => (
            <div key={it.id || idx} className={`p-3 rounded-md ${it.role === 'user' ? 'bg-primary bg-opacity-20' : 'bg-opacity-20 bg-white'}`}>
              <div className="text-sm opacity-80">{it.role || it.sender}</div>
              <div className="mt-1 text-sm">{it.content || it.text}</div>
              <div className="text-xs opacity-60 mt-1">
                {it.timestamp ? new Date(it.timestamp).toLocaleString() : ''}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center opacity-60 py-4">No memory interactions</div>
        )}
      </div>
    </div>
  );

  const renderSettingsPanel = () => (
    <div className="animate-fade-in">
      <h3 className="text-lg font-medium mb-3">Settings</h3>

      <div className="bg-opacity-20 bg-white rounded-md p-3 mb-4">
        <div className="text-sm font-medium mb-2">Theme</div>
        <div className="flex items-center space-x-2">
          <button onClick={() => dispatch(setTheme('blue'))} className="w-6 h-6 rounded-full bg-blue-500" aria-label="Blue theme"></button>
          <button onClick={() => dispatch(setTheme('teal'))} className="w-6 h-6 rounded-full bg-teal-500" aria-label="Teal theme"></button>
          <button onClick={() => dispatch(setTheme('violet'))} className="w-6 h-6 rounded-full bg-violet-500" aria-label="Violet theme"></button>
        </div>
      </div>

      <div className="bg-opacity-20 bg-white rounded-md p-3 mb-4">
        <div className="text-sm font-medium mb-2">Security Level</div>
        <div className="flex items-center space-x-2">
          {['standard', 'high', 'custom'].map((level) => (
            <button
              key={level}
              onClick={() => dispatch(setSecurityLevel(level))}
              className={`jarvis-button ${securityLevel === level ? '' : 'bg-opacity-50'}`}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-opacity-20 bg-white rounded-md p-3">
        <div className="text-sm font-medium mb-2">Privacy</div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between items-center">
            <div>Data Retention (days)</div>
            <input
              type="number"
              min="0"
              value={privacySettings.dataRetention}
              onChange={(e) => dispatch(updatePrivacySettings({ dataRetention: Number(e.target.value) }))}
              className="jarvis-input w-24 ml-2"
            />
          </div>
          <div className="flex justify-between items-center">
            <div>Voice Data Storage</div>
            <button
              className="jarvis-button w-24"
              onClick={() => dispatch(updatePrivacySettings({ voiceDataStorage: !privacySettings.voiceDataStorage }))}
            >
              {privacySettings.voiceDataStorage ? 'Enabled' : 'Disabled'}
            </button>
          </div>
          <div className="flex justify-between items-center">
            <div>Location Tracking</div>
            <button
              className="jarvis-button w-24"
              onClick={() => dispatch(updatePrivacySettings({ locationTracking: !privacySettings.locationTracking }))}
            >
              {privacySettings.locationTracking ? 'Enabled' : 'Disabled'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderActivePanel = () => {
    switch (activePanel) {
      case 'context':
        return renderContextPanel();
      case 'update':
        return renderUpdatePanel();
      case 'security':
        return renderSecurityPanel();
      case 'logs':
        return renderLogsPanel();
      case 'memory':
        return renderMemoryPanel();
      case 'settings':
        return renderSettingsPanel();
      default:
        return renderContextPanel();
    }
  };

  return (
    <div className="jarvis-status-panel w-80 bg-opacity-80 backdrop-blur-md border-l border-opacity-20 border-white p-4 overflow-y-auto">
      {renderActivePanel()}
    </div>
  );
};

export default StatusPanel;