document.addEventListener("DOMContentLoaded", function() {
    // The DOM is fully loaded, so we can now safely attach event listeners.
    var dropdown = document.getElementById("sandbox_scripts_dropdown");
    if (dropdown) {
        dropdown.addEventListener("change", changeSandboxScript);
    }
});

function changeSandboxScript() {
    var dropdown = document.getElementById("sandbox_scripts_dropdown");
    var selectedScript = dropdown.value;
    fetch("/api/sandbox/set_file", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ file_name: selectedScript })
    })
    .then(response => {
        if (response.ok) {
            console.log("Script changed successfully");
        } else {
            console.error("Failed to change script");
        }
    }
    )
    
}