'''
Add new URL patterns here
'''

from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from usermgmnt import views

app_name = "usermgmnt"

urlpatterns = [
    # DELETE (Django Template view to Delete Volunteer Profile)
    re_path(r'delete-account/(?P<uniqueID>[-\w]*)/', views.DeleteUserAccountView.as_view(), name='delete-account-view'), 
    # DELETE (Delete Action for the Django Template)
    re_path(r'delete-account-action/(?P<uniqueID>[-\w]*)/', views.deleteUserAccountAction, name='delete-account-action'), 

]+static(settings.MEDIA_URL, documne_root=settings.MEDIA_ROOT)