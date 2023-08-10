from .models import Volunteer
from app.authentication import create_access_token, create_refresh_token 

import os
import requests
from bs4 import BeautifulSoup
import urllib
import re
import json
import csv

def get_access_token(id):
    user = Volunteer.objects.get(id=id)
    volunteer_access_token = create_access_token(user.id)
    print('Token {token}'.format(token=str(volunteer_access_token)))

#   <-------------------------------------------------------------- From PCRM Website -------------------------------------------------------------->
def extract_recipe_page(url):
    try:
        final_recipe_data = []
        for num in range(0,25):
            recipe_data = extract_recipe_lists(f'{url}recipes?page={num}')
            final_recipe_data += recipe_data

        with open('recipeData.csv', 'w', newline='') as file:
            fieldnames = ["Recipe Name", "Ingredients", "Instructions", "Category", "Image", "Recipe Source", "Recipe Credits"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for  row in final_recipe_data:
                try:
                    writer.writerow(row)
                except UnicodeEncodeError:
                    print("UNICODE ERROR")

    except Exception as e:
        print(f"An error occurred in Writing CSV: {str(e)}")

def extract_recipe_lists(url):
    try:
        # Send an HTTP GET request to the website and get its HTML content
        response = requests.get(url)
        if response.status_code != 200:
            return print("Failed to fetch the webpage.")
            
        html_content = response.text
        # Parse the HTML using BeautifulSoup to extract image URLs
        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_class = soup.find_all('a', class_='f-teaser-title f-teaser-title--horizontal teaser__title')

        csv_rows = []
        # Now you can loop through the elements or perform any other operations as needed
        for element in elements_with_class:            
            # Get the URL, using element['href'] for anchor tags
            recipe_url = "https://www.pcrm.org"+element['href']
            csv_rows.append(extract_recipe_data(recipe_url))

        return csv_rows
            
    except Exception as e:
        print(f"An error occurred (extract_recipe_lists): {str(e)}")
        
# ------------------------------------------------------------------ Refactored Code -----------------------------------------------------------------------------------
def extract_json_data(script_tags):
    for script in script_tags:
        script_content = script.string
        if script_content and '"@graph"' in script_content:
            return json.loads(script_content)
    return None

def get_value_or_default(dictionary, key, default):
    try:
        return dictionary[key]
    except Exception:
        return default

def extract_recipe_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch the webpage."

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        script_tags = soup.find_all('script')

        data = extract_json_data(script_tags)
        graph_keyword = '@graph'
        if data and graph_keyword in data:
            graph_data = data[graph_keyword][1]
            credits_source_data = data[graph_keyword][0]

            recipe_credits = get_value_or_default(credits_source_data, 'name', 'Credits not Available')
            recipe_source = get_value_or_default(credits_source_data, 'url', 'Source not Available')
            recipe_name = get_value_or_default(graph_data, 'name', 'Name not Available')
            ingredient_list = get_value_or_default(graph_data, 'recipeIngredient', ['Ingrediants Not Available'])
            instruction_list = get_value_or_default(graph_data, 'recipeInstructions', ['Instructions Not Available'])
            category_list = get_value_or_default(graph_data, 'recipeCategory', ['Category Not Available'])
            img_url = get_value_or_default(graph_data, 'image', {}).get('url', 'Image Not Available')

            return {
                "Recipe Name": recipe_name,
                "Ingredients": ingredient_list,
                "Instructions": instruction_list,
                "Category": category_list,
                "Image": img_url,
                "Recipe Source": recipe_source,
                "Recipe Credits": recipe_credits
            }
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
#   <-------------------------------------------------------------- End of PCRM Website Recipe Extraction -------------------------------------------------------------->