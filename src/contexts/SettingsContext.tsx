import React, { createContext, useContext, useEffect, useState } from 'react';
import safeStorage from '@/utils/safeStorage';

interface SettingsContextValue {
  geminiApiKey: string;
  setGeminiApiKey: (key: string) => void;
}

const SettingsContext = createContext<SettingsContextValue>({
  geminiApiKey: '',
  setGeminiApiKey: () => {},
});

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [geminiApiKey, setGeminiApiKeyState] = useState('');

  useEffect(() => {
    const stored = safeStorage.get<string>('gemini_api_key', '');
    setGeminiApiKeyState(stored);
  }, []);

  const setGeminiApiKey = (key: string) => {
    setGeminiApiKeyState(key);
    safeStorage.set('gemini_api_key', key);
  };

  return (
    <SettingsContext.Provider value={{ geminiApiKey, setGeminiApiKey }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => useContext(SettingsContext);
