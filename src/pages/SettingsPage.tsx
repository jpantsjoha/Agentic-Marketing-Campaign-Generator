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
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <div className="max-w-md space-y-4">
        <label htmlFor="gemini-key" className="block text-sm font-medium">Google Gemini API Key</label>
        <Input id="gemini-key" value={key} onChange={(e) => setKey(e.target.value)} />
        <Button onClick={handleSave}>Save</Button>
      </div>
    </div>
  );
};

export default SettingsPage;
