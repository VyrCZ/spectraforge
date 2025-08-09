// https://motocal.com/
var groups = new vis.DataSet([
    { content: "Layer 1", id: "Layer 1", value: 1, className: "layer_1" },
    { content: "Layer 2", id: "Layer 2", value: 2, className: "layer_2" },
    { content: "Layer 3", id: "Layer 3", value: 3, className: "layer_3" },
    { content: "Layer 4", id: "Layer 4", value: 4, className: "layer_4" },
    { content: "Layer 5", id: "Layer 5", value: 5, className: "layer_5" },
]);

// function to make all groups visible again
function showAllGroups() {
    groups.forEach(function (group) {
        groups.update({ id: group.id, visible: true });
    });
}

// create a dataset with items
// note that months are zero-based in the JavaScript Date object, so month 3 is April
var items = new vis.DataSet([
    {
        start: 1,
        end: 1000,
        group: "Layer 1",
        className: "layer_1",
        content: "fade",
        id: "fade_1",
    },
]);

// create visualization
var container = document.getElementById("timeline");
var options = {
    // option groupOrder can be a property name or a sort function
    // the sort function must compare two groups and return a value
    //     > 0 when a > b
    //     < 0 when a < b
    //       0 when a == b
    groupOrder: function (a, b) {
        return a.value - b.value;
    },
    groupOrderSwap: function (a, b, groups) {
        var v = a.value;
        a.value = b.value;
        b.value = v;
    },
    groupTemplate: function (group) {
        var container = document.createElement("div");
        var label = document.createElement("span");
        label.innerHTML = group.content + " ";
        container.insertAdjacentElement("afterBegin", label);
        return container;
    },
    // snap to .25
    snap: function (date, scale) {
        var ms = date.getTime();
        var step = 250; // 0.25 seconds in milliseconds
        var remainder = ms % step;
        if (remainder < step / 2) {
            ms -= remainder; // round down
        } else {
            ms += step - remainder; // round up
        }
        return new Date(ms);
    },
    orientation: "both",
    editable: true,
    groupEditable: false,

    onAdd: function (item, callback) {
        item.content = "New Effect"; // Set default content for the new item.
        item.end = new Date(item.start.getTime() + 1000); // Set an end time 1 second after the start time.
        callback(item); // Add the modified item to the timeline.
    },

    start: 0,
    end: 10000, // Increased end time to show more labels
    format: {
        minorLabels: function (date, scale, step) {
            // When using a number range, 'date' is a number in milliseconds.
            // Show labels only for whole seconds (multiples of 1000 ms).
            if (date % 1000 === 0) {
                var totalSeconds = date / 1000;
                var minutes = Math.floor(totalSeconds / 60);
                var seconds = totalSeconds % 60;
                return String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
            }
            return "";
        },
        majorLabels: {
            day: "",
            month: "",
            year: ""
        }
    },
    showMajorLabels: false,
    showMinorLabels: true,
    timeAxis: { scale: "second", step: 0.25 }
};

var timeline = new vis.Timeline(container);
timeline.setOptions(options);
timeline.setGroups(groups);
timeline.setItems(items);
