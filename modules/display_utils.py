import modules.mathutils as mu
from PIL import Image

def map_image_to_leds(img: Image.Image, renderer, coords: list, bounds, mode: str, radius: int):
    """
    Shared logic to map a PIL Image to the LED renderer based on coordinates.
    """
    if not coords or not bounds:
        return

    img_w, img_h = img.size
    pixels = img.load()

    # Determine dimensions
    x_min, x_max = bounds.min_x, bounds.max_x
    y_min, y_max = bounds.min_y, bounds.max_y
    
    led_width = max(1.0, x_max - x_min)
    led_height = max(1.0, y_max - y_min)
    
    led_center_x = (x_min + x_max) / 2.0
    led_center_y = (y_min + y_max) / 2.0
    img_center_x, img_center_y = img_w / 2.0, img_h / 2.0

    scale_w = img_w / led_width
    scale_h = img_h / led_height
    
    # Mode logic
    if mode == "fill":
        scale = min(scale_w, scale_h) 
    elif mode == "fit":
        scale = max(scale_w, scale_h)
    else:
        # Fallback to fill
        scale = min(scale_w, scale_h)

    leds = renderer.leds
    count = min(len(leds), len(coords))

    # Pixel mapping loop
    for i in range(count):
        coord = coords[i]
        # Calculate UV (flipping Y for standard image coordinates)
        u = int(img_center_x + ((coord[0] - led_center_x) * scale))
        v = int(img_center_y + (-(coord[1] - led_center_y) * scale))
        
        u = max(0, min(u, img_w - 1))
        v = max(0, min(v, img_h - 1))

        if radius <= 0:
            leds[i] = pixels[u, v]
        else:
            # Simple box blur sampling
            r, g, b, c = 0, 0, 0, 0
            u_min, u_max = max(0, u - radius), min(img_w, u + radius + 1)
            v_min, v_max = max(0, v - radius), min(img_h, v + radius + 1)
            
            for pu in range(u_min, u_max):
                for pv in range(v_min, v_max):
                    pr, pg, pb = pixels[pu, pv]
                    r += pr
                    g += pg
                    b += pb
                    c += 1
            if c > 0: 
                leds[i] = (r//c, g//c, b//c)