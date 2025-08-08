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

# Set up colours
white = colour(255,255,255)
red = colour(255,0,0)
green = colour(0,255,0)
blue = colour(0,0,255)
yellow = colour(255,255,0)
orange = colour(255,128,30)
black = colour(0,0,0)
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
    
def status_screen(tap_id, status, color):
    init_screen()
    hollow_circle(120, 125, 75, color, 5, grey)
    LCD.write_text("Tap", 95, 70, 2, white)
    LCD.write_text(tap_id, 100, 105, 5, white)
    LCD.write_text(status, 90, 165, 2, white)
    LCD.show()

def pressure_to_angle(pressure_mbar):
    """Convert pressure to gauge angle (0-270° range)"""
    # Logarithmic scale for better vacuum resolution
    if pressure_mbar <= 0:
        return 270  # Prevent math errors
    
    log_max = math.log10(ATM_PRESSURE)
    log_min = math.log10(MIN_PRESSURE)
    log_p = math.log10(max(pressure_mbar, MIN_PRESSURE))
    
    # Scale to 0-270 degrees (left to right)
    return 270 - (log_p - log_min) / (log_max - log_min) * 270

def pressure_screen(pressure_mbar):
    """Display pressure gauge with atmospheric on left"""
    LCD.fill_rect(0, 40, 240, 170, black)
    
    # Draw gauge outline
    hollow_circle(center_x, center_y, 80, orange, 5, black)
    
    # Draw scale ticks (left to right)
    r = 75
    pressure_points = [ATM_PRESSURE, 100, 10, 1]
    
    for p in pressure_points:
        angle = pressure_to_angle(p)
        theta_rad = math.radians(angle)
        xn = -int(r * math.cos(theta_rad))
        yn = -int(r * math.sin(theta_rad))
        LCD.line(center_x, center_y, center_x + xn, center_y + yn, white)
        
        # Label position
        label_x = center_x + int((r+15) * math.cos(theta_rad))
        label_y = center_y + int((r+15) * math.sin(theta_rad))
        LCD.write_text(f"{p}", label_x-10, label_y-5, 1, white)
    
    # Clear center
    circle(center_x, center_y, 60, black)
    
    # Calculate pointer position
    angle = pressure_to_angle(pressure_mbar)
    theta_rad = math.radians(angle)
    pointer_length = 55
    xn = -int(pointer_length * math.cos(theta_rad))
    yn = -int(pointer_length * math.sin(theta_rad))
    
    # Draw pointer
    pointer_color = red
    LCD.line(center_x, center_y, center_x + xn, center_y + yn, pointer_color)
    LCD.line(center_x, center_y, center_x + int(yn/5), center_y - int(xn/5), pointer_color)
    LCD.line(center_x, center_y, center_x - int(yn/5), center_y + int(xn/5), pointer_color)
    
    # Draw center circle
    circle(center_x, center_y, 5, pointer_color)
    
    # Display pressure value
    if pressure_mbar >= 1:
        pressure_text = f"{pressure_mbar:.1f} mbar"
    else:
        pressure_text = f"{pressure_mbar:.3f} mbar"
    LCD.write_text(pressure_text, center_x - 50, center_y - 20, 2, white)

def demo_pressure_gauge():
    """Simulate pressure changes from ATM to vacuum"""
    init_screen()
    
    pressure = ATM_PRESSURE  # Start at atmospheric
    direction = -1  # Start pumping down
    
    while True:
        # Exponential pressure change
        if direction < 0:  # Pumping down
            pressure *= 0.95
            if pressure < MIN_PRESSURE:
                pressure = MIN_PRESSURE
                direction = 1  # Start venting
        else:  # Venting up
            pressure *= 1.05
            if pressure > ATM_PRESSURE:
                pressure = ATM_PRESSURE
                direction = -1  # Start pumping
        
        pressure_screen(pressure)
        LCD.show()
        
        if touch.Flag == 1:
            touch.Flag = 0
            break
        
        time.sleep(0.1)

if __name__=='__main__':
    while True:
        demo_pressure_gauge()
        status_screen("A", "Idle", orange)