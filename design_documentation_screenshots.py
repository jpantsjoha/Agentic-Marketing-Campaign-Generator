#!/usr/bin/env python3
"""
Design Documentation Screenshot Capture
Captures comprehensive screenshots for documenting the visual design language and palette
of the video-venture-launch application.
"""

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class DesignDocumentationCapture:
    def __init__(self):
        self.setup_driver()
        self.base_url = "http://localhost:8096"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.screenshot_dir = "design_documentation_screenshots"
        self.ensure_screenshot_dir()
        
    def setup_driver(self):
        """Setup Chrome driver with optimal settings for design documentation"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--high-dpi-support=1")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        
    def ensure_screenshot_dir(self):
        """Create screenshot directory if it doesn't exist"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            
    def wait_for_page_load(self, timeout=10):
        """Wait for page to fully load"""
        try:
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            time.sleep(2)  # Additional wait for any animations or dynamic content
        except TimeoutException:
            print("Page load timeout - continuing anyway")
            
    def take_screenshot(self, filename, description=""):
        """Take a screenshot with descriptive filename"""
        filepath = os.path.join(self.screenshot_dir, f"{self.timestamp}_{filename}")
        self.driver.save_screenshot(filepath)
        print(f"✅ Screenshot saved: {filepath}")
        if description:
            print(f"   📋 {description}")
        return filepath
        
    def scroll_to_element(self, element):
        """Scroll element into view smoothly"""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(1)
        
    def capture_homepage_design(self):
        """Capture homepage design language and components"""
        print("\n🎨 CAPTURING HOMEPAGE DESIGN LANGUAGE...")
        
        self.driver.get(self.base_url)
        self.wait_for_page_load()
        
        # Full homepage - showing overall design system
        self.take_screenshot(
            "01_homepage_full_design_system.png",
            "Complete homepage showing Apple/Google-quality design system with header, hero, and feature sections"
        )
        
        # Focus on header and navigation design
        header = self.driver.find_element(By.TAG_NAME, "header")
        self.scroll_to_element(header)
        self.take_screenshot(
            "02_header_navigation_design.png",
            "Header navigation design showing typography, spacing, and brand elements"
        )
        
        # Hero section design details
        try:
            hero_section = self.driver.find_element(By.CSS_SELECTOR, "[class*='hero'], .hero, h1")
            self.scroll_to_element(hero_section)
            self.take_screenshot(
                "03_hero_section_design.png",
                "Hero section design showing typography hierarchy, CTA buttons, and color scheme"
            )
        except NoSuchElementException:
            print("Hero section not found - skipping")
            
        # Feature sections showing card design and layout
        try:
            feature_sections = self.driver.find_elements(By.CSS_SELECTOR, "[class*='feature'], [class*='card'], .card")
            if feature_sections:
                self.scroll_to_element(feature_sections[0])
                self.take_screenshot(
                    "04_feature_cards_design.png",
                    "Feature cards showing consistent design language, shadows, and spacing"
                )
        except NoSuchElementException:
            print("Feature sections not found - skipping")
            
    def capture_settings_page_design(self):
        """Capture settings page design including tabs and form elements"""
        print("\n⚙️ CAPTURING SETTINGS PAGE DESIGN...")
        
        settings_url = f"{self.base_url}/settings"
        self.driver.get(settings_url)
        self.wait_for_page_load()
        
        # Full settings page overview
        self.take_screenshot(
            "05_settings_page_full.png",
            "Complete settings page showing tabbed interface and professional layout"
        )
        
        # Focus on tab design
        try:
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "[role='tab'], .tab, [class*='tab']")
            if tabs:
                self.scroll_to_element(tabs[0])
                self.take_screenshot(
                    "06_settings_tabs_design.png",
                    "Tab interface design showing active/inactive states and clean typography"
                )
        except NoSuchElementException:
            print("Tabs not found - capturing general settings area")
            
        # API Configuration tab details
        try:
            api_tab = self.driver.find_element(By.XPATH, "//button[contains(text(), 'API')]")
            api_tab.click()
            time.sleep(1)
            self.take_screenshot(
                "07_api_config_tab_design.png",
                "API Configuration tab showing form design, input fields, and button styling"
            )
        except NoSuchElementException:
            print("API Configuration tab not found")
            
        # Form elements close-up
        try:
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, "input, button, select, textarea")
            if form_elements:
                self.scroll_to_element(form_elements[0])
                self.take_screenshot(
                    "08_form_elements_design.png",
                    "Form elements design showing input styling, focus states, and button hierarchy"
                )
        except NoSuchElementException:
            print("Form elements not found")
            
    def capture_campaign_form_design(self):
        """Capture campaign creation form design"""
        print("\n📝 CAPTURING CAMPAIGN FORM DESIGN...")
        
        # Go back to homepage first
        self.driver.get(self.base_url)
        self.wait_for_page_load()
        
        # Click "Create Your Campaign" button
        try:
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'campaign')]"))
            )
            create_button.click()
            self.wait_for_page_load()
            
            # Full campaign form
            self.take_screenshot(
                "09_campaign_form_full.png",
                "Complete campaign creation form showing clean layout and organization"
            )
            
            # Focus on form sections
            try:
                form_sections = self.driver.find_elements(By.CSS_SELECTOR, "form, .form, [class*='form']")
                if form_sections:
                    self.scroll_to_element(form_sections[0])
                    self.take_screenshot(
                        "10_campaign_form_sections.png",
                        "Campaign form sections showing input grouping and visual hierarchy"
                    )
            except NoSuchElementException:
                print("Form sections not found")
                
            # Input field styling
            try:
                input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email'], textarea")
                if input_fields:
                    self.scroll_to_element(input_fields[0])
                    self.take_screenshot(
                        "11_input_field_styling.png",
                        "Input field styling showing borders, focus states, and typography"
                    )
            except NoSuchElementException:
                print("Input fields not found")
                
        except TimeoutException:
            print("Create campaign button not found - navigating directly to form")
            # Try direct navigation to campaign form
            campaign_url = f"{self.base_url}/campaign"
            self.driver.get(campaign_url)
            self.wait_for_page_load()
            self.take_screenshot(
                "09_campaign_form_direct.png",
                "Campaign form accessed directly"
            )
            
    def capture_color_palette_analysis(self):
        """Capture different sections to analyze color palette consistency"""
        print("\n🎨 CAPTURING COLOR PALETTE ANALYSIS...")
        
        # Navigate through different pages to capture color consistency
        pages = [
            ("homepage", self.base_url),
            ("settings", f"{self.base_url}/settings"),
            ("ideation", f"{self.base_url}/ideation"),
            ("scheduling", f"{self.base_url}/scheduling")
        ]
        
        for page_name, url in pages:
            try:
                self.driver.get(url)
                self.wait_for_page_load()
                self.take_screenshot(
                    f"12_color_palette_{page_name}.png",
                    f"Color palette consistency on {page_name} page - primary blue (#4F46E5), backgrounds, and text colors"
                )
            except Exception as e:
                print(f"Could not capture {page_name}: {e}")
                
    def capture_design_system_elements(self):
        """Capture specific design system components"""
        print("\n🔧 CAPTURING DESIGN SYSTEM ELEMENTS...")
        
        # Go to homepage for component examples
        self.driver.get(self.base_url)
        self.wait_for_page_load()
        
        # Button variations
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            if buttons:
                # Focus on first few buttons to show variations
                for i, button in enumerate(buttons[:3]):
                    self.scroll_to_element(button)
                    self.take_screenshot(
                        f"13_button_variation_{i+1}.png",
                        f"Button design variation {i+1} showing styling and hierarchy"
                    )
        except Exception as e:
            print(f"Could not capture button variations: {e}")
            
        # Typography hierarchy
        try:
            headings = self.driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4, h5, h6")
            if headings:
                self.scroll_to_element(headings[0])
                self.take_screenshot(
                    "14_typography_hierarchy.png",
                    "Typography hierarchy showing font sizes, weights, and spacing"
                )
        except Exception as e:
            print(f"Could not capture typography: {e}")
            
        # Card components
        try:
            cards = self.driver.find_elements(By.CSS_SELECTOR, "[class*='card'], .card, [class*='feature']")
            if cards:
                self.scroll_to_element(cards[0])
                self.take_screenshot(
                    "15_card_components.png",
                    "Card component design showing shadows, borders, and content layout"
                )
        except Exception as e:
            print(f"Could not capture card components: {e}")
            
    def capture_responsive_design(self):
        """Capture responsive design at different viewport sizes"""
        print("\n📱 CAPTURING RESPONSIVE DESIGN...")
        
        viewports = [
            ("desktop", 1920, 1080),
            ("tablet", 1024, 768),
            ("mobile", 375, 667)
        ]
        
        for device_name, width, height in viewports:
            self.driver.set_window_size(width, height)
            time.sleep(1)
            
            self.driver.get(self.base_url)
            self.wait_for_page_load()
            
            self.take_screenshot(
                f"16_responsive_{device_name}_{width}x{height}.png",
                f"Responsive design on {device_name} ({width}x{height}) showing layout adaptation"
            )
            
        # Reset to desktop size
        self.driver.maximize_window()
        
    def generate_summary_report(self):
        """Generate a summary of captured screenshots"""
        print("\n📋 GENERATING DESIGN DOCUMENTATION SUMMARY...")
        
        summary_file = os.path.join(self.screenshot_dir, f"{self.timestamp}_design_documentation_summary.md")
        
        with open(summary_file, 'w') as f:
            f.write(f"# Design Documentation Screenshots - {self.timestamp}\n\n")
            f.write("## Visual Design Language Documentation\n\n")
            f.write("This collection of screenshots documents the Apple/Google-quality design system implemented in the video-venture-launch application.\n\n")
            
            f.write("### Design System Elements Captured:\n\n")
            f.write("1. **Homepage Design Language** - Overall visual hierarchy and brand identity\n")
            f.write("2. **Settings Page Design** - Professional tabbed interface and form styling\n")
            f.write("3. **Campaign Form Design** - Clean form layout and input styling\n")
            f.write("4. **Color Palette Analysis** - Consistent use of primary blue (#4F46E5) and supporting colors\n")
            f.write("5. **Design System Components** - Buttons, typography, cards, and interactive elements\n")
            f.write("6. **Responsive Design** - Layout adaptation across different screen sizes\n\n")
            
            f.write("### Key Design Principles Documented:\n\n")
            f.write("- **Professional Typography Hierarchy** - Clean, readable fonts with proper scaling\n")
            f.write("- **Consistent Color Palette** - Primary blue accents with neutral backgrounds\n")
            f.write("- **Thoughtful Spacing** - Generous whitespace and logical content grouping\n")
            f.write("- **Interactive Element Design** - Clear button hierarchy and focus states\n")
            f.write("- **Card-Based Layout** - Consistent shadows and borders for content organization\n")
            f.write("- **Responsive Grid System** - Adaptive layout for multiple screen sizes\n\n")
            
            f.write(f"All screenshots saved in: `{self.screenshot_dir}/`\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            
        print(f"✅ Summary report saved: {summary_file}")
        
    def run_complete_capture(self):
        """Run the complete design documentation capture process"""
        print("🚀 STARTING DESIGN DOCUMENTATION SCREENSHOT CAPTURE")
        print(f"📁 Screenshots will be saved to: {self.screenshot_dir}")
        print(f"🕒 Timestamp: {self.timestamp}")
        
        try:
            # Main capture sequence
            self.capture_homepage_design()
            self.capture_settings_page_design()
            self.capture_campaign_form_design()
            self.capture_color_palette_analysis()
            self.capture_design_system_elements()
            self.capture_responsive_design()
            
            # Generate summary
            self.generate_summary_report()
            
            print("\n✅ DESIGN DOCUMENTATION CAPTURE COMPLETED SUCCESSFULLY!")
            print(f"📂 Check the '{self.screenshot_dir}' directory for all screenshots and summary report.")
            
        except Exception as e:
            print(f"\n❌ Error during capture: {e}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    capturer = DesignDocumentationCapture()
    capturer.run_complete_capture()