import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine

with open("index.html") as file:
    webpage = file.read()

ssid = "robotica"
password = "77SERVER"

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    i = 0
    while wlan.isconnected() == False:
        i += 1
        print(f"WLAN > CONN {i}")
        sleep(1)
        if i >= 0x20:
            print(f"WLAN > CERR")
            while True:
                sleep(0xFFFF)
    localip = wlan.ifconfig()[0]
    print(f"WLAN > DONE {localip}")
    return localip
def open_socket(ip):
    # Open a socket
    addr = (ip, 80)
    conn = socket.socket()
    conn.bind(addr)
    conn.listen(1)
    print(f"SOCK > CONN")
    return conn


try:
    localip = connect()
    conn = open_socket(localip)
except:
    machine.reset()