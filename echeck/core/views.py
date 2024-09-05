from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_date
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.utils.timezone import make_aware, timedelta
from .models import Entry, UserProfile, Person,ExitRecord
from .forms import PersonForm, UserProfileForm
from django.core.files.storage import FileSystemStorage
from .serial_com import read_card_id_from_serial
from django.views.decorators.csrf import csrf_exempt
from .forms import UserProfileForm, UserCreationForm
import win32print
import win32api
import win32con
from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from .models import Entry, Person,Notification
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
from django.utils.dateparse import parse_datetime
from django.db.models import Count
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Entry, Person,ExitRecord
from datetime import datetime,timedelta
import qrcode
from django.conf import settings
from django.conf.urls.static import static
from .models import Person, Entry
import csv
from io import StringIO
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import Person, Entry, ExitRecord
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from functools import wraps
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import pytz
from PIL import Image, ImageWin  # Ensure ImageWin is imported
from win32com import client
from win32com.client import Dispatch
from django.templatetags.static import static
import win32com.client
import fitz  # PyMuPDF
from PIL import Image
import win32print
import win32ui
from reportlab.lib.utils import ImageReader
import time
CAT = pytz.timezone('Africa/Kigali')  # Set the timezone to Central Africa Time
DEFAULT_IMAGE = static('images/default.jpg')
TIME_LIMIT = timedelta(seconds=50)  # Set the time limit to prevent duplicate entries
def user_access_required(required_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if required_type == 'staff' and request.user.is_staff:
                    return view_func(request, *args, **kwargs)
                elif required_type == 'superuser' and request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                elif required_type == 'none' and not request.user.is_staff and not request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                else:
                    # Pass the reason for access denial in the URL
                    return redirect(reverse('access_denied') + f'?reason={required_type}')
            else:
                return redirect(reverse('index'))
        return _wrapped_view
    return decorator
@login_required(login_url='index')
def access_denied(request):
    
    reason = request.GET.get('reason', 'unknown')
    return render(request, 'pages/access_denied.html', {'reason': reason})
def custom_server_error_view(request):
    return render(request, '500.html', status=500)

def extracted_serial_number(serial_number):
        """
        Extracts the serial number from the stored QR code data by removing the constant part.
        
        Returns:
        - str: The extracted serial number or an empty string if the constant part is not found.
        """
        constant_part = 'PF9XB382'
        if constant_part in serial_number:
            constant_index = serial_number.index(constant_part)
            return serial_number[:constant_index].strip()
        return serial_number

def print_pdf(pdf_file_path):
    temp_image_path = "temp_image.png"
    
    try:
        # Convert the first page of the PDF to an image
        pdf_document = fitz.open(pdf_file_path)
        page = pdf_document.load_page(0)
        pix = page.get_pixmap()
        pix.save(temp_image_path)
        print("Converted PDF to image:", temp_image_path)
        
        # Load the image using PIL
        image = Image.open(temp_image_path)
        print("Image mode after conversion:", image.mode)

        # Get the default printer
        printer_name = win32print.GetDefaultPrinter()
        print("Default printer:", printer_name)
        hPrinter = win32print.OpenPrinter(printer_name)
        
        # Set up the printing job
        doc_info = ("Print Job", None, None)
        job_id = win32print.StartDocPrinter(hPrinter, 1, doc_info)
        win32print.StartPagePrinter(hPrinter)
        print("Started print job.")
        
        # Create a device context (DC) for the printer
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        hDC.StartDoc("Print Job")
        hDC.StartPage()

        # Get the printer's page size
        printable_area = hDC.GetDeviceCaps(win32con.HORZRES), hDC.GetDeviceCaps(win32con.VERTRES)
        print(f"Printable area: {printable_area}")

        # Calculate the scaling factor to fit the image to the page width
        width, height = image.size
        scale_factor = printable_area[0] / width
        
        # Calculate the new dimensions based on the scale factor
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Prepare the destination rectangle (printing area)
        dst_rect = (0, 0, new_width, new_height)
        print(f"Destination rectangle: {dst_rect}")

        # Convert the image to a device-independent bitmap (DIB)
        dib = ImageWin.Dib(image.resize((new_width, new_height)))

        # Draw the DIB on the printer's DC
        dib.draw(hDC.GetHandleOutput(), dst_rect)
        
        # End the printing job
        hDC.EndPage()
        hDC.EndDoc()
        
    except win32ui.error as e:
        print(f"Win32UI Error: {e}")
    except Exception as e:
        print(f"Error during printing: {e}")
    finally:
        # Clean up GDI objects and printer handle
        if hDC:
            hDC.DeleteDC()
        if hPrinter:
            win32print.EndDocPrinter(hPrinter)
            win32print.ClosePrinter(hPrinter)
        
        # Retry deletion of the temporary image file
        for i in range(10):
            try:
                os.remove(temp_image_path)
                print("Temporary image file deleted successfully.")
                break
            except PermissionError:
                time.sleep(0.5)
                print(f"Attempt {i + 1}: Retrying to delete the file.")

class CoreView:
    
    @staticmethod
    @csrf_exempt
    @login_required(login_url='index')
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
    @user_access_required('staff')
    def generate_report(request):
        if request.method == 'POST':
            # Extract and parse the form data
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            report_type = request.POST.get('report_type')
            category = request.POST.get('category')

            # Convert dates to timezone-aware datetime objects if necessary
            start_date = parse_datetime(start_date)  # Converts string to datetime
            end_date = parse_datetime(end_date)  # Converts string to datetime

            # Ensure the dates are timezone-aware
            if start_date and end_date:
                start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
                end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

            # Initialize querysets
            headers = []
            rows = []

            # Check for valid dates
            if not start_date or not end_date:
                return JsonResponse({'success': False, 'error': 'Invalid date range'})

            # Filter entries based on the report type and category
            if report_type == 'person':
                if category == 'all':
                    people = Person.objects.all()  # Query all persons if category is 'all'
                else:
                    people = Person.objects.filter(card_type=category)  # Filter by card_type otherwise

                headers = ['First Name', 'Last Name', 'Card ID', 'Card Type', 'City', 'Phone']
                rows = [[p.fname, p.lname, p.card_id, p.card_type, p.city, p.phone] for p in people]

            elif report_type == 'entry':
                entries = Entry.objects.filter(entry_date__range=[start_date, end_date])
                headers = ['Person', 'Card ID', 'Entry Date']
                rows = [[e.person.fname + ' ' + e.person.lname, e.card_id, e.entry_date] for e in entries]

            elif report_type == 'exit':
                exits = ExitRecord.objects.filter(exit_time__range=[start_date, end_date])
                headers = ['Person', 'Exit Time']
                rows = [[e.person.fname + ' ' + e.person.lname, e.exit_time] for e in exits]

            else:
                return JsonResponse({'success': False, 'error': 'Invalid report type'})

            return JsonResponse({'success': True, 'headers': headers, 'rows': rows})

        return render(request, 'pages/report.html')

    
    @user_access_required('staff')
    def download_report_csv(request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        report_type = request.GET.get('report_type')
        category = request.GET.get('category')

        # Convert dates to timezone-aware datetime objects if necessary
        start_date = parse_datetime(start_date)  # Converts string to datetime
        end_date = parse_datetime(end_date)  # Converts string to datetime

        if start_date and end_date:
            start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
            end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

        headers = []
        rows = []

        if report_type == 'person':
            if category == 'all':
                people = Person.objects.all()
            else:
                people = Person.objects.filter(card_type=category)

            headers = ['First Name', 'Last Name', 'Card ID', 'Card Type', 'City', 'Phone']
            rows = [[p.fname, p.lname, p.card_id, p.card_type, p.city, p.phone] for p in people]

        elif report_type == 'entry':
            entries = Entry.objects.filter(entry_date__range=[start_date, end_date])
            headers = ['Person', 'Card ID', 'Entry Date']
            rows = [[e.person.fname + ' ' + e.person.lname, e.card_id, e.entry_date] for e in entries]

        elif report_type == 'exit':
            exits = ExitRecord.objects.filter(exit_time__range=[start_date, end_date])
            headers = ['Person', 'Exit Time']
            rows = [[e.person.fname + ' ' + e.person.lname, e.exit_time] for e in exits]

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="e-check-report.csv"'
        return response
    @user_access_required('staff')
    def download_report_pdf(request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        report_type = request.GET.get('report_type')
        category = request.GET.get('category')

        # Convert dates to timezone-aware datetime objects if necessary
        start_date = parse_datetime(start_date)  # Converts string to datetime
        end_date = parse_datetime(end_date)  # Converts string to datetime

        if start_date and end_date:
            start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
            end_date = timezone.make_aware(end_date, timezone.get_current_timezone())

        data = {
            'headers': [],
            'rows': []
        }

        if report_type == 'person':
            if category == 'all':
                people = Person.objects.all()
            else:
                people = Person.objects.filter(card_type=category)

            data['headers'] = ['First Name', 'Last Name', 'Card ID', 'Card Type', 'City', 'Phone']
            data['rows'] = [[p.fname, p.lname, p.card_id, p.card_type, p.city, p.phone] for p in people]

        elif report_type == 'entry':
            entries = Entry.objects.filter(entry_date__range=[start_date, end_date])
            data['headers'] = ['Person', 'Card ID', 'Entry Date']
            data['rows'] = [[e.person.fname + ' ' + e.person.lname, e.card_id, e.entry_date] for e in entries]

        elif report_type == 'exit':
            exits = ExitRecord.objects.filter(exit_time__range=[start_date, end_date])
            data['headers'] = ['Person', 'Exit Time']
            data['rows'] = [[e.person.fname + ' ' + e.person.lname, e.exit_time] for e in exits]

        html = render_to_string('pages/report_pdf.html', {'data': data})
        output = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=output)

        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)

        response = HttpResponse(output.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="e-check-report.pdf"'
        return response

    @staticmethod
    @login_required(login_url='index')
    def print_qr_code_view(request, qr_code_filename):
        qr_code_url = request.build_absolute_uri(f'/media/qrcodes/{qr_code_filename}')
        return render(request, 'pages/print.html', {'qr_code_url': qr_code_url})
    @staticmethod
    @login_required(login_url='index')
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
    @login_required(login_url="index")
    def dash(request):
        # Fetch data for statistics
        today_date = datetime.today()
        total_today_entries = Entry.objects.filter(entry_date__date=today_date).count()
        total_entries = Entry.objects.count()
        total_students = Person.objects.filter(card_type='student').count()
        total_staff = Person.objects.filter(card_type='staff').count()
        total_teachers = Person.objects.filter(card_type='teacher').count()
        total_visitors = Person.objects.filter(card_type='visitor').count()
        
        # Fetch exit data
        total_today_exits = ExitRecord.objects.filter(exit_time__date=today_date).count()
        total_exits = ExitRecord.objects.count()
        total_students_exits = ExitRecord.objects.filter(person__card_type='student').count()
        total_staff_exits = ExitRecord.objects.filter(person__card_type='staff').count()
        total_teachers_exits = ExitRecord.objects.filter(person__card_type='teacher').count()
        total_visitors_exits = ExitRecord.objects.filter(person__card_type='visitor').count()

        context = {
            'total_today_entries': total_today_entries,
            'total_entries': total_entries,
            'total_students': total_students,
            'total_staff': total_staff,
            'total_teachers': total_teachers,
            'total_visitors': total_visitors,
            'total_today_exits': total_today_exits,
            'total_exits': total_exits,
            'total_students_exits': total_students_exits,
            'total_staff_exits': total_staff_exits,
            'total_teachers_exits': total_teachers_exits,
            'total_visitors_exits': total_visitors_exits,
            'today_date': today_date.strftime('%d %b %Y'),  # Format today's date
        }
        
        return render(request, 'pages/dashboard.html', context)
    @staticmethod
    @login_required(login_url='index')
    @user_access_required('staff')
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

def extract_serial_number(qr_data):
        constant_part = 'PF9XB382'
        if constant_part in qr_data:
            constant_index = qr_data.index(constant_part)
            return qr_data[:constant_index].strip()
        return qr_data

def get_last_entry(person_id):
        try:
            person = Person.objects.get(pk=person_id)  # Assuming person_id is the primary key of Person model
            last_entry = Entry.objects.filter(person=person).order_by('-entry_date').first()
            if last_entry:
                return last_entry
            else:
                return None
        except Person.DoesNotExist:
            return None

class EntryView:

    @staticmethod
    @login_required(login_url='index')
    def entry_interface(request):
        return render(request, 'pages/entry_interface.html')

    @staticmethod
    @csrf_exempt
    @login_required(login_url='index')
    def fetch_person_details(request):
        if request.method == 'GET':
            try:
                card_id = read_card_id_from_serial()  # Function to read the card ID from serial
                print(f"Received card ID from Arduino: {card_id}")
                
                if card_id:
                    person = Person.objects.filter(card_id=card_id).first()
                    if person:
                        last_entry = EntryView.get_last_entry(person.id)
                        current_time = timezone.now().astimezone(CAT)
                        
                        if last_entry is None or current_time - last_entry.entry_date.astimezone(CAT) > TIME_LIMIT:
                            entry = Entry.objects.create(person=person, card_id=card_id)
                            Notification.objects.create(user=request.user, message="New Entry Created.")
                            entry_now = entry.entry_date.astimezone(CAT).strftime('%Y-%m-%d %H:%M:%S')
                            message = 'Entry recorded successfully'
                        else:
                            entry_now = current_time.strftime('%Y-%m-%d %H:%M:%S')
                            message = 'Entry already recorded recently'
                        
                        person_data = {
                            'id': person.id,
                            'fname': person.fname,
                            'lname': person.lname,
                            'card_id': person.card_id,
                            'entry_now': entry_now,
                            'card_type': person.card_type,
                            'last_entry_date': last_entry.entry_date.astimezone(CAT).strftime('%Y-%m-%d %H:%M:%S') if last_entry else None,
                            'img_url': str(person.img.url) if person.img else DEFAULT_IMAGE,
                            'message': message
                        }
                        return JsonResponse({'person': person_data})
                    else:
                        return JsonResponse({'error': 'Person with this card ID does not exist'}, status=404)
                else:
                    return JsonResponse({'error': 'Failed to fetch card ID'}, status=500)
            except Exception as e:
                print(f"Error fetching card ID: {str(e)}")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)

    @staticmethod
    @csrf_exempt
    @login_required(login_url='index')
    def record_entry(request):
        if request.method == 'POST' and request.is_ajax():
            card_id = request.POST.get('card_id')
            entry_date_str = request.POST.get('entry_date')
            try:
                entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d %H:%M:%S').astimezone(CAT)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)
            
            person = get_object_or_404(Person, card_id=card_id)
            last_entry = EntryView.get_last_entry(person.id)
            
            if last_entry is None or entry_date - last_entry.entry_date.astimezone(CAT) > TIME_LIMIT:
                Entry.objects.create(person=person, entry_date=entry_date)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'success', 'message': 'Entry already recorded recently'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid request method or not AJAX'}, status=400)

    @staticmethod
    @login_required(login_url='index')
    def list_entry(request):
        entry_list = Entry.objects.all()  # Query all entries or apply filters as needed
        paginator = Paginator(entry_list, 5)  # Show 5 entries per page

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'pages/list_entry.html', {'page_obj': page_obj})

    @staticmethod
    @login_required(login_url='index')
    def report_entry(request):
        return render(request, 'pages/create_entry.html')

    @staticmethod
    def get_last_entry(person_id):
        return Entry.objects.filter(person_id=person_id).order_by('-entry_date').first()

class PersonView:
    form_class = PersonForm

    @login_required(login_url='index')
    @user_access_required('staff')
    def create_person(request):
        if request.method == 'POST':
            # Extract form data
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            card_id = request.POST.get('card_id')
            card_type = request.POST.get('card_type')
            gender = request.POST.get('gender')
            img = request.FILES.get('img')
            city = request.POST.get('city')
            phone = request.POST.get('phone')
            serial_number = request.POST.get('serial_number')
            brand = request.POST.get('brand')

            # Perform validation
            errors = PersonView.validate_person_fields(fname, lname, card_id, serial_number)
            if errors:
                return render(request, 'pages/add_person.html', {'errors': errors})

            # Handle image upload if present
            if img:
                fs = FileSystemStorage()
                filename = fs.save(img.name, img)
                uploaded_file_url = fs.url(filename)
                print(f"Uploaded file URL: {uploaded_file_url}")

            # Generate QR code data
            qr_data = f"""
            First Name: {fname}
            Serial Number: {extracted_serial_number(serial_number)}
            """

            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill='black', back_color='white')

            # Ensure the qrcodes directory exists
            qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
            if not os.path.exists(qr_codes_dir):
                os.makedirs(qr_codes_dir)

            # Save QR code image
            qr_img_filename = f'{fname}_{card_id}.png'
            qr_img_path = os.path.join(qr_codes_dir, qr_img_filename)
            qr_img.save(qr_img_path)

            # Generate PDF with QR code for the custom paper size 58x210mm
            pdf_filename = f'{fname}_{card_id}.pdf'
            pdf_path = os.path.join(qr_codes_dir, pdf_filename)

            # Custom paper size in points (58mm x 210mm)
            custom_paper_size = (164.43, 595.35)  # width x height in points

            c = canvas.Canvas(pdf_path, pagesize=custom_paper_size)

            # Load the QR code image
            qr_image = ImageReader(qr_img_path)

            # Get the dimensions of the QR code image
            img_width, img_height = qr_image.getSize()

            # Define margins
            top_margin = 10
            left_margin = 10
            right_margin = custom_paper_size[0] - 10

            # Calculate the position to center the QR code at the top of the page
            qr_code_width = right_margin - left_margin
            qr_code_height = (qr_code_width / img_width) * img_height

            # Calculate the vertical position to place the QR code at the top and center it horizontally
            vertical_position = custom_paper_size[1] - qr_code_height - top_margin
            horizontal_position = (custom_paper_size[0] - qr_code_width) / 2

            # Draw the QR code centered at the top of the page
            c.drawImage(qr_img_path, horizontal_position, vertical_position, width=qr_code_width, height=qr_code_height)

            c.save()

            # Save person record with the QR code and PDF paths
            person = Person(
                qr_code=f'qrcodes/{qr_img_filename}',
                qr_code_pdf=f'qrcodes/{pdf_filename}',  # Ensure you have a field for this in your model
                fname=fname,
                lname=lname,
                card_id=card_id,
                card_type=card_type,
                gender=gender,
                img=filename if img else '',  # Use filename, not URL
                city=city,
                phone=phone,
                serial_number=serial_number,
                brand=brand
            )
            person.save()

   
        return render(request, 'pages/add_person.html')

    @staticmethod
    def validate_person_fields(fname, lname, card_id, serial_number):
        errors = {}

        # Check if card_id already exists
        if Person.objects.filter(card_id=card_id).exists():
            errors['card_id'] = 'Card ID already exists.'

        # Check if serial_number already exists
        if Person.objects.filter(serial_number=serial_number).exists():
            errors['serial_number'] = 'Serial Number already exists.'

        # Validate first name length
        if len(fname.strip()) < 2:
            errors['fname'] = 'First name is too short.'

        # Validate last name length
        if len(lname.strip()) < 2:
            errors['lname'] = 'Last name is too short.'

        return errors

    @staticmethod
    def validate_field(request):
        field_name = request.GET.get('field_name', '').strip()
        value = request.GET.get('value', '').strip()

        if field_name == 'card_id':
            if Person.objects.filter(card_id=value).exists():
                return JsonResponse({'error': 'Card ID already exists.'})
        elif field_name == 'serial_number':
            if Person.objects.filter(serial_number=value).exists():
                return JsonResponse({'error': 'Serial Number already exists.'})
        elif field_name == 'fname':
            if len(value) < 2:
                return JsonResponse({'error': 'First name is too short.'})
        elif field_name == 'lname':
            if len(value) < 2:
                return JsonResponse({'error': 'Last name is too short.'})
        else:
            return JsonResponse({'error': 'Invalid field name.'})

        return JsonResponse({'success': True})

    @staticmethod
    @login_required(login_url='index')
    def list_persons(request):
        person_list = Person.objects.all()  # Query your Person model
        paginator = Paginator(person_list, 5)  # Show 5 persons per page

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'pages/list_persons.html', {'page_obj': page_obj})

    @staticmethod
    @login_required(login_url='index')
    def read_person(request, pk):
        person = get_object_or_404(Person, pk=pk)
        pdf_file_path = str(person.qr_code_pdf.path)

        if request.method == 'POST':
            if 'print' in request.POST:
                # Call the function to print the PDF
                print_pdf(pdf_file_path)
                # Respond with JSON indicating success
                return JsonResponse({'status': 'success', 'message': 'PDF sent to printer.'})

        serial_number = person.extracted_serial_number
        return render(request, 'pages/manage_person.html', {
            'person': person,
            'serial_number': serial_number,
            'pdf_file_path': pdf_file_path
        })
    @staticmethod
    @login_required(login_url='index')
    def report_persons(request):
        return render(request, 'pages/report_persons.html')

    @staticmethod
    @login_required(login_url='index')
    @user_access_required('staff')
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
    @user_access_required('staff')
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
    @user_access_required('staff')
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

    @csrf_exempt
    @staticmethod
    @user_access_required('staff')
    def validate_form(request):
        if request.method == 'POST':
            errors = {}

            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            # Validate username
            if username and User.objects.filter(username=username).exists():
                errors['username'] = 'Username already exists.'

            # Validate email
            if email:
                try:
                    validate_email(email)
                    if User.objects.filter(email=email).exists():
                        errors['email'] = 'Email already exists.'
                except ValidationError:
                    errors['email'] = 'Enter a valid email address.'

            # Validate passwords
            if password1:
                if len(password1) < 8:
                    errors['password1'] = 'Password is too short (minimum 8 characters).'
                if password1 != password2:
                    errors['password2'] = 'Passwords do not match.'

            # Validate name
            if first_name and last_name:
                if Person.objects.filter(fname=first_name, lname=last_name).exists():
                    errors['name'] = 'Person with this name already exists.'

            if errors:
                return JsonResponse({'error': errors}, status=400)

            return JsonResponse({'success': True})

        return JsonResponse({'error': 'Invalid request method'}, status=400)

    @staticmethod
    @login_required(login_url='index')
    @user_access_required('staff')
    def read_user(request):
        users = User.objects.all()
        return render(request, 'pages/read_user.html', {'users': users})

    @login_required(login_url='index')
    @user_access_required('staff')
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
    @user_access_required('staff')
    def user_detail(request, id):
        user = get_object_or_404(User, id=id)
        return render(request, 'pages/user_detail.html', {'user': user})

    @staticmethod
    @user_access_required('staff')
    def delete_user(request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user or (user.is_superuser and not request.user.is_superuser):
            return redirect('access_denied')
        if request.method == 'POST':
            user.delete()
            Notification.objects.create(user=request.user, message="User Deleted.")
            return redirect('read_user')
        return render(request, 'pages/delete_user.html', {'user': user})
class ExitView:
    @staticmethod
    def get_last_exit(person_id):
        return ExitRecord.objects.filter(id=person_id).order_by('-exit_time').first()

    @staticmethod
    def extract_serial_number(qr_data):
        constant_part = 'PF9XB382'
        if 'Serial Number:' in qr_data:
            parts = qr_data.split('Serial Number:')
            if len(parts) > 1:
                return parts[1].strip()
        elif constant_part in qr_data:
            constant_index = qr_data.index(constant_part)
            return qr_data[:constant_index].strip()
        return qr_data.strip()

    @staticmethod
    def exit_interface(request):
        if request.method == 'POST':
            qr_data = request.POST.get('qr_data')
            serial_number = ExitView.extract_serial_number(qr_data)
            print(f"This is QR code data: {serial_number}")

            person = Person.objects.filter(
                serial_number__startswith=serial_number
            ).first()
            default_img_url = static('images/default.jpg')
            if person:
                last_exit = ExitView.get_last_exit(person.id)

                # Get current time in CAT timezone
                current_time = timezone.now().astimezone(CAT)
                exit_now = current_time.strftime('%Y-%m-%d %H:%M:%S')

                if last_exit is None or current_time - last_exit.exit_time > TIME_LIMIT:
                    exit_record = ExitRecord.objects.create(person=person, exit_time=current_time)
                else:
                    exit_record = last_exit
                    exit_now = exit_record.exit_time.strftime('%Y-%m-%d %H:%M:%S')

                response_data = {
                    'person': {
                        'fname': person.fname,
                        'lname': person.lname,
                        'brand': person.brand,
                        'serial_number': person.extracted_serial_number,
                        'exit_now': exit_now,
                        'qr_code_type': person.card_type,
                        'img_url': person.img.url if person.img else default_img_url,
                    }
                }

                return JsonResponse(response_data)
            else:
                print("Person not found in db........")
                return JsonResponse({'error': 'No person found with this serial number'}, status=404)

        return render(request, 'pages/exit_interface.html')
    def view_exit(request):
        exit_list = ExitRecord.objects.all()  # Query your Exit model
        paginator = Paginator(exit_list, 5)  # Show 5 exits per page

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'pages/exit_view.html', {'page_obj': page_obj})

    @staticmethod
    def report_exit(request):
        # Logic to generate exit reports if needed
        if request.method == 'POST':
            serial_number = request.POST.get('serial_number')
            try:
                person = Person.objects.get(serial_number=serial_number)
                current_time = timezone.now().astimezone(CAT)
                response_data = {
                    'person': {
                        'fname': person.fname,
                        'lname': person.lname,
                        'serial_number': person.serial_number,
                        'exit_now': current_time.strftime('%Y-%m-%d %H:%M:%S'),  # Current time as exit time
                        'qr_code_type': person.card_type,  # Assuming this is the QR code type
                        'img_url': person.img.url if person.img else '',  # Ensure URL is available
                    }
                }
                return JsonResponse(response_data)
            except Person.DoesNotExist:
                return JsonResponse({'error': 'No person found with this serial number'}, status=404)