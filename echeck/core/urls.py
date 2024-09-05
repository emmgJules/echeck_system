from django.urls import path
from .views import PersonView, CoreView, UserView, EntryView,ExitView,access_denied
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', CoreView.index, name='index'),
    path('dashboard/', CoreView.dash, name='dash'),
    path('fetch-card-id/', CoreView.fetch_card_id, name='fetch_card_id'),
    path('create-person/', PersonView.create_person, name='create_person'),
    path('person/<int:pk>/', PersonView.read_person, name='read_person'),
    path('list-persons/', PersonView.list_persons, name='list_persons'),
    path('report-persons/', PersonView.report_persons, name='report_persons'),
    path('update-person/<int:pk>/', PersonView.update_person, name='update_person'),
    path('delete-person/<int:pk>/', PersonView.delete_person, name='delete_person'),
    path('validate-field/', PersonView.validate_field, name='validate_field'),
    path('create-entry/', EntryView.record_entry, name='record_entry'),
    path('entry-interface/', EntryView.entry_interface, name='entry'),
    path('list-entry/', EntryView.list_entry, name='list_entry'),
    path('report-entry/', EntryView.report_entry, name='report_entry'),
    path('fetch-person-details/', EntryView.fetch_person_details, name='fetch_person_details'),
    path('logout/', CoreView.logout, name='logout'),
    path('create-user/', UserView.create_user, name='create_user'),
    path('user-list/', UserView.read_user, name='read_user'),
    path('validate/', UserView.validate_form, name='validate_form'),
    path('fetch-notifications/', CoreView.fetch_notifications, name='fetch_notifications'),
    path('generate-report/', CoreView.generate_report, name='generate_report'),
    path('download_report/csv/',CoreView.download_report_csv , name='download_report_csv'),
    path('download_report/pdf/', CoreView.download_report_pdf, name='download_report_pdf'),
    path('delete-user/<int:pk>/', UserView.delete_user, name='delete_user'),
    path('profile/<int:pk>/', UserView.update_user, name='user-profile'),
    path('user/<int:id>/',UserView.user_detail, name='user_detail'),
    path('search/', CoreView.search, name='search'),
    path('print-qr-code/<str:qr_code_filename>/',CoreView.print_qr_code_view, name='print_qr_code'),
    path('view_exit',ExitView.view_exit,name='view_exit'),
    path('access-denied/', access_denied, name='access_denied'),
    path('exit/',ExitView.exit_interface,name='exit'),
    

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
