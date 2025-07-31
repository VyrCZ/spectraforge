const inspector_resizer = document.getElementById("inspector_resizer");
const inspector = document.getElementById("inspector");
const main_container = document.getElementById("main_container");

inspector_resizer.addEventListener("mousedown", (e) => {
    e.preventDefault();
    document.addEventListener("mousemove", resize);
    document.addEventListener("mouseup", stopResize);
});

function resize(e) {
    const newWidth = window.innerWidth - e.clientX; // Calculate width from the right edge
    if (newWidth > 250 && newWidth < 800) { // Set min and max width
        inspector.style.width = `${newWidth}px`;
    }
}

function stopResize() {
    document.removeEventListener("mousemove", resize);
    document.removeEventListener("mouseup", stopResize);
}

const previewResizer = document.getElementById("preview_resizer");
const preview = document.getElementById("preview");
const timeline = document.getElementById("timeline");

previewResizer.addEventListener("mousedown", (e) => {
    e.preventDefault();
    document.addEventListener("mousemove", resizePreview);
    document.addEventListener("mouseup", stopResizePreview);
});

function resizePreview(e) {
    const containerRect = document.getElementById("main_container").getBoundingClientRect();
    const newHeight = e.clientY - containerRect.top; // Calculate new height for preview
    const minHeight = 250; // Minimum height for preview
    const maxHeight = containerRect.height - 250; // Prevent timeline from being too small

    if (newHeight > minHeight && newHeight < maxHeight) {
        preview.style.height = `${newHeight}px`;
        timeline.style.height = `${containerRect.height - newHeight - 5}px`; // Adjust timeline height
    }
}

function stopResizePreview() {
    document.removeEventListener("mousemove", resizePreview);
    document.removeEventListener("mouseup", stopResizePreview);
}

document.addEventListener("DOMContentLoaded", () => {
    const ruler = document.querySelector(".timeline_ruler");
    const rowsContainer = document.getElementById("timeline_rows_container");
    const totalTicks = 100; // how many numbers you want visible
    const tickWidth = 50; // Corresponds to .timeline_tick width in CSS

    const totalWidth = totalTicks * tickWidth;
    ruler.style.width = `${totalWidth}px`;
    rowsContainer.style.width = `${totalWidth}px`;

    for (let i = 0; i < totalTicks; i++) {
        const tick = document.createElement("div");
        tick.className = "timeline_tick";
        const tickLabel = document.createElement("span");
        tickLabel.textContent = i;
        tick.appendChild(tickLabel);
        ruler.appendChild(tick);
    }
});