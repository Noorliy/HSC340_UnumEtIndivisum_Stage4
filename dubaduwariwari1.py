from machine import Pin, ADC
import time
import network

import uasyncio as asyncio
import urequests as urequests 

# ======== KONFIGURASI WIFI DAN UBIDOTS ========
WIFI_SSID = 'OPPO A9 2020'
WIFI_PASSWORD = 'bismillah'
UBIDOTS_TOKEN = 'BBUS-HaZSh1YQOy7sczeUh64WgTlfTCZvuf' 
DEVICE_LABEL = 'esp32'
UBIDOTS_URL = f'https://stem.ubidots.com/app/devices/67ff2ffc9cd1850bd57e44a4'

# ======== API LOKAL UNTUK MONGODB (PC/Laptop) ========
LOCAL_API_URL = '192.168.43.86' 

# ======== SENSOR DAN AKTUATOR SETUP ========
turbidity = ADC(Pin(32))
turbidity.atten(ADC.ATTN_11DB)

ph_sensor = ADC(Pin(33))
ph_sensor.atten(ADC.ATTN_11DB)

tds_sensor = ADC(Pin(34))
tds_sensor.atten(ADC.ATTN_11DB)

pump = Pin(26, Pin.OUT)

# ======== KONEKSI WIFI ========
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Menyambung ke WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Terhubung ke WiFi:", wlan.ifconfig())

# ======== KIRIM KE UBIDOTS ========
def send_to_ubidots(turb, ph, tds):
    headers = {
        "X-Auth-Token": UBIDOTS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "turbidity": turb,
        "ph": ph,
        "tds": tds
    }
    try:
        response = urequests.post(UBIDOTS_URL, headers=headers, json=payload)
        print("Kirim ke Ubidots:", response.status_code)
        response.close()
    except Exception as e:
        print("Gagal kirim ke Ubidots:", e)

# ======== KIRIM KE API LOKAL (UNTUK MONGODB) ========
def send_to_local_api(turb, ph, tds):
    headers = {"Content-Type": "application/json"}
    payload = {
        "turbidity": turb,
        "ph": ph,
        "tds": tds
    }
    try:
        response = urequests.post(LOCAL_API_URL, headers=headers, json=payload)
        print("Kirim ke API Lokal:", response.status_code)
        response.close()
    except Exception as e:
        print("Gagal kirim ke API lokal:", e)

# ======== PROGRAM UTAMA ========
connect_wifi()

while True:
    turbidity_val = turbidity.read()
    print("Turbidity:", turbidity_val)

    if turbidity_val > 1600:
        pump.value(1)
        print("Air keruh: Mengalir ke filter.")
        ph_val = 0
        tds_val = 0
    else:
        pump.value(0)
        print("Air jernih: Mengalir ke bak selanjutnya.")
        
        time.sleep(5)
        ph_val = ph_sensor.read()
        tds_val = tds_sensor.read()
        print("PH:", ph_val, "TDS:", tds_val)

    # Kirim ke Ubidots & MongoDB
    send_to_ubidots(turbidity_val, ph_val, tds_val)
    send_to_local_api(turbidity_val, ph_val, tds_val)

    time.sleep(10)