let world_coords = [];
let canvas_coords = [];
let canvas, ctx;
let canvasWidth = 0;
let canvasHeight = 0;

function calculateCanvasCoords() {
    canvas_coords = [];
    const minX = Math.min(...world_coords.map(coord => coord[0]));
    const minY = Math.min(...world_coords.map(coord => coord[1]));
    const maxX = Math.max(...world_coords.map(coord => coord[0]));
    const maxY = Math.max(...world_coords.map(coord => coord[1]));
    // Using the same scale for both axes to preserve aspect ratio
    const scale = Math.min(canvasWidth / (maxX - minX), canvasHeight / (maxY - minY));
    // Optionally calculate offsets to center the drawing:
    const offsetX = (canvasWidth - (maxX - minX) * scale) / 2;
    const offsetY = (canvasHeight - (maxY - minY) * scale) / 2;
    for (let i = 0; i < world_coords.length; i++) {
        const x = (world_coords[i][0] - minX) * scale + offsetX;
        const y = (world_coords[i][1] - minY) * scale + offsetY;
        canvas_coords.push([x, y]);
    }
}

function drawCanvas(){
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);
    ctx.beginPath();
    for (let i = 0; i < canvas_coords.length; i++) {
        const x = canvas_coords[i][0];
        const y = canvas_coords[i][1];
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    ctx.closePath();
    ctx.stroke();
    
    for (let i = 0; i < canvas_coords.length; i++) {
        const x = canvas_coords[i][0];
        const y = canvas_coords[i][1];
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    canvas = document.getElementById("canvas");
    ctx = canvas.getContext("2d");
    canvasWidth = canvas.width;
    canvasHeight = canvas.height;
    fetch("/api/get_coords")
        .then(response => response.json())
        .then(data => {
            const {coords} = data;
            world_coords = coords.map(coord => [coord[0], coord[1]]);
            calculateCanvasCoords();
            drawCanvas();
        })
});