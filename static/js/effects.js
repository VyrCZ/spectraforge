function changeEffect(effectName) {
    // Update the server about the selected effect
    clearAudioSelection();
    fetch(`/api/set_effect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ effect: effectName }),
    })
        .then(response => response.json())
        .then(data => {
            console.log(`Effect set to ${effectName}`);
            // prevent the audio/lightshow file from being played again
            sessionStorage.removeItem('audioFile');
            sessionStorage.removeItem('lightshowFile');
            // go back to the main page
            window.location.href = "/";
        })
        .catch(error => console.error("Error setting effect:", error));
}

// Update a specific parameter on the server
function updateParameter(name, value, type) {
    console.log(`Updating parameter: ${name} with value: ${value} of type: ${type}`);
    fetch("/api/set_parameter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, value }),
    })
        .then(response => response.json())
        .then(data => {
            console.log(`Parameter ${name} updated to ${value}`);
        })
        .catch(error => console.error("Error updating parameter:", error));
}

function getState(handleParams = true) {
    fetch('/api/get_state')
    .then(response => response.json())
    .then(data => {
        console.log("Fetched state:", data);
        const { current_effect, parameters, effect_type } = data;
        // set the display elements of the current effect
        const effectText = document.querySelector(".active.effect_container").querySelector("p");
        if (effectText) {
            effectText.textContent = current_effect;
            console.log(`Setting current effect to: ${current_effect}`);
        } else {
            console.error("No active effect container found.");
        }
        const effectTag = document.querySelector(".active.effect_container").querySelector(".effect_tag");
        if (effectTag) {
            effectTag.textContent = effect_type;
            colorizeTags();
        } else {
            console.error("No effect tag found.");
        }
        if (!handleParams){
            return; // Exit if we are not handling parameters
        }
        // Fetch and display parameters for the current effect
        fetch(`/api/get_parameters/${current_effect}`)
            .then(response => response.json())
            .then(parameterData => {
                const parametersDiv = document.getElementById('parameters');
                parametersDiv.innerHTML = ""; // Clear existing parameters

                // Update parameters dynamically
                for (const [name, param] of Object.entries(parameterData)) {
                    const container = document.createElement("div");
                    container.className = "parameter_container";
                    const label = document.createElement("label");
                    label.textContent = `${name}: `;

                    let input;
                    if (param.param_type === "slider") {
                        input = document.createElement("input");
                        input.type = "range";
                        input.min = param.options.min;
                        input.max = param.options.max;
                        input.step = param.options.step;
                        input.value = parameters[name]; // Set value from state
                    } else if (param.param_type === "color") {
                        input = document.createElement("div");
                        const colorPicker = new iro.ColorPicker(input, {
                            width: 200,
                            color: `rgb(${parameters[name].join(",")})`,
                            borderWidth: 1,
                            borderColor: "#ccc",
                        });
                        colorPicker.on("input:end", color => updateParameter(name, color.hexString, param.param_type));
                    } else if (param.param_type === "checkbox") {
                        input = document.createElement("input");
                        input.type = "checkbox";
                        input.checked = parameters[name];
                    } else if (param.param_type === "button") {
                        input = document.createElement("button");
                        input.type = "button";
                        input.className = "param-button";
                        // Use label text for the button
                        input.textContent = param.options && param.options.label ? param.options.label : name;

                        const sendState = (state) => {
                            updateParameter(name, state, param.param_type);
                        };

                        // Pointer events cover mouse and touch
                        input.addEventListener("pointerdown", (e) => {
                            e.preventDefault();
                            sendState(true);
                        });
                        input.addEventListener("pointerup", (e) => {
                            e.preventDefault();
                            sendState(false);
                        });
                        input.addEventListener("pointercancel", () => sendState(false));
                        // In case pointer leaves the button while pressed
                        input.addEventListener("pointerleave", (e) => {
                            if (e.pressure && e.pressure > 0) {
                                // some platforms may use pressure; ensure release is sent
                                sendState(false);
                            }
                        });
                        // Keyboard accessibility (Space / Enter)
                        input.addEventListener("keydown", (e) => {
                            if (e.key === " " || e.key === "Enter") {
                                e.preventDefault();
                                sendState(true);
                            }
                        });
                        input.addEventListener("keyup", (e) => {
                            if (e.key === " " || e.key === "Enter") {
                                e.preventDefault();
                                sendState(false);
                            }
                        });
                    } else {
                        input = document.createElement("input");
                        input.type = "text";
                        input.value = parameters[name]; // Set value from state
                    }

                    // Only attach onchange handler for inputs that support it (not the button)
                    if (!(param.param_type === "button")) {
                        input.onchange = () => updateParameter(name, (input.type === "checkbox") ? input.checked : input.value, param.param_type);
                    }

                    parametersDiv.appendChild(container);
                    container.appendChild(label);
                    container.appendChild(input);
                    //parametersDiv.appendChild(document.createElement("br"));
                }
            })
            .catch(error => console.error("Error fetching parameters:", error));
        })
        .catch(error => console.error("Error fetching current effect:", error));
}

// Functions are called straight from the HTML



// util functions
function clearAudioSelection() {
    sessionStorage.removeItem('audioFile');
    sessionStorage.removeItem('lightshowFile');
    sessionStorage.removeItem('videoFile');
}

function isAudioEngineSelected() {
    return (
        sessionStorage.getItem('audioFile') !== null ||
        sessionStorage.getItem('lightshowFile') !== null ||
        sessionStorage.getItem('videoFile') !== null
    )
}