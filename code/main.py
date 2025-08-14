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
    
def draw_triangle(x1, y1, x2, y2, x3, y3, outline_color, fill_color=None, thickness=3):
    """Draw triangle with thick outline by drawing two triangles"""
    if fill_color is None:
        fill_color = black  # If no fill color, make it transparent
    
    # Calculate center point for scaling
    center_x = (x1 + x2 + x3) // 3
    center_y = (y1 + y2 + y3) // 3
    
    # Draw the larger outline triangle first
    if thickness > 0:
        # Calculate scaled up points
        scale = 1 + (thickness * 0.08)  # Adjust this factor to control thickness
        x1_out = int(center_x + (x1 - center_x) * scale)
        y1_out = int(center_y + (y1 - center_y) * scale)
        x2_out = int(center_x + (x2 - center_x) * scale)
        y2_out = int(center_y + (y2 - center_y) * scale)
        x3_out = int(center_x + (x3 - center_x) * scale)
        y3_out = int(center_y + (y3 - center_y) * scale)
        
        # Draw and fill the larger outline triangle
        LCD.line(x1_out, y1_out, x2_out, y2_out, outline_color)
        LCD.line(x2_out, y2_out, x3_out, y3_out, outline_color)
        LCD.line(x3_out, y3_out, x1_out, y1_out, outline_color)
        fill_triangle(x1_out, y1_out, x2_out, y2_out, x3_out, y3_out, outline_color)
    
    # Then draw the smaller filled triangle
    LCD.line(x1, y1, x2, y2, fill_color)
    LCD.line(x2, y2, x3, y3, fill_color)
    LCD.line(x3, y3, x1, y1, fill_color)
    fill_triangle(x1, y1, x2, y2, x3, y3, fill_color)

def fill_triangle(x1, y1, x2, y2, x3, y3, color):
    """Helper function to fill a triangle"""
    min_y = min(y1, y2, y3)
    max_y = max(y1, y2, y3)
    
    for y in range(min_y, max_y + 1):
        x_points = []
        edges = [(x1, y1, x2, y2), (x2, y2, x3, y3), (x3, y3, x1, y1)]
        
        for (xa, ya, xb, yb) in edges:
            if (ya <= y <= yb) or (yb <= y <= ya):
                if ya != yb:
                    x = int(xa + (y - ya) * (xb - xa) / (yb - ya))
                    x_points.append(x)
        
        if len(x_points) >= 2:
            LCD.hline(min(x_points), y, max(x_points) - min(x_points), color)

# Set up colours
white = colour(255,255,255)
red = colour(255,0,0)
dark_red = colour(156,0,0)
darker_red = colour(80,0,0)
green = colour(0,255,0)
blue = colour(0,0,255)
yellow = colour(255,255,0)
orange = colour(255,128,30)
dark_orange = colour(168, 77, 7)
black = colour(0,0,0)
grey = colour(30,30,30)
purple = colour(135, 6, 186)
purple = colour(135, 6, 186)
dark_purple = colour(89, 4, 122)
darker_purple = colour(54, 1, 74)

center_x = LCD.width // 2
center_y = LCD.height // 2

# Pressure constants
ATM_PRESSURE = 1013  # mbar
MIN_PRESSURE = 1      # mbar (minimum vacuum we'll display)

def init_screen():
    LCD.fill(black)
    hollow_circle(120, 120, 120, orange, 7, black)
    hollow_circle(120, 120, 115, dark_orange, 7, black)
    LCD.fill_rect(0, 0, 240, 30, orange)    
    LCD.text("AutoSchlenk", 78, 15, white)
    LCD.fill_rect(0,215,230,50,0x180f)
    LCD.text("V0.1",105,225,white)
    
def status_screen(tap_id, tap_status, motor_status, color):
    init_screen()
    hollow_circle(120, 95, 60, red, 5, grey)
    hollow_circle(120, 95, 55, dark_red, 5, darker_red)
    LCD.write_text("Motor", 100, 55, 1, white)
    LCD.write_text(motor_status, 92, 65, 1, white)
    hollow_circle(120, 145, 65, purple, 5, grey) #horizontal,vertical,size
    hollow_circle(120, 145, 60, dark_purple, 5, darker_purple) #horizontal,vertical,size
    LCD.write_text("Tap", 95, 110, 2, white)
    LCD.write_text(tap_id, 105, 135, 4, white)
    LCD.write_text(tap_status, 105, 175, 1, white)
    draw_triangle(10, 120, 40, 90, 40, 150, green, orange, thickness=5)
    draw_triangle(230, 120, 200, 90, 200, 150, green, orange, thickness=5)


    
    LCD.show()

# Example usage in your main loop (add this to your existing __main__ section)
if __name__ == '__main__':
    while True:
        status_screen("A", "Idle","Enabled", orange)
        

