import math
import json

def generate_fixed_string_wrap(tree_height, base_diameter, led_count):
    """
    Fits a fixed number of LEDs onto a tree by calculating the optimal spiral pitch.
    """
    
    # --- Configuration of the Strip ---
    # Wire length rules: 10cm usually, 20cm after every 50th LED.
    # We pre-calculate the target distance for every segment.
    segment_lengths = []
    for i in range(1, led_count):
        # The wire connects LED (i-1) to LED (i).
        # If the PREVIOUS LED (i-1) was index 49 (50th led), 99, etc., gap is 20.
        # User said: "every 50th led, it's 20cm to the next".
        if i % 50 == 0:
            segment_lengths.append(20.0)
        else:
            segment_lengths.append(10.0)

    # Total length of the wire (for validation)
    total_wire_length = sum(segment_lengths)
    
    # Check physical possibility
    if total_wire_length < tree_height:
        print(f"Error: Wire length ({total_wire_length}cm) is shorter than tree ({tree_height}cm). Impossible to reach top.")
        return None

    R = base_diameter / 2.0
    H = tree_height

    # --- The Simulation Function ---
    def simulate_wrap(vertical_pitch_candidate):
        """
        Simulates wrapping the wire with a specific 'tightness' (vertical pitch).
        Returns the final height (y) reached by the last LED.
        """
        # k links angle to height: y = k * theta
        # vertical_pitch is how much Y rises in one full turn (2pi)
        if vertical_pitch_candidate <= 0: return 0
        k = vertical_pitch_candidate / (2 * math.pi)
        
        current_theta = 0.0
        current_y = 0.0
        
        # We only need to track the previous position to calculate distances
        prev_x = R  # At theta=0, x=R, z=0
        prev_y = 0.0
        prev_z = 0.0
        
        for target_dist in segment_lengths:
            # We need to find the next theta that creates a 3D distance of 'target_dist'
            # Local binary search for the step angle
            
            # Bounds for the angle step (delta_theta)
            # Lower bound 0, Upper bound: Estimate based on circumference
            dt_low = 0.0
            dt_high = 4.0 * math.pi # Generous upper bound
            
            found_dt = 0.0
            
            # Optimization: 10 iterations is enough for this inner loop
            for _ in range(10):
                dt_mid = (dt_low + dt_high) / 2.0
                test_theta = current_theta + dt_mid
                
                # Calculate test coordinates
                test_y = k * test_theta
                
                # If we go past the peak, we clamp the radius to 0 to simulate the wire bunching at top
                # or strictly stop. Let's allow valid calculation but r becomes 0 if y > H.
                if test_y > H:
                    # If we overshoot height, the distance increases rapidly (straight up)
                    # This logic works to pull dt_high down.
                    r = 0
                else:
                    r = R * (1.0 - (test_y / H))
                
                test_x = r * math.cos(test_theta)
                test_z = r * math.sin(test_theta)
                
                # Calc 3D distance
                dist = math.sqrt((test_x-prev_x)**2 + (test_y-prev_y)**2 + (test_z-prev_z)**2)
                
                if dist < target_dist:
                    dt_low = dt_mid
                else:
                    dt_high = dt_mid
            
            found_dt = (dt_low + dt_high) / 2.0
            current_theta += found_dt
            current_y = k * current_theta
            
            # Update prev for next segment
            if current_y > H:
                return current_y # Return early if we topped out
            
            r = R * (1.0 - (current_y / H))
            prev_x = r * math.cos(current_theta)
            prev_y = current_y
            prev_z = r * math.sin(current_theta)

        return current_y

    # --- Solver: Find the correct Vertical Pitch ---
    # We want the final Y to equal H (tree height).
    # If pitch is huge (loose), final Y will be > H (we run out of tree before wire).
    # If pitch is tiny (tight), final Y will be < H (we run out of wire before top).
    
    pitch_low = 0.001
    pitch_high = H * 2 # Start with a very loose coil
    best_pitch = pitch_low
    
    print("Optimizing winding angle...")
    for _ in range(30): # 30 iterations to zoom in on the perfect pitch
        pitch_mid = (pitch_low + pitch_high) / 2.0
        final_y = simulate_wrap(pitch_mid)
        
        if final_y < H:
            # Wire didn't reach the top; we coiled too tightly. 
            # Need to increase pitch (make it looser/steeper).
            pitch_low = pitch_mid
        else:
            # Wire went past the top; we coiled too loosely.
            # Need to decrease pitch (make it tighter/flatter).
            pitch_high = pitch_mid
            
    best_pitch = (pitch_low + pitch_high) / 2.0
    print(f"Optimal Vertical Pitch found: {best_pitch:.2f} cm per turn")

    # --- Generation: Run one last time to save coordinates ---
    k = best_pitch / (2 * math.pi)
    current_theta = 0.0
    coords = []
    
    # First LED at base
    coords.append([round(R, 2), 0.0, 0.0])
    
    prev_pos = (R, 0.0, 0.0)
    
    for i, target_dist in enumerate(segment_lengths):
        # Same geometric solver as above to find exact coords
        dt_low = 0.0
        dt_high = 4.0 * math.pi
        
        for _ in range(20): # High precision for final output
            dt_mid = (dt_low + dt_high) / 2.0
            test_theta = current_theta + dt_mid
            test_y = k * test_theta
            
            if test_y > H:
                # Cap at tip
                r = 0
                test_y = H # Visual clamp
            else:
                r = R * (1.0 - (test_y / H))
                
            test_x = r * math.cos(test_theta)
            test_z = r * math.sin(test_theta)
            
            dist = math.sqrt((test_x-prev_pos[0])**2 + (test_y-prev_pos[1])**2 + (test_z-prev_pos[2])**2)
            
            if dist < target_dist:
                dt_low = dt_mid
            else:
                dt_high = dt_mid
                
        current_theta += (dt_low + dt_high) / 2.0
        y = k * current_theta
        
        # Visual cleanup: if we exceed H slightly due to float math, clamp to H
        if y > H: y = H
        r = R * (1.0 - (y / H))
        x = r * math.cos(current_theta)
        z = r * math.sin(current_theta)
        
        coords.append([round(x, 2), round(y, 2), round(z, 2)])
        prev_pos = (x, y, z)

    return {"type": "3D", "coordinates": coords}

# --- Usage ---
result = generate_fixed_string_wrap(tree_height=200.0, base_diameter=100.0, led_count=200)

if result:
    with open("fixed_tree_lights.json", "w") as f:
        json.dump(result, f, indent=4)
    print(f"Generated {len(result['coordinates'])} LEDs.")
    print("Preview:", json.dumps(result['coordinates'][:3], indent=4))