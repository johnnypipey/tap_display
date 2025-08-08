# main.py - Pressure Gauge for Schlenk Line
from display import LCD_1inch28, Touch_CST816T
from machine import Pin,I2C,SPI,PWM,Timer,ADC
import framebuf
import time
import math
import random

# Initialize Display
LCD = LCD_1inch28()
LCD.set_bl_pwm(65535)

# Initialize Touch
touch = Touch_CST816T(mode=1)
touch.Set_Mode(1)

def colour(R,G,B): # Convert RGB888 to RGB565
    return (((G&0b00011100)<<3) +((B&0b11111000)>>3)<<8) + (R&0b11111000)+((G&0b11100000)>>5)

def circle(x,y,r,c):
    LCD.hline(x-r,y,r*2,c)
    for i in range(1,r):
        a = int(math.sqrt(r*r-i*i)) # Pythagoras!
        LCD.hline(x-a,y+i,a*2,c) # Lower half
        LCD.hline(x-a,y-i,a*2,c) # Upper half
        
def hollow_circle(x0, y0, radius, color, thickness=1, bg_color=None):
    if bg_color is None:
        bg_color = black
    
    circle(x0, y0, radius, color)
    if radius > thickness:
        circle(x0, y0, radius - thickness, bg_color)
        
def button(xx, yy, txt, bc, fc):
    """Draw a square button at (xx, yy) with text"""
    LCD.rect(xx, yy, 70, 70, bc, True)       # Background square
    LCD.write_text(txt, xx+8, yy+10, 1, fc) 

# Set up colours
white = colour(255,255,255)
red = colour(255,0,0)
green = colour(0,255,0)
blue = colour(0,0,255)
yellow = colour(255,255,0)
orange = colour(255,128,30)
black = colour(0,0,0)
grey = colour(30,30,30)

center_x = LCD.width // 2
center_y = LCD.height // 2

# Pressure constants
ATM_PRESSURE = 1013  # mbar
MIN_PRESSURE = 1      # mbar (minimum vacuum we'll display)

def init_screen():
    LCD.fill(black)
    hollow_circle(120, 120, 120, orange, 10, black)
    LCD.fill_rect(0, 0, 240, 40, orange)
    LCD.text("AutoSchlenk", 78, 25, white)
    LCD.fill_rect(0,210,240,35,0x180f)
    LCD.text("V1.0",105,220,white)
    

        
def gesture_test_screen():
    """Gesture test screen with visual feedback"""
    # Initialize gesture mode
    Touch.Mode = 0
    Touch.Set_Mode(Touch.Mode)
    
    # Define gesture names and codes
    gestures = [
        {"name": "UP", "code": 0x01, "color": LCD.red},
        {"name": "DOWN", "code": 0x02, "color": LCD.green},
        {"name": "LEFT", "code": 0x03, "color": LCD.blue},
        {"name": "RIGHT", "code": 0x04, "color": LCD.brown},
        {"name": "LONG PRESS", "code": 0x0C, "color": LCD.orange},
        {"name": "DOUBLE CLICK", "code": 0x0B, "color": 0x07E0}  # Cyan
    ]
    
    # Header and footer
    LCD.fill(LCD.white)
    LCD.fill_rect(0, 0, 240, 40, 0x180f)  # Header
    LCD.write_text("Gesture Test", 70, 15, 2, LCD.white)
    
    LCD.fill_rect(0, 200, 240, 40, 0x180f)  # Footer
    LCD.write_text("Exit", 105, 215, 2, LCD.white)
    
    # Instructions
    LCD.write_text("Perform gestures", 50, 60, 1, LCD.black)
    LCD.write_text("as they appear", 55, 80, 1, LCD.black)
    LCD.show()
    time.sleep(2)
    
    # Test each gesture
    for gesture in gestures:
        LCD.fill_rect(0, 40, 240, 160, LCD.white)  # Clear main area
        
        # Draw prompt
        LCD.fill_rect(40, 80, 160, 80, gesture["color"])
        LCD.write_text(gesture["name"], 70, 110, 2, LCD.white)
        LCD.show()
        
        # Wait for correct gesture
        while Touch.Gestures != gesture["code"]:
            time.sleep(0.1)
        
        # Visual feedback
        LCD.fill_rect(40, 80, 160, 80, LCD.white)
        LCD.write_text("✓ " + gesture["name"], 60, 110, 2, LCD.black)
        LCD.show()
        time.sleep(1)
    
    # Completion message
    LCD.fill_rect(0, 40, 240, 160, LCD.white)
    LCD.write_text("All gestures", 70, 90, 2, LCD.black)
    LCD.write_text("completed!", 75, 120, 2, LCD.black)
    LCD.show()
    
    # Wait for exit touch
    while True:
        if Touch.Flag == 1:
            if 200 <= Touch.Y_point <= 240:  # Footer touched
                Touch.Flag = 0
                break
        time.sleep(0.1)

# Example usage in your main loop (add this to your existing __main__ section)
if __name__ == '__main__':
    LCD = LCD_1inch28()
    LCD.set_bl_pwm(65535)
    Touch = Touch_CST816T(mode=1, LCD=LCD)
    while True:
        gesture_test_screen()
