import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Brain, Clock, Search, Trash2, Star } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import FloatingPanel from './FloatingPanel';
import { GlassInput, GlassButton } from '../Glass/GlassComponents';
import ApiService from '../../services/api';

const MemoryGrid = styled.div`
  display: grid;
  gap: 16px;
  margin-bottom: 20px;
`;

const MemoryCard = styled(motion.div)`
  background: ${props => props.theme.glass};
  border: 1px solid ${props => props.theme.border};
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: ${props => props.theme.primary};
    box-shadow: 0 0 20px ${props => props.theme.glow};
    transform: translateY(-2px);
  }
`;

const MemoryHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const MemoryType = styled.span`
  background: ${props => props.theme.primary}20;
  color: ${props => props.theme.primary};
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
`;

const MemoryTimestamp = styled.div`
  color: ${props => props.theme.textSecondary};
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
`;

const MemoryContent = styled.div`
  color: ${props => props.theme.text};
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
`;

const MemoryActions = styled.div`
  display: flex;
  gap: 8px;
  justify-content: flex-end;
`;

const ActionButton = styled(motion.button)`
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: transparent;
  border: 1px solid ${props => props.theme.border};
  color: ${props => props.theme.textSecondary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: ${props => props.theme.glassHover};
    border-color: ${props => props.theme.primary};
    color: ${props => props.theme.primary};
  }
`;

const SearchContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: ${props => props.theme.textSecondary};
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: ${props => props.theme.textSecondary};
`;

const MemoryPanel = ({ isVisible, onClose }) => {
  const { theme } = useTheme();
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredMemories, setFilteredMemories] = useState([]);

  useEffect(() => {
    if (isVisible) {
      fetchMemories();
    }
  }, [isVisible]);

  useEffect(() => {
    if (searchTerm) {
      const filtered = memories.filter(memory =>
        memory.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        memory.type.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredMemories(filtered);
    } else {
      setFilteredMemories(memories);
    }
  }, [searchTerm, memories]);

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const data = await ApiService.listMemories();
      // Expecting { memories: [...] } but support array directly
      const items = Array.isArray(data) ? data : (data?.memories || []);
      setMemories(items);
    } catch (error) {
      console.error('Failed to fetch memories:', error);
      // Fallback to mock data for development
      setMemories([
        {
          id: 1,
          type: 'conversation',
          content: 'User asked about weather forecast for tomorrow',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          importance: 'medium'
        },
        {
          id: 2,
          type: 'preference',
          content: 'User prefers dark theme and voice interactions',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          importance: 'high'
        },
        {
          id: 3,
          type: 'context',
          content: 'Working on React desktop application project',
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          importance: 'high'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const deleteMemory = async (memoryId) => {
    try {
      await ApiService.deleteMemory(memoryId);
      setMemories(prev => prev.filter(m => m.id !== memoryId));
    } catch (error) {
      console.error('Failed to delete memory:', error);
    }
  };

  const toggleImportance = async (memoryId) => {
    try {
      const memory = memories.find(m => m.id === memoryId);
      const newImportance = memory.importance === 'high' ? 'medium' : 'high';
      await ApiService.updateMemory(memoryId, { importance: newImportance });
      setMemories(prev => prev.map(m => 
        m.id === memoryId ? { ...m, importance: newImportance } : m
      ));
    } catch (error) {
      console.error('Failed to update memory importance:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <FloatingPanel
      isVisible={isVisible}
      onClose={onClose}
      title="Memory & Context"
      icon={Brain}
      maxWidth="700px"
    >
      <SearchContainer>
        <GlassInput
          theme={theme}
          type="text"
          placeholder="Search memories..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ flex: 1 }}
        />
        <GlassButton
          theme={theme}
          onClick={fetchMemories}
          disabled={loading}
        >
          <Search size={16} />
        </GlassButton>
      </SearchContainer>

      {loading ? (
        <LoadingState theme={theme}>
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <Brain size={24} />
          </motion.div>
          <span style={{ marginLeft: '12px' }}>Loading memories...</span>
        </LoadingState>
      ) : filteredMemories.length > 0 ? (
        <MemoryGrid>
          {filteredMemories.map((memory, index) => (
            <MemoryCard
              key={memory.id}
              theme={theme}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <MemoryHeader>
                <MemoryType theme={theme}>
                  {memory.type}
                </MemoryType>
                <MemoryTimestamp theme={theme}>
                  <Clock size={12} />
                  {formatTimestamp(memory.timestamp)}
                </MemoryTimestamp>
              </MemoryHeader>
              
              <MemoryContent theme={theme}>
                {memory.content}
              </MemoryContent>
              
              <MemoryActions>
                <ActionButton
                  theme={theme}
                  onClick={() => toggleImportance(memory.id)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  style={{
                    color: memory.importance === 'high' ? theme.primary : theme.textSecondary
                  }}
                >
                  <Star size={14} fill={memory.importance === 'high' ? 'currentColor' : 'none'} />
                </ActionButton>
                
                <ActionButton
                  theme={theme}
                  onClick={() => deleteMemory(memory.id)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <Trash2 size={14} />
                </ActionButton>
              </MemoryActions>
            </MemoryCard>
          ))}
        </MemoryGrid>
      ) : (
        <EmptyState theme={theme}>
          <Brain size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
          <div>No memories found</div>
          <div style={{ fontSize: '14px', marginTop: '8px' }}>
            {searchTerm ? 'Try a different search term' : 'Start a conversation to build memory'}
          </div>
        </EmptyState>
      )}
    </FloatingPanel>
  );
};

export default MemoryPanel;