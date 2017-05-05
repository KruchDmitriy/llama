'use-strict';


const timeline = document.getElementById('timeline');
const input = document.getElementById('input');
var counter = 0;

const spawn = require('child_process').spawn;
const python = spawn('python3', ['processing_text.py']);

getNewTimelineBlock = function(type, data) {
    var li = document.createElement('li');
    if (type === 'Out') {
        li.className = "timeline-inverted";
    }

    var div = document.createElement('div');
    div.className = 'timeline-panel';

    var innerDiv = document.createElement('div');
    innerDiv.className = 'timeline-body';

    innerDiv.innerHTML = data;

    var headDiv = document.createElement('div');
    headDiv.className = 'timeline-heading';

    var h4 = document.createElement('h4');
    h4.className = 'timeline-title';
    h4.innerHTML = type + '[' + counter + ']:';

    headDiv.appendChild(h4);
    div.appendChild(headDiv);
    div.appendChild(innerDiv);
    li.appendChild(div);
    timeline.appendChild(li);

    if (type === 'Out') {
        counter++;
        input.value = '';
    }
};

python.stdout.on('data', function(data) {
    getNewTimelineBlock('Out', data);
});

document.getElementById('submit').addEventListener('click', function() {
    python.stdin.write(input.value + "\n");
});

document.getElementById('submit').addEventListener('click', function() {
    getNewTimelineBlock('In', input.value);
});

