from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import serial
import serial.tools.list_ports
import time
from .models import Person


def find_serial_port():
    try:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description:
                return port.device
        return None
    except:
        print("Arduino Error")

def read_card_id_from_serial(port=None, baud_rate=115200, timeout=1):
    try:
        if port is None:
            port = find_serial_port()
        
        if port is None:
            print("No Arduino found")
            return None
    except:
        print("Error")

    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        ser.write(b'#')  # Send '#' to Arduino to start card detection
        while True:
            if ser.in_waiting > 0:
                card_id = ser.readline().decode('utf-8').strip()
                if card_id and card_id not in ['1', '2', '#']:
                    print(f"Received card ID: {card_id}")
                    handle_card_id(card_id, ser)
                    time.sleep(2)  # Wait for 2 seconds before restarting card detection
                    ser.write(b'#')  # Send '#' to Arduino to restart card detection
                    print("Sent '#' to Arduino to restart card detection")
                    return card_id
    except serial.SerialException as e:
        print(f"Serial communication error: {str(e)}")
        return None

def handle_card_id(card_id, ser):
    # Check if card_id corresponds to any Person in the database
    try:
        person = Person.objects.get(card_id=card_id)
        response = '1'  # Recognized card ID
    except Person.DoesNotExist:
        response = '2'  # Unrecognized card ID
    
    # Send response to Arduino
    ser.write(response.encode('utf-8'))
    print(f"Sent response: {response} to Arduino")
