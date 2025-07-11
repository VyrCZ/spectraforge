"""
Converts the legacy text-based lightshow label format from Audacity to the new custom JSON format.
"""
import json
import re

PARAMETER_TABLE = {
    "solid_color": ["color"],
    "fade": ["color_from", "color_to", "steps"],
    "flash": ["color_from", "color_to", "frequency"],
    "flash2": ["color_from", "color_to", "frequency"],
    "flash_times": ["color_from", "color_to", "times"],
    "flash2_times": ["color_from", "color_to", "times"],
    "swipe_up": ["color", "width", "steps", "no_clear"],
    "swipe_down": ["color", "width", "steps", "no_clear"],
    "swipe_right": ["color", "width", "steps", "no_clear"],
    "swipe_left": ["color", "width", "steps", "no_clear"],
    "swipe_forward": ["color", "width", "steps", "no_clear"],
    "swipe_backward": ["color", "width", "steps", "no_clear"],
    "rainbow": ["speed", "steps"],
    "gradient": ["color_from", "color_to", "speed", "steps"],
    "string_up": ["color", "trail_length", "steps", "no_clear"],
    "string_down": ["color", "trail_length", "steps", "no_clear"],
    "split_vertical": ["color_from", "color_to", "steps", "no_clear"],
}

input_file = "lightshow/labels/overkill.txt"
output_file = "lightshows/overkill.json"

def parse_color(s):
    match = re.match(r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', s)
    if match:
        r, g, b = map(int, match.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
    return None

def parse_value(s):
    s = s.strip()
    color = parse_color(s)
    if color:
        return color
    if s.lower() == 'true':
        return True
    if s.lower() == 'false':
        return False
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

def main():
    timeline = []
    layer_end_times = []  # Stores the end time of the last effect on each layer

    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 3:
                continue

            start_time, end_time, label_str = parts
            start_time = float(start_time)
            end_time = float(end_time)
            label_parts = [p.strip() for p in label_str.split(';')]
            effect_name = label_parts[0]
            
            if effect_name not in PARAMETER_TABLE:
                print(f"Warning: Effect '{effect_name}' not in PARAMETER_TABLE. Skipping.")
                continue

            param_names = PARAMETER_TABLE[effect_name]
            param_values = label_parts[1:]

            parameters = {}
            for i, value_str in enumerate(param_values):
                if i < len(param_names):
                    param_name = param_names[i]
                    parameters[param_name] = parse_value(value_str)

            # Determine layer
            assigned_layer = -1
            for i, last_end_time in enumerate(layer_end_times):
                if start_time >= last_end_time:
                    assigned_layer = i
                    break
            
            if assigned_layer == -1:
                assigned_layer = len(layer_end_times)
                layer_end_times.append(0)

            layer_end_times[assigned_layer] = end_time

            effect_obj = {
                "start": start_time,
                "end": end_time,
                "effect": effect_name,
                "parameters": parameters,
                "layer": assigned_layer
            }
            timeline.append(effect_obj)

    output_data = {"timeline": timeline}

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)

    print(f"Successfully converted {input_file} to {output_file}")

if __name__ == "__main__":
    main()