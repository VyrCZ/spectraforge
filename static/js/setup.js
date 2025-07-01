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
setupType = null;
function nextStep() {
    if (currentStep === 1) {
        // Validate the first step
        const name = document.querySelector('#setup_name').value;
        if (!name) {
            alert('Please enter a name for your setup.');
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
                type: setupType
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
        
            socket.on("take_photo", async () => {
                const imageData = await capturePhoto();
                socket.emit("photo_data", { image: imageData });
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

var edited_image = null;
var edited_image_x = null;
var edited_image_y = null;
var editing = false;

function setupEditCanvas() {
    const canvas = document.querySelector('#led_pos_canvas');
    const ctx = canvas.getContext('2d');

    // When user clicks
    canvas.addEventListener("click", (e) => {
        console.log("Clicked on canvas at: ", e.clientX, e.clientY);
        const rect = canvas.getBoundingClientRect();
        edited_image_x = Math.floor(e.clientX - rect.left);
        edited_image_y = Math.floor(e.clientY - rect.top);

        drawImageAndCross();

        // Redraw image and draw new cross
        //socket.emit("pixel_selected", { x, y });
    });

    
    document.addEventListener('keydown', function(event) {
        console.log("Key pressed: ", event.key);
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
    const data = {
        x: edited_image_x,
        y: edited_image_y
    };
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