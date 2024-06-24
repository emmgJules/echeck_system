from django.urls import path,include
from django.contrib import admin
from . import views
from .views import PersonView

urlpatterns=[
    path('',views.index,name='index'),
    path('dashboard/',views.dash,name='dash'),
    path('videofeed/',views.video_feed,name='video'),
    path('save_image/', views.save_image, name='save_image'),
    path('update-user/',views.updateUser,name="update-user"),
    path('search',views.search,name='search'),
    path('create-person/', PersonView.create_person, name='create_person'),
    path('person/<int:pk>/', PersonView.read_person, name='read_person'),
    path('list_persons/',PersonView.list_persons,name='list_persons'),
    path('update-person/<int:pk>/', PersonView.update_person, name='update_person'),
    path('delete-person/<int:pk>/', PersonView.delete_person, name='delete_person'),
]

    