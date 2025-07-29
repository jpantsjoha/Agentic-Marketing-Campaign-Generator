# Settings Page - User Configuration Management

**Version:** 2.0  
**Date:** 2025-07-29  
**Status:** MVP Required Feature  
**Priority:** High  

---

## 📋 Executive Summary

The Settings Page is a critical MVP component that enables self-service user onboarding by allowing users to configure their own Google AI API keys. This eliminates dependency on shared credentials and provides a scalable solution for user management.

### Key Benefits
- **Self-Service Onboarding**: Users can test the platform immediately with their own API keys
- **Scalability**: Eliminates shared credential bottlenecks
- **Security**: Each user manages their own API credentials
- **Cost Management**: Users control their own API usage and costs

---

## 🎯 Core Requirements

### Functional Requirements
1. **Google API Key Management**: Secure input, validation, and storage
2. **Model Configuration**: Select from available AI models (Gemini, Imagen, Veo)
3. **Usage Monitoring**: Real-time API usage tracking and quotas
4. **Security**: Encrypted storage and secure credential handling
5. **User Experience**: Intuitive interface with helpful guidance

### Non-Functional Requirements
- **Performance**: API key validation under 3 seconds
- **Security**: End-to-end encryption for stored credentials
- **Accessibility**: WCAG 2.1 AA compliance
- **Responsiveness**: Mobile-first responsive design

---

## 🏗️ Technical Architecture

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │───▶│   FastAPI       │───▶│  Google AI API  │
│   Settings Page │    │   Backend       │    │   Validation    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Encrypted      │
                       │  Database       │
                       │  Storage        │
                       └─────────────────┘
```

### Data Flow
1. **User Input**: API key entered in secure form
2. **Frontend Validation**: Basic format validation
3. **Backend Processing**: Encryption and secure transmission
4. **API Validation**: Real-time testing with Google AI
5. **Storage**: Encrypted storage in database
6. **Usage Tracking**: Real-time monitoring and quota management

---

## 🎨 User Interface Components

### 1. Google API Key Management Section

#### **Component Structure:**
```tsx
// Settings Page Main Component
interface SettingsPageProps {
  user: User;
  onSettingsUpdate: (settings: UserSettings) => void;
}

interface UserSettings {
  googleApiKey: string;
  geminiModel: string;
  imagenModel: string;
  veoModel: string;
  apiQuotaLimits: QuotaLimits;
  enableAnalytics: boolean;
  theme: 'light' | 'dark';
}

interface QuotaLimits {
  dailyLimit: number;
  monthlyLimit: number;
  currentUsage: ApiUsageStats;
}
```

#### **API Key Input Section:**
```tsx
const GoogleApiKeySection: React.FC<{
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  onValidate: () => void;
  validationStatus: 'idle' | 'validating' | 'valid' | 'invalid';
}> = ({ apiKey, onApiKeyChange, onValidate, validationStatus }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Google AI API Configuration
      </h3>
      
      <div className="space-y-4">
        {/* API Key Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Google AI API Key
            <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => onApiKeyChange(e.target.value)}
              placeholder="Enter your Google AI API key (AIza...)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={onValidate}
              disabled={!apiKey || validationStatus === 'validating'}
              className="absolute right-2 top-2 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {validationStatus === 'validating' ? 'Testing...' : 'Test'}
            </button>
          </div>
          
          {/* validation Status */}
          <ValidationStatus status={validationStatus} />
          
          {/* Help Text */}
          <p className="mt-2 text-sm text-gray-600">
            Your API key is encrypted and stored securely. 
            <a href="#api-setup-guide" className="text-blue-600 hover:underline ml-1">
              Need help getting an API key?
            </a>
          </p>
        </div>

        {/* Model Selection */}
        <ModelSelectionSection />
        
        {/* Quota Management */}
        <QuotaManagementSection />
      </div>
    </div>
  );
};
```

### 2. Model Configuration Section

#### **Model Selection Component:**
```tsx
const ModelSelectionSection: React.FC<{
  settings: UserSettings;
  onSettingsChange: (settings: Partial<UserSettings>) => void;
}> = ({ settings, onSettingsChange }) => {
  const modelOptions = {
    gemini: [
      { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro (Recommended)', cost: 'Higher quality, higher cost' },
      { value: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash', cost: 'Balanced performance' },
      { value: 'gemini-1.0-pro', label: 'Gemini 1.0 Pro', cost: 'Lower cost option' }
    ],
    imagen: [
      { value: 'imagen-3.0', label: 'Imagen 3.0 (Recommended)', cost: 'Latest image generation' },
      { value: 'imagen-2.0', label: 'Imagen 2.0', cost: 'Previous generation' }
    ],
    veo: [
      { value: 'veo-2.0', label: 'Veo 2.0 (Recommended)', cost: 'Latest video generation' },
      { value: 'veo-1.0', label: 'Veo 1.0', cost: 'Previous generation' }
    ]
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <h4 className="font-medium text-gray-900 mb-3">AI Model Configuration</h4>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Gemini Model Selection */}
        <ModelSelector
          label="Text Generation Model"
          options={modelOptions.gemini}
          value={settings.geminiModel}
          onChange={(value) => onSettingsChange({ geminiModel: value })}
        />
        
        {/* Imagen Model Selection */}
        <ModelSelector
          label="Image Generation Model"
          options={modelOptions.imagen}
          value={settings.imagenModel}
          onChange={(value) => onSettingsChange({ imagenModel: value })}
        />
        
        {/* Veo Model Selection */}
        <ModelSelector
          label="Video Generation Model"
          options={modelOptions.veo}
          value={settings.veoModel}
          onChange={(value) => onSettingsChange({ veoModel: value })}
        />
      </div>
    </div>
  );
};
```

### 3. Usage Monitoring & Quota Management

#### **Quota Display Component:**
```tsx
const QuotaManagementSection: React.FC<{
  usage: ApiUsageStats;
  limits: QuotaLimits;
  onLimitsChange: (limits: QuotaLimits) => void;
}> = ({ usage, limits, onLimitsChange }) => {
  return (
    <div className="bg-blue-50 rounded-lg p-4">
      <h4 className="font-medium text-gray-900 mb-3">API Usage & Quotas</h4>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Daily Usage */}
        <UsageMetric
          label="Today's Usage"
          current={usage.dailyUsage}
          limit={limits.dailyLimit}
          unit="requests"
        />
        
        {/* Monthly Usage */}
        <UsageMetric
          label="Monthly Usage"
          current={usage.monthlyUsage}
          limit={limits.monthlyLimit}
          unit="requests"
        />
      </div>
      
      {/* Cost Estimation */}
      <div className="border-t border-blue-200 pt-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Estimated Monthly Cost:</span>
          <span className="font-medium text-green-600">
            ${calculateEstimatedCost(usage, limits).toFixed(2)}
          </span>
        </div>
      </div>
      
      {/* Quota Limit Controls */}
      <QuotaLimitControls
        limits={limits}
        onLimitsChange={onLimitsChange}
      />
    </div>
  );
};
```

### 4. API Key Setup Guide

#### **Expandable Help Section:**
```tsx
const ApiSetupGuide: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full text-left"
      >
        <h4 className="font-medium text-yellow-800">
          How to get your Google AI API Key
        </h4>
        <ChevronDownIcon 
          className={`h-5 w-5 text-yellow-600 transform transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
        />
      </button>
      
      {isExpanded && (
        <div className="mt-4 space-y-3 text-sm text-yellow-700">
          <ol className="list-decimal list-inside space-y-2">
            <li>
              Visit the <a href="https://makersuite.google.com/app/apikey" 
              className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
              Google AI Studio
              </a>
            </li>
            <li>Sign in with your Google account</li>
            <li>Click "Create API Key" button</li>
            <li>Select your Google Cloud project or create a new one</li>
            <li>Copy the generated API key (starts with "AIza...")</li>
            <li>Paste it in the field above and click "Test"</li>
          </ol>
          
          <div className="bg-yellow-100 p-3 rounded border">
            <p className="font-medium">Important Notes:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>Keep your API key secure and never share it publicly</li>
              <li>Enable billing in Google Cloud Console for full access</li>
              <li>Set up usage quotas to avoid unexpected charges</li>
              <li>Monitor your usage in the Google Cloud Console</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## 🔧 Backend Integration

### API Key Storage & Encryption

#### **Secure Storage Implementation:**
```python
# backend/services/user_settings_service.py
from cryptography.fernet import Fernet
from typing import Optional
import os

class UserSettingsService:
    """Secure user settings management service"""
    
    def __init__(self):
        # Get encryption key from environment
        self.encryption_key = os.getenv('SETTINGS_ENCRYPTION_KEY')
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    async def store_api_key(self, user_id: str, api_key: str) -> bool:
        """Securely store encrypted API key"""
        try:
            # Encrypt the API key
            encrypted_key = self.cipher_suite.encrypt(api_key.encode())
            
            # Store in database
            await self.db.execute(
                """
                INSERT INTO user_settings (user_id, encrypted_api_key, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                encrypted_api_key = excluded.encrypted_api_key,
                updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, encrypted_key)
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to store API key for user {user_id}: {e}")
            return False
    
    async def get_api_key(self, user_id: str) -> Optional[str]:
        """Retrieve and decrypt API key"""
        try:
            result = await self.db.fetch_one(
                "SELECT encrypted_api_key FROM user_settings WHERE user_id = ?",
                (user_id,)
            )
            
            if result:
                encrypted_key = result['encrypted_api_key']
                decrypted_key = self.cipher_suite.decrypt(encrypted_key).decode()
                return decrypted_key
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve API key for user {user_id}: {e}")
            return None
    
    async def validate_api_key(self, api_key: str) -> dict:
        """Validate Google AI API key"""
        try:
            # Test with a simple Gemini request
            client = genai.Client(api_key=api_key)
            
            # Test text generation
            response = await client.agenerate_text(
                model="gemini-1.5-flash",
                prompt="Say 'API key validation successful'",
                max_output_tokens=50
            )
            
            # Test available models
            models = await client.list_models()
            
            return {
                "valid": True,
                "message": "API key is valid and working",
                "available_models": [model.name for model in models],
                "test_response": response.text
            }
            
        except Exception as e:
            return {
                "valid": False,
                "message": f"API key validation failed: {str(e)}",
                "error_type": type(e).__name__
            }
```

### Settings API Endpoints

#### **FastAPI Routes:**
```python
# backend/api/routes/settings.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

class UserSettingsRequest(BaseModel):
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    imagen_model: str = "imagen-3.0"
    veo_model: str = "veo-2.0"
    daily_limit: int = 100
    monthly_limit: int = 1000
    enable_analytics: bool = True

class ApiKeyValidationResponse(BaseModel):
    valid: bool
    message: str
    available_models: Optional[list] = None
    error_type: Optional[str] = None

@router.post("/api-key/validate")
async def validate_api_key(
    request: dict,
    current_user = Depends(get_current_user)
) -> ApiKeyValidationResponse:
    """Validate Google AI API key"""
    
    api_key = request.get("api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    
    settings_service = UserSettingsService()
    validation_result = await settings_service.validate_api_key(api_key)
    
    return ApiKeyValidationResponse(**validation_result)

@router.post("/update")
async def update_user_settings(
    settings: UserSettingsRequest,
    current_user = Depends(get_current_user)
):
    """Update user settings"""
    
    settings_service = UserSettingsService()
    
    # Store API key securely if provided
    if settings.google_api_key:
        success = await settings_service.store_api_key(
            current_user.id, 
            settings.google_api_key
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store API key")
    
    # Update other settings
    await settings_service.update_settings(current_user.id, settings.dict())
    
    return {"message": "Settings updated successfully"}

@router.get("/usage")
async def get_usage_stats(
    current_user = Depends(get_current_user)
):
    """Get API usage statistics"""
    
    usage_service = ApiUsageService()
    stats = await usage_service.get_user_usage_stats(current_user.id)
    
    return {
        "daily_usage": stats.daily_usage,
        "monthly_usage": stats.monthly_usage,
        "estimated_cost": stats.estimated_monthly_cost,
        "last_updated": stats.last_updated.isoformat()
    }
```

---

## 🎨 UI Design Specifications

### Light Theme Design System

#### **Color Palette:**
```css
/* Light Theme Color Variables */
:root {
  /* Primary Colors */
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-500: #3b82f6;
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  
  /* Gray Scale */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-900: #111827;
  
  /* Success/Error States */
  --green-50: #f0fdf4;
  --green-600: #16a34a;
  --red-50: #fef2f2;
  --red-600: #dc2626;
  --yellow-50: #fefce8;
  --yellow-600: #ca8a04;
}
```

#### **Component Styling:**
```css
/* Settings Page Styles */
.settings-page {
  background: linear-gradient(135deg, var(--gray-50) 0%, var(--primary-50) 100%);
  min-height: 100vh;
  padding: 2rem 1rem;
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--gray-200);
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.settings-section-header {
  background: var(--primary-50);
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--primary-100);
}

.settings-section-content {
  padding: 1.5rem;
}

/* Form Elements */
.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-primary {
  background: var(--primary-600);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--primary-700);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Status Indicators */
.status-valid {
  color: var(--green-600);
  background: var(--green-50);
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status-invalid {
  color: var(--red-600);
  background: var(--red-50);
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}
```

---

## 📊 Success Criteria

### Functional Requirements
- [ ] **API Key Input**: Secure password field with validation
- [ ] **Key Testing**: Real-time validation with Google AI APIs
- [ ] **Model Selection**: Dropdown menus for different AI models
- [ ] **Usage Monitoring**: Display current API usage and limits
- [ ] **Quota Management**: Set daily/monthly usage limits
- [ ] **Help Integration**: Inline help for API key setup

### User Experience Requirements
- [ ] **Intuitive Interface**: Clean, organized layout
- [ ] **Immediate Feedback**: Real-time validation status
- [ ] **Error Handling**: Clear error messages and recovery paths
- [ ] **Mobile Responsive**: Works on all device sizes
- [ ] **Accessibility**: WCAG 2.1 AA compliance

### Security Requirements
- [ ] **Encrypted Storage**: API keys encrypted at rest
- [ ] **Secure Transmission**: HTTPS for all API communications
- [ ] **Input Validation**: Sanitize all user inputs
- [ ] **Rate Limiting**: Prevent API abuse
- [ ] **Audit Logging**: Track settings changes

### Performance Requirements
- [ ] **Fast Validation**: API key testing under 3 seconds
- [ ] **Responsive UI**: Settings changes reflected immediately
- [ ] **Caching**: Cache validation results appropriately
- [ ] **Error Recovery**: Graceful handling of API failures

---

---

## 🚀 Implementation Roadmap

### 📅 Phase 1: Foundation (Days 1-3)
**Objective**: Core settings infrastructure

#### Frontend Development
- [ ] Create `SettingsPage.tsx` component with modern light theme
- [ ] Implement `GoogleApiKeySection` with secure input validation
- [ ] Add basic form validation and user feedback
- [ ] Create responsive layout using new VVL light theme classes

#### Backend Development
- [ ] Create `/api/v1/settings` endpoints in FastAPI
- [ ] Implement `UserSettingsService` with encryption capabilities
- [ ] Add database schema for user settings
- [ ] Create API key validation service

#### Security Implementation
- [ ] Set up Fernet encryption for API key storage
- [ ] Implement secure environment variable management
- [ ] Add rate limiting for API validation requests
- [ ] Create audit logging for settings changes

### 📅 Phase 2: Enhanced Features (Days 4-6)
**Objective**: Advanced functionality and user experience

#### User Experience Enhancements
- [ ] Implement model selection dropdowns (Gemini, Imagen, Veo)
- [ ] Add real-time API usage monitoring
- [ ] Create quota management with cost estimation
- [ ] Build expandable help guide with step-by-step instructions

#### API Integration
- [ ] Integrate with Google AI Studio for key validation
- [ ] Add support for multiple model configurations
- [ ] Implement usage tracking and analytics
- [ ] Create webhook system for quota alerts

### 📅 Phase 3: Production Ready (Days 7-9)
**Objective**: Polish, security, and deployment

#### Quality Assurance
- [ ] Comprehensive unit test coverage (>90%)
- [ ] Integration testing with Google AI APIs
- [ ] End-to-end testing with Playwright
- [ ] Accessibility testing (WCAG 2.1 AA)
- [ ] Performance testing and optimization

#### Production Deployment
- [ ] Vercel deployment configuration
- [ ] Environment variable management
- [ ] Monitoring and alerting setup
- [ ] Documentation and user guides

---

## 🎯 Success Metrics

### Technical Metrics
- **API Key Validation**: <3 seconds response time
- **Test Coverage**: >90% unit test coverage
- **Security**: 100% encrypted credential storage
- **Performance**: Page load <2 seconds

### User Experience Metrics
- **Onboarding Time**: <5 minutes to configure and validate
- **Success Rate**: >95% successful API key validation
- **User Satisfaction**: Intuitive interface with clear feedback
- **Error Recovery**: Clear error messages with actionable solutions

### Business Impact
- **Self-Service Rate**: 90% of users can configure independently
- **Support Reduction**: 70% reduction in API key support tickets
- **User Retention**: Improved onboarding leads to higher retention
- **Scalability**: Platform can handle 1000+ concurrent users

---

## 📚 Documentation & Resources

### User Documentation
- **Getting Started Guide**: Step-by-step API key setup
- **FAQ**: Common issues and solutions
- **Video Tutorial**: Visual walkthrough of configuration
- **API Reference**: Available models and configuration options

### Developer Documentation
- **Technical Specification**: Detailed implementation guide
- **API Documentation**: Backend endpoint specifications
- **Security Guide**: Encryption and security best practices
- **Testing Guide**: Comprehensive testing procedures

---

**This structured settings page implementation will transform user onboarding from a manual, support-heavy process into a seamless, self-service experience that scales efficiently while maintaining enterprise-grade security.**