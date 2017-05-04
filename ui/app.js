'use-strict';

const spawn = require('child_process').spawn;

const python = spawn('python', ['example.py']);

var exec = require('child_process').exec
function execute(command, callback) {
	exec(command, function(error, stdout, stderr) { callback(stdout); });
}

const input = document.getElementById('input');
const output = document.getElementById('output');

python.stdout.on('data', (data) => {
	output.value = data;
});

document.getElementById('async-msg').addEventListener('click', function(e) {
	python.stdin.write(input.value + "\n");
});

document.getElementById('exit').addEventListener('click', function() {
	python.stdin.end();
});
