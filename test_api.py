#!/usr/bin/env python3
"""
Test script for PatentScope API
Can be used locally or against Railway deployment
"""

import requests
import time
import json
import sys

def test_api(base_url):
    """Test the PatentScope API"""
    print("=" * 70)
    print(f"  Testing PatentScope API: {base_url}")
    print("=" * 70)

    try:
        # 1. Health check
        print("\n1️⃣  Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    try:
        # 2. API info
        print("\n2️⃣  Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        data = response.json()
        print(f"   Message: {data['message']}")
        print(f"   Version: {data['version']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    try:
        # 3. Start search
        print("\n3️⃣  Starting patent search...")
        search_data = {
            "term": "aspirin",
            "limit": 5,
            "countries": ["US"],
            "get_details": False
        }

        print(f"   Search parameters: {json.dumps(search_data, indent=2)}")
        response = requests.post(f"{base_url}/search", json=search_data, timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        result = response.json()
        print(f"   Task ID: {result['task_id']}")
        print(f"   Status: {result['status']}")

        task_id = result['task_id']
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # 4. Poll for results
    print("\n4️⃣  Checking search status...")
    print("   (This may take 30-60 seconds...)")
    max_attempts = 60  # 5 minutes max
    attempt = 0

    while attempt < max_attempts:
        try:
            response = requests.get(f"{base_url}/status/{task_id}", timeout=10)
            data = response.json()

            status_msg = f"   Attempt {attempt + 1}/60: Status = {data['status']}"
            if data.get('progress'):
                status_msg += f" | {data['progress']}"
            print(status_msg)

            if data["status"] == "completed":
                print("\n   ✅ Search completed!")
                print(f"   Total patents found: {data['result']['total_patents']}")

                stats = data['result']['statistics']
                print(f"\n   📊 Statistics:")
                print(f"   - Countries: {stats['por_pais']}")
                print(f"   - Years: {stats['por_ano']}")
                print(f"   - Unique applicants: {len(stats['top_applicants'])}")
                print(f"   - Unique inventors: {len(stats['top_inventors'])}")

                if data['result']['patents']:
                    print(f"\n   📄 First patent:")
                    patent = data['result']['patents'][0]
                    print(f"   - Number: {patent.get('publicationNumber', 'N/A')}")
                    print(f"   - Title: {patent.get('title', 'N/A')[:70]}...")
                    print(f"   - Date: {patent.get('publicationDate', 'N/A')}")
                    print(f"   - Applicants: {', '.join(patent.get('applicants', ['N/A'])[:2])}")

                break
            elif data["status"] == "failed":
                print(f"\n   ❌ Search failed!")
                print(f"   Error: {data.get('error', 'Unknown error')}")
                return False

            attempt += 1
            time.sleep(5)

        except Exception as e:
            print(f"   ⚠️  Error checking status: {e}")
            attempt += 1
            time.sleep(5)

    if attempt >= max_attempts:
        print("\n   ⚠️  Timeout waiting for results (exceeded 5 minutes)")
        return False

    # 5. List all tasks
    try:
        print("\n5️⃣  Listing all tasks...")
        response = requests.get(f"{base_url}/tasks", timeout=10)
        tasks_data = response.json()
        print(f"   ✅ Total tasks: {tasks_data['total']}")
        for task in tasks_data['tasks'][:3]:  # Show first 3
            print(f"   - {task['task_id'][:8]}... | {task['status']} | {task['created_at']}")
    except Exception as e:
        print(f"   ⚠️  Error listing tasks: {e}")

    print("\n" + "=" * 70)
    print("  ✅ ALL TESTS PASSED!")
    print("=" * 70)
    print(f"\n  🌐 Interactive API docs available at:")
    print(f"     {base_url}/docs (Swagger UI)")
    print(f"     {base_url}/redoc (ReDoc)")
    print("=" * 70)

    return True


def main():
    """Main function"""
    # Default to localhost
    default_url = "http://localhost:8000"

    # Check if URL provided as argument
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        print(f"\n💡 Usage: python test_api.py [API_URL]")
        print(f"   Example: python test_api.py https://your-app.railway.app")
        print(f"\n   Using default: {default_url}")
        print(f"   (Start local server with: uvicorn api:app --reload)\n")
        base_url = default_url

    success = test_api(base_url)

    if not success:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
