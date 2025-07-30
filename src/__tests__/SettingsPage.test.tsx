import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { SettingsProvider } from '@/contexts/SettingsContext';
import SettingsPage from '@/pages/SettingsPage';
import { vi } from 'vitest';

vi.mock('@/lib/api', () => ({
  VideoVentureLaunchAPI: {
    setGeminiKey: vi.fn(() => Promise.resolve()),
  },
}));

describe('SettingsPage', () => {
  test('saves gemini api key', async () => {
    render(
      <BrowserRouter>
        <SettingsProvider>
          <SettingsPage />
        </SettingsProvider>
      </BrowserRouter>
    );
    const input = screen.getByLabelText(/Google Gemini API Key/i);
    fireEvent.change(input, { target: { value: 'abc123' } });
    fireEvent.click(screen.getByText(/Save/i));
    await waitFor(() => {
      expect(localStorage.getItem('gemini_api_key')).toContain('abc123');
    });
  });
});
