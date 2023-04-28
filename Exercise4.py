import ssd1306
from led import Led
from machine import Pin, I2C
from utime import sleep_ms,time


class rotary_encoder:

    def __init__(self):
        self.count = 1 
        self.t0 = time()
        self.mode = True
        self.direction = 1
        
        
    def handler(self, pin):
        print(self.count)
        if rotA.value() == 1 and rotB.value() == 0:
            self.count += 1
            if self.mode == False:
                self.direction = 1
            print("Rotated clockwise")
        elif rotA.value() == 0 and rotB.value() == 1:
            print("Rotated anti-clockwise") 
            if self.mode == False:
                self.direction = -1
            self.count -= 1
        elif self.count > 3:
            self.count = 1
        elif self.count < 1:
            self.count = 3
        
            
            
    def button_pressed(self, pin):
        t1 = time()
        if abs(t1 - self.t0) > 1.0:
            print('Knob pushed')
            self.t0 = t1
            self.mode = not self.mode
            print(self.mode)
            
            
    def get_value(self):
        return self.count


class Oled:
    def __init__(self, width=128, length=64):
        self.width = width
        self.length = length
        self.i2c = I2C(1, sda=Pin(14), scl=Pin(15)) 
        self.oled = ssd1306.SSD1306_I2C(self.width, self.length, self.i2c) 
        
    def write(self, text, x, y):
        self.oled.text(text, x, y)
        
    def show(self):
        self.oled.show()

    def delete(self):
        self.oled.fill(0)


def led_selection():
    oled.delete()
    oled.write('LED D1', 40, 15)
    oled.write('LED D2', 40, 30)
    oled.write('LED D3', 40, 45)
    if rot.count == 1:
        oled.write('> ', 25, 15)
    elif rot.count == 2:
        oled.write('> ', 25, 30)
    elif rot.count == 3:
        oled.write('> ', 25, 45)
    oled.show()


oled = Oled()
rot = rotary_encoder()

rotA = Pin(10, mode = Pin.IN) 
rotB = Pin(11, mode = Pin.IN)  
rotary_push = Pin(12, mode=Pin.IN, pull=Pin.PULL_UP)

rotA.irq(handler = rot.handler, trigger= Pin.IRQ_RISING)
rotB.irq(handler = rot.handler, trigger= Pin.IRQ_RISING)
rotary_push.irq(handler = rot.button_pressed, trigger=Pin.IRQ_RISING)


brightness_led1 = 0
brightness_led2 = 0
brightness_led3 = 0
led_d1 = Led(22, brightness_led1)
led_d2 = Led(21, brightness_led2)
led_d3 = Led(20, brightness_led3)

led_list = [led_d1, led_d2, led_d3]
brightness_list = [brightness_led1, brightness_led2, brightness_led3]


for led in led_list:
    led.off()


max_brightness = 35000 

while True:
    mode = rot.mode
    if mode == True:
        selected_led = rot.count
        led_selection()
    elif mode == False:
        oled.delete()
        oled.write(f"D{selected_led}: {brightness_list[selected_led-1]} PWM", 0, 30)
        oled.write(f"Brightness: {int(brightness_list[selected_led-1]* 100 / max_brightness)}%", 0, 45)
        oled.show()
        if rot.direction == 1:                 
            brightness_list[selected_led-1] += 2000
            rot.direction = 0
        elif rot.direction == -1:
            brightness_list[selected_led-1] -= 2000
            rot.direction = 0
        pwm_value = brightness_list[selected_led-1]
        if pwm_value >= max_brightness:
            brightness_list[selected_led-1] = max_brightness
            pwm_value = max_brightness
        elif pwm_value <= 0:
            pwm_value = 0
            brightness_list[selected_led-1] = 0
        led_list[selected_led-1]._pwm.duty_u16(pwm_value)
        
        
