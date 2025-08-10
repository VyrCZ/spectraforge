document.addEventListener("DOMContentLoaded", function () {
    const uploadContainer = document.querySelector(".upload_container");
    const fileInput = document.getElementById("file_input");

    uploadContainer.addEventListener("click", () => {
        fileInput.click();
    });

    // Prevent default behaviors for drag-and-drop
    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
        uploadContainer.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when a file is dragged over it
    ["dragenter", "dragover"].forEach(eventName => {
        uploadContainer.addEventListener(eventName, () => {
            uploadContainer.classList.add("highlight");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        uploadContainer.addEventListener(eventName, () => {
            uploadContainer.classList.remove("highlight");
        }, false);
    });

    // Handle dropped files
    uploadContainer.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        // You can add code here to automatically start the upload.
    }, false);
});


function handleFileInputChange(event) {
    const files = event.target.files;
    if (files.length > 0) {
        uploadFiles(files);
    }
}

function uploadFiles(files) {
    createToast("Uploading files...", "upload");
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    fetch('/api/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            createToast("Files uploaded successfully!", "check_circle");
        } else {
            createToast("Failed to upload files: " + data.error, "error");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        createToast("An error occurred while uploading files.", "error");
    });
}

function createToast(message, icon) {
    /* structure:
    <div class="upload_toast">
        <img class="upload_toast_icon" src="static/icons/$icon.svg">
        <p class="upload_toast_text">$message</p>
        <button class="upload_toast_close" onclick="closeUploadToast()">
            <img src="static/icons/close.svg" alt="Close">
        </button>
    </div>*/
    // create this structure
    const container = document.createElement("div");
    container.className = "upload_toast";

    const iconElement = document.createElement("img");
    iconElement.className = "upload_toast_icon";
    iconElement.src = `static/icons/${icon}.svg`;
    container.appendChild(iconElement);

    const textElement = document.createElement("p");
    textElement.className = "upload_toast_text";
    textElement.textContent = message;
    container.appendChild(textElement);

    const closeButton = document.createElement("button");
    closeButton.className = "upload_toast_close";
    closeButton.onclick = function() { closeUploadToast(container); };
    const closeIcon = document.createElement("img");
    closeIcon.src = "static/icons/close.svg";
    closeIcon.alt = "Close";
    closeButton.appendChild(closeIcon);
    container.appendChild(closeButton);

    document.body.appendChild(container);
    // auto close the toast after 5 seconds
    setTimeout(() => {
        closeUploadToast(container);
    }, 5000);
}

function closeUploadToast(toast) {
    toast.classList.add("slideOut");
    toast.addEventListener("animationend", function() {
        toast.remove();
    }, { once: true });
}