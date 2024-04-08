from microbit import *
import machine
from ssd1306 import initialize, clear_oled, draw_text, display_oled
import utime

start_time = 0
stop_time = 0
moisture_threshold = 60
dry = 0
well_watered = 0
overhydrated = 0
fastest_pot = ""

oled_width = 128
oled_height = 64

# Initialize OLED display
initialize(pinout={'sda': pin20, 'scl': pin19})

def start_stopwatch():
    global start_time
    start_time = utime.ticks_ms()

def stop_stopwatch():
    global stop_time
    stop_time = utime.ticks_ms()

def upload_data_to_thingspeak():
    global dry, well_watered, overhydrated
    ESP8266_IoT.connect_thing_speak()  # Connect to ThingSpeak
    ESP8266_IoT.set_data("ANOEVA0S3DWQEYH0", dry, well_watered, overhydrated)  # Set data fields
    ESP8266_IoT.upload_data()  # Upload data to ThingSpeak

def display_result():
    global fastest_pot
    clear_oled()
    if fastest_pot == "":
        draw_text("No fastest pot", 0, 0)
    else:
        draw_text(f"Fastest pot: {fastest_pot}", 0, 0)
    display_oled()

def measure_soil_moisture():
    global dry, well_watered, overhydrated
    dry = pin1.read_analog()
    well_watered = pin2.read_analog()
    overhydrated = pin3.read_analog()

# Connect to WiFi
ESP8266_IoT.init_wifi(SerialPin.P8, SerialPin.P12, BaudRate.BAUD_RATE115200)
ESP8266_IoT.connect_wifi("", "")

while not ESP8266_IoT.wifi_state(False):  # Check if WiFi connection failed
    clear_oled()
    draw_text("WiFi not connected", 0, 0)
    display_oled()
    sleep(1000)

while True:
    if button_a.was_pressed():
        start_stopwatch()

    measure_soil_moisture()

    if max(dry, well_watered, overhydrated) > moisture_threshold:
        stop_stopwatch()

        elapsed_dry = utime.ticks_diff(stop_time, start_time)

        start_stopwatch()
        sleep(1000)

        measure_soil_moisture()

        stop_stopwatch()

        elapsed_well_watered = utime.ticks_diff(stop_time, start_time)

        start_stopwatch()
        sleep(1000)

        measure_soil_moisture()

        stop_stopwatch()

        elapsed_overhydrated = utime.ticks_diff(stop_time, start_time)

        if elapsed_dry < elapsed_well_watered and elapsed_dry < elapsed_overhydrated:
            fastest_pot = "dry"
        elif elapsed_well_watered < elapsed_dry and elapsed_well_watered < elapsed_overhydrated:
            fastest_pot = "well_watered"
        else:
            fastest_pot = "overhydrated"

        ESP8266_IoT.connect_wifi("alto_wifi", "aventail123")  # Reconnect to WiFi before uploading
        while not ESP8266_IoT.wifi_state(False):  # Check if WiFi connection failed
            clear_oled()
            draw_text("WiFi not connected", 0, 0)
            display_oled()
            sleep(1000)
        
        upload_data_to_thingspeak()
        display_result()

    sleep(100)
