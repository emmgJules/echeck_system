from django.shortcuts import render, redirect, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Students, Entry, UserProfile, Person
from .forms import PersonForm,UserProfileForm
import cv2
import face_recognition
import numpy as np
import base64
import os
import uuid
import json

# Create a temporary image folder if not exists
def create_temp_image_folder():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    temp_image_folder = os.path.join(base_dir, 'students_images')
    if not os.path.exists(temp_image_folder):
        os.makedirs(temp_image_folder)
    return temp_image_folder

temp_image_folder = create_temp_image_folder()

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
    return render(request, 'skydash/login.html')

@login_required(login_url='login')
def dash(request):
    q = request.GET.get('q', '')
    students = Person.objects.filter(Q(fname__icontains=q) )
    return render(request, 'skydash/pages/dashboard.html', {'students': students})

@login_required(login_url='login')
def search(request):
    q = request.GET.get('q', '')
    students = Students.objects.filter(Q(fname__icontains=q) | Q(lname__icontains=q) | Q(serial_number__icontains=q))
    return render(request, 'skydash/pages/search.html', {'students': students})

class PersonView:
    form_class = PersonForm

    @staticmethod
    def create_person(request):
        if request.method == 'POST':
            form = PersonForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('view_students')
        else:
            form = PersonForm()
        return render(request, 'skydash/pages/add_person.html', {'form': form})

    @staticmethod
    def list_persons(request):
        persons = Person.objects.all()
        return render(request, 'view_persons.html', {'persons': persons})

    @staticmethod
    def read_person(request, pk):
        person = get_object_or_404(Person, pk=pk)
        return render(request, 'read_person.html', {'person': person})

    @staticmethod
    def update_person(request, pk):
        person = get_object_or_404(Person, pk=pk)
        if request.method == 'POST':
            form = PersonForm(request.POST, instance=person)
            if form.is_valid():
                form.save()
                return redirect('view_students')
        else:
            form = PersonForm(instance=person)
        return render(request, 'skydash/pages/edit_person.html', {'form': form})

    @staticmethod
    def delete_person(request, pk):
        person = get_object_or_404(Person, pk=pk)
        if request.method == 'POST':
            person.delete()
            return redirect('view_students')
        return render(request, 'skydash/pages/confirm_delete.html', {'person': person})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    profile_form = UserProfileForm(instance=user_profile)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('user-profile', pk=user.id)
    context = {'profile_form': profile_form}
    return render(request, 'skydash/pages/edit_user.html', context)

def add_entry(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        try:
            student = Students.objects.get(fname=fname, lname=lname)
            entry = Entry.objects.create(student_id=student.id)
            return redirect('view_entries')
        except Students.DoesNotExist:
            return HttpResponse("Student Not Found")
    return render(request, 'skydash/pages/addentry.html')

def digital(request):
    return render(request, 'skydash/pages/digital.html')

def view_students(request):
    students = Students.objects.all()
    return render(request, 'skydash/pages/viewstudent.html', {'students': students})

def view_entries(request):
    entries = Entry.objects.all()
    return render(request, 'skydash/pages/viewentry.html', {'entries': entries})

def viewstudent(request, id):
    student = get_object_or_404(Students, id=id)
    return render(request, "skydash/pages/managestudent.html", {'student': student})

def edit_student(request, pk):
    student = get_object_or_404(Students, pk=pk)
    if request.method == 'POST':
        student.fname = request.POST.get('firstName')
        student.lname = request.POST.get('lastName')
        student.postion = request.POST.get('postion')
        student.gender = request.POST.get('gender')
        student.city = request.POST.get('city')
        student.phone = request.POST.get('phone')
        student.serial_number = request.POST.get('serial_number')
        student.brand = request.POST.get('brand')
        student.img = request.POST.get('img')
        student.save()
        return redirect('view_students')
    return render(request, 'skydash/pages/edit_student.html', {'student': student})

def delete_student(request, pk):
    student = get_object_or_404(Students, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('view_students')
    return render(request, 'skydash/pages/delete_student.html', {'student': student})

@csrf_exempt
def save_image(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            image_data = data.get('image_data')

            if image_data and first_name and last_name:
                format, imgstr = image_data.split(';base64,') 
                nparr = np.frombuffer(base64.b64decode(imgstr), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                image_filename = f'{first_name}_{last_name}_{uuid.uuid4().hex}.jpg'
                image_path = os.path.join(temp_image_folder, image_filename)
                cv2.imwrite(image_path, img)

                face_encoding = face_recognition.face_encodings(img)
                if face_encoding:
                    face_encoding_str = base64.b64encode(face_encoding[0].tobytes()).decode('utf-8')
                    return JsonResponse({'success': True, 'message': 'Image captured successfully', 'image_filename': image_filename, 'face_encoding': face_encoding_str})
                else:
                    return JsonResponse({'success': False, 'message': 'No face detected in the image'})
            else:
                return JsonResponse({'success': False, 'message': 'Incomplete data received'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def resize(img, size):
    width = int(img.shape[1] * size)
    height = int(img.shape[0] * size)
    dimension = (width, height)
    return cv2.resize(img, dimension, interpolation=cv2.INTER_AREA)

path = temp_image_folder
studentimgs = []
studentnames = []
mylist = os.listdir(path)
for cl in mylist:
    curimg = cv2.imread(f'{path}/{cl}')
    studentimgs.append(curimg)
    studentnames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    encoding_list = []
    for img in images:
        img = resize(img, 0.50)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoding = face_recognition.face_encodings(img)[0]
        encoding_list.append(encoding)
    return encoding_list

encode_list = findEncodings(studentimgs)
print("Number of face encodings:", len(encode_list))


def generate_frames():
    vid = cv2.VideoCapture(0)
    while True:
        success, frame = vid.read()
        frames = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        frames = cv2.cvtColor(frames, cv2.COLOR_BGR2RGB)
        face_in_frame = face_recognition.face_locations(frames)
        encoding_in_frame = face_recognition.face_encodings(frames, face_in_frame)

        for incodeface, face_loc in zip(encoding_in_frame, face_in_frame):
            matches = face_recognition.compare_faces(encode_list, incodeface)
            facedis = face_recognition.face_distance(encode_list, incodeface)
            matchindex = np.argmin(facedis)
            if matches[matchindex]:
                name = studentnames[matchindex]
                name=name + '.jpg'
                print(f"This is The names {name}")
                try:

                    student=Students.objects.get(img=name) 
                    stn = student.fname + ' ' + student.lname
                    student_info = {'id': student.id, 'name': stn}
                    student_info_json = json.dumps(student_info)
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.rectangle(frame, (x1, y2 - 25), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(frame, stn, (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                


                    _, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()

                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
                        b'Content-Type: application/json\r\n\r\n' + student_info_json.encode() + b'\r\n')
                except Students.DoesNotExist:
                    pass
            