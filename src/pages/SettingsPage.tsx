import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  Settings, 
  Key, 
  Eye, 
  EyeOff, 
  CheckCircle, 
  XCircle, 
  Loader2, 
  ChevronDown,
  ExternalLink,
  Shield,
  BarChart3,
  DollarSign
} from 'lucide-react';
import { VideoVentureLaunchAPI } from '@/lib/api';

interface UserSettings {
  googleApiKey: string;
  geminiModel: string;
  imagenModel: string;
  veoModel: string;
  dailyLimit: number;
  monthlyLimit: number;
  enableAnalytics: boolean;
}

interface ApiUsageStats {
  dailyUsage: number;
  monthlyUsage: number;
  estimatedMonthlyCost: number;
  lastUpdated: string;
}

interface ValidationStatus {
  status: 'idle' | 'validating' | 'valid' | 'invalid';
  message?: string;
  availableModels?: string[];
}

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<UserSettings>({
    googleApiKey: '',
    geminiModel: 'gemini-1.5-flash',
    imagenModel: 'imagen-3.0',
    veoModel: 'veo-2.0',
    dailyLimit: 100,
    monthlyLimit: 1000,
    enableAnalytics: true,
  });

  const [showApiKey, setShowApiKey] = useState(false);
  const [validationStatus, setValidationStatus] = useState<ValidationStatus>({ status: 'idle' });
  const [isHelpExpanded, setIsHelpExpanded] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [usageStats] = useState<ApiUsageStats>({
    dailyUsage: 23,
    monthlyUsage: 456,
    estimatedMonthlyCost: 12.45,
    lastUpdated: new Date().toISOString(),
  });

  const modelOptions = {
    gemini: [
      { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro', description: 'Highest quality, higher cost' },
      { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash', description: 'Balanced performance' },
      { value: 'gemini-1.0-pro', label: 'Gemini 1.0 Pro', description: 'Lower cost option' }
    ],
    imagen: [
      { value: 'imagen-3.0', label: 'Imagen 3.0', description: 'Latest image generation' },
      { value: 'imagen-2.0', label: 'Imagen 2.0', description: 'Previous generation' }
    ],
    veo: [
      { value: 'veo-2.0', label: 'Veo 2.0', description: 'Latest video generation' },
      { value: 'veo-1.0', label: 'Veo 1.0', description: 'Previous generation' }
    ]
  };

  const handleApiKeyValidation = async () => {
    if (!settings.googleApiKey) return;

    setValidationStatus({ status: 'validating' });

    try {
      // Simulate API validation call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock successful validation
      if (settings.googleApiKey.startsWith('AIza') && settings.googleApiKey.length > 30) {
        setValidationStatus({
          status: 'valid',
          message: 'API key is valid and working',
          availableModels: ['gemini-1.5-pro', 'gemini-1.5-flash', 'imagen-3.0', 'veo-2.0']
        });
      } else {
        setValidationStatus({
          status: 'invalid',
          message: 'Invalid API key format or authentication failed'
        });
      }
    } catch (error) {
      setValidationStatus({
        status: 'invalid',
        message: 'Failed to validate API key. Please check your connection.'
      });
    }
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    try {
      // Simulate save operation
      await new Promise(resolve => setTimeout(resolve, 1000));
      // In real implementation, save to backend
      console.log('Settings saved:', settings);
    } finally {
      setIsSaving(false);
    }
  };

  const getValidationIcon = () => {
    switch (validationStatus.status) {
      case 'validating':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'valid':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'invalid':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getValidationBadge = () => {
    switch (validationStatus.status) {
      case 'valid':
        return <Badge className="vvl-badge-success">✓ Valid</Badge>;
      case 'invalid':
        return <Badge className="vvl-badge-error">✗ Invalid</Badge>;
      case 'validating':
        return <Badge className="vvl-badge">Validating...</Badge>;
      default:
        return null;
    }
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);
    try {
      // Save API key via our API client
      await VideoVentureLaunchAPI.setGeminiKey(settings.googleApiKey);
      console.log('Settings saved:', settings);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen vvl-gradient-bg p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="vvl-section">
          <div className="flex items-center gap-3 mb-6">
            <Settings className="h-8 w-8 text-primary" />
            <div>
              <h1 className="text-3xl font-bold vvl-text-primary">Settings</h1>
              <p className="vvl-text-secondary">Configure your AI models and API settings</p>
            </div>
          </div>
        </div>

        <Tabs defaultValue="api-keys" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="api-keys" className="flex items-center gap-2">
              <Key className="h-4 w-4" />
              API Configuration
            </TabsTrigger>
            <TabsTrigger value="usage" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Usage & Quotas
            </TabsTrigger>
            <TabsTrigger value="models" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Model Selection
            </TabsTrigger>
          </TabsList>

          {/* API Keys Tab */}
          <TabsContent value="api-keys" className="space-y-6">
            <Card className="vvl-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-primary" />
                  Google AI API Configuration
                </CardTitle>
                <CardDescription>
                  Enter your Google AI API key to enable AI-powered features
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="api-key" className="text-sm font-medium">
                    Google AI API Key *
                  </Label>
                  <div className="relative">
                    <Input
                      id="api-key"
                      type={showApiKey ? 'text' : 'password'}
                      value={settings.googleApiKey}
                      onChange={(e) => setSettings(prev => ({ ...prev, googleApiKey: e.target.value }))}
                      placeholder="Enter your Google AI API key (AIza...)"
                      className="vvl-input pr-20"
                    />
                    <div className="absolute right-2 top-2 flex items-center gap-2">
                      {getValidationIcon()}
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="h-6 w-6 p-0"
                      >
                        {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getValidationBadge()}
                      {validationStatus.message && (
                        <span className="text-sm text-muted-foreground">
                          {validationStatus.message}
                        </span>
                      )}
                    </div>
                    <Button
                      onClick={handleApiKeyValidation}
                      disabled={!settings.googleApiKey || validationStatus.status === 'validating'}
                      size="sm"
                      className="vvl-button-secondary"
                    >
                      {validationStatus.status === 'validating' ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Testing...
                        </>
                      ) : (
                        'Test Connection'
                      )}
                    </Button>
                  </div>
                </div>

                {/* API Key Help Section */}
                <Collapsible open={isHelpExpanded} onOpenChange={setIsHelpExpanded}>
                  <CollapsibleTrigger asChild>
                    <Button variant="ghost" className="w-full justify-between p-0 h-auto">
                      <span className="text-sm font-medium text-primary">
                        How to get your Google AI API Key
                      </span>
                      <ChevronDown className={`h-4 w-4 transition-transform ${isHelpExpanded ? 'rotate-180' : ''}`} />
                    </Button>
                  </CollapsibleTrigger>
                  <CollapsibleContent className="space-y-3 mt-4">
                    <Alert>
                      <AlertDescription>
                        <ol className="list-decimal list-inside space-y-2 text-sm">
                          <li>
                            Visit the{' '}
                            <a 
                              href="https://makersuite.google.com/app/apikey" 
                              className="text-primary hover:underline inline-flex items-center gap-1"
                              target="_blank" 
                              rel="noopener noreferrer"
                            >
                              Google AI Studio
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          </li>
                          <li>Sign in with your Google account</li>
                          <li>Click "Create API Key" button</li>
                          <li>Select your Google Cloud project or create a new one</li>
                          <li>Copy the generated API key (starts with "AIza...")</li>
                          <li>Paste it in the field above and click "Test Connection"</li>
                        </ol>
                      </AlertDescription>
                    </Alert>
                    <Alert>
                      <AlertDescription>
                        <p className="font-medium mb-2">Important Security Notes:</p>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                          <li>Keep your API key secure and never share it publicly</li>
                          <li>Enable billing in Google Cloud Console for full access</li>
                          <li>Set up usage quotas to avoid unexpected charges</li>
                          <li>Monitor your usage in the Google Cloud Console</li>
                        </ul>
                      </AlertDescription>
                    </Alert>
                  </CollapsibleContent>
                </Collapsible>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Usage Tab */}
          <TabsContent value="usage" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="vvl-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Daily Usage</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">{usageStats.dailyUsage}</div>
                  <div className="text-sm text-muted-foreground">of {settings.dailyLimit} requests</div>
                  <div className="w-full bg-muted rounded-full h-2 mt-2">
                    <div 
                      className="h-2 bg-primary rounded-full" 
                      style={{ width: `${(usageStats.dailyUsage / settings.dailyLimit) * 100}%` }}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card className="vvl-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Monthly Usage</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">{usageStats.monthlyUsage}</div>
                  <div className="text-sm text-muted-foreground">of {settings.monthlyLimit} requests</div>
                  <div className="w-full bg-muted rounded-full h-2 mt-2">
                    <div 
                      className="h-2 bg-primary rounded-full" 
                      style={{ width: `${(usageStats.monthlyUsage / settings.monthlyLimit) * 100}%` }}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card className="vvl-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <DollarSign className="h-4 w-4" />
                    Estimated Cost
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    ${usageStats.estimatedMonthlyCost.toFixed(2)}
                  </div>
                  <div className="text-sm text-muted-foreground">This month</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Models Tab */}
          <TabsContent value="models" className="space-y-6">
            <Card className="vvl-card">
              <CardHeader>
                <CardTitle>AI Model Configuration</CardTitle>
                <CardDescription>
                  Select the AI models to use for different types of content generation
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Gemini Model Selection */}
                  <div className="space-y-2">
                    <Label htmlFor="gemini-model">Text Generation Model</Label>
                    <Select 
                      value={settings.geminiModel} 
                      onValueChange={(value) => setSettings(prev => ({ ...prev, geminiModel: value }))}
                    >
                      <SelectTrigger className="vvl-input">
                        <SelectValue placeholder="Select Gemini model" />
                      </SelectTrigger>
                      <SelectContent>
                        {modelOptions.gemini.map((model) => (
                          <SelectItem key={model.value} value={model.value}>
                            <div>
                              <div className="font-medium">{model.label}</div>
                              <div className="text-xs text-muted-foreground">{model.description}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Imagen Model Selection */}
                  <div className="space-y-2">
                    <Label htmlFor="imagen-model">Image Generation Model</Label>
                    <Select 
                      value={settings.imagenModel} 
                      onValueChange={(value) => setSettings(prev => ({ ...prev, imagenModel: value }))}
                    >
                      <SelectTrigger className="vvl-input">
                        <SelectValue placeholder="Select Imagen model" />
                      </SelectTrigger>
                      <SelectContent>
                        {modelOptions.imagen.map((model) => (
                          <SelectItem key={model.value} value={model.value}>
                            <div>
                              <div className="font-medium">{model.label}</div>
                              <div className="text-xs text-muted-foreground">{model.description}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Veo Model Selection */}
                  <div className="space-y-2">
                    <Label htmlFor="veo-model">Video Generation Model</Label>
                    <Select 
                      value={settings.veoModel} 
                      onValueChange={(value) => setSettings(prev => ({ ...prev, veoModel: value }))}
                    >
                      <SelectTrigger className="vvl-input">
                        <SelectValue placeholder="Select Veo model" />
                      </SelectTrigger>
                      <SelectContent>
                        {modelOptions.veo.map((model) => (
                          <SelectItem key={model.value} value={model.value}>
                            <div>
                              <div className="font-medium">{model.label}</div>
                              <div className="text-xs text-muted-foreground">{model.description}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button 
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="vvl-button-primary"
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Settings'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
