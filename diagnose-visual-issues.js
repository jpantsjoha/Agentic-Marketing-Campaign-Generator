/**
 * Direct Visual Issues Diagnostic
 * Focus on the specific issues:
 * 1. Light/faded text on social posts
 * 2. Broken thumbnails not displaying
 * 3. Content generation issues
 */

import { chromium } from 'playwright';

async function diagnoseVisualIssues() {
    console.log('🔍 DIAGNOSTIC: Visual Content Issues Analysis');
    console.log('===========================================');
    
    const browser = await chromium.launch({ 
        headless: false, 
        slowMo: 500 
    });
    const page = await browser.newContext({ 
        viewport: { width: 1400, height: 900 } 
    }).then(ctx => ctx.newPage());

    const issues = [];
    
    try {
        // Step 1: Navigate to ideation page directly (where issues are visible)
        console.log('📍 Step 1: Navigating to ideation page...');
        await page.goto('http://localhost:8080/ideation');
        await page.waitForLoadState('networkidle');
        
        await page.screenshot({ path: 'diagnostic-01-ideation-page.png', fullPage: true });
        
        // Step 2: Analyze text visibility issues
        console.log('📝 Step 2: Analyzing text visibility...');
        
        const textElements = await page.locator('p, span, div[class*="post"], .post-content, .social-post').all();
        let textIssuesFound = 0;
        
        for (let i = 0; i < textElements.length; i++) {
            const element = textElements[i];
            const text = await element.textContent();
            
            if (text && text.trim().length > 10) {
                const styles = await element.evaluate(el => {
                    const computed = window.getComputedStyle(el);
                    return {
                        opacity: computed.opacity,
                        color: computed.color,
                        backgroundColor: computed.backgroundColor,
                        fontSize: computed.fontSize
                    };
                });
                
                // Check for low opacity
                if (parseFloat(styles.opacity) < 0.8) {
                    textIssuesFound++;
                    issues.push({
                        type: 'TEXT_OPACITY',
                        severity: 'HIGH',
                        description: `Low opacity text (${styles.opacity}): "${text.substring(0, 50)}..."`,
                        styles: styles
                    });
                    console.log(`🟡 Low opacity text found: opacity=${styles.opacity}, text="${text.substring(0, 30)}..."`);
                }
                
                // Check for light gray text
                if (styles.color && styles.color.includes('rgb')) {
                    const matches = styles.color.match(/\d+/g);
                    if (matches && matches.length >= 3) {
                        const [r, g, b] = matches.map(Number);
                        if (r > 180 && g > 180 && b > 180) { // Very light gray
                            textIssuesFound++;
                            issues.push({
                                type: 'TEXT_COLOR_LIGHT',
                                severity: 'HIGH',
                                description: `Light text color (RGB: ${r},${g},${b}): "${text.substring(0, 50)}..."`,
                                styles: styles
                            });
                            console.log(`🟡 Light text color found: RGB(${r},${g},${b}), text="${text.substring(0, 30)}..."`);
                        }
                    }
                }
            }
        }
        
        console.log(`📊 Text Analysis: ${textIssuesFound} visibility issues found`);
        
        // Step 3: Analyze thumbnail/image issues
        console.log('🖼️ Step 3: Analyzing thumbnail issues...');
        
        const images = await page.locator('img').all();
        let thumbnailIssuesFound = 0;
        
        console.log(`Found ${images.length} images to analyze...`);
        
        for (let i = 0; i < images.length; i++) {
            const img = images[i];
            const src = await img.getAttribute('src');
            const alt = await img.getAttribute('alt');
            
            if (src) {
                console.log(`🔍 Image ${i + 1}: ${src.substring(0, 60)}...`);
                
                // Check if image is broken
                const imageStatus = await img.evaluate((el) => {
                    return {
                        naturalWidth: el.naturalWidth,
                        naturalHeight: el.naturalHeight,
                        complete: el.complete,
                        width: el.width,
                        height: el.height
                    };
                });
                
                if (imageStatus.naturalWidth === 0 || imageStatus.naturalHeight === 0) {
                    thumbnailIssuesFound++;
                    issues.push({
                        type: 'BROKEN_THUMBNAIL',
                        severity: 'HIGH',
                        description: `Broken thumbnail: src="${src}", alt="${alt}"`,
                        imageStatus: imageStatus
                    });
                    console.log(`❌ Broken thumbnail: ${src}`);
                } else {
                    console.log(`✅ Working thumbnail: ${imageStatus.naturalWidth}x${imageStatus.naturalHeight}`);
                }
                
                // Check for placeholder or error images
                if (src.includes('placeholder') || src.includes('error') || alt?.includes('error')) {
                    issues.push({
                        type: 'PLACEHOLDER_THUMBNAIL',
                        severity: 'MEDIUM',
                        description: `Placeholder/error image: src="${src}", alt="${alt}"`
                    });
                    console.log(`⚠️ Placeholder image: ${src}`);
                }
            }
        }
        
        console.log(`📊 Thumbnail Analysis: ${thumbnailIssuesFound} broken thumbnails found`);
        
        // Step 4: Check for regenerate/error messages
        console.log('🔄 Step 4: Checking for content generation errors...');
        
        const errorMessages = await page.locator('text=/regenerate|error|failed|could not/i').all();
        const regenerateButtons = await page.locator('button:has-text("Regenerate")').all();
        
        console.log(`Found ${errorMessages.length} error messages and ${regenerateButtons.length} regenerate buttons`);
        
        if (errorMessages.length > 0 || regenerateButtons.length > 0) {
            issues.push({
                type: 'CONTENT_GENERATION_ERRORS',
                severity: 'HIGH',
                description: `Content generation failures: ${errorMessages.length} error messages, ${regenerateButtons.length} regenerate prompts`,
                details: {
                    errorMessages: errorMessages.length,
                    regenerateButtons: regenerateButtons.length
                }
            });
        }
        
        // Step 5: Try generating new content to test current functionality
        console.log('⚡ Step 5: Testing content generation...');
        
        const generateButtons = await page.locator('button:has-text("Generate")').all();
        console.log(`Found ${generateButtons.length} generate buttons`);
        
        if (generateButtons.length > 0) {
            console.log('🔄 Testing content generation...');
            await generateButtons[0].click();
            
            // Wait and check for new content
            await page.waitForTimeout(10000);
            await page.screenshot({ path: 'diagnostic-02-after-generation.png', fullPage: true });
            
            // Check if new content appeared
            const newImages = await page.locator('img').all();
            const newImagesCount = newImages.length;
            
            console.log(`📊 Images after generation: ${newImagesCount} (was ${images.length})`);
            
            if (newImagesCount <= images.length) {
                issues.push({
                    type: 'GENERATION_FAILURE',
                    severity: 'HIGH',
                    description: 'Content generation did not produce new visual content',
                    details: {
                        imagesBefore: images.length,
                        imagesAfter: newImagesCount
                    }
                });
            }
        }
        
        await page.screenshot({ path: 'diagnostic-03-final-state.png', fullPage: true });
        
        // Generate summary report
        const report = {
            timestamp: new Date().toISOString(),
            testType: 'Visual Content Issues Diagnostic',
            summary: {
                totalIssues: issues.length,
                highSeverityIssues: issues.filter(i => i.severity === 'HIGH').length,
                mediumSeverityIssues: issues.filter(i => i.severity === 'MEDIUM').length,
                textVisibilityIssues: issues.filter(i => i.type.includes('TEXT')).length,
                thumbnailIssues: issues.filter(i => i.type.includes('THUMBNAIL')).length,
                generationIssues: issues.filter(i => i.type.includes('GENERATION')).length
            },
            issues: issues,
            recommendations: [
                {
                    category: 'Text Visibility',
                    priority: issues.filter(i => i.type.includes('TEXT')).length > 0 ? 'HIGH' : 'LOW',
                    description: 'Fix text opacity and color contrast issues',
                    solution: 'Review CSS styles, ensure opacity >= 0.8 and contrast ratio >= 4.5:1'
                },
                {
                    category: 'Image Display',
                    priority: issues.filter(i => i.type.includes('THUMBNAIL')).length > 0 ? 'HIGH' : 'LOW',
                    description: 'Fix broken thumbnail display',
                    solution: 'Check image URLs, CORS settings, and implement error handling with fallback images'
                },
                {
                    category: 'Content Generation',
                    priority: issues.filter(i => i.type.includes('GENERATION')).length > 0 ? 'HIGH' : 'LOW',
                    description: 'Improve content generation reliability',
                    solution: 'Review ADK agent configuration, API timeouts, and implement retry mechanisms'
                }
            ]
        };
        
        // Save report
        const reportPath = `visual-issues-diagnostic-report-${Date.now()}.json`;
        await page.evaluate((reportData, path) => {
            // This won't work in browser context, we'll save it on the Node.js side
        }, report, reportPath);
        
        console.log('\n📋 DIAGNOSTIC SUMMARY:');
        console.log('====================');
        console.log(`🔴 High severity issues: ${report.summary.highSeverityIssues}`);
        console.log(`🟡 Medium severity issues: ${report.summary.mediumSeverityIssues}`);
        console.log(`📝 Text visibility issues: ${report.summary.textVisibilityIssues}`);
        console.log(`🖼️ Thumbnail issues: ${report.summary.thumbnailIssues}`);
        console.log(`⚡ Generation issues: ${report.summary.generationIssues}`);
        
        console.log('\n💡 KEY FINDINGS:');
        issues.forEach((issue, index) => {
            console.log(`${index + 1}. [${issue.severity}] ${issue.type}: ${issue.description}`);
        });
        
        console.log('\n🔧 RECOMMENDATIONS:');
        report.recommendations.forEach((rec, index) => {
            if (rec.priority === 'HIGH') {
                console.log(`${index + 1}. [${rec.priority}] ${rec.category}: ${rec.description}`);
                console.log(`   💡 Solution: ${rec.solution}`);
            }
        });
        
        // Save report to file
        const fs = await import('fs');
        fs.default.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log(`\n📄 Detailed report saved: ${reportPath}`);
        
        return report;
        
    } catch (error) {
        console.error('❌ Diagnostic failed:', error);
        await page.screenshot({ path: 'diagnostic-error.png', fullPage: true });
        throw error;
    } finally {
        await browser.close();
    }
}

// Run diagnostic
diagnoseVisualIssues()
    .then(report => {
        const criticalIssues = report.summary.highSeverityIssues;
        console.log(`\n🎯 DIAGNOSTIC RESULT: ${criticalIssues === 0 ? 'PASS' : 'ISSUES FOUND'}`);
        console.log(`Critical issues requiring immediate attention: ${criticalIssues}`);
    })
    .catch(error => {
        console.error('💥 Diagnostic execution failed:', error);
    });