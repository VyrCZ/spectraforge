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
    // 1. PREVENT NEGATIVE TIME
    // The 'min' property strictly restricts navigation past this date/number.
    min: 0, 
    
    // (Optional) Set a max limit if the song has a fixed length
    // max: 200000, 

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
    
    snap: function (date, scale) {
        var ms = date.getTime();
        var step = 250; 
        var remainder = ms % step;
        if (remainder < step / 2) {
            ms -= remainder; 
        } else {
            ms += step - remainder; 
        }
        return new Date(ms);
    },
    
    orientation: "both",
    editable: true,
    groupEditable: false,

    onAdd: function (item, callback) {
        item.content = "New Effect"; 
        item.end = new Date(item.start.getTime() + 1000); 
        callback(item); 
    },

    start: 0,
    end: 10000, 
    
    // 2. DISPLAY BEATS (Bar.Beat)
    showMajorLabels: false, 
    showMinorLabels: true,
    
    // We lock the scale to seconds and step to 0.25 (250ms) so the grid aligns with beats
    timeAxis: { scale: "second", step: 0.25 },

    format: {
        minorLabels: function (date, scale, step) {
            // Convert the date object to milliseconds
            var ms = date.valueOf();
            
            // CONFIGURATION:
            // Based on your snap of 250ms, we assume:
            // 250ms = 1 Beat
            // 4 Beats = 1 Bar (Standard 4/4 time)
            var msPerBeat = 250;
            var beatsPerBar = 4;

            // Calculate total beats elapsed since time 0
            // We use Math.round to avoid floating point errors (e.g. 249.9999)
            var totalBeats = Math.round(ms / msPerBeat);

            // Calculate which Bar we are in (1-based index)
            var bar = Math.floor(totalBeats / beatsPerBar) + 1;
            
            // Calculate which Beat we are on (1-based index)
            var beat = (totalBeats % beatsPerBar) + 1;

            // Return string "1.1", "1.2", "1.3", "1.4", "2.1", etc.
            return bar + "." + beat;
        },
        majorLabels: {
             // You can leave this blank or return empty strings since we disabled major labels above
            second: "",
            minute: "",
            hour: ""
        }
    }
};

var timeline = new vis.Timeline(container);
timeline.setOptions(options);
timeline.setGroups(groups);
timeline.setItems(items);
