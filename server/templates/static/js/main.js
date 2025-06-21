function changeEffect() {
    const effect = document.getElementById("effect").value;

    // Update the server about the selected effect
    fetch(`/set_effect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ effect }),
    })
        .then(response => response.json())
        .then(data => {
            console.log(`Effect set to ${effect}`);
            // go back to the main page
            window.location.href = "/index";
        })
        .catch(error => console.error("Error setting effect:", error));
}

// Update a specific parameter on the server
function updateParameter(name, value, type) {
    if (type === "checkbox") {
        value = document.querySelector(`input[name="${name}"]`).checked;
    }
    fetch("/set_parameter", {
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
    fetch('/get_state')
    .then(response => response.json())
    .then(data => {
        const { current_effect, parameters } = data;
        // set the name of the current effect
        const effectText = document.getElementsByClassName("active effect_container").item(0);
        if (effectText) {
            effectText.textContent = current_effect;
        } else {
            console.error("No active effect container found.");
        }
        if (!handleParams){
            return; // Exit if we are not handling parameters
        }
        // Fetch and display parameters for the current effect
        fetch(`/get_parameters/${current_effect}`)
            .then(response => response.json())
            .then(parameterData => {
                const parametersDiv = document.getElementById('parameters');
                parametersDiv.innerHTML = ""; // Clear existing parameters

                // Update parameters dynamically
                for (const [name, param] of Object.entries(parameterData)) {
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
                    } else {
                        input = document.createElement("input");
                        input.type = "text";
                        input.value = parameters[name]; // Set value from state
                    }

                    input.onchange = () => updateParameter(name, input.value, param.param_type);

                    parametersDiv.appendChild(label);
                    parametersDiv.appendChild(input);
                    parametersDiv.appendChild(document.createElement("br"));
                }
            })
            .catch(error => console.error("Error fetching parameters:", error));[]
        })
        .catch(error => console.error("Error fetching current effect:", error));
}

// Load initial parameters for the default effect on page load
document.addEventListener("DOMContentLoaded", getState);