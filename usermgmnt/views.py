import firebase_admin.auth as auth
from rest_framework.views import APIView
from app.models import (Volunteer, CustomToken, Document, Vehicle, Donation, FoodEvent, FoodRecipe, Category, DOCUMENT_TYPE)
from django.shortcuts import render
import ast
import urllib, base64
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
    df = pd.read_csv(bulk_recipe_file, encoding='latin-1', encoding_errors='ignore')

    try:
        for lst in df.index:
            name_column = 'Recipe Name'
            ingredients_column = 'Ingredients'
            instructions_column = 'Instructions'
            image_column = 'Image'
            category_column = 'Category'
            source_column = 'Recipe Source'
            credits_column = 'Recipe Credits'
            
            if any(col not in df.columns for col in [name_column, ingredients_column, instructions_column, image_column, category_column, source_column, credits_column]):
                return render(request, template_name, {'success': False, 'error': 'Required columns are missing'})

            food_name = df[name_column][lst]
            ingredients = df[ingredients_column][lst]
            cooking_instructions = df[instructions_column][lst]
            image = df[image_column][lst]
            category = df[category_column][lst]
            recipe_source = df[source_column][lst]
            recipe_credits = df[credits_column][lst]

            try:
                category_list = ast.literal_eval(category)
            except Exception:
                category_list = [category]

            if not FoodRecipe.objects.filter(foodName=food_name).exists():
                try:
                    extension = os.path.splitext(image)[1]
                    filename = os.path.join("images", f"{food_name}{extension}")

                    if not os.path.exists("images"):
                        os.makedirs("images")

                    urllib.request.urlretrieve(image, filename)

                    recipe = FoodRecipe.objects.create(
                        foodName=food_name,
                        ingredients=ingredients,
                        cookingInstructions=cooking_instructions,
                        recipeSource=recipe_source,
                        recipeCredits=recipe_credits
                    )

                    for cat in category_list:
                        recipe_category, _ = Category.objects.get_or_create(name=cat, active=True)
                        recipe.category.add(recipe_category)

                    recipe.slug = recipe.id
                    recipe.tags.add(*category_list)

                    with open(filename, 'rb') as f:
                        recipe.foodImage.save(food_name + extension, File(f))
                    recipe.save()

                    recipe_docs = Document.objects.create(
                        docType=DOCUMENT_TYPE[2][0],
                        createdAt=timezone.now(),
                        food=recipe
                    )

                    with open(filename, 'rb') as f:
                        recipe_docs.document.save(food_name + extension, File(f))
                    recipe_docs.save()

                except Exception:
                    pass

        return render(request, template_name, {'success': True, 'message': 'Recipes Uploaded Successfully'})

    except Exception as e:
        return render(request, template_name, {'success': False, 'error': str(e)})
