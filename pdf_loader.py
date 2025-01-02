import os
import aiohttp
import asyncio
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from urllib.parse import urlparse
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

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text(errors='ignore')  # Ignore decoding errors

async def url_to_docx(urls):
    """
    Extract relevant text content from multiple URLs using Selenium and BeautifulSoup and save as .docx files.
    
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
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        
        responses = await asyncio.gather(*tasks)
        
        for url, response in zip(urls, responses):
            try:
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
                
                # Extract relevant text content using BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                main_content = soup.find('main') or soup.find('body')  # Adjust based on the structure of the websites
                if main_content:
                    text_content = main_content.get_text(separator='\n', strip=True)
                else:
                    text_content = soup.get_text(separator='\n', strip=True)
                
                # Clean the text content
                text_content = clean_text(text_content)
                
                # Save the text content to a .docx file
                doc = Document()
                doc.add_paragraph(text_content)
                doc.save(output_path)
                
                results.append((url, output_path, True, None))
                print(f"Successfully extracted text from {url} to {output_path}")
                
            except Exception as e:
                error_msg = f"Error extracting text from {url}: {str(e)}"
                results.append((url, None, False, error_msg))
                print(error_msg)
    
    # Clean up
    driver.quit()
    return results

def clean_text(text):
    """Clean the extracted text by removing unnecessary data"""
    # Add your text cleaning logic here
    # For example, remove navigation menus, advertisements, etc.
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if len(line.strip()) > 0 and 'advertisement' not in line.lower()]
    return '\n'.join(cleaned_lines)

def main():
    urls = [
        "http://admission.daffodilvarsity.edu.bd/#/",
        "http://dspace.daffodilvarsity.edu.bd:8080/",
        "http://erp.daffodilvarsity.edu.bd/#/",
        "http://financialaid.daffodilvarsity.edu.bd/",
        "http://forum.daffodilvarsity.edu.bd/",
        "http://ic.daffodilvarsity.edu.bd",
        "http://pd.daffodilvarsity.edu.bd/support_ticket",
        "http://research.daffodilvarsity.edu.bd",
        "http://vc.daffodilvarsity.edu.bd/",
        "https://admission.daffodilvarsity.edu.bd",
        "https://admission.daffodilvarsity.edu.bd/",
        "https://admission.daffodilvarsity.edu.bd/#/",
        "https://alumni.daffodilvarsity.edu.bd/",
        "https://apfdp.daffodilvarsity.edu.bd/",
        "https://apsp.daffodilvarsity.edu.bd",
        "https://blog.daffodilvarsity.edu.bd",
        "https://career.daffodilvarsity.edu.bd/?app=home",
        "https://cdc.daffodilvarsity.edu.bd",
        "https://certificate.daffodilvarsity.edu.bd/",
        "https://clubs.daffodilvarsity.edu.bd",
        "https://convocation.daffodilvarsity.edu.bd",
        "https://daffodilvarsity.edu.bd/",
        "https://daffodilvarsity.edu.bd/academic/academic-handbook/",
        "https://daffodilvarsity.edu.bd/admission",
        "https://daffodilvarsity.edu.bd/admission-contact",
        "https://daffodilvarsity.edu.bd/admission-eligibility",
        "https://daffodilvarsity.edu.bd/admission-test",
        "https://daffodilvarsity.edu.bd/article/academic-guidelines",
        "https://daffodilvarsity.edu.bd/article/administration-directory",
        "https://daffodilvarsity.edu.bd/article/apps",
        "https://daffodilvarsity.edu.bd/article/associate-deans-heads",
        "https://daffodilvarsity.edu.bd/article/at-a-glance",
        "https://daffodilvarsity.edu.bd/article/bangladesh-corner",
        "https://daffodilvarsity.edu.bd/article/chairman-message",
        "https://daffodilvarsity.edu.bd/article/chancellor-profile",
        "https://daffodilvarsity.edu.bd/article/cm-profile",
        "https://daffodilvarsity.edu.bd/article/contact",
        "https://daffodilvarsity.edu.bd/article/copyright-issue",
        "https://daffodilvarsity.edu.bd/article/corona",
        "https://daffodilvarsity.edu.bd/article/credit-transfer",
        "https://daffodilvarsity.edu.bd/article/daffodil-agro-complex",
        "https://daffodilvarsity.edu.bd/article/deans-heads",
        "https://daffodilvarsity.edu.bd/article/diu-best",
        "https://daffodilvarsity.edu.bd/article/downloads",
        "https://daffodilvarsity.edu.bd/article/erp",
        "https://daffodilvarsity.edu.bd/article/extra-curricular",
        "https://daffodilvarsity.edu.bd/article/faculty",
        "https://daffodilvarsity.edu.bd/article/forms",
        "https://daffodilvarsity.edu.bd/article/green-campus",
        "https://daffodilvarsity.edu.bd/article/guidelines-for-guardians",
        "https://daffodilvarsity.edu.bd/article/gymnasium",
        "https://daffodilvarsity.edu.bd/article/harmony-project",
        "https://daffodilvarsity.edu.bd/article/history",
        "https://daffodilvarsity.edu.bd/article/industrial-linkage",
        "https://daffodilvarsity.edu.bd/article/international-adviser",
        "https://daffodilvarsity.edu.bd/article/life-insurance-for-student-and-guardian",
        "https://daffodilvarsity.edu.bd/article/pc-purchase-schemes",
        "https://daffodilvarsity.edu.bd/article/provc-profile",
        "https://daffodilvarsity.edu.bd/article/research-projects",
        "https://daffodilvarsity.edu.bd/article/security-issues",
        "https://daffodilvarsity.edu.bd/article/semester-schedule",
        "https://daffodilvarsity.edu.bd/article/strategy",
        "https://daffodilvarsity.edu.bd/article/student-activities",
        "https://daffodilvarsity.edu.bd/article/students",
        "https://daffodilvarsity.edu.bd/article/transport",
        "https://daffodilvarsity.edu.bd/article/valued-employers",
        "https://daffodilvarsity.edu.bd/article/vc-message",
        "https://daffodilvarsity.edu.bd/article/visiting-professors",
        "https://daffodilvarsity.edu.bd/bscic",
        "https://daffodilvarsity.edu.bd/committee/academic-council",
        "https://daffodilvarsity.edu.bd/committee/board-of-trustees",
        "https://daffodilvarsity.edu.bd/committee/committees",
        "https://daffodilvarsity.edu.bd/committee/syndicate",
        "https://daffodilvarsity.edu.bd/csr-activities",
        "https://daffodilvarsity.edu.bd/daycare",
        "https://daffodilvarsity.edu.bd/delegates/delegates-abroad",
        "https://daffodilvarsity.edu.bd/department/cis",
        "https://daffodilvarsity.edu.bd/department/cse",
        "https://daffodilvarsity.edu.bd/department/itm",
        "https://daffodilvarsity.edu.bd/department/mct",
        "https://daffodilvarsity.edu.bd/department/swe",
        "https://daffodilvarsity.edu.bd/departments",
        "https://daffodilvarsity.edu.bd/faculty/fsit",
        "https://daffodilvarsity.edu.bd/faculty/sitemap",
        "https://daffodilvarsity.edu.bd/faq",
        "https://daffodilvarsity.edu.bd/flipbook/brochure",
        "https://daffodilvarsity.edu.bd/flipbook/diu-annual-report",
        "https://daffodilvarsity.edu.bd/gallery/mou-2014",
        "https://daffodilvarsity.edu.bd/iip",
        "https://daffodilvarsity.edu.bd/int-scholarship/scholarship-int",
        "https://daffodilvarsity.edu.bd/int-tuition-fees",
        "https://daffodilvarsity.edu.bd/international-conferences",
        "https://daffodilvarsity.edu.bd/international-linkage",
        "https://daffodilvarsity.edu.bd/international/incoming-student-exchange",
        "https://daffodilvarsity.edu.bd/international/international-alumni",
        "https://daffodilvarsity.edu.bd/international/international-contact",
        "https://daffodilvarsity.edu.bd/international/international-event",
        "https://daffodilvarsity.edu.bd/international/policy-for-int-student",
        "https://daffodilvarsity.edu.bd/lab-facilities",
        "https://daffodilvarsity.edu.bd/lecture-series",
        "https://daffodilvarsity.edu.bd/list/international",
        "https://daffodilvarsity.edu.bd/location",
        "https://daffodilvarsity.edu.bd/medical/diu-medical-center",
        "https://daffodilvarsity.edu.bd/mps/members",
        "https://daffodilvarsity.edu.bd/mps/partners",
        "https://daffodilvarsity.edu.bd/noticeboard",
        "https://daffodilvarsity.edu.bd/photos/international/Booklet-for-Int-Students.pdf",
        "https://daffodilvarsity.edu.bd/photos/pdf/Admission-Flow-Chart19.pdf",
        "https://daffodilvarsity.edu.bd/photos/pdf/Report-on-traffic-mgt.pdf",
        "https://daffodilvarsity.edu.bd/photos/pdf/admission-checklist.pdf",
        "https://daffodilvarsity.edu.bd/photos/pdf/payment-guidelines.pdf",
        "https://daffodilvarsity.edu.bd/proctor-office",
        "https://daffodilvarsity.edu.bd/programs",
        "https://daffodilvarsity.edu.bd/prospectus",
        "https://daffodilvarsity.edu.bd/rankings",
        "https://daffodilvarsity.edu.bd/registrar-office",
        "https://daffodilvarsity.edu.bd/registrar-office/academic-calendar",
        "https://daffodilvarsity.edu.bd/safetyandsecurity",
        "https://daffodilvarsity.edu.bd/scholarship",
        "https://daffodilvarsity.edu.bd/sitemap",
        "https://daffodilvarsity.edu.bd/tuition-fee-calculator",
        "https://daffodilvarsity.edu.bd/tuition-fees",
        "https://daffodilvarsity.edu.bd/vip",
        "https://daffodilvarsity.edu.bd/virtual-photo-exhibition",
        "https://daffodilvarsity.edu.bd/virtual-tour",
        "https://dil.daffodilvarsity.edu.bd",
        "https://diujahs.daffodilvarsity.edu.bd",
        "https://diujbe.daffodilvarsity.edu.bd",
        "https://diujhss.daffodilvarsity.edu.bd",
        "https://diujst.daffodilvarsity.edu.bd",
        "https://dsa.daffodilvarsity.edu.bd",
        "https://elearn.daffodilvarsity.edu.bd",
        "https://employability.daffodilvarsity.edu.bd",
        "https://faculty.daffodilvarsity.edu.bd",
        "https://forum.daffodilvarsity.edu.bd/",
        "https://hall.daffodilvarsity.edu.bd/",
        "https://iic.daffodilvarsity.edu.bd/",
        "https://internship.daffodilvarsity.edu.bd",
        "https://iqac.daffodilvarsity.edu.bd",
        "https://it.daffodilvarsity.edu.bd",
        "https://library.daffodilvarsity.edu.bd",
        "https://news.daffodilvarsity.edu.bd",
        "https://newsletter.daffodilvarsity.edu.bd/",
        "https://parents.daffodilvarsity.edu.bd/",
        "https://pd.daffodilvarsity.edu.bd/contact-us",
        "https://sustainability4d.daffodilvarsity.edu.bd",
        "https://www.facebook.com/daffodilvarsity.edu.bd"
    ]
    
    print(f"Text content will be saved in: {DOCUMENTS_DIR}")
    results = asyncio.run(url_to_docx(urls))
    
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