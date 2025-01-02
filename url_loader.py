import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3
import json

def get_all_links(url):
    """
    Extract all links from a given webpage
    
    Parameters:
    url (str): The URL of the webpage to scrape
    
    Returns:
    list: A list of all unique links found on the page
    """
    # Disable SSL verification warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        # Send GET request to the URL
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all <a> tags
        links = set()
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(url, href)
                links.add(absolute_url)
        
        return sorted(list(links))
    
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

def filter_domain_links(links, domain):
    """
    Filter links to only include those from a specific domain
    
    Parameters:
    links (list): List of URLs to filter
    domain (str): Domain to filter by
    
    Returns:
    list: Filtered list of URLs
    """
    return [link for link in links if domain in link]

def save_urls_to_file(urls, filename):
    """
    Save URLs to a text file in array format
    
    Parameters:
    urls (list): List of URLs to save
    filename (str): Name of the file to save to
    """
    try:
        # Save as JSON array
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2)
        print(f"\nSuccessfully saved {len(urls)} URLs to {filename}")
    except Exception as e:
        print(f"Error saving to file: {e}")

# Example usage
if __name__ == "__main__":
    target_url = "https://daffodilvarsity.edu.bd/faculty/fsit"
    domain = "daffodilvarsity.edu.bd"
    output_file = "university_links.txt"
    
    print(f"Fetching links from: {target_url}")
    all_links = get_all_links(target_url)
    
    # Filter links to only include those from the same domain
    domain_links = filter_domain_links(all_links, domain)
    
    print("\nFound links:")
    for idx, link in enumerate(domain_links, 1):
        print(f"{idx}. {link}")
    
    # Save URLs to file
    save_urls_to_file(domain_links, output_file)