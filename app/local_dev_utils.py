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

#   <--------------------------------------------------------------Recipe Extraction From PCRM Website -------------------------------------------------------------->
def pcrm_extract_recipe_page(url):
    try:
        final_recipe_data = []
        for num in range(0,25):
            recipe_data = pcrm_extract_recipe_lists(f'{url}recipes?page={num}')
            final_recipe_data += recipe_data

        with open('pcrmRecipeData.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["Recipe Name", "Ingredients", "Instructions", "Category", "Prepration Time","Image", "Recipe Source", "Recipe Credits"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for  row in final_recipe_data:
                try:
                    writer.writerow(row)
                except UnicodeEncodeError:
                    print("UNICODE ERROR")

    except Exception as e:
        print(f"An error occurred in Writing CSV: {str(e)}")

def pcrm_extract_recipe_lists(url):
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
            csv_rows.append(pcrm_extract_recipe_data(recipe_url))

        return csv_rows
            
    except Exception as e:
        print(f"An error occurred (extract_recipe_lists): {str(e)}")
        
# ------------------------------------------------------------------ Refactored Code -----------------------------------------------------------------------------------
def pcrm_extract_json_data(script_tags):
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

def pcrm_extract_recipe_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch the webpage."

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        script_tags = soup.find_all('script')

        data = pcrm_extract_json_data(script_tags)
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
                "Prepration Time":'Prepration Time Not Available',
                "Image": img_url,
                "Recipe Source": recipe_source,
                "Recipe Credits": recipe_credits
            }
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
#   <-------------------------------------------------------------- End of Recipe Extraction from PCRM Website  -------------------------------------------------------------->


#   <-------------------------------------------------------------- Start Recipe Extraction From ForkOverKnives Website -------------------------------------------------------------->
def fok_extract_recipe_page(url):
    try:
        final_recipe_data = []
        for num in range(1,115):
            recipe_data = fok_extract_recipe_lists(f'{url}recipes/page/{num}/?type=grid')
            final_recipe_data += recipe_data

        with open('forkOverKnivesRecipeData.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["Recipe Name", "Ingredients", "Instructions", "Category", "Prepration Time", "Image", "Recipe Source", "Recipe Credits"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            abc = 0
            for  row in final_recipe_data:
                try:
                    writer.writerow(row)
                except UnicodeEncodeError:
                    abc+=1
                    print("UNICODE ERROR", abc)

    except Exception as e:
        print(f"An error occurred in Writing CSV: {str(e)}")

def fok_extract_recipe_lists(url):
    try:
        # Send an HTTP GET request to the website and get its HTML content
        response = requests.get(url)
        if response.status_code != 200:
            return print("Failed to fetch the webpage.")
            
        html_content = response.text
        # Parse the HTML using BeautifulSoup to extract image URLs
        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_class = soup.find_all('a', {'title': 'See the Recipe'})

        csv_rows = []
        # Now you can loop through the elements or perform any other operations as needed
        for element in elements_with_class:         
            # Get the URL, using element['href'] for anchor tags
            recipe_url = element['href']
            csv_rows.append(fok_extract_recipe_data(recipe_url))

        return csv_rows
            
    except Exception as e:
        print(f"An error occurred (extract_recipe_lists): {str(e)}")
        
def fok_extract_json_data(script_tags):
    for script in script_tags:
        script_content = script.string
        if script_content and '"@context"' in script_content:
            return json.loads(script_content)
    return None

def fok_extract_recipe_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch the webpage."

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        script_tags = soup.find_all('script')

        data = fok_extract_json_data(script_tags)
       
        recipe_name = get_value_or_default(data, 'name', 'Name not Available')        
        ingredient_list = get_value_or_default(data, 'recipeIngredient', ['Ingrediants Not Available'])        
        instruction_list = get_value_or_default(data, 'recipeInstructions', ['Instructions Not Available'])
        img_url = get_value_or_default(data, 'image', 'Image Not Available')
        raw_category = get_value_or_default(data, 'recipeCategory', ['Category Not Available'])

        category_list = []
        
        category_soup = BeautifulSoup(raw_category, 'html.parser')
        category_list.append(category_soup.a.get_text())

        prep_time = get_value_or_default(data, 'totalTime', 'Prepration Time not Available')


        return {
            "Recipe Name": recipe_name,
            "Ingredients": ingredient_list,
            "Instructions": instruction_list,
            "Category": category_list,
            "Prepration Time": prep_time,
            "Image": img_url,
            "Recipe Source": 'https://www.forksoverknives.com/recipes/',
            "Recipe Credits": "FORKS OVER KNIVES"
        }
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
#   <-------------------------------------------------------------- End of Recipe Extraction from ForkOverKnives Website  -------------------------------------------------------------->


#   <-------------------------------------------------------------- Start Recipe Extraction From SHARAN Website -------------------------------------------------------------->
def sharan_extract_recipe_page(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return print("Failed to fetch the webpage.")
            
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_links = soup.find('div', class_='colps-hed').find_all("a")

        final_recipe_data = []
        # Loop through the links 
        for link in elements_with_links:
            href = link.get("href")
            recipe_data = sharan_extract_recipe_lists(href)
            final_recipe_data += recipe_data

        with open('sharanRecipeData.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["Recipe Name", "Ingredients", "Instructions", "Category", "Prepration Time", "Image", "Recipe Source", "Recipe Credits"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for  row in final_recipe_data:
                try:
                    writer.writerow(row)
                except UnicodeEncodeError:
                    print("UNICODE ERROR")

    except Exception as e:
        print(f"An error occurred in Writing CSV: {str(e)}")

def sharan_extract_recipe_lists(url):
    try:
        # Send an HTTP GET request to the website and get its HTML content
        response = requests.get(url)
        if response.status_code != 200:
            return print("Failed to fetch the webpage.")
            
        html_content = response.text
        # Parse the HTML using BeautifulSoup to extract image URLs
        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_class = soup.find('div', class_= 'recipie-list').find_all('a')

        csv_rows = []
        # Now you can loop through the elements or perform any other operations as needed
        for element in elements_with_class:         
            # Get the URL, using element['href'] for anchor tags
            recipe_url = element['href']
            csv_rows.append(sharan_extract_recipe_data(recipe_url))

        return csv_rows
            
    except Exception as e:
        print(f"An error occurred (extract_recipe_lists): {str(e)}")
        
def sharan_extract_json_data(script_tags):
    for script in script_tags:
        script_content = script.string
        if script_content and '"@context"' in script_content:
            return json.loads(script_content)
    return None

def sharan_extract_recipe_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch the webpage."

        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        elements_with_name = soup.find('div', class_= 'reci-cat-head').find('h3')
        recipe_name = elements_with_name.get_text()

        elements_with_image = soup.find_all('img', class_= 'lazy')
        img_url = elements_with_image[0]['src']

        elements_with_ingredients = soup.find_all('div', class_= 'recip-ing')
        ingredient_list =[]
        for ingredients in elements_with_ingredients:
            ingredient_list.append(ingredients.get_text())        

        elements_with_instructions = soup.find('div', class_= 'recip-meth')
        instruction_list = []
        
        for instruction in elements_with_instructions:
            instruction_list.append(instruction.get_text())

        return {
            "Recipe Name": recipe_name,
            "Ingredients": ingredient_list,
            "Instructions": instruction_list,
            "Category": ['Category Not Available'],
            "Prepration Time": "Prepration Time not Available",
            "Image": img_url,
            "Recipe Source": 'https://sharan-india.org/recipe/',
            "Recipe Credits": "SHARAN"
        }
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
#   <-------------------------------------------------------------- End of Recipe Extraction from SHARAN Website  -------------------------------------------------------------->

#   <-------------------------------------------------------------- Start Recipe Extraction From Veganista Website -------------------------------------------------------------->

def veganista_extract_menue_links(soup, menu_id):
    menu = soup.find('ul', {'id': menu_id})
    if menu:
        menu_links = menu.find_all('a')
        final_recipe_data = []
        for link in menu_links:
            recipe_cat_url=link.get('href')
            if recipe_cat_url != 'https://simple-veganista.com/vegan-recipe-index/' and recipe_cat_url != '#':
                print(recipe_cat_url,'=========> RECIPE MAIN URL')
                recipe_data = veganista_extract_recipe_lists(recipe_cat_url)
                final_recipe_data += recipe_data
        return final_recipe_data

def veganista_extract_recipe_page(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return print("Failed to fetch the webpage.")
            
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        # Find and print links for the primary menu
        primary_recipe_data = veganista_extract_menue_links(soup, 'primary-menu')
        # Find and print links for the secondary menu
        secondary_recipe_data = veganista_extract_menue_links(soup, 'secondary-menu')

        full_recipe_data = primary_recipe_data + secondary_recipe_data

        with open('veganistaRecipeData.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["Recipe Name", "Ingredients", "Instructions", "Category", "Prepration Time", "Image", "Recipe Source", "Recipe Credits"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for  row in full_recipe_data:
                try:
                    writer.writerow(row)
                except UnicodeEncodeError:
                    print("UNICODE ERROR")

    except Exception as e:
        print(f"An error occurred in Writing CSV: {str(e)}")

def veganista_extract_recipe_lists(url):
    try:
        # Send an HTTP GET request to the website and get its HTML content
        response = requests.get(url)
        if response.status_code != 200:
            return print("Failed to fetch the webpage.")
            
        html_content = response.text
        # Parse the HTML using BeautifulSoup to extract image URLs
        soup = BeautifulSoup(html_content, "html.parser")
        elements_with_class = soup.find_all('a', {'rel': 'bookmark'})

        # element_with_next_page = soup.find('link', {'rel': 'next'})
        # if element_with_next_page:
            # pass

        csv_rows = []
        for element in elements_with_class:         
            recipe_url = element['href']
            csv_rows.append(veganista_extract_recipe_data(recipe_url))

        return csv_rows
            
    except Exception as e:
        print(f"An error occurred (extract_recipe_lists): {str(e)}")
        
def veganista_extract_json_data(script_tags):
    for script in script_tags:
        script_content = script.string
        if script_content and '"@context"' in script_content:
            return json.loads(script_content)
    return None

def veganista_extract_recipe_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch the webpage."

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Recipe Name
        recipe_name_element = soup.find('h2', class_='tasty-recipes-title')
        recipe_name = recipe_name_element.get_text().strip()
        
        try:
            img_url_element = soup.find('div', class_='tasty-recipes-image').find('img')
            img_url = img_url_element.get('data-lazy-src') 
            if not img_url:
                img_url = "Not Available" 
        except:
            img_url = "Not Available" 

        # Extract Ingredients
        ingredients_elements = soup.find('div', class_='tasty-recipes-ingredients-body').find_all('li')
        ingredient_list = [ingredient.get_text().strip() for ingredient in ingredients_elements]

        # Extract Instructions
        elements_with_instructions = soup.find('div', class_= 'tasty-recipes-instructions-body')
        instruction_list = []
        for instruction in elements_with_instructions:
            instruction_list.append(instruction.get_text())

        # Extract Preparation Time
        prep_time_element = soup.find('span', class_='tasty-recipes-total-time')
        prep_time = prep_time_element.get_text().strip()

        # Extract Category
        category_element = soup.find('span', class_='tasty-recipes-category')
        category = category_element.get_text().strip()

        return {
            "Recipe Name": recipe_name,
            "Ingredients": ingredient_list,
            "Instructions": instruction_list,
            "Category": category,
            "Prepration Time": prep_time,
            "Image": img_url,
            "Recipe Source": 'https://simple-veganista.com/vegan-recipe-index/',
            "Recipe Credits": "Simple Veganista"
        }
    except Exception as e:
        return f"An error occurred: {str(e)}"

#   <-------------------------------------------------------------- End of Recipe Extraction from Veganista Website  -------------------------------------------------------------->

def plantbased_extract_next_link(url):
    response = requests.get(url)
    if response.status_code != 200:
        return print("Failed to fetch the webpage.")
        
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        elements_with_links = soup.find('div', class_='post-pagination').find("a")
        prev_recipe_link = elements_with_links.get("href") 
        return prev_recipe_link 
    except:
        return None
    

def plantbased_extract_recipe_page(url):
    try:
        final_recipe_data = []
        next = url
        while True:  
            recipe_data = plantbased_extract_recipe_data(next) 
            final_recipe_data.append(recipe_data)
            next = plantbased_extract_next_link(next)
            print(next,'============>')
            if next == None or next=='https://plantbasedcookingshow.com/2015/04/18/vegan-bean-and-cheese-enchiladas/':
                break

        with open('plantBasedRecipeData.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["Recipe Name", "Ingredients", "Instructions", "Category", "Prepration Time", "Image", "Recipe Source", "Recipe Credits"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for  row in final_recipe_data:
                try:
                    writer.writerow(row)
                except UnicodeEncodeError:
                    print("UNICODE ERROR")

    except Exception as e:
        print(f"An error occurred in Writing CSV: {str(e)}")


def plantbased_extract_recipe_data(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return "Failed to fetch the webpage."

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract Recipe Name
        recipe_name_element = soup.find('h1', class_='post-title single-post-title entry-title')
        recipe_name = recipe_name_element.get_text().strip()
        
        # Extract Image
        try:
            image_tag = soup.find('div', class_='wprm-recipe-image').find('img')
            img_url = image_tag['src']
            if not img_url:
                img_url = "Not Available" 
        except:
            img_url = "Not Available" 

        # Extract Ingredients
        ingredient = soup.find('ul', class_='wprm-recipe-ingredients')
        ingredient_list = []

        if ingredient:
            for ingredient_item in ingredient.find_all('li', class_='wprm-recipe-ingredient'):
                ingredient_text = ingredient_item.text.strip()
                ingredient_list.append(ingredient_text)

        # Extract instructions
        try:
            instructions_div = soup.find('div', class_='wprm-recipe-instructions-container')
            instruction = instructions_div.find('ul', class_='wprm-recipe-instructions')
            instruction_list = [li.get_text(strip=True) for li in instruction.find_all('li')]
        except:
            instruction_list=[]

        # Extarct Prepration time
        try:
            total_time_container = soup.find('div', class_='wprm-recipe-total-time-container')
            hours_span = total_time_container.find('span', class_='wprm-recipe-total_time-hours')
            minutes_span = total_time_container.find('span', class_='wprm-recipe-total_time-minutes')
            hours = hours_span.text.strip() if hours_span else ''
            minutes = minutes_span.text.strip() if minutes_span else ''
            prep_time = f'{hours} {minutes}'.strip()
        except:
            prep_time="Preparation time not Available"

        # Extract Category
        category_element = soup.find('div', class_='penci-standard-cat penci-single-cat')
        if category_element:
            category = category_element.get_text(strip=True)
        else:
            category="Category Not Available"

        return {
            "Recipe Name": recipe_name,
            "Ingredients": ingredient_list,
            "Instructions": instruction_list,
            "Category": category,
            "Prepration Time": prep_time,
            "Image": img_url,
            "Recipe Source": 'https://plantbasedcookingshow.com/category/recipes/',
            "Recipe Credits": "Whole Food Plant Based Cooking Show"
        }
    except Exception as e:
        return f"An error occurred: {str(e)}"
   
