from machine import ADC, Pin
import time

mq135 = ADC(Pin(1))

green_led = Pin(21, Pin.OUT)
red_led = Pin(22, Pin.OUT)

THRESHOLD = 20000

print("MQ135 warming up...")
time.sleep(2)

while True:
    value = mq135.read_u16()
    print("Raw value:", value)
    
    if value > THRESHOLD:
        red_led.value(1)
        green_led.value(0)
    else:
        green_led.value(1)
        red_led.value(0)
    
    time.sleep(2)