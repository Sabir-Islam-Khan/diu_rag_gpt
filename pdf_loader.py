import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import requests
from urllib.parse import urlparse
import time
from bs4 import BeautifulSoup
from docx import Document

# Get the current script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(SCRIPT_DIR, "documents")

def setup_chrome_options():
    """Set up Chrome options for headless browsing"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    return chrome_options

def url_to_docx(urls):
    """
    Extract text content from multiple URLs using Selenium and BeautifulSoup and save as .docx files.
    
    Args:
        urls (list): List of URLs to extract text from
    
    Returns:
        list: List of tuples containing (url, output_path, success_status, error_message)
    """
    # Create documents directory if it doesn't exist
    if not os.path.exists(DOCUMENTS_DIR):
        os.makedirs(DOCUMENTS_DIR)
    
    results = []
    chrome_options = setup_chrome_options()
    
    # Initialize the browser
    driver = webdriver.Chrome(options=chrome_options)
    
    for url in urls:
        try:
            # Check if URL is valid
            response = requests.get(url)
            response.raise_for_status()
            
            # Generate short filename
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.split('.')[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}.docx"
            output_path = os.path.join(DOCUMENTS_DIR, filename)
            
            # Load the page
            driver.get(url)
            
            # Wait for page to load (adjust time if needed)
            time.sleep(5)
            
            # Extract text content using BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Save the text content to a .docx file
            doc = Document()
            doc.add_paragraph(text_content)
            doc.save(output_path)
            
            results.append((url, output_path, True, None))
            print(f"Successfully extracted text from {url} to {output_path}")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch URL: {str(e)}"
            results.append((url, None, False, error_msg))
            print(error_msg)
            
        except Exception as e:
            error_msg = f"Error extracting text from {url}: {str(e)}"
            results.append((url, None, False, error_msg))
            print(error_msg)
    
    # Clean up
    driver.quit()
    return results

def main():
    urls = [
        "https://daffodilvarsity.edu.bd/faculty/fsit",
        "https://daffodilvarsity.edu.bd/department/cse",
        "https://daffodilvarsity.edu.bd/dept/cse/scholarship/diu-scholarship"
    ]
    
    print(f"Text content will be saved in: {DOCUMENTS_DIR}")
    results = url_to_docx(urls)
    
    # Print summary
    print("\nExtraction Summary:")
    print("-" * 50)
    for url, path, success, error in results:
        if success:
            print(f"✓ {url} -> {path}")
        else:
            print(f"✗ {url}: {error}")

if __name__ == "__main__":
    main()