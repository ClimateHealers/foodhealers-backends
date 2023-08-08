from .models import *
from app.authentication import create_access_token, create_refresh_token 

import os
import requests
from bs4 import BeautifulSoup
import urllib
import re
import json
import csv

def getAccessToken(id):
    user = Volunteer.objects.get(id=id)
    accessToken = create_access_token(user.id)
    refreshToken = create_refresh_token(user.id)
    print('Token {token}'.format(token=str(accessToken)))

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

def extract_recipe_data(url):
    try:
        # Send an HTTP GET request to the website and get its HTML content
        response = requests.get(url)
        if response.status_code != 200:
            return print("Failed to fetch the webpage.")
            
        html_content = response.text
        # Parse the HTML using BeautifulSoup to extract image URLs
        soup = BeautifulSoup(html_content, "html.parser")
        script_tags = soup.find_all('script')            
            
        for script in script_tags:
            script_content = script.string

            # Check if the script contains the "@graph" keyword
            if script_content and '"@graph"' in script_content:
                # Extract the content within the <script> tag and load it as a JSON object
                data = json.loads(script_content)

                # Now, we can access the "@graph" data as a dictionary
                if '@graph' in data:
                    graph_data = data['@graph'][1]
                    credits_source_data = data['@graph'][0]

                    try:
                        recipe_credits = credits_source_data['name']
                    except:
                        recipe_credits = 'Credits not Available'

                    try:
                        recipe_source = credits_source_data['url']
                    except:
                        recipe_source = 'Source not Available'

                    # print(' Name ')
                    try:
                        recipe_name = graph_data['name']
                    except:
                        recipe_name = 'Name not Available'

                    # print(' Ingrediants ')
                    try:
                        ingredient_list = graph_data['recipeIngredient']
                    except:
                        ingredient_list = ['Ingrediants Not Available']

                    # print(' Instructions ')  
                    try: 
                        instruction_list =  graph_data['recipeInstructions']                
                    except:
                        instruction_list = ['Instructions Not Available']

                    # print(' Category ')  
                    try:
                        category_list = graph_data['recipeCategory']                  
                    except:
                        category_list = ['Category Not Available']

                    # print(' Image ')
                    try:
                        img_url = graph_data['image']['url'] 

                        # # To Download The Image Un-comment the code below ---------------------->
                        # extension = os.path.splitext(img_url)[1]
                        # if not os.path.exists("images"):
                        #     os.makedirs("images")
                        # # Download each image
                        # filename = os.path.join("images", f"{recipe_name}{extension}")
                        # urllib.request.urlretrieve(img_url, filename)
                    except:
                        img_url = 'Image Not Available'
                    
                    return {"Recipe Name": recipe_name, "Ingredients": ingredient_list, "Instructions": instruction_list, "Category": category_list, "Image":img_url, "Recipe Source": recipe_source, "Recipe Credits":recipe_credits }
    except Exception as e:
        print(f"An error occurred: {str(e)}")

#   <-------------------------------------------------------------- End of PCRM Website Recipe Extraction -------------------------------------------------------------->