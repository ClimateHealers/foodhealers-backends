import firebase_admin.auth as auth
from rest_framework.views import APIView
from app.models import (Volunteer, CustomToken, Document, Vehicle, Donation, FoodEvent, FoodRecipe, Category, DOCUMENT_TYPE)
from django.shortcuts import render
import ast
import urllib, base64
from urllib.parse import urlparse, urlunparse
import os
import pandas as pd
import requests
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from django.core.files.base import File
from django.utils import timezone
from django.core.files.base import ContentFile
# Create your views here.

class DeleteUserAccountView(APIView):

    def get(self, request, *args, **kwargs):

        # Retrieve the URL parameter 'unique_id' using self.kwargs
        unique_id = self.kwargs.get('unique_id')

        return render(request, 'EmailConfirmationForUserDeletion.html', {'unique_id': unique_id})

def delete_user_account_action(request, unique_id):
    template_name = 'ThankYouPage.html'
    try:
        firebase_user = auth.get_user(unique_id)
        email = firebase_user.email
        
        try:
            user = Volunteer.objects.get(email=email)
            
            # Delete Custom Token Object
            CustomToken.objects.filter(user=user).delete()
            
            # Delete Volunteer-related documents
            Document.objects.filter(volunteer=user, docType=DOCUMENT_TYPE[0][0]).delete()
            
            # Delete Volunteer Vehicles and related documents
            vehicles = Vehicle.objects.filter(owner=user)
            for vehicle in vehicles:
                Document.objects.filter(vehicle=vehicle, docType=DOCUMENT_TYPE[3][0]).delete()
            vehicles.delete()
            
            # Delete Donations
            Donation.objects.filter(donatedBy=user).delete()
            
            # Delete Food Events and related documents
            food_events_list = FoodEvent.objects.filter(createdBy=user)
            for food_event in food_events_list:
                Document.objects.filter(docType=DOCUMENT_TYPE[1][0], event=food_event).delete()
            food_events_list.delete()
            
            user.delete()
            auth.delete_user(unique_id)
            
            return render(request, template_name, {'success': True, 'message': 'User has been successfully Deleted'})
        
        except Volunteer.DoesNotExist:
            return render(request, template_name, {'success': False, 'message': 'User with Id does not exist'})
        
    except Exception as e:
        return render(request, template_name, {'success': False, 'error': str(e)})

class UploadBulkRecipeView(APIView):

    def get(self, request):
        return render(request, 'BulkRecipeUpload.html', {'success':True, 'message':'upload recipe'})

def upload_recipes_action(request):
    template_name = 'BulkRecipeUpload.html'
    bulk_recipe_file = request.FILES.get('bulkRecipeFile')

    try:
        df = pd.read_csv(bulk_recipe_file, encoding='utf-8', encoding_errors='ignore') 
        required_columns = ['Recipe Name', 'Ingredients', 'Instructions', 'Image', 'Category', 'Prepration Time','Recipe Source', 'Recipe Credits']

        if not all(col in df.columns for col in required_columns):
            return render(request, template_name, {'success': False, 'error': 'Required columns are missing'})
        
        for _, row in df.iterrows():
            try:
                food_name, ingredients, cooking_instructions, image, category, prepration_time, recipe_source, recipe_credits = row[required_columns]

                try:
                    ingredients_test = ast.literal_eval(ingredients) if ingredients else []
                except:
                    ingredients_test = []
                    ingredients_test.append(ingredients)
                cleaned_ingredients = [s.replace('\n', '') for s in ingredients_test]

                try:
                    instructions_test = ast.literal_eval(cooking_instructions) if cooking_instructions else []
                except:
                    instructions_test = []
                    instructions_test.append(cooking_instructions)
                cleaned_instructions = [s.replace('\n', '') for s in instructions_test]

                try:
                    category_list = ast.literal_eval(category) if category else []
                except:
                    category_list = []
                    category_list.append(category)
            
                if not FoodRecipe.objects.filter(foodName=food_name).exists():
                    # Parse the URL to extract its components
                    parsed_url = urlparse(image)
                    # Extract the path and file name from the URL
                    path = parsed_url.path
                    file_name = path.split("/")[-1]

                    filename = os.path.join("images", f"{file_name}")

                    if not os.path.exists("images"):
                        os.makedirs("images")
                    try:
                        urllib.request.urlretrieve(image, filename)
                    except:
                        response = requests.get(image)
                        if response.status_code == 200:
                            with open(filename, 'wb') as file:
                                file.write(response.content)

                    recipe = FoodRecipe.objects.create(
                        foodName=food_name,
                        ingredients=cleaned_ingredients,
                        cookingInstructions=cleaned_instructions,
                        preparationTime=prepration_time,
                        recipeSource=recipe_source,
                        recipeCredits=recipe_credits
                    )
                
                    for cat in category_list:
                        recipe_category, _ = Category.objects.get_or_create(name=cat, active=True)
                        recipe.category.add(recipe_category)

                    recipe.slug = recipe.id
                    recipe.tags.add(*category_list)
                    with open(filename, 'rb') as f:
                        recipe.foodImage.save(file_name, File(f))

            except Exception as e :
                print(str(e))
                return render(request, template_name, {'success': False, 'error': str(e)})
                # pass

        return render(request, template_name, {'success': True, 'message': 'Recipes Uploaded Successfully'})

    except Exception as e:
        return render(request, template_name, {'success': False, 'error': str(e)})