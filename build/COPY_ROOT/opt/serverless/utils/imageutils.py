import math

def calculate_aspect_ratio(width, height):
    if height == 0:
        return "Height cannot be zero"
    gcd = math.gcd(width, height)
    simplified_width = width // gcd
    simplified_height = height // gcd
    return f"{simplified_width}:{simplified_height}"