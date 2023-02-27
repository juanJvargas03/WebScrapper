import os
import requests
from easynmt import EasyNMT
from lxml import html
import time

dir_path = './ClassCentral-Hindi/www.classcentral.com'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

nmt = EasyNMT('opus-mt')
batch_size = 10 

with open('XPath.txt', 'r') as file:
    xpath_expressions = file.read().splitlines()


for subdir, dirs, files in os.walk(dir_path):
    for file in files:
        file_path = os.path.join(subdir, file)
        if file.endswith(".html"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    contents = f.read()
                    soup = html.fromstring(contents)
                    texts_to_translate = [] 
                    replacements = {}

                    for xpath_expression in xpath_expressions:
                        matches = soup.xpath(xpath_expression)
                        for match in matches:
                            if match.strip() != "":
                                texts_to_translate.append(match.strip())

                    texts_to_translate = [text for text in texts_to_translate if text.strip()]

                    
                    if texts_to_translate:
                        for i in range(0, len(texts_to_translate), batch_size):
                            batch = texts_to_translate[i:i+batch_size]
                            translations = nmt.translate(batch, source_lang='en', target_lang='hi')
                            for j, translation in enumerate(translations):
                                original_text = batch[j]
                                if original_text not in replacements:
                                    replacements[original_text] = translation

                        
                        for original_text, translation in replacements.items():
                            contents = contents.replace(original_text, translation)

                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(contents)

            except (UnicodeDecodeError, ValueError):
                print(f"Error: File {file_path} cannot be decoded with UTF-8 encoding")
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
            except Exception as e:
                print(match)
                print(f"Translation failed. Reason: {str(e)}")
