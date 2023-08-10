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

        # Retrieve the URL parameter 'uniqueID' using self.kwargs
        unique_id = self.kwargs.get('uniqueID')

        return render(request, 'EmailConfirmationForUserDeletion.html', {'uniqueID': unique_id})

def delete_user_account_action(request, uniqueID):
    template_name = 'ThankYouPage.html'
    try:
        firebase_user = auth.get_user(uniqueID)
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
            food_events = FoodEvent.objects.filter(createdBy=user)
            for fEvent in food_events:
                Document.objects.filter(docType=DOCUMENT_TYPE[1][0], event=fEvent).delete()
            food_events.delete()
            
            user.delete()
            auth.delete_user(uniqueID)
            
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
        for lst in list(df.index):

            name_column = 'Recipe Name'
            if name_column in list(df.columns):
                if df[name_column][lst] is not None:
                    food_name = df[name_column][lst]
                else:
                    food_name = None
            else:
                return render(request, template_name, {'success': False, 'error':'Recipe Name column not present'})

            ingredients_column = 'Ingredients'
            if ingredients_column in list(df.columns): 
                if df[ingredients_column][lst] is not None:
                    ingredients = df[ingredients_column][lst]
                else:
                    ingredients = None
            else:
                return render(request, template_name, {'success': False, 'error':'Ingredients column not present'})
            
            instructions_column = 'Instructions'
            if instructions_column in list(df.columns):
                if df[instructions_column][lst] is not None:
                    cooking_instructions = df[instructions_column][lst]
                else:
                    cooking_instructions = None
            else:
                return render(request, template_name, {'success': False, 'error':'Instruction column not present'})
            
            image_column = 'Image'
            if image_column in list(df.columns):
                if df[image_column][lst] is not None:
                    image = df[image_column][lst]
                else:
                    image = None
            else:
                return render(request, template_name, {'success': False, 'error':'Image column not present'})
            
            category_column = 'Category'
            if category_column in list(df.columns):
                if df[category_column][lst] is not None:
                    category = df[category_column][lst]
                else:
                    category = None
            else:
                return render(request, template_name, {'success': False, 'error':'Category column not present'})
            
            source_column = 'Recipe Source'
            if source_column in list(df.columns):
                if df[source_column][lst] is not None:
                    recipe_source = df[source_column][lst]
                else:
                    recipe_source = None
            else:
                return render(request, template_name, {'success': False, 'error':'Recipe Source column not present'})
            
            credits_column = 'Recipe Credits'
            if credits_column in list(df.columns):
                if df[credits_column][lst] is not None:
                    recipe_credits = df[credits_column][lst]
                else:
                    recipe_credits = None
            else:
                return render(request, template_name, {'success': False, 'error':'Recipe Credits column not present'})

            try:
                category_list = ast.literal_eval(category)
            except Exception as e:
                category_list=[]
                category_list.append(category)

            if FoodRecipe.objects.filter(foodName=food_name).exists():
                pass
            else:
                try:
                    extension = os.path.splitext(image)[1]
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    # Download each image
                    filename = os.path.join("images", f"{food_name}{extension}")

                    # Get the image name from the URL (you can modify this logic based on your needs)
                    urllib.request.urlretrieve(image, filename)

                    recipe = FoodRecipe.objects.create(foodName=food_name, ingredients=ingredients, cookingInstructions=cooking_instructions, recipeSource=recipe_source, recipeCredits=recipe_credits)
                    for cat in  category_list:
                        if Category.objects.filter(name=cat).exists():
                            recipe_category = Category.objects.get(name=cat)
                        else:
                            recipe_category = Category.objects.create(name=cat, active=True)

                        recipe.category.add(recipe_category)

                    recipe.slug = recipe.id 
                    recipe.tags.add(*category_list)

                    with open(filename, 'rb') as f:
                        recipe.foodImage.save(food_name+extension, File(f))
                    recipe.save()

                    recipe_docs = Document.objects.create(docType=DOCUMENT_TYPE[2][0], createdAt=timezone.now(), food=recipe)
                    with open(filename, 'rb') as f:
                        recipe_docs.document.save(food_name+extension, File(f))
                    recipe_docs.save()
                except Exception as e:
                    pass

        return render(request, template_name, {'success': True, 'message':'Recipes Uploaded Successfully'})
    except Exception as e:
        return render(request, template_name, {'success': False, 'error': str(e)})