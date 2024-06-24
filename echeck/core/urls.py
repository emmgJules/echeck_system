from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('dashboard/',views.dash,name='dash'),
    path('add/student/', views.add_student, name='add_student'),
    # path('add/laptop/', views.add_laptop, name='add_laptop'),
    path('add/entry/', views.add_entry, name='add_entry'),
    path('view/students/', views.view_students, name='view_students'),
    # path('view/laptops/', views.view_laptops, name='view_laptops'),
    path('view/entries/', views.view_entries, name='view_entries'),
    path('digital/', views.digital, name='digital'),
    path('videofeed/',views.video_feed,name='video'),
    path('view/stuntent/<int:id>/',views.viewstudent,name='viewstudent'),
    path('save_image/', views.save_image, name='save_image'),
    path('student/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('student/<int:pk>/edit/', views.edit_student, name='edit_student'),
    path('update-user/',views.updateUser,name="update-user"),
    path('search',views.search,name='search'),
    



]
