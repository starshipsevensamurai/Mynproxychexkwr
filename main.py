
import requests
import concurrent.futures
import time
import json
import sys
from urllib.parse import urlparse
import socket

class ProxyChecker:
    def __init__(self, timeout=10, max_workers=15):
        """
        Initialize the proxy checker with Replit-optimized settings

        Args:
            timeout (int): Request timeout in seconds (optimized for Replit)
            max_workers (int): Maximum concurrent threads (reduced for Replit)
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.test_urls = [
            'http://httpbin.org/ip',
            'https://api.ipify.org?format=json',
            'http://ip-api.com/json'
        ]
        self.results = []

    def check_proxy(self, proxy):
        """
        Check if a single proxy is working

        Args:
            proxy (str): Proxy in format ip:port or ip:port:username:password

        Returns:
            dict: Proxy test results
        """
        try:
            # Parse proxy string
            proxy_parts = proxy.strip().split(':')
            if len(proxy_parts) < 2:
                return {'proxy': proxy, 'status': 'invalid', 'error': 'Invalid format'}

            ip = proxy_parts[0]
            port = proxy_parts[1]

            # Handle authentication
            auth = None
            if len(proxy_parts) == 4:
                username = proxy_parts[2]
                password = proxy_parts[3]
                auth = (username, password)

            proxy_dict = {
                'http': f'http://{ip}:{port}',
                'https': f'http://{ip}:{port}'
            }

            # Test the proxy
            start_time = time.time()

            try:
                response = requests.get(
                    self.test_urls[0], 
                    proxies=proxy_dict,
                    auth=auth,
                    timeout=self.timeout,
                    headers={'User-Agent': 'ProxyChecker/1.0'}
                )

                response_time = round((time.time() - start_time) * 1000, 2)

                if response.status_code == 200:
                    # Try to get anonymity level
                    anonymity = self.check_anonymity(proxy_dict, auth)

                    return {
                        'proxy': proxy,
                        'status': 'working',
                        'response_time': response_time,
                        'anonymity': anonymity,
                        'country': self.get_country(response.text)
                    }
                else:
                    return {
                        'proxy': proxy,
                        'status': 'failed',
                        'error': f'HTTP {response.status_code}',
                        'response_time': response_time
                    }

            except requests.exceptions.ProxyError:
                return {'proxy': proxy, 'status': 'failed', 'error': 'Proxy connection failed'}
            except requests.exceptions.Timeout:
                return {'proxy': proxy, 'status': 'failed', 'error': 'Timeout'}
            except requests.exceptions.ConnectionError:
                return {'proxy': proxy, 'status': 'failed', 'error': 'Connection error'}

        except Exception as e:
            return {'proxy': proxy, 'status': 'error', 'error': str(e)}

    def check_anonymity(self, proxy_dict, auth=None):
        """Check proxy anonymity level"""
        try:
            response = requests.get(
                'http://httpbin.org/headers',
                proxies=proxy_dict,
                auth=auth,
                timeout=self.timeout
            )

            headers = response.json().get('headers', {})

            # Check for anonymity indicators
            if 'X-Forwarded-For' in headers or 'X-Real-Ip' in headers:
                return 'transparent'
            elif 'Via' in headers or 'X-Forwarded-By' in headers:
                return 'anonymous'
            else:
                return 'elite'

        except:
            return 'unknown'

    def get_country(self, response_text):
        """Extract country from IP response"""
        try:
            if 'country' in response_text.lower():
                return 'Available'
            return 'Unknown'
        except:
            return 'Unknown'

    def check_proxies_from_file(self, filename):
        """
        Check proxies from a file

        Args:
            filename (str): Path to proxy file

        Returns:
            dict: Results summary
        """
        try:
            with open(filename, 'r') as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]

            return self.check_proxy_list(proxies)

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def check_proxy_list(self, proxies):
        """
        Check a list of proxies concurrently

        Args:
            proxies (list): List of proxy strings

        Returns:
            dict: Results summary
        """
        print(f"\nTesting {len(proxies)} proxies with {self.max_workers} workers...")
        print("=" * 60)

        working_proxies = []
        failed_proxies = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {executor.submit(self.check_proxy, proxy): proxy for proxy in proxies}

            for i, future in enumerate(concurrent.futures.as_completed(future_to_proxy), 1):
                result = future.result()

                if result['status'] == 'working':
                    working_proxies.append(result)
                    print(f"[OK] {result['proxy']} - {result['response_time']}ms - {result['anonymity']}")
                else:
                    failed_proxies.append(result)
                    print(f"[FAIL] {result['proxy']} - {result.get('error', 'Failed')}")

                # Show progress
                progress = (i / len(proxies)) * 100
                print(f"Progress: {progress:.1f}% ({i}/{len(proxies)})")

        results_summary = {
            'total_tested': len(proxies),
            'working': len(working_proxies),
            'failed': len(failed_proxies),
            'success_rate': round((len(working_proxies) / len(proxies)) * 100, 2) if proxies else 0,
            'working_proxies': working_proxies,
            'failed_proxies': failed_proxies
        }

        self.results = results_summary
        return results_summary

    def save_results(self, filename, format='txt'):
        """
        Save results to file

        Args:
            filename (str): Output filename
            format (str): Output format ('txt', 'json', 'csv')
        """
        if not self.results:
            print("No results to save.")
            return

        try:
            if format == 'txt':
                with open(filename, 'w') as f:
                    f.write("Working Proxies:\n")
                    f.write("=" * 40 + "\n")
                    for proxy in self.results['working_proxies']:
                        f.write(f"{proxy['proxy']}\n")

            elif format == 'json':
                with open(filename, 'w') as f:
                    json.dump(self.results, f, indent=2)

            elif format == 'csv':
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Proxy', 'Status', 'Response Time', 'Anonymity', 'Error'])

                    for proxy in self.results['working_proxies']:
                        writer.writerow([
                            proxy['proxy'],
                            proxy['status'],
                            proxy.get('response_time', ''),
                            proxy.get('anonymity', ''),
                            ''
                        ])

                    for proxy in self.results['failed_proxies']:
                        writer.writerow([
                            proxy['proxy'],
                            proxy['status'],
                            '',
                            '',
                            proxy.get('error', '')
                        ])

            print(f"Results saved to {filename}")

        except Exception as e:
            print(f"Error saving results: {e}")

def interactive_menu():
    """Interactive menu for easy use in Replit"""
    checker = ProxyChecker()

    while True:
        print("\n" + "=" * 50)
        print("REPLIT PROXY CHECKER")
        print("=" * 50)
        print("1. Test proxies from file")
        print("2. Test single proxy")
        print("3. Create sample proxy file")
        print("4. Show help")
        print("5. Exit")
        print("-" * 50)

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            filename = input("Enter proxy file name (or press Enter for 'proxies.txt'): ").strip()
            if not filename:
                filename = 'proxies.txt'

            results = checker.check_proxies_from_file(filename)
            if results:
                print(f"\nRESULTS SUMMARY:")
                print(f"Total tested: {results['total_tested']}")
                print(f"Working: {results['working']}")
                print(f"Failed: {results['failed']}")
                print(f"Success rate: {results['success_rate']}%")

                if results['working'] > 0:
                    save = input("\nSave working proxies? (y/n): ").lower()
                    if save == 'y':
                        format_choice = input("Format (txt/json/csv): ").lower()
                        if format_choice not in ['txt', 'json', 'csv']:
                            format_choice = 'txt'

                        output_file = f"working_proxies.{format_choice}"
                        checker.save_results(output_file, format_choice)

        elif choice == '2':
            proxy = input("Enter proxy (ip:port or ip:port:user:pass): ").strip()
            if proxy:
                print("\nTesting proxy...")
                result = checker.check_proxy(proxy)

                if result['status'] == 'working':
                    print(f"[SUCCESS] Proxy is working!")
                    print(f"Response time: {result['response_time']}ms")
                    print(f"Anonymity: {result['anonymity']}")
                else:
                    print(f"[FAILED] Proxy failed: {result.get('error', 'Unknown error')}")

        elif choice == '3':
            create_sample_file()

        elif choice == '4':
            show_help()

        elif choice == '5':
            print("Thanks for using Replit Proxy Checker!")
            break

        else:
            print("Invalid choice. Please enter 1-5.")

def create_sample_file():
    """Create a sample proxy file"""
    sample_content = """# Sample proxy file for Replit Proxy Checker
# Format: ip:port or ip:port:username:password
# Lines starting with # are comments

# HTTP Proxies (these are examples, replace with real proxies)
8.8.8.8:8080
1.1.1.1:3128
192.168.1.100:8080

# HTTPS Proxies with authentication
# proxy.example.com:8080:username:password
# 10.0.0.1:3128:myuser:mypass

# Add your real proxies here
"""

    try:
        with open('sample_proxies.txt', 'w') as f:
            f.write(sample_content)
        print("[SUCCESS] Sample proxy file created: sample_proxies.txt")
        print("Edit this file and add your real proxies!")
    except Exception as e:
        print(f"Error creating sample file: {e}")

def show_help():
    """Show help information"""
    help_text = """
HELP - Replit Proxy Checker

PROXY FILE FORMAT:
- One proxy per line
- Format: ip:port or ip:port:username:password  
- Lines starting with # are comments
- Example: 8.8.8.8:8080

FEATURES:
- Multi-threaded testing (15 workers for Replit)
- Anonymity detection (transparent/anonymous/elite)
- Response time measurement
- Multiple export formats (TXT, JSON, CSV)
- Replit-optimized performance

OUTPUT FORMATS:
- TXT: Simple list of working proxies
- JSON: Detailed results with metadata
- CSV: Spreadsheet-compatible format

REPLIT OPTIMIZATIONS:
- Limited to 15 concurrent threads
- 10-second timeout for stability
- Automatic dependency management
- Interactive menu system

TIPS:
- Use reliable proxy sources
- Test small batches first
- Check Replit's bandwidth limits
- Save results before closing
"""
    print(help_text)

def main():
    """Main function that runs when script starts"""
    print("Starting Replit Proxy Checker...")

    # Check if running in Replit
    try:
        import os
        if 'REPL_ID' in os.environ:
            print("[INFO] Replit environment detected!")
        else:
            print("[INFO] Not running in Replit, but should work fine.")
    except:
        pass

    # Start interactive menu
    interactive_menu()

if __name__ == "__main__":
    main()
