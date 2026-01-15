from machine import ADC, Pin
import time

mq135 = ADC(Pin(1))

green_led = Pin(21, Pin.OUT)
red_led = Pin(12, Pin.OUT)

THRESHOLD = 20000

print("MQ135 warming up...")
time.sleep(120)

while True:
    value = mq135.read_u16()
    print("Raw value:", value)
    
    if value > THRESHOLD