/**
 * Selenium MCP Test: ADK 1.8.0 Visual Content Issues Validation
 * Focus: Text visibility and thumbnail functionality issues
 * 
 * Issues to validate:
 * 1. Light/faded text on social posts
 * 2. Broken thumbnails (not loading)
 * 3. Content generation failures
 * 4. ADK 1.8.0 features validation
 */

import { Builder, By, until } from 'selenium-webdriver';
import chrome from 'selenium-webdriver/chrome.js';
import fs from 'fs';
import path from 'path';

const TEST_CONFIG = {
    baseUrl: 'http://localhost:8080',
    campaign: {
        businessUrl: 'https://www.liatvictoriaphotography.co.uk/',
        name: 'Liat Victoria Photography Spring Campaign 2025',
        description: 'Professional photography services showcasing weddings, portraits, and special events'
    },
    timeouts: {
        pageLoad: 30000,
        elementWait: 15000,
        contentGeneration: 120000
    }
};

class VisualContentIssuesTest {
    constructor() {
        this.driver = null;
        this.issues = [];
        this.screenshots = [];
    }

    async setupSeleniumMCP() {
        console.log('🔧 Setting up Selenium MCP WebDriver...');
        
        const options = new chrome.Options();
        options.addArguments([
            '--disable-web-security',
            '--window-size=1920,1200',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]);
        
        // Use system Chrome
        options.setChromeBinaryPath('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome');
        
        this.driver = await new Builder()
            .forBrowser('chrome')
            .setChromeOptions(options)
            .build();
            
        await this.driver.manage().setTimeouts({ implicit: TEST_CONFIG.timeouts.elementWait });
        console.log('✅ Selenium MCP WebDriver initialized');
    }

    async takeScreenshot(name, description) {
        try {
            const screenshot = await this.driver.takeScreenshot();
            const filepath = `selenium-mcp-${name}-${Date.now()}.png`;
            fs.writeFileSync(filepath, screenshot, 'base64');
            
            this.screenshots.push({
                name,
                description,
                filepath,
                timestamp: new Date().toISOString()
            });
            
            console.log(`📸 Screenshot: ${filepath} - ${description}`);
            return filepath;
        } catch (error) {
            console.error(`❌ Screenshot failed for ${name}:`, error.message);
        }
    }

    logIssue(type, description, severity = 'medium', element = null) {
        const issue = {
            type,
            description,
            severity,
            element: element ? element.toString() : null,
            timestamp: new Date().toISOString()
        };
        
        this.issues.push(issue);
        const icon = severity === 'high' ? '🔴' : severity === 'medium' ? '🟡' : '🟢';
        console.log(`${icon} ISSUE [${severity.toUpperCase()}]: ${description}`);
    }

    async navigateAndCreateCampaign() {
        console.log('\n🚀 Step 1: Navigate and Create Campaign');
        
        await this.driver.get(TEST_CONFIG.baseUrl);
        await this.driver.wait(until.titleContains('Marketing'), TEST_CONFIG.timeouts.pageLoad);
        
        await this.takeScreenshot('01-homepage', 'Initial homepage load');
        
        // Click create campaign
        const createButton = await this.driver.wait(
            until.elementLocated(By.xpath("//button[contains(text(), 'Create')]")),
            TEST_CONFIG.timeouts.elementWait
        );
        await createButton.click();
        
        await this.takeScreenshot('02-campaign-form', 'Campaign creation form');
        
        // Fill campaign details
        await this.driver.findElement(By.css('input[placeholder*="Summer 2025"]'))
            .sendKeys(TEST_CONFIG.campaign.name);
        
        await this.driver.findElement(By.css('input[placeholder*="brand awareness"]'))
            .sendKeys('Increase website traffic and photography bookings');
        
        await this.driver.findElement(By.css('textarea[placeholder*="company"]'))
            .sendKeys(TEST_CONFIG.campaign.description);
        
        await this.driver.findElement(By.css('input[placeholder*="website"]'))
            .sendKeys(TEST_CONFIG.campaign.businessUrl);
        
        await this.takeScreenshot('03-form-filled', 'Campaign form filled out');
        
        // Submit campaign
        const submitButton = await this.driver.findElement(By.xpath("//button[contains(text(), 'Start AI')]"));
        await submitButton.click();
        
        // Wait for ideation page
        await this.driver.wait(until.urlContains('ideation'), TEST_CONFIG.timeouts.pageLoad);
        console.log('✅ Campaign created and navigated to ideation page');
    }

    async validateTextVisibility() {
        console.log('\n🔍 Step 2: Validate Text Visibility Issues');
        
        await this.takeScreenshot('04-ideation-page', 'Ideation page for text analysis');
        
        // Check for text elements that might be faded/light
        const textElements = await this.driver.findElements(By.css('p, span, div, h1, h2, h3, h4, h5, h6'));
        
        let lightTextCount = 0;
        let totalTextElements = 0;
        
        for (const element of textElements) {
            try {
                const text = await element.getText();
                if (text && text.trim().length > 0) {
                    totalTextElements++;
                    
                    // Check CSS styles for opacity/color issues
                    const styles = await this.driver.executeScript(`
                        const elem = arguments[0];
                        const computedStyle = window.getComputedStyle(elem);
                        return {
                            opacity: computedStyle.opacity,
                            color: computedStyle.color,
                            visibility: computedStyle.visibility
                        };
                    `, element);
                    
                    // Check for light/faded text
                    if (parseFloat(styles.opacity) < 0.7) {
                        lightTextCount++;
                        this.logIssue('text-visibility', 
                            `Text element with low opacity (${styles.opacity}): "${text.substring(0, 50)}..."`,
                            'medium', element);
                    }
                    
                    // Check for very light colors (basic RGB analysis)
                    if (styles.color && styles.color.includes('rgb')) {
                        const rgbValues = styles.color.match(/\d+/g);
                        if (rgbValues && rgbValues.length >= 3) {
                            const [r, g, b] = rgbValues.map(Number);
                            const brightness = (r + g + b) / 3;
                            
                            // If text is very light (brightness > 200 on white background)
                            if (brightness > 200) {
                                lightTextCount++;
                                this.logIssue('text-contrast', 
                                    `Light text color detected (RGB: ${r},${g},${b}): "${text.substring(0, 50)}..."`,
                                    'high', element);
                            }
                        }
                    }
                }
            } catch (error) {
                // Skip elements that can't be analyzed
                continue;
            }
        }
        
        console.log(`📊 Text Analysis: ${lightTextCount}/${totalTextElements} elements have visibility issues`);
        
        if (lightTextCount > totalTextElements * 0.1) { // More than 10% of text is light
            this.logIssue('text-visibility-systemic', 
                `High percentage of light text detected: ${lightTextCount}/${totalTextElements} (${Math.round(lightTextCount/totalTextElements*100)}%)`,
                'high');
        }
    }

    async validateThumbnails() {
        console.log('\n🖼️ Step 3: Validate Thumbnail Functionality');
        
        // Generate some content first
        const generateButtons = await this.driver.findElements(By.xpath("//button[contains(text(), 'Generate')]"));
        
        if (generateButtons.length > 0) {
            console.log(`🎯 Found ${generateButtons.length} generate buttons, testing content generation...`);
            
            // Try generating text + image content
            for (let i = 0; i < Math.min(2, generateButtons.length); i++) {
                try {
                    await generateButtons[i].click();
                    console.log(`⏳ Triggered generation ${i + 1}, waiting...`);
                    await this.driver.sleep(15000); // Wait for generation
                } catch (error) {
                    this.logIssue('content-generation', 
                        `Failed to trigger content generation ${i + 1}: ${error.message}`,
                        'high');
                }
            }
        }
        
        await this.takeScreenshot('05-after-generation', 'After content generation attempts');
        
        // Analyze thumbnails
        const images = await this.driver.findElements(By.css('img'));
        console.log(`🔍 Found ${images.length} image elements to analyze...`);
        
        let brokenThumbnails = 0;
        let workingThumbnails = 0;
        let totalThumbnails = 0;
        
        for (const img of images) {
            try {
                const src = await img.getAttribute('src');
                const alt = await img.getAttribute('alt');
                const naturalWidth = await this.driver.executeScript('return arguments[0].naturalWidth', img);
                const naturalHeight = await this.driver.executeScript('return arguments[0].naturalHeight', img);
                
                totalThumbnails++;
                
                console.log(`🖼️ Image ${totalThumbnails}: src="${src?.substring(0, 60)}...", size=${naturalWidth}x${naturalHeight}`);
                
                // Check for broken images
                if (naturalWidth === 0 || naturalHeight === 0) {
                    brokenThumbnails++;
                    this.logIssue('broken-thumbnail', 
                        `Broken thumbnail detected: src="${src}", alt="${alt}"`,
                        'high', img);
                } else if (src && !src.startsWith('data:image/svg')) {
                    workingThumbnails++;
                    
                    // Test if image actually loads by trying to fetch it
                    if (src.startsWith('http')) {
                        try {
                            const response = await this.driver.executeScript(`
                                return fetch('${src}')
                                    .then(r => ({ status: r.status, ok: r.ok }))
                                    .catch(e => ({ error: e.message }));
                            `);
                            
                            if (response.error || !response.ok) {
                                this.logIssue('thumbnail-network-error', 
                                    `Thumbnail network error: ${src} - ${response.error || `HTTP ${response.status}`}`,
                                    'high');
                            }
                        } catch (e) {
                            this.logIssue('thumbnail-fetch-error', 
                                `Could not test thumbnail fetch: ${src}`,
                                'medium');
                        }
                    }
                } else if (src && src.includes('placeholder')) {
                    this.logIssue('placeholder-thumbnail', 
                        `Placeholder thumbnail found instead of generated content: ${src}`,
                        'medium', img);
                }
                
            } catch (error) {
                this.logIssue('thumbnail-analysis-error', 
                    `Could not analyze thumbnail: ${error.message}`,
                    'low');
            }
        }
        
        console.log(`📊 Thumbnail Analysis: ${workingThumbnails} working, ${brokenThumbnails} broken out of ${totalThumbnails} total`);
        
        // Check for error messages or regenerate prompts
        const errorMessages = await this.driver.findElements(By.xpath("//text()[contains(., 'Regenerate')] | //text()[contains(., 'error')] | //text()[contains(., 'failed')]"));
        if (errorMessages.length > 0) {
            this.logIssue('content-generation-errors', 
                `Found ${errorMessages.length} error/regenerate messages indicating content generation issues`,
                'high');
        }
    }

    async validateADKFeatures() {
        console.log('\n🔧 Step 4: Validate ADK 1.8.0 Features');
        
        // Check for ADK-specific elements and functionality
        const adkElements = await this.driver.findElements(By.css('[data-adk], [class*="adk"], [id*="adk"]'));
        console.log(`🛠️ Found ${adkElements.length} ADK-related elements`);
        
        // Check for streaming functionality
        const streamingElements = await this.driver.findElements(By.css('[class*="stream"], [data-stream], .streaming, .real-time'));
        if (streamingElements.length > 0) {
            console.log(`📡 Found ${streamingElements.length} streaming-related elements`);
        } else {
            this.logIssue('missing-streaming', 
                'No streaming functionality detected - expected in ADK 1.8.0',
                'medium');
        }
        
        // Check for enhanced visual generation indicators
        const visualGenElements = await this.driver.findElements(By.css('[class*="visual"], [class*="generation"], .ai-generated'));
        console.log(`🎨 Found ${visualGenElements.length} visual generation elements`);
        
        await this.takeScreenshot('06-adk-features', 'ADK features validation');
    }

    async generateReport() {
        console.log('\n📊 Generating Comprehensive Test Report...');
        
        const report = {
            testSuite: 'ADK 1.8.0 Visual Content Issues Validation - Liat Victoria Photography',
            timestamp: new Date().toISOString(),
            campaign: TEST_CONFIG.campaign,
            summary: {
                totalIssues: this.issues.length,
                highSeverityIssues: this.issues.filter(i => i.severity === 'high').length,
                mediumSeverityIssues: this.issues.filter(i => i.severity === 'medium').length,
                lowSeverityIssues: this.issues.filter(i => i.severity === 'low').length,
                screenshotsTaken: this.screenshots.length
            },
            issues: this.issues,
            screenshots: this.screenshots,
            recommendations: []
        };
        
        // Generate specific recommendations based on issues found
        const textIssues = this.issues.filter(i => i.type.includes('text'));
        const thumbnailIssues = this.issues.filter(i => i.type.includes('thumbnail'));
        const generationIssues = this.issues.filter(i => i.type.includes('generation'));
        
        if (textIssues.length > 0) {
            report.recommendations.push({
                category: 'Text Visibility',
                priority: 'HIGH',
                description: 'Fix light/faded text issues affecting readability',
                technicalSolution: 'Review CSS opacity, color contrast, and ensure minimum contrast ratio of 4.5:1 for accessibility compliance'
            });
        }
        
        if (thumbnailIssues.length > 0) {
            report.recommendations.push({
                category: 'Image Generation',
                priority: 'HIGH', 
                description: 'Resolve broken thumbnail display and image generation failures',
                technicalSolution: 'Check image generation API endpoints, file storage paths, and implement proper error handling with fallback images'
            });
        }
        
        if (generationIssues.length > 0) {
            report.recommendations.push({
                category: 'Content Generation',
                priority: 'HIGH',
                description: 'Fix content generation pipeline to ensure reliable visual content creation',
                technicalSolution: 'Review ADK agent configuration, API timeouts, and implement retry mechanisms for failed generations'
            });
        }
        
        // Save report
        const reportPath = `selenium-mcp-test-report-${Date.now()}.json`;
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        
        console.log(`📄 Test report saved: ${reportPath}`);
        return report;
    }

    async runComprehensiveTest() {
        console.log('🧪 SELENIUM MCP: ADK 1.8.0 Visual Content Issues Test');
        console.log('==================================================');
        
        try {
            await this.setupSeleniumMCP();
            await this.navigateAndCreateCampaign();
            await this.validateTextVisibility();
            await this.validateThumbnails();
            await this.validateADKFeatures();
            
            const report = await this.generateReport();
            
            console.log('\n📋 TEST SUMMARY:');
            console.log(`🔴 High severity issues: ${report.summary.highSeverityIssues}`);
            console.log(`🟡 Medium severity issues: ${report.summary.mediumSeverityIssues}`);
            console.log(`🟢 Low severity issues: ${report.summary.lowSeverityIssues}`);
            console.log(`📸 Screenshots captured: ${report.summary.screenshotsTaken}`);
            
            if (report.recommendations.length > 0) {
                console.log('\n💡 TOP RECOMMENDATIONS:');
                report.recommendations.forEach((rec, index) => {
                    console.log(`${index + 1}. [${rec.priority}] ${rec.category}: ${rec.description}`);
                });
            }
            
            return report;
            
        } catch (error) {
            console.error('❌ Test execution failed:', error);
            await this.takeScreenshot('error', 'Test execution error');
            throw error;
        } finally {
            if (this.driver) {
                await this.driver.quit();
            }
        }
    }
}

// Execute the test
async function main() {
    const test = new VisualContentIssuesTest();
    return await test.runComprehensiveTest();
}

export { VisualContentIssuesTest, main };

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().then(report => {
        const success = report.summary.highSeverityIssues === 0;
        console.log(`\n🎯 Test Result: ${success ? 'PASS' : 'FAIL'}`);
        process.exit(success ? 0 : 1);
    }).catch(error => {
        console.error('💥 Test failed:', error);
        process.exit(1);
    });
}