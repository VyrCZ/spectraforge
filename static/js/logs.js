function get_logs(){
    fetch('/api/get_log')
    .then(response => response.json())
    .then(data => {
        const { logs } = data;
        const logBox = document.getElementById('log_container');
        logBox.innerHTML = ""; // Clear existing logs
        const channels = new Set();

        // Create a new div for each log entry
        logs.forEach(log => {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'log_entry'; // Add a class for styling
            // template: [$DATETIME] [$CHANNEL] [$LOGTYPE]: $MESSAGE
            const separatorIndex = log.indexOf(': ');
            if (separatorIndex === -1) {
                messageDiv.textContent = log; // fallback for unexpected format
                logBox.appendChild(messageDiv);
                return;
            }

            const headerPart = log.substring(0, separatorIndex);
            const messagePart = log.substring(separatorIndex + 2);

            const tags = headerPart.match(/\[.*?\]/g) || [];
            const partSpans = [];
            for(let i = 0; i < tags.length; i++) {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'log_tag';
                tagSpan.textContent = tags[i];
                partSpans.push(tagSpan);
            }
            if (partSpans.length >= 3) {
                partSpans[0].classList.add('log_datetime');
                partSpans[1].classList.add('log_channel');
                const channel = tags[1].substring(1, tags[1].length - 1);
                messageDiv.dataset.channel = channel;
                channels.add(channel);
                partSpans[2].classList.add('log_type');
                const logType = partSpans[2].textContent;
                if (logType.includes("ERROR")) {
                    partSpans[2].classList.add('log_error');
                } else if (logType.includes("WARN")) {
                    partSpans[2].classList.add('log_warn');
                }
                else if (logType.includes("INFO")) {
                    partSpans[2].classList.add('log_info');
                }
                else if (logType.includes("DEBUG")) {
                    partSpans[2].classList.add('log_debug');
                }
            }
            partSpans.forEach(span => messageDiv.appendChild(span));
            const messageText = document.createElement('span');
            messageText.className = 'log_text';
            messageText.textContent = " " + messagePart; // The message part after the colon
            messageDiv.appendChild(messageText);
            logBox.appendChild(messageDiv);
        });
        populateFilters(channels);
    });
}

function populateFilters(channels) {
    const filterList = document.querySelector('.filter-list');
    // Clear existing channel filters, keeping "All"
    const existingFilters = filterList.querySelectorAll('li:not(:first-child)');
    existingFilters.forEach(li => li.remove());

    const sortedChannels = Array.from(channels).sort();

    sortedChannels.forEach(channel => {
        const li = document.createElement('li');
        const button = document.createElement('button');
        button.dataset.filter = channel;
        button.textContent = channel;
        li.appendChild(button);
        filterList.appendChild(li);
    });

    addFilterListeners();
}

function addFilterListeners() {
    const filterButtons = document.querySelectorAll('.filter-list button');
    filterButtons.forEach(button => {
        // Remove old listener to prevent duplicates
        button.replaceWith(button.cloneNode(true));
    });

    // Re-query for buttons to attach new listeners
    document.querySelectorAll('.filter-list button').forEach(button => {
        button.addEventListener('click', () => {
            // Handle active state
            document.querySelectorAll('.filter-list button').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filter = button.dataset.filter;
            const logEntries = document.querySelectorAll('.log_entry');

            logEntries.forEach(entry => {
                if (filter === '*' || entry.dataset.channel === filter) {
                    entry.style.display = 'flex';
                } else {
                    entry.style.display = 'none';
                }
            });
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    get_logs(); // Fetch logs when the page is loaded
});