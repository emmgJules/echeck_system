# # Import necessary libraries
# import cv2
# import numpy as np
# import face_recognition
# import os
# from django.http import StreamingHttpResponse
# from django.views.decorators import gzip

# import os

# # Define a temporary folder to store captured images
# temp_image_folder = 'temp_images'

# # Function to create the temporary folder if it doesn't exist
# def create_temp_folder():
#     if not os.path.exists(temp_image_folder):
#         os.makedirs(temp_image_folder)


# # Function to generate frames with face recognition
# def generate_frames():
#     vid = cv2.VideoCapture(0)

#     while True:
#         success, frame = vid.read()
#         if not success:
#             break

#         # Resize the frame for faster processing
#         resized_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#         rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

#         # Find all face locations and encodings in the current frame
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for face_encoding, face_location in zip(face_encodings, face_locations):
#             # Compare the face encoding with each image in the temp_images folder
#             create_temp_folder()
#             for filename in os.listdir(temp_image_folder):
#                 image_path = os.path.join(temp_image_folder, filename)
#                 known_image = face_recognition.load_image_file(image_path)
#                 known_encoding = face_recognition.face_encodings(known_image)[0]
                
#                 # Compare the face encodings
#                 matches = face_recognition.compare_faces([known_encoding], face_encoding)
#                 if matches[0]:
#                     # If a match is found, get the name of the image and draw a rectangle
#                     name = os.path.splitext(filename)[0]
#                     top, right, bottom, left = face_location
#                     top *= 4
#                     right *= 4
#                     bottom *= 4
#                     left *= 4
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#                     cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

#         # Encode the frame as JPEG
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# # Route for video feed with face recognition
# @gzip.gzip_page
# def video_feed(request):
#     return StreamingHttpResponse(generate_frames(), content_type="multipart/x-mixed-replace;boundary=frame")
