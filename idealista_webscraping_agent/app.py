from firecrawl import FirecrawlApp
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import pandas as pd
from datetime import datetime


def scrape_data(url):
    load_dotenv()

    app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
    scraped_data = app.scrape_url(url)

    if 'markdown' in scraped_data:
        return scraped_data['markdown']
    else:
        raise KeyError("The key 'markdown' does not exist in the scraped data.")


def save_raw_data(raw_data, timestamp, output_folder='output'):
    os.makedirs(output_folder, exist_ok=True)
    raw_output_path = os.path.join(output_folder, f'rawData_{timestamp}.md')
    with open(raw_output_path, 'w', encoding='utf-8') as f:
        f.write(raw_data)
    print(f'Raw data saved to {raw_output_path}')


def format_data(data, fields=None):
    load_dotenv()

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    if fields is None:
        fields = ["Adress", "Real Estate Agency", "Price", "Beds", "Baths", "Sqft", "Home Type",
                  "Listing Age", "Picture of the home URL", "Listing URL"]

        system_message = f"""You are an intelligent text extraction and conversion assistent. Your task is to
                        extract structured information from the given text and convert it into a pure JSON format.
                        The JSON should contain only the structure data extracted from the text, with no aditional 
                        commentary, explanations, or extraneous information. You could encounter cases where where you 
                        cant find the data of the yields you have to extract or the data will be in a foreign language.
                        Please process the following text and provide the output in pure JSON format with no words
                        before or after the JSON:"""

        user_message = f"Extract the following information from the provided text:\nPage content:\n\n{data}\n\n:Information: {fields}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        if response and response.choices:
            formatted_data = response.choices[0].message.content.strip()
            print(f"Formatted data received from API: {formatted_data}")

            try:
                parsed_json = json.loads(formatted_data)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                print(f"Formatted data that caused the error:")

            return parsed_json

        else:
            raise ValueError("The OpenAI API response did not contain the expected choices data.")


def save_formatted_data(formatted_data, timestamp, output_folder='output'):

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(f'sorted_data_{timestamp}.json')

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=4)
    print(f'Formatted data saved to {output_path}')

    if isinstance(formatted_data, dict) and len(formatted_data) == 1:
        key = next(iter(formatted_data))
        formatted_data = formatted_data[key]

    df = pd.DataFrame(formatted_data)

    if isinstance(formatted_data, dict):
        formatted_data = [formatted_data]

    df = pd.DataFrame(formatted_data)

    excel_output_path = os.path.join(output_folder, f"sorted_data_{timestamp}.xlsx")
    df.to_excel(excel_output_path, index=False)
    print(f"Formatted data saved to Excel at {excel_output_path}")


if __name__ == "__main__":
    # url = "https://www.idealista.pt/comprar-casas/lisboa/com-preco-max_200000,t2,t3,t4-t5"
    # url = "https://www.zillow.com/CA/San_Francisco/"
    url = "https://www.investing.com/rates-bonds/portugal-10-year-bond-historical-data"
    # print(scrape_data('https://www.idealista.pt/comprar-casas/lisboa/com-preco-max_200000,t2,t3,t4-t5,publicado_ultimas-48-horas,bom-estado/'))

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        raw_data = scrape_data(url)
        print(raw_data)
        save_raw_data(raw_data, timestamp)
        formatted_data = format_data(raw_data)
        save_formatted_data(formatted_data, timestamp)
    except Exception as e:
        print(f'An error as occurred: {e}')
