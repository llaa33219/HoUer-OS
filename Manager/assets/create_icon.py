#!/usr/bin/env python3
"""
Create a simple icon for HoUer Manager
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PIL not available, creating a simple placeholder icon")
    # Create a simple text file as placeholder
    with open('icon.png', 'w') as f:
        f.write("# Placeholder icon file\n")
    exit()

def create_icon():
    """Create a simple HoUer Manager icon"""
    # Create a 64x64 icon
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw container-like shape
    # Outer container
    draw.rectangle([8, 12, size-8, size-8], outline=(70, 130, 180), width=3, fill=(240, 248, 255))
    
    # Inner containers (stacked)
    draw.rectangle([16, 20, size-16, 32], outline=(100, 149, 237), width=2, fill=(173, 216, 230))
    draw.rectangle([16, 36, size-16, 48], outline=(100, 149, 237), width=2, fill=(173, 216, 230))
    
    # HoUer text
    try:
        font = ImageFont.load_default()
        draw.text((12, size-20), "HoUer", fill=(25, 25, 112), font=font)
    except:
        # Fallback if font loading fails
        draw.text((12, size-20), "HoUer", fill=(25, 25, 112))
    
    # Save icon
    img.save('icon.png', 'PNG')
    print("Icon created: icon.png")

if __name__ == "__main__":
    create_icon() 