import React, { useState } from 'react';
import { useSettings } from '@/contexts/SettingsContext';
import { VideoVentureLaunchAPI } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

const SettingsPage: React.FC = () => {
  const { geminiApiKey, setGeminiApiKey } = useSettings();
  const [key, setKey] = useState(geminiApiKey);

  const handleSave = async () => {
    setGeminiApiKey(key);
    try {
      await VideoVentureLaunchAPI.setGeminiKey(key);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen vvl-gradient-bg p-6">
      <div className="container mx-auto">
        <h1 className="text-2xl font-bold mb-4 vvl-text-primary">Settings</h1>
        <div className="vvl-card max-w-md p-6 space-y-4">
          <label htmlFor="gemini-key" className="block text-sm font-medium vvl-text-primary">Google Gemini API Key</label>
          <Input id="gemini-key" value={key} onChange={(e) => setKey(e.target.value)} className="vvl-input" />
          <div>
            <Button onClick={handleSave} className="vvl-button-primary">Save</Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
