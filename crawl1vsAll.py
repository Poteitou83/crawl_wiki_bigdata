import os
import csv
from crawlbase import CrawlingAPI
from bs4 import BeautifulSoup

def crawl(page_url, api_token):
    # Initialize the CrawlingAPI object with your token
    api = CrawlingAPI({'token': api_token})

    # Get the page content
    response = api.get(page_url)

    # Check if the request was successful
    if response['status_code'] == 200:
        # Scraped data
        return scrape_data(response)
    else:
        print(f"Error: {response}")
        return None

def scrape_data(response):
    try:
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response['body'], 'html.parser')

        # Extract the title of the Wikipedia page
        title = soup.find('h1', id='firstHeading').get_text(strip=True)

        # Extract the main content of the Wikipedia page
        content_div = soup.find('div', id='mw-content-text')
        elements = content_div.find_all(['p', 'h2', 'h3']) if content_div else []
        content = []

        for element in elements:
            # Handle headings (h2 and h3)
            if element.name == 'h2':
                heading_text = element.get_text(strip=True)
                content.append(f"== {heading_text} ==")
            elif element.name == 'h3':
                heading_text = element.get_text(strip=True)
                content.append(f"=== {heading_text} ===")
            # Handle paragraph content
            elif element.name == 'p':
                for sup in element.find_all('sup'):
                    sup.decompose()  # Remove footnotes and references

                processed_paragraph = []
                for sub_element in element.descendants:
                    if sub_element.name == 'a':
                        processed_paragraph.append(f"[{sub_element.get_text(strip=True)}]")
                    elif sub_element.string:
                        processed_paragraph.append(sub_element.string.strip())

                content.append(' '.join(processed_paragraph))

        # Join all content lines with newline
        content = '\n'.join(content)

        return {
            'title': title,
            'content': content
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def save_to_csv(scraped_data_list, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['keyword', 'title', 'content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()

            # Write data rows
            for data in scraped_data_list:
                writer.writerow(data)

        print(f"Data has been saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while saving data to file: {e}")

def crawl_keywords(api_token, keywords_file, output_file):
    # Read keywords from file
    with open(keywords_file, 'r', encoding='utf-8') as file:
        keywords = [line.strip() for line in file.readlines() if line.strip()]

    scraped_data_list = []

    cnt=0
    # Crawl data for each keyword
    for keyword in keywords:
        print(cnt)
        cnt+=1
        page_url = f"https://en.wikipedia.org/wiki/{keyword.replace(' ', '_')}"
        print(f"Crawling data for: {keyword}")
        scraped_data = crawl(page_url, api_token)

        if scraped_data:
            scraped_data['keyword'] = keyword
            scraped_data_list.append(scraped_data)

    # Save all scraped data to a single CSV file
    save_to_csv(scraped_data_list, output_file)

if __name__ == "__main__":
    # Specify your Crawlbase API token
    api_token = 'RX8U0YDT1DNPn70uji3IJQ'

    # File containing keywords (one keyword per line)
    keywords_file = 'keywords.txt'

    # Output CSV file
    output_file = 'scraped_data.csv'

    # Crawl data for all keywords
    crawl_keywords(api_token, keywords_file, output_file)
