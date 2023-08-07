import firebase_admin.auth as auth
from rest_framework.views import APIView
from app.models import *
from app.serializers import *
from django.shortcuts import render

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
        uniqueID = self.kwargs.get('uniqueID')

        return render(request, 'EmailConfirmationForUserDeletion.html', {'uniqueID': uniqueID})

def deleteUserAccountAction(request, uniqueID):

    try:
        firebase_user = auth.get_user(uniqueID)
            
        email = firebase_user.email

        if Volunteer.objects.filter(email=email).exists():
            user = Volunteer.objects.get(email=email)

            # Delete Custom Token Object
            CustomToken.objects.filter(user=user).delete()

            # Volunteer Profile Photo Deleted
            if Document.objects.filter(volunteer=user, docType=DOCUMENT_TYPE[0][0]).exists():
                allDocuments = Document.objects.filter(volunteer=user, docType=DOCUMENT_TYPE[0][0])
                for doc in allDocuments:
                    doc.delete()
            
            # Volunteer Vehicle and Vehicle Photo Deleted
            if Vehicle.objects.filter(owner=user).exists():
                allVehicles = Vehicle.objects.filter(owner=user)
                for vehicle in allVehicles:
                    if Document.objects.filter(vehicle=vehicle, docType=DOCUMENT_TYPE[3][0]).exists():
                        allVehicleDocs = Document.objects.filter(vehicle=vehicle, docType=DOCUMENT_TYPE[3][0])
                        for vehicleDocs in allVehicleDocs:
                            vehicleDocs.delete()
                    vehicle.delete()

            # Donations Deleted (Donation to be Deleted Before Food Events Deletion)
            if Donation.objects.filter(donatedBy=user).exists():
                allDonations = Donation.objects.filter(donatedBy=user)
                for donation in allDonations:
                    donation.delete()

            # Food Event and Event Photo Deleted
            if FoodEvent.objects.filter(createdBy=user).exists():
                foodEvents = FoodEvent.objects.filter(createdBy=user)
                for fEvent in foodEvents:
                    if Document.objects.filter(docType=DOCUMENT_TYPE[1][0], event=fEvent).exists():
                        allFoodEventDocs = Document.objects.filter(docType=DOCUMENT_TYPE[1][0], event=fEvent)
                        for foodEventDocs in allFoodEventDocs:
                            foodEventDocs.delete()
                    fEvent.delete()

            user.delete()
            auth.delete_user(uniqueID)
            
            return render(request, 'ThankYouPage.html', {'success': True, 'message': 'User has been successfully Deleted'})
        else:
            return render(request, 'ThankYouPage.html', {'success': False, 'message': 'User with Id does not exist'})

    except Exception as e:
        return render(request, 'ThankYouPage.html', {'success': False, 'error': str(e)})

class UploadBulkRecipeView(APIView):

    def get(self, request):
        return render(request, 'BulkRecipeUpload.html', {'success':True, 'message':'upload recipe'})

def upload_recipes_action(request):
    bulkRecipeFile = request.FILES.get('bulkRecipeFile')
    df = pd.read_csv(bulkRecipeFile, encoding='latin-1', encoding_errors='ignore')
   
    try:
        for lst in list(df.index):
            if 'Recipe Name' in list(df.columns):
                if df['Recipe Name'][lst] is not None:
                    foodName = df['Recipe Name'][lst]
                else:
                    foodName = None
            else:
                return render(request, 'BulkRecipeUpload.html', {'success': False, 'error':'Recipe Name column not present'})

            if 'Ingredients' in list(df.columns): 
                if df['Ingredients'][lst] is not None:
                    ingredients = df['Ingredients'][lst]
                else:
                    ingredients = None
            else:
                return render(request, 'BulkRecipeUpload.html', {'success': False, 'error':'Ingredients column not present'})
            
            if 'Instructions' in list(df.columns):
                if df['Instructions'][lst] is not None:
                    cookingInstructions = df['Instructions'][lst]
                else:
                    cookingInstructions = None
            else:
                return render(request, 'BulkRecipeUpload.html', {'success': False, 'error':'Instruction column not present'})
            
            if 'Image' in list(df.columns):
                if df['Image'][lst] is not None:
                    image = df['Image'][lst]
                else:
                    image = None
            else:
                return render(request, 'BulkRecipeUpload.html', {'success': False, 'error':'Image column not present'})
            
            if 'Category' in list(df.columns):
                if df['Category'][lst] is not None:
                    category = df['Category'][lst]
                else:
                    category = None
            else:
                return render(request, 'BulkRecipeUpload.html', {'success': False, 'error':'Category column not present'})
            import ast

            try:
                category_list = ast.literal_eval(category)
            except:
                category_list=[]
                category_list.append(category)

            if FoodRecipe.objects.filter(foodName=foodName).exists():
                recipe = FoodRecipe.objects.get(foodName=foodName)
                pass
                # return HttpResponse({'success': False, 'error': 'Food Recipe with the same name is already present'}, content_type='text/plain')
            else:
                try:
                    extension = os.path.splitext(image)[1]
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    # Download each image
                    filename = os.path.join("images", f"{foodName}{extension}")

                    # Get the image name from the URL (you can modify this logic based on your needs)
                    urllib.request.urlretrieve(image, filename)

                    recipe = FoodRecipe.objects.create(foodName=foodName, ingredients=ingredients, cookingInstructions=cookingInstructions)
                    for cat in  category_list:
                        if Category.objects.filter(name=cat).exists():
                            recipe_category = Category.objects.get(name=cat)
                        else:
                            recipe_category = Category.objects.create(name=cat, active=True)

                        recipe.category.add(recipe_category)

                    recipe.slug = recipe.id 
                    recipe.tags.add(*category_list)

                    with open(filename, 'rb') as f:
                        recipe.foodImage.save(foodName+extension, File(f))
                    recipe.save()

                    recipeDocs = Document.objects.create(docType=DOCUMENT_TYPE[2][0], createdAt=timezone.now(), food=recipe)
                    with open(filename, 'rb') as f:
                        recipeDocs.document.save(foodName+extension, File(f))
                    recipeDocs.save()
                except:
                    pass

        return render(request, 'BulkRecipeUpload.html', {'success': True, 'message':'Recipes Uploaded Successfully'})
    except Exception as e:
        return render(request, 'BulkRecipeUpload.html', {'success': False, 'error': str(e)})