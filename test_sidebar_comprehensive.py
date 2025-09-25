#!/usr/bin/env python3
"""
Comprehensive Sidebar Testing Script
Tests the improved sidebar across different pages to verify consistency and functionality
"""

import requests
import time
import json
from urllib.parse import urljoin

class SidebarTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            "login_test": None,
            "page_loads": {},
            "sidebar_consistency": {},
            "navigation_functionality": {},
            "response_times": {},
            "errors": [],
            "warnings": []
        }
    
    def test_login(self):
        """Test login functionality"""
        print("🔐 Testing login functionality...")
        try:
            # Get login page
            login_url = urljoin(self.base_url, "/auth/login")
            response = self.session.get(login_url)
            
            if response.status_code == 200:
                print("✅ Login page loads successfully")
                
                # Test with default credentials
                login_data = {
                    'email': 'dev.admin@example.com',
                    'password': 'devpass123',
                    'csrf_token': self._extract_csrf_token(response.text)
                }
                
                # Attempt login
                login_response = self.session.post(login_url, data=login_data)
                
                if login_response.status_code in [200, 302]:
                    print("✅ Login successful")
                    self.test_results["login_test"] = "SUCCESS"
                    return True
                else:
                    print(f"❌ Login failed with status: {login_response.status_code}")
                    self.test_results["login_test"] = "FAILED"
                    return False
            else:
                print(f"❌ Login page failed to load: {response.status_code}")
                self.test_results["login_test"] = "PAGE_LOAD_FAILED"
                return False
                
        except Exception as e:
            print(f"❌ Login test error: {str(e)}")
            self.test_results["login_test"] = f"ERROR: {str(e)}"
            self.test_results["errors"].append(f"Login test error: {str(e)}")
            return False
    
    def _extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML (simplified)"""
        # This is a basic implementation - in a real test you'd use BeautifulSoup
        import re
        token_match = re.search(r'name="csrf_token"[^>]+value="([^"]+)"', html_content)
        return token_match.group(1) if token_match else ""
    
    def test_page_loads(self):
        """Test loading of key pages"""
        print("\n📄 Testing page loads...")
        
        test_pages = [
            ("/", "Home Page"),
            ("/dashboard", "Dashboard"),
            ("/ogrenci_yonetimi/liste", "Student Management"),
            ("/ilk_kayit_formu/kayit_formu", "Registration Form"),
            ("/gorusme_defteri/", "Meeting Log"),
            ("/etkinlik_kayit/", "Event Registration"),
            ("/ders_konu_yonetimi/lista", "Subject Management"),
            ("/anket_yonetimi/", "Survey Management"),
            ("/rapor_yonetimi/rapor_yonetimi_index", "Report Management"),
            ("/parametre_yonetimi/", "Parameter Management"),
            ("/yapay_zeka_asistan/", "AI Assistant")
        ]
        
        for path, page_name in test_pages:
            try:
                start_time = time.time()
                url = urljoin(self.base_url, path)
                response = self.session.get(url, timeout=10)
                response_time = time.time() - start_time
                
                self.test_results["response_times"][page_name] = response_time
                
                if response.status_code == 200:
                    print(f"✅ {page_name}: Loaded successfully ({response_time:.2f}s)")
                    self.test_results["page_loads"][page_name] = "SUCCESS"
                    self._analyze_sidebar_in_page(response.text, page_name)
                elif response.status_code == 302:
                    print(f"⚠️  {page_name}: Redirected (might need login)")
                    self.test_results["page_loads"][page_name] = "REDIRECT"
                else:
                    print(f"❌ {page_name}: Failed to load ({response.status_code})")
                    self.test_results["page_loads"][page_name] = f"FAILED_{response.status_code}"
                    
            except Exception as e:
                print(f"❌ {page_name}: Error loading - {str(e)}")
                self.test_results["page_loads"][page_name] = f"ERROR: {str(e)}"
                self.test_results["errors"].append(f"{page_name} load error: {str(e)}")
    
    def _analyze_sidebar_in_page(self, html_content, page_name):
        """Analyze sidebar presence and consistency in a page"""
        sidebar_checks = {
            "sidebar_present": "sidebar" in html_content,
            "nav_links_present": "sidebar-nav-link" in html_content,
            "modern_styling": "Inter" in html_content,
            "responsive_classes": "d-md-none" in html_content,
            "toggle_functionality": "sidebar-toggle" in html_content,
            "student_tabs": "student-tabs-container" in html_content
        }
        
        self.test_results["sidebar_consistency"][page_name] = sidebar_checks
        
        # Check for specific styling elements
        modern_elements = [
            "sidebar-nav-icon",
            "sidebar-nav-text", 
            "modern-welcome",
            "student-info-header"
        ]
        
        modern_count = sum(1 for element in modern_elements if element in html_content)
        if modern_count >= 3:
            print(f"✅ {page_name}: Modern styling elements present")
        else:
            print(f"⚠️  {page_name}: Limited modern styling elements ({modern_count}/4)")
            self.test_results["warnings"].append(f"{page_name}: Limited modern styling")
    
    def test_navigation_functionality(self):
        """Test navigation link functionality"""
        print("\n🔗 Testing navigation functionality...")
        
        # Test key navigation endpoints
        nav_links = [
            ("/dashboard", "Dashboard"),
            ("/ogrenci_yonetimi/liste", "Student Management"),
            ("/ilk_kayit_formu/kayit_formu", "Registration Form")
        ]
        
        for path, link_name in nav_links:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.get(url, timeout=5)
                
                if response.status_code in [200, 302]:
                    print(f"✅ {link_name}: Navigation working")
                    self.test_results["navigation_functionality"][link_name] = "SUCCESS"
                else:
                    print(f"❌ {link_name}: Navigation failed ({response.status_code})")
                    self.test_results["navigation_functionality"][link_name] = f"FAILED_{response.status_code}"
                    
            except Exception as e:
                print(f"❌ {link_name}: Navigation error - {str(e)}")
                self.test_results["navigation_functionality"][link_name] = f"ERROR: {str(e)}"
    
    def analyze_performance(self):
        """Analyze performance metrics"""
        print("\n⚡ Analyzing performance...")
        
        response_times = self.test_results["response_times"]
        if response_times:
            avg_response = sum(response_times.values()) / len(response_times)
            max_response = max(response_times.values())
            
            print(f"📊 Average response time: {avg_response:.2f}s")
            print(f"📊 Maximum response time: {max_response:.2f}s")
            
            if avg_response < 2.0:
                print("✅ Performance: Good")
            elif avg_response < 5.0:
                print("⚠️  Performance: Acceptable")
            else:
                print("❌ Performance: Needs improvement")
                self.test_results["warnings"].append("Slow response times detected")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📋 COMPREHENSIVE SIDEBAR TEST REPORT")
        print("=" * 50)
        
        # Login Status
        print(f"🔐 Login Test: {self.test_results['login_test']}")
        
        # Page Load Summary
        successful_loads = sum(1 for status in self.test_results["page_loads"].values() if status == "SUCCESS")
        total_pages = len(self.test_results["page_loads"])
        print(f"📄 Page Loads: {successful_loads}/{total_pages} successful")
        
        # Navigation Summary
        successful_nav = sum(1 for status in self.test_results["navigation_functionality"].values() if status == "SUCCESS")
        total_nav = len(self.test_results["navigation_functionality"])
        print(f"🔗 Navigation: {successful_nav}/{total_nav} working")
        
        # Sidebar Consistency Analysis
        print("\n🎨 SIDEBAR CONSISTENCY ANALYSIS:")
        sidebar_scores = {}
        for page, checks in self.test_results["sidebar_consistency"].items():
            score = sum(checks.values()) / len(checks) * 100
            sidebar_scores[page] = score
            print(f"  {page}: {score:.1f}% consistency")
        
        if sidebar_scores:
            avg_consistency = sum(sidebar_scores.values()) / len(sidebar_scores)
            print(f"\n📊 Average Sidebar Consistency: {avg_consistency:.1f}%")
            
            if avg_consistency >= 90:
                print("✅ Excellent sidebar consistency")
            elif avg_consistency >= 75:
                print("✅ Good sidebar consistency")
            elif avg_consistency >= 60:
                print("⚠️  Acceptable sidebar consistency")
            else:
                print("❌ Poor sidebar consistency - needs attention")
        
        # Issues Summary
        if self.test_results["errors"]:
            print(f"\n❌ ERRORS FOUND ({len(self.test_results['errors'])}):")
            for error in self.test_results["errors"]:
                print(f"  • {error}")
        
        if self.test_results["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.test_results['warnings'])}):")
            for warning in self.test_results["warnings"]:
                print(f"  • {warning}")
        
        if not self.test_results["errors"] and not self.test_results["warnings"]:
            print("\n✅ NO ISSUES FOUND - Sidebar implementation looks excellent!")
        
        return self.test_results
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Sidebar Testing...")
        print("=" * 50)
        
        # Test login first
        login_success = self.test_login()
        
        # Test page loads (works better after login)
        self.test_page_loads()
        
        # Test navigation functionality  
        self.test_navigation_functionality()
        
        # Analyze performance
        self.analyze_performance()
        
        # Generate comprehensive report
        return self.generate_report()

if __name__ == "__main__":
    tester = SidebarTester()
    results = tester.run_comprehensive_test()
    
    # Save detailed results to file
    with open("sidebar_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to sidebar_test_results.json")