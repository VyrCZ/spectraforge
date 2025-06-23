function createNewSetup(){
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
    if(currentStep === 1){
        // Validate the first step
        const name = document.querySelector('#setup_name').value;
        if (!name) {
            alert('Please enter a name for your setup.');
            return;
        }
        setupType = document.querySelector('#setup_type').value;
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

