import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { AnalysisApiResponse } from '../api/client';

export interface HistoryEntry {
  id: string;
  timestamp: string;
  task: string;
  query: string;
  model: string;
  status: string;
  confidenceLevel: 'LOW' | 'MEDIUM' | 'HIGH' | null;
  confidenceScore: number | null;
  primaryPreview?: string | null;
  secondPreview?: string | null;
  sarPreview?: string | null;
  result: AnalysisApiResponse;
}

interface HistoryContextType {
  history: HistoryEntry[];
  addHistoryEntry: (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => void;
  deleteHistoryEntry: (id: string) => void;
  clearHistory: () => void;
  getEntryById: (id: string) => HistoryEntry | undefined;
}

const STORAGE_KEY = 'satquery_analysis_history_v1';
const HistoryContext = createContext<HistoryContextType | null>(null);

export const HistoryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [history, setHistory] = useState<HistoryEntry[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Failed to load analysis history from localStorage:', e);
    }
    return [];
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (e) {
      console.warn('Failed to persist analysis history:', e);
    }
  }, [history]);

  const addHistoryEntry = useCallback((entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => {
    const newEntry: HistoryEntry = {
      ...entry,
      id: `hist-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      timestamp: new Date().toISOString(),
    };
    setHistory((prev) => [newEntry, ...prev.slice(0, 49)]); // keep last 50 entries
  }, []);

  const deleteHistoryEntry = useCallback((id: string) => {
    setHistory((prev) => prev.filter((item) => item.id !== id));
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {}
  }, []);

  const getEntryById = useCallback(
    (id: string) => {
      return history.find((h) => h.id === id);
    },
    [history]
  );

  return (
    <HistoryContext.Provider
      value={{ history, addHistoryEntry, deleteHistoryEntry, clearHistory, getEntryById }}
    >
      {children}
    </HistoryContext.Provider>
  );
};

export function useHistory(): HistoryContextType {
  const ctx = useContext(HistoryContext);
  if (!ctx) {
    throw new Error('useHistory must be used within a HistoryProvider');
  }
  return ctx;
}
