let world_coords = [];
let canvas_coords = [];
let led_container;
let containerWidth = 0;
let containerHeight = 0;
let drawing = false;
let brushActive = false;
let brushSize = 24;
let picker = null;
let undoStack = [];
let redoBuffer = [];

function updateBrushSize(size) {
    brushSize = parseInt(size, 10);
    const cursorBrush = document.getElementById('cursor_brush');
    cursorBrush.style.width = `${brushSize}px`;
    cursorBrush.style.height = `${brushSize}px`;
}

function calculateLedPositions() {
    canvas_coords = [];
    if (world_coords.length === 0) return;

    const minX = Math.min(...world_coords.map(coord => coord[0]));
    const minY = Math.min(...world_coords.map(coord => coord[1]));
    const maxX = Math.max(...world_coords.map(coord => coord[0]));
    const maxY = Math.max(...world_coords.map(coord => coord[1]));

    const worldWidth = maxX - minX;
    const worldHeight = maxY - minY;

    if (worldWidth === 0 || worldHeight === 0) {
        // Handle cases with single point or all points on a line
        for (let i = 0; i < world_coords.length; i++) {
            canvas_coords.push([containerWidth / 2, containerHeight / 2]);
        }
        return;
    }

    const padding = 10; // Add some padding
    const scaleX = (containerWidth - 2 * padding) / worldWidth;
    const scaleY = (containerHeight - 2 * padding) / worldHeight;
    const scale = Math.min(scaleX, scaleY);

    const offsetX = (containerWidth - worldWidth * scale) / 2;
    const offsetY = (containerHeight - worldHeight * scale) / 2;

    for (let i = 0; i < world_coords.length; i++) {
        const x = (world_coords[i][0] - minX) * scale + offsetX;
        const y = (world_coords[i][1] - minY) * scale + offsetY;
        canvas_coords.push([x, y]);
    }
}

function drawLeds(){
    led_container.innerHTML = ''; // Clear previous leds
    
    for (let i = 0; i < canvas_coords.length; i++) {
        const x = canvas_coords[i][0];
        const y = canvas_coords[i][1];
        const led = document.createElement('div');
        led.classList.add('led');
        led.style.left = `${x}px`;
        led.style.top = `${y}px`;
        led_container.appendChild(led);
    }
}

function updateLedPositions() {
    const leds = led_container.getElementsByClassName('led');
    for (let i = 0; i < leds.length; i++) {
        const led = leds[i];
        const x = canvas_coords[i][0];
        const y = canvas_coords[i][1];
        led.style.left = `${x}px`;
        led.style.top = `${y}px`;
    }
}

function fillCanvas() {
    addToUndoStack();
    redoBuffer = [];
    const leds = led_container.getElementsByClassName('led');
    for (let i = 0; i < leds.length; i++) {
        const led = leds[i];
        led.style.backgroundColor = picker.color.hexString;
    }
    sendPixels();
}

function clearCanvas() {
    addToUndoStack();
    redoBuffer = [];
    const leds = led_container.getElementsByClassName('led');
    for (let i = 0; i < leds.length; i++) {
        const led = leds[i];
        led.style.backgroundColor = 'black'; // Reset to black
    }
    sendPixels();
}

function sendPixels(pixel_list = null){
    if (!pixel_list) {
        pixel_list = getLedState().map(color => {
            const rgb = parseRgbString(color);
            return [rgb[0], rgb[1], rgb[2]]; // Convert to [R, G, B] array
        });
    }
        
    fetch("/api/canvas/set_pixels", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({pixels: pixel_list})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            console.log("Pixels updated successfully.");
        } else {
            console.error("Error updating pixels:", data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function getEventCoords(event) {
    if (event.touches && event.touches.length > 0) {
        return { x: event.touches[0].clientX, y: event.touches[0].clientY };
    }
    return { x: event.clientX, y: event.clientY };
}

function checkAndDraw(event){
    if (event.type.startsWith('touch')) {
        event.preventDefault();
    }
    const coords = getEventCoords(event);

    if (brushActive) {
        // Update the cursor position
        const cursorBrush = document.getElementById('cursor_brush');
        cursorBrush.style.display = 'block';
        cursorBrush.style.width = `${brushSize}px`;
        cursorBrush.style.height = `${brushSize}px`;
        cursorBrush.style.left = `${coords.x - brushSize / 2}px`; // Center the brush
        cursorBrush.style.top = `${coords.y - brushSize / 2}px`;
    }
    if (!drawing) return;

    // if over any led, change its color
    const x = coords.x - led_container.getBoundingClientRect().left;
    const y = coords.y - led_container.getBoundingClientRect().top;

    const leds = led_container.getElementsByClassName('led');
    for (let i = 0; i < leds.length; i++) {
        const led = leds[i];
        const rect = led.getBoundingClientRect();
        const ledX = rect.left - led_container.getBoundingClientRect().left + rect.width / 2;
        const ledY = rect.top - led_container.getBoundingClientRect().top + rect.height / 2;

        if (Math.abs(x - ledX) < brushSize / 2 && Math.abs(y - ledY) < brushSize / 2) {
            // Change color of the LED
            led.style.backgroundColor = picker.color.hexString;
        }
    }
}

function parseRgbString(rgbString) {
    const result = rgbString.match(/\d+/g);
    return result ? result.map(Number) : [0, 0, 0];
}

function getLedState() {
    const leds = led_container.getElementsByClassName('led');
    const pixel_list = [];
    for (let i = 0; i < leds.length; i++) {
        const led = leds[i];
        const color = led.style.backgroundColor || 'black'; // Default to black if no color set
        pixel_list.push(color);
    }
    return pixel_list;
}

function setLedState(state) {
    const leds = led_container.getElementsByClassName('led');
    for (let i = 0; i < leds.length; i++) {
        const led = leds[i];
        led.style.backgroundColor = state[i] || 'black'; // Default to black if no state provided
    }
}

function addToUndoStack() {
    undoStack.push(getLedState());
}

function undo() {
    if (undoStack.length === 0) return;
    const lastState = undoStack.pop();
    redoBuffer.push(getLedState());
    setLedState(lastState);
    sendPixels(lastState);
}

function redo() {
    if (redoBuffer.length === 0) return;
    const lastState = redoBuffer.pop();
    undoStack.push(getLedState());
    setLedState(lastState);
    sendPixels(lastState);
}

document.addEventListener("DOMContentLoaded", function() {
    led_container = document.getElementById("led_container");
    // brush cursor
    led_container.addEventListener('mouseenter', function(event) {
        // hide the cursor
        const cursorBrush = document.getElementById('cursor_brush');
        document.body.style.cursor = 'none';
        cursorBrush.style.display = 'block';
        brushActive = true;
        checkAndDraw(event);
    });
    led_container.addEventListener('mouseleave', function(event) {
        // show the cursor
        const cursorBrush = document.getElementById('cursor_brush');
        cursorBrush.style.display = 'none';
        document.body.style.cursor = 'default';
        brushActive = false;
    });
    const brushSizeSlider = document.getElementById('brush_size_slider');
    if (brushSizeSlider) {
        updateBrushSize(brushSizeSlider.value);
    }
    
    // get coordinates from the server and draw the leds
    fetch("/api/get_coords")
        .then(response => response.json())
        .then(data => {
            containerWidth = led_container.offsetWidth;
            containerHeight = led_container.offsetHeight;
            const {coords} = data;
            world_coords = coords.map(coord => [coord[0], coord[1]]);
            calculateLedPositions();
            drawLeds();
            // window resize event to recalculate positions
            window.addEventListener('resize', function() {
                containerWidth = led_container.offsetWidth;
                containerHeight = led_container.offsetHeight;
                calculateLedPositions();
                updateLedPositions();
            });

            // add events for mouse down, move, and up
            led_container.addEventListener('mousedown', function(event) {
                drawing = true;
                addToUndoStack();
                redoBuffer = [];
                checkAndDraw(event);
            });
            
            led_container.addEventListener('mouseup', function(event) {
                drawing = false;
                sendPixels();
            });
            
            led_container.addEventListener('mousemove', checkAndDraw)

            // add touch events
            led_container.addEventListener('touchstart', function(event) {
                drawing = true;
                brushActive = true;
                addToUndoStack();
                redoBuffer = [];
                checkAndDraw(event);
            });

            led_container.addEventListener('touchend', function(event) {
                drawing = false;
                brushActive = false;
                const cursorBrush = document.getElementById('cursor_brush');
                cursorBrush.style.display = 'none';
                sendPixels();
            });

            led_container.addEventListener('touchmove', checkAndDraw);

            // add shortcuts for undo and redo
            document.addEventListener('keydown', function(event) {
                if (event.ctrlKey && event.key === 'z') {
                    event.preventDefault();
                    undo();
                } else if (event.ctrlKey && event.key === 'y') {
                    event.preventDefault();
                    redo();
                }
            });
        });
    picker = new iro.ColorPicker("#color_picker", {
        width: 235,
        color: "#fff",
        layout: [
            { component: iro.ui.Box },
            { component: iro.ui.Slider, options: { sliderType: 'hue' } }
        ],
        "borderWidth": 3,
        "borderColor": "#333",
    }); 
});
