import network, socket, machine
from time import sleep
from ssd1306 import SSD1306_I2C

ssid = "robotica"
password = "77SERVER"

scr = SSD1306_I2C(128, 64, machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16), freq=200000))
scr.poweroff()
scr.poweron()
scr.invert(1)

FMR = 1000000
FWR = 750000
NMR = 500000
BWR = 250000
BMR = 100000

servo_l = machine.PWM(machine.Pin(2))
servo_l.freq(50)
servo_l.duty_ns(NMR)

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
            servo_l.duty_ns(FWR)
        elif request == "/control?c=2":
            servo_l.duty_ns(BWR)
        elif request == "/control?c=3":
            servo_l.duty_ns(BWR)
        elif request == "/control?c=4":
            servo_l.duty_ns(FWR)
        elif request =="/control?c=0":
            servo_l.duty_ns(NMR)
        html = "404: Not found"
        if request[0:8] == "/control":
            html = getwebpage("/control")
        client.send(html)
        client.close()


try:
    localip = connect()
    scr.text(str(localip), 5, 5)
    scr.show()
    conn = open_socket(localip)
    serve(conn=conn)
except KeyboardInterrupt:
    pass
except:
    machine.reset()