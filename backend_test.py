import requests
import sys
import json
from datetime import datetime

class TravelPhraseAPITester:
    def __init__(self, base_url="https://english-skills-5-11.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                self.test_results.append({
                    "test": name,
                    "status": "PASSED",
                    "response_code": response.status_code,
                    "data": response_data
                })
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                self.test_results.append({
                    "test": name,
                    "status": "FAILED",
                    "expected_code": expected_status,
                    "actual_code": response.status_code,
                    "error": response.text[:200]
                })

            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "test": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test /api/ endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        if success and "message" in response:
            print(f"   Message: {response['message']}")
            return True
        return False

    def test_languages_endpoint(self):
        """Test /api/languages endpoint"""
        success, response = self.run_test(
            "Languages Endpoint",
            "GET", 
            "languages",
            200
        )
        if success and "languages" in response:
            languages = response["languages"]
            print(f"   Found {len(languages)} languages")
            
            # Check if we have all 14 expected languages
            expected_count = 14
            if len(languages) == expected_count:
                print(f"   ✅ Correct number of languages ({expected_count})")
            else:
                print(f"   ❌ Expected {expected_count} languages, got {len(languages)}")
                return False
                
            # Check language structure
            required_fields = ["code", "name", "native_name", "flag"]
            for lang in languages[:3]:  # Check first 3 languages
                for field in required_fields:
                    if field not in lang:
                        print(f"   ❌ Missing field '{field}' in language data")
                        return False
            print(f"   ✅ Language structure is correct")
            
            # Print some examples
            for lang in languages[:3]:
                print(f"   - {lang['name']} ({lang['code']}): {lang['native_name']} {lang['flag']}")
            
            return True
        return False

    def test_categories_endpoint(self):
        """Test /api/categories endpoint"""
        success, response = self.run_test(
            "Categories Endpoint",
            "GET",
            "categories", 
            200
        )
        if success and "categories" in response:
            categories = response["categories"]
            print(f"   Found {len(categories)} categories")
            
            # Check if we have all 8 expected categories
            expected_count = 8
            if len(categories) == expected_count:
                print(f"   ✅ Correct number of categories ({expected_count})")
            else:
                print(f"   ❌ Expected {expected_count} categories, got {len(categories)}")
                return False
                
            # Check category structure
            required_fields = ["id", "name", "icon"]
            for cat in categories:
                for field in required_fields:
                    if field not in cat:
                        print(f"   ❌ Missing field '{field}' in category data")
                        return False
            print(f"   ✅ Category structure is correct")
            
            # Print categories
            for cat in categories:
                print(f"   - {cat['name']} (id: {cat['id']}, icon: {cat['icon']})")
            
            return True
        return False

    def test_phrases_endpoint(self):
        """Test /api/phrases endpoint with Japanese"""
        success, response = self.run_test(
            "All Phrases Endpoint (Japanese)",
            "GET",
            "phrases",
            200,
            params={"language_code": "ja"}
        )
        if success and "phrases" in response:
            phrases = response["phrases"]
            print(f"   Found {len(phrases)} phrases")
            
            if len(phrases) > 0:
                # Check phrase structure
                required_fields = ["id", "category", "english", "native", "language_code"]
                phrase = phrases[0]
                for field in required_fields:
                    if field not in phrase:
                        print(f"   ❌ Missing field '{field}' in phrase data")
                        return False
                print(f"   ✅ Phrase structure is correct")
                
                # Print some examples
                for phrase in phrases[:3]:
                    print(f"   - {phrase['english']} → {phrase['native']} ({phrase['category']})")
                
                return True
            else:
                print(f"   ❌ No phrases returned")
                return False
        return False

    def test_category_phrases_endpoint(self):
        """Test /api/phrases/{category_id} endpoint"""
        success, response = self.run_test(
            "Category Phrases Endpoint (Greetings)",
            "GET",
            "phrases/greetings",
            200,
            params={"language_code": "ja"}
        )
        if success and "phrases" in response and "category" in response:
            phrases = response["phrases"]
            category = response["category"]
            print(f"   Found {len(phrases)} phrases in category '{category}'")
            
            if len(phrases) > 0:
                # Check phrase structure
                required_fields = ["id", "english", "native", "language_code"]
                phrase = phrases[0]
                for field in required_fields:
                    if field not in phrase:
                        print(f"   ❌ Missing field '{field}' in phrase data")
                        return False
                print(f"   ✅ Category phrase structure is correct")
                
                # Print some examples
                for phrase in phrases[:3]:
                    print(f"   - {phrase['english']} → {phrase['native']}")
                
                return True
            else:
                print(f"   ❌ No phrases returned for category")
                return False
        return False

    def test_tts_endpoint(self):
        """Test /api/tts/generate endpoint"""
        success, response = self.run_test(
            "TTS Generate Endpoint",
            "POST",
            "tts/generate",
            200,
            data={"text": "Hello", "language_code": "en"}
        )
        if success:
            required_fields = ["audio_base64", "format", "text"]
            for field in required_fields:
                if field not in response:
                    print(f"   ❌ Missing field '{field}' in TTS response")
                    return False
            
            print(f"   ✅ TTS response structure is correct")
            print(f"   - Format: {response['format']}")
            print(f"   - Text: {response['text']}")
            print(f"   - Audio data length: {len(response['audio_base64'])} characters")
            
            return True
        return False

def main():
    print("🚀 Starting Travel Phrase Companion API Tests")
    print("=" * 50)
    
    # Setup
    tester = TravelPhraseAPITester()
    
    # Run all tests
    tests = [
        tester.test_root_endpoint,
        tester.test_languages_endpoint,
        tester.test_categories_endpoint,
        tester.test_phrases_endpoint,
        tester.test_category_phrases_endpoint,
        tester.test_tts_endpoint,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            tester.test_results.append({
                "test": test.__name__,
                "status": "ERROR",
                "error": str(e)
            })
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())