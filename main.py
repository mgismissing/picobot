import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine

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
def getwebpage(pagename):
    if pagename == "/control":
        with open("control.html") as file:
            return file.read()
def serve(conn):
    while True:
        client = conn.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        print(f"SOCK > WGET {request}")
        if request == "/control?c=1":
            pico_led.on()
        elif request =="/control?c=0":
            pico_led.off()
        html = getwebpage("/control")
        client.send(html)
        client.close()


try:
    localip = connect()
    conn = open_socket(localip)
    serve(conn=conn)
except KeyboardInterrupt:
    pass
except:
    machine.reset()