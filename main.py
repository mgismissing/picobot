import network, socket, machine
from time import sleep
from ssd1306 import SSD1306_I2C
from conf import ssid, password

print("BUZZ > INIT")
buzzer = machine.PWM(machine.Pin(9))
def snd(pwm, freq, volume):
    pwm.freq(freq)
    pwm.duty_u16(volume)

print("SLED > INIT")
sled = machine.Pin(3, machine.Pin.OUT)

print("OLED > INIT")
scr = SSD1306_I2C(128, 64, machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16), freq=200000))
scr.poweroff()
scr.poweron()
with open("dm.s", "r") as s:
    if s.read() == "0":
        scr.invert(0)
    elif s.read() == "1":
        scr.invert(1)
    else:
        scr.invert(1)
        with open("dm.s", "w") as sw:
            sw.write("1")

print("MOVE > INIT")
FMR = 1000000
FWR = 750000
NMR = 500000
BWR = 250000
BMR = 100000

print("MOVE > LSET")
servo_l = machine.PWM(machine.Pin(2))
servo_l.freq(50)
servo_l.duty_ns(NMR)

print("BUZZ > TEST")
snd(buzzer, 300, 1000)
sleep(0.1)
snd(buzzer, 300, 0)

print("SLED > DSOK")
sled.value(1)

def connect():
    #Connect to WLAN
    print("WLAN > INIT")
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
            scr.fill(0)
            scr.text("Connection Error", 0, 5)
            scr.text("Make sure the", 0, 18)
            scr.text("WiFi you are", 0, 27)
            scr.text("trying to", 0, 36)
            scr.text("connect to", 0, 45)
            scr.text("exists.", 0, 54)
            scr.show()
            sled.value(0)
            for i in range(3):
                snd(buzzer, 500, 1000)
                sleep(0.1)
                snd(buzzer, 300, 0)
                sleep(0.1)
            while True:
                sleep(0.2)
                sled.value(1)
                sleep(0.2)
                sled.value(0)
        scr.fill(0)
        scr.text(f"Please wait... {i}", 0, 5)
        scr.text("Connecting to:", 0, 18)
        scr.text(ssid, 0, 27)
        scr.text(f"{password[0:2]}{"*" * (len(password) - 3)}{password[-1]}", 0, 36)
        scr.text("Connect to this", 0, 45)
        scr.text("WiFi.", 0, 54)
        scr.show()
    localip = wlan.ifconfig()[0]
    print(f"WLAN > DONE {localip}")
    return localip
def open_socket(ip):
    # Open a socket
    addr = (ip, 80)
    conn = socket.socket()
    conn.bind(addr)
    conn.listen(1)
    print("SOCK > OPEN")
    return conn
def getwebpage(pagename):
    if pagename == "/control":
        with open("control.html") as file:
            return file.read()
    if pagename == "/reqerr/404":
        with open("reqerr_404.html") as file:
            return file.read()
    if pagename == "/info":
        with open("info.html") as file:
            return file.read()
    return "Internal Error: Could not GET /reqerr/404"
def serve(conn):
    firstconn = True
    while True:
        client = conn.accept()[0]
        request = client.recv(1024)
        request = str(request)
        if firstconn:
            firstconn = False
            scr.fill(0)
            scr.text(str(localip), 0, 5)
            scr.text("You successfully", 0, 18)
            scr.text("connected to the", 0, 27)
            scr.text("PicoBot! To see", 0, 36)
            scr.text("examples go to", 0, 45)
            scr.text("bit.ly/xpicobot", 0, 54)
            scr.show()
            snd(buzzer, 659, 1000)
            sleep(0.1)
            snd(buzzer, 523, 1000)
            sleep(0.2)
            snd(buzzer, 300, 0)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        # Control
        if request == "/control?c=1":
            print("MOVE > LFWR")
            servo_l.duty_ns(FWR)
        elif request == "/control?c=2":
            print("MOVE > LBWR")
            servo_l.duty_ns(BWR)
        elif request == "/control?c=3":
            print("MOVE > LBWR")
            servo_l.duty_ns(BWR)
        elif request == "/control?c=4":
            print("MOVE > LFWR")
            servo_l.duty_ns(FWR)
        elif request == "/control?c=0":
            print("MOVE > LNMR")
            servo_l.duty_ns(NMR)
        # Settings
        elif request == "/control?dm=0":
            scr.invert(0)
            with open("dm.s", "w") as s:
                s.write("0")
        elif request == "/control?dm=1":
            scr.invert(1)
            with open("dm.s", "w") as s:
                s.write("1")
        print(f"SOCK > WGET {request}")
        html = getwebpage("/reqerr/404")
        if request.split("?")[0] == "/control":
            print("SOCK > SEND /control")
            html = getwebpage("/control")
        elif request.split("?")[0] == "/reqerr/404":
            print("SOCK > SEND /reqerr/404")
            html = getwebpage("/reqerr/404")
        elif request.split("?")[0] == "/info" or request.split("?")[0] == "/":
            print("SOCK > SEND /info")
            html = getwebpage("/info")
        client.send(html)
        client.close()
try:
    localip = connect()
    scr.fill(0)
    scr.text(str(localip), 0, 5)
    scr.text("Type the number", 0, 18)
    scr.text("above in a web", 0, 27)
    scr.text("browser. Make", 0, 36)
    scr.text("sure you're on", 0, 45)
    scr.text("the same WiFi.", 0, 54)
    scr.show()
    conn = open_socket(localip)
    snd(buzzer, 400, 1000)
    sleep(0.1)
    snd(buzzer, 300, 0)
    serve(conn=conn)
except KeyboardInterrupt:
    pass
except:
    machine.reset()