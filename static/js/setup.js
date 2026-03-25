function createNewSetup() {
    document.location.href = "/setup/new";
}

function updateInstructions() {
    if (setupType === '3D') {
        document.querySelectorAll('.instruction_3d').forEach(instruction => {
            instruction.style.display = 'block';
        });
        document.querySelectorAll('.instruction_2d').forEach(instruction => {
            instruction.style.display = 'none';
        });
    } else {
        document.querySelectorAll('.instruction_2d').forEach(instruction => {
            instruction.style.display = 'block';
        });
        document.querySelectorAll('.instruction_3d').forEach(instruction => {
            instruction.style.display = 'none';
        });
    }
}

currentStep = 1;
var setupType = '2D';
function nextStep() {
    if (currentStep === 1) {
        // Validate the first step
        const name = document.querySelector('#setup_name').value;
        const ledCount = document.querySelector('#led_count').value;
        if (!name) {
            alert('Please enter a name for your setup.');
            return;
        }
        else if (isNaN(ledCount) || ledCount <= 0) {
            alert('Please enter a valid number of LEDs.');
            return;
        }
        setupType = document.querySelector('#setup_type').value;
        fetch('/api/calibration/new_setup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                type: setupType,
                led_count: parseInt(ledCount)
            })
        })
    }
    else if (currentStep === 2) {
        setupCamera();
    }
    else if( currentStep === 3) {
        setupEditCanvas();
    }
    currentStep++;
    // hide all steps, then show the current step
    document.querySelectorAll('.setup_step').forEach(step => {
        step.style.display = 'none';
    });
    document.querySelector('#setup_step_' + currentStep).style.display = 'block';
    // hide or show all instructions specific to the setup type
    updateInstructions();
}

var socket = null;
function setupCamera() {
    // start camera capture
    const video = document.querySelector('#webcam_video');

    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            socket = io.connect();
            console.log("Setting up camera...");

            socket.on("connect", () => {
                socket.emit("photo_start");
            });
        
            socket.on("take_photo", async (data) => {
                const view = data && data.view !== undefined ? data.view : null;
                if (view !== null) {
                    // 3D mode: show which view to position and wait for manual capture
                    document.getElementById('view_instruction_text').textContent =
                        `Rotate to ${VIEW_LABELS_3D[view]} view, then click Capture`;
                    document.getElementById('view_indicator_3d').style.display = 'block';
                    document.getElementById('capture_button').style.display = 'block';
                } else {
                    // 2D mode: auto-capture
                    const imageData = await capturePhoto();
                    socket.emit("photo_data", { image: imageData });
                }
            });
        
            socket.on("edit_photo_data", ({ image, x, y }) => {
                console.log("Received image data for editing from server:", x, y);
                if (!editing) {
                    editing = true;
                    nextStep();
                }
                const img = new Image();
                img.onload = () => {
                    const canvas = document.querySelector('#led_pos_canvas');
                    const ctx = canvas.getContext('2d');
        
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    edited_image = img;
                    edited_image_x = x;
                    edited_image_y = y;
                    drawImageAndCross();
                };
                img.src = image; // Corrected from `image_data` to `image`
            });

            socket.on("edit_photo_data_3d", ({ images, x, y, z, center_x, center_y }) => {
                console.log("Received 3D image data for editing from server:", x, y, z);
                if (!editing) {
                    editing = true;
                    nextStep();
                }
                images3d = images;
                coords3d = { x, y, z };
                center3d = { x: center_x, y: center_y };
                current3dView = 0;
                document.getElementById('view_controls_3d').style.display = 'block';
                drawView3d();
            });

            socket.on("setup_done", () => {
                setupDone();
            });
        })
        .catch((err) => {
            alert("Error accessing camera: " + err.message);
        });
}

async function capturePhoto() {
    // capture a frame from video element, convert to base64
    const canvas = document.createElement('canvas');
    const video = document.querySelector('video');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg');
}

function takePhoto() {
    capturePhoto().then(imageData => {
        document.getElementById('view_indicator_3d').style.display = 'none';
        socket.emit("photo_data", { image: imageData });
    });
}

var edited_image = null;
var edited_image_x = null;
var edited_image_y = null;
var editing = false;
var images3d = {};
var coords3d = { x: 0, y: 0, z: 0 };
var center3d = { x: 0, y: 0 };
var current3dView = 0;

var VIEW_NAMES_3D = ["front", "right", "back", "left"];
var VIEW_LABELS_3D = ["FRONT", "RIGHT", "BACK", "LEFT"];

function worldToImage3d(world, view, center) {
    const { x, y, z } = world;
    const cx = center.x;
    const cy = center.y;
    if (view === 0) return { x: x + cx, y: y + cy };   // front
    if (view === 1) return { x: z + cx, y: y + cy };   // right
    if (view === 2) return { x: cx - x, y: y + cy };   // back
    if (view === 3) return { x: cx - z, y: y + cy };   // left
    return { x: cx, y: cy };
}

function imageToWorld3d(px, py, view, center, current) {
    const cx = center.x;
    const cy = center.y;
    if (view === 0) return { x: px - cx, y: py - cy, z: current.z };   // front: update x, y
    if (view === 1) return { x: current.x, y: py - cy, z: px - cx };   // right: update y, z
    if (view === 2) return { x: cx - px, y: py - cy, z: current.z };   // back: update x, y
    if (view === 3) return { x: current.x, y: py - cy, z: cx - px };   // left: update y, z
    return current;
}

function drawView3d() {
    const viewName = VIEW_NAMES_3D[current3dView];
    document.getElementById('current_view_label').textContent = VIEW_LABELS_3D[current3dView];

    const img = new Image();
    img.onload = () => {
        const canvas = document.querySelector('#led_pos_canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        edited_image = img;

        const pixelPos = worldToImage3d(coords3d, current3dView, center3d);
        edited_image_x = pixelPos.x;
        edited_image_y = pixelPos.y;
        drawImageAndCross();
    };
    img.src = images3d[viewName];
}

function prevView3d() {
    current3dView = (current3dView - 1 + VIEW_NAMES_3D.length) % VIEW_NAMES_3D.length;
    drawView3d();
}

function nextView3d() {
    current3dView = (current3dView + 1) % VIEW_NAMES_3D.length;
    drawView3d();
}

function setupEditCanvas() {
    const canvas = document.querySelector('#led_pos_canvas');
    const ctx = canvas.getContext('2d');

    // When user clicks
    canvas.addEventListener("click", (e) => {
        console.log("Clicked on canvas at: ", e.clientX, e.clientY);
        const rect = canvas.getBoundingClientRect();
        const cx = Math.floor(e.clientX - rect.left);
        const cy = Math.floor(e.clientY - rect.top);

        if (setupType === '3D') {
            const updated = imageToWorld3d(cx, cy, current3dView, center3d, coords3d);
            coords3d = updated;
            const pixelPos = worldToImage3d(coords3d, current3dView, center3d);
            edited_image_x = pixelPos.x;
            edited_image_y = pixelPos.y;
        } else {
            edited_image_x = cx;
            edited_image_y = cy;
        }

        drawImageAndCross();
    });

    
    document.addEventListener('keydown', function(event) {
        console.log("Key pressed: ", event.key);
        if (setupType === '3D') {
            if (event.key === 'ArrowLeft') {
                prevView3d();
            } else if (event.key === 'ArrowRight') {
                nextView3d();
            }
        }
        if (event.key === 'Space') {
            // Prevent default spacebar behavior (like scrolling)
            event.preventDefault();
            // Trigger the next step
            sendLedPosition();
        }
    });
}

function drawImageAndCross() {
    if (!edited_image) return;
    const x = edited_image_x;
    const y = edited_image_y;
    
    const canvas = document.querySelector('#led_pos_canvas');
    const ctx = canvas.getContext('2d');

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(edited_image, 0, 0);
    if (x !== undefined && y !== undefined) {
        ctx.beginPath();
        ctx.strokeStyle = 'red';
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
}

function sendLedPosition(){
    var data;
    if (setupType === '3D') {
        if (coords3d.x === undefined || coords3d.y === undefined || coords3d.z === undefined) {
            console.warn("3D coordinates not yet initialized, skipping send.");
            return;
        }
        data = { x: coords3d.x, y: coords3d.y, z: coords3d.z };
    } else {
        data = { x: edited_image_x, y: edited_image_y };
    }
    console.log("Sending LED position to server:", data);
    socket.emit("led_position", data);
}

function setupDone(){
    document.location.href = "/setup";
}

function changeSetup(setupName){
    console.log("Changing setup to:", setupName);
    fetch('/api/change_setup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: setupName })
    }).then(response => {
        if (response.ok) {
            document.location.href = "/setup";
        } else {
            alert(`Error changing setup: ${response.statusText}`);
        }
    });
}