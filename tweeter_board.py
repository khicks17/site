import serial
import requests

def main():
    arduino = serial.Serial("COM21")

    while True:
        raw_msg = arduino.readline()
        msg_str = raw_msg.decode('ascii')
        msg = msg_str.rstrip()
        print("Got:", msg)
        if msg == 'button':
            print("Button Pressed")
            result = requests.get("http://notkyle.wattsworth.net/like.json?id=8")
            print(result.json())
main()
