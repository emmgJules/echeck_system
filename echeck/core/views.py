from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Entry, UserProfile, Person
from .forms import PersonForm, UserProfileForm
from django.core.files.storage import FileSystemStorage
from .serial_com import read_card_id_from_serial
from django.views.decorators.csrf import csrf_exempt
from .forms import UserProfileForm, UserCreationForm
 # views.py
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from .models import Entry, Person,Notification
from datetime import datetime




from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Entry, Person
from datetime import datetime
from .serial_com import read_card_id_from_serial  # Assuming you have a function for serial communication
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as django_logout

from django.shortcuts import render
from .models import Entry, Person
from django.db.models import Count
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Entry, Person
from datetime import datetime

class CoreView:
    # views.py


    @staticmethod
    @csrf_exempt
    def fetch_card_id(request):
        if request.method == 'GET':
            card_id = read_card_id_from_serial()
            print(f"Received card ID from Arduino: {card_id}")
            if card_id:
                return JsonResponse({'card_id': card_id})
            else:
                return JsonResponse({'error': 'Failed to fetch card ID'}, status=500)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    def generate_report(request):
    # Handle form submission
        if request.method == 'POST':
            # Retrieve form data
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            card_type = request.POST.get('card_type')

            # Query entries based on selected criteria
            entries = Entry.objects.filter(entry_date__range=[start_date, end_date])
            if card_type:
                entries = entries.filter(person__card_type=card_type)

            # Prepare context for rendering
            context = {
                'entries': entries,
                'start_date': start_date,
                'end_date': end_date,
                'card_type': card_type,
            }
            return render(request, 'pages/report.html', context)

        # Render initial form
        return render(request, 'pages/report_form.html')

    @staticmethod
    def fetch_notifications(request):
        notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')[:5]
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'message': notification.message,
                'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as needed
            })
        return JsonResponse(notifications_data, safe=False)

    @staticmethod
    def index(request):
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dash')
            else:
                messages.error(request, "Username/Password does not exist!")   
        return render(request, 'login.html')

    @staticmethod
    @login_required(login_url='index')
    def dash(request):
        # Fetch data for statistics
        total_today_entries = Entry.objects.filter(entry_date__date=datetime.today()).count()
        total_entries = Entry.objects.count()
        total_students = Person.objects.filter(card_type='student').count()
        total_staff = Person.objects.filter(card_type='staff').count()
        total_teachers = Person.objects.filter(card_type='teacher').count()
        total_visitors = Person.objects.filter(card_type='visitor').count()
        
        # Additional data retrieval as needed
        
        context = {
            'total_today_entries': total_today_entries,
            'total_entries': total_entries,
            'total_students': total_students,
            'total_staff': total_staff,
            'total_teachers': total_teachers,
            'total_visitors': total_visitors,
            'today_date': datetime.today().strftime('%d %b %Y'),  # Format today's date
        }
        
        return render(request, 'pages/dashboard.html', context)

    @staticmethod
    @login_required(login_url='index')
    
    def search(request):
        query = request.GET.get('q')
        context = {}
        if query:
            # Perform search across relevant models
            entries = Entry.objects.filter(
                Q(person__fname__icontains=query) |
                Q(person__lname__icontains=query) |
                Q(person__card_id__icontains=query) |
                Q(card_id__icontains=query)
            ).distinct()

            persons = Person.objects.filter(
                Q(fname__icontains=query) |
                Q(lname__icontains=query) |
                Q(card_id__icontains=query)
            ).distinct()

            users = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query)
            ).distinct()

            context = {
                'entries': entries,
                'persons': persons,
                'users': users,
                'query': query
            }

        return render(request, 'pages/search.html', context)

    
    @staticmethod

    def logout(request):
        django_logout(request)
        return redirect('index')

# Additional views as per your application needs

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Person, Entry, Notification
from datetime import datetime
from .serial_com import read_card_id_from_serial  # Assuming you have a function for serial communication

class EntryView:
    @staticmethod
    @login_required(login_url='index')
    def entry_interface(request):
        card = read_card_id_from_serial()

        return render(request, 'pages/entry_interface.html', {'card': card})

    @staticmethod
    @csrf_exempt
    @login_required(login_url='index')
    def fetch_person_details(request):
        if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            
            card_id = read_card_id_from_serial()  # Replace with your function to read card ID from Arduino
            if card_id:
                person = get_object_or_404(Person, card_id=card_id)
                
                # Retrieve the last entry date before creating a new one
                last_entry = Entry.objects.filter(person=person).order_by('-entry_date').first()
                last_entry_date_str = last_entry.entry_date.strftime('%Y-%m-%d %H:%M:%S') if last_entry else 'No previous entry'
                
                # Create a new entry for the person (auto_now_add will set entry_date)
                entry = Entry.objects.create(person=person, card_id=card_id)
                Notification.objects.create(user=request.user, message="New Entry Created.")
                
                # Get the current entry date
                current_entry_date_str = entry.entry_date.strftime('%Y-%m-%d %H:%M:%S')
                
                person_data = {
                    'id': person.id,
                    'fname': person.fname,
                    'lname': person.lname,
                    'img_url': str(person.img) if person.img else '',  # Convert ImageFieldFile to URL
                    'last_entry_date': last_entry_date_str,  # Return the last entry date from the database
                    'current_entry_date': current_entry_date_str,  # Return the current entry date
                    'card_id': card_id  # Include the card ID
                }
                
                return JsonResponse({'person': person_data})
            else:
                return JsonResponse({'error': 'Failed to fetch card ID'}, status=500)
        else:
            return HttpResponseBadRequest('Invalid request method or not AJAX')

    @staticmethod
    @csrf_exempt
    @login_required(login_url='index')
    def record_entry(request):
        if request.method == 'POST' and request.is_ajax():
            card_id = request.POST.get('card_id')
            entry_date_str = request.POST.get('entry_date')
            entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d %H:%M:%S')
            
            # Retrieve person based on card_id (assuming card_id uniquely identifies a person)
            person = get_object_or_404(Person, card_id=card_id)
            
            # Record the entry
            entry = Entry.objects.create(person=person, entry_date=entry_date)
            
            # Return success response
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid request method or not AJAX'})

    @staticmethod
    @login_required(login_url='index')
    def list_entry(request):
        entries = Entry.objects.all()  # Query all entries or apply filters as needed
        context = {'entries': entries}
        return render(request, 'pages/list_entry.html', context)

    @staticmethod
    def report_entry(request):
        return render(request, 'pages/create_entry.html')

class PersonView:
    form_class = PersonForm

    @staticmethod
    @login_required(login_url='index')
    def create_person(request):
        if request.method == 'POST':
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            card_id = request.POST.get('card_id')
            card_type = request.POST.get('card_type')
            gender = request.POST.get('gender')
            img = request.FILES['img']
            city = request.POST.get('city')
            phone = request.POST.get('phone')
            serial_number = request.POST.get('serial_number')
            brand = request.POST.get('brand')

            fs = FileSystemStorage()
            filename = fs.save(img.name, img)
            uploaded_file_url = fs.url(filename)
            print(f"Uploaded file URL: {uploaded_file_url}")


            person = Person(
                fname=fname,
                lname=lname,
                card_id=card_id,
                card_type=card_type,
                gender=gender,
                img=uploaded_file_url,
                city=city,
                phone=phone,
                serial_number=serial_number,
                brand=brand
            )
            person.save()
            Notification.objects.create(user=request.user, message="New person created.")
            print(f"Person image URL in DB: {person.img}")  # Debugging line
            return redirect('list_persons')  # Redirect to a view that lists persons

        return render(request, 'pages/add_person.html')

    @staticmethod
    @login_required(login_url='index')
    def list_persons(request):
        persons = Person.objects.all()
        return render(request, 'pages/list_persons.html', {'persons': persons})
   
    @staticmethod
    @login_required(login_url='index')
    def read_person(request, pk):
        person = get_object_or_404(Person, pk=pk)
        return render(request, 'pages/manage_person.html', {'person': person})

    @staticmethod
    @login_required(login_url='index')
    def report_persons(request):
        return render(request, 'pages/report_persons.html')

    @staticmethod
    @login_required(login_url='index')
    def update_person(request, pk):
        person = get_object_or_404(Person, pk=pk)
        if request.method == 'POST':
            form = PersonForm(request.POST, instance=person)
            if form.is_valid():
                form.save()
                Notification.objects.create(user=request.user, message="Person Updated.")
                return redirect('list_persons')
        else:
            form = PersonForm(instance=person)
        return render(request, 'pages/edit_person.html', {'form': form})

    @staticmethod
    @login_required(login_url='index')
    def delete_person(request, pk):
        person = get_object_or_404(Person, pk=pk)
        if request.method == 'POST':
            person.delete()
            Notification.objects.create(user=request.user, message="Person Deleted.")
            return redirect('list_persons')
        return render(request, 'pages/delete_person.html', {'person': person})

class UserView:
    @staticmethod
    @login_required(login_url='index')
    def create_user(request):
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            profile_form = UserProfileForm(request.POST, request.FILES)
            if form.is_valid() and profile_form.is_valid():
                user = form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                Notification.objects.create(user=request.user, message="New User created.")
                return redirect('read_user')
        else:
            form = UserCreationForm()
            profile_form = UserProfileForm()
        context = {'form': form, 'profile_form': profile_form}
        return render(request, 'pages/create_user.html', context)

    @staticmethod
    @login_required(login_url='index')
    def read_user(request):
        users = User.objects.all()
        return render(request, 'pages/read_user.html', {'users': users})

    @login_required(login_url='index')
    def update_user(request, pk):
        user = get_object_or_404(User, pk=pk)
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'POST':
            user_form = UserCreationForm(request.POST, instance=user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                Notification.objects.create(user=request.user, message="User Updated.")
                
                # Optionally, update the session to reflect changes
                request.session['user'] = user_form.cleaned_data.get('username')

                return redirect('user-profile', pk=pk)  # Redirect to the profile read view
        else:
            user_form = UserCreationForm(instance=user)
            profile_form = UserProfileForm(instance=user_profile)
        
        context = {'user_form': user_form, 'profile_form': profile_form}
        return render(request, 'pages/edit_user.html', context)
    @staticmethod
    @login_required(login_url='INDEX')
    def delete_user(request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            user.delete()
            Notification.objects.create(user=request.user, message="User Deleted.")
            return redirect('read_user')
        return render(request, 'pages/delete_user.html', {'user': user})
