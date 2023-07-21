import firebase_admin.auth as auth
from rest_framework.views import APIView
from app.models import *
from app.serializers import *
from django.shortcuts import render

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