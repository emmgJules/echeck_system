# Assuming you have a Django app named 'app_name'

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import serial
import serial.tools.list_ports
import time

# List of known card IDs for testing purposes
KNOWN_CARD_IDS = ['1234567890', 'da1ef8900', '1122334455']

@csrf_exempt
def fetch_card_id(request):
    if request.method == 'GET':
        card_id = read_card_id_from_serial()
        if card_id:
            return JsonResponse({'card_id': card_id})
        else:
            return JsonResponse({'error': 'Failed to fetch card ID'}, status=500)

def find_serial_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description:
            return port.device
    return None

def read_card_id_from_serial(port=None, baud_rate=115200, timeout=1):
    if port is None:
        port = find_serial_port()
    
    if port is None:
        print("No Arduino found")
        return None

    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        ser.write('#'.encode('utf-8'))  # Send '#' to Arduino to start card detection
        while True:
            if ser.in_waiting > 0:
                card_id = ser.readline().decode('utf-8').strip()
                if card_id and card_id not in ['1', '2', '#']:
                    print(f"Received card ID: {card_id}")
                    handle_card_id(card_id, ser)
                    time.sleep(2)  # Wait for 2 seconds before restarting card detection
                    ser.write('#'.encode('utf-8'))  # Send '#' to Arduino to restart card detection
                    print("Sent '#' to Arduino to restart card detection")
                    return card_id
    except serial.SerialException as e:
        print(f"Serial communication error: {str(e)}")
        return None

def handle_card_id(card_id, ser):
    # Check if card_id is in the known list
    if card_id in KNOWN_CARD_IDS:
        response = '1'
    else:
        response = '2'
    
    # Send response to Arduino
    ser.write(response.encode('utf-8'))
    print(f"Sent response: {response} to Arduino")
