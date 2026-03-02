from machine import Pin, SPI
from mfrc522 import MFRC522
import time

spi = SPI(1, baudrate=2500000, polarity=0, phase=0, sck=Pin(6), mosi=Pin(7), miso=Pin(2))
rdr = MFRC522(spi=spi, gpioRst=9, gpioCs=10)

print("Scan a RFID tag")

while True:
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, uid) = rdr.anticoll()
        if stat == rdr.OK:
            tag_id = "".join("{:02X}".format(x) for x in uid)
            print("UID:", tag_id)
    time.sleep(0.2)