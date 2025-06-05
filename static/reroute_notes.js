document.addEventListener("DOMContentLoaded", function () {

	console.log("DOM fully loaded and parsed")

	document.getElementById("noteForm").addEventListener("submit", function (event) {
		event.preventDefault();
		fetchDataUrl();
	});

	document.getElementById("noteFormNonUrl").addEventListener("submit", function (event) {
		event.preventDefault();
		fetchDataNonUrl();
	});

});

function fetchDataUrl() {

	const inputUrl = document.getElementById('input_url').value;

	fetch('/generate_url', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ input_url: inputUrl })
	})
		.then(response => response.json())
		.then(data => {
			document.getElementById('generated_text').innerHTML = data.summary;
		})
		.catch(error => {
			console.error('Error:', error);
		});
}

function fetchDataNonUrl() {

	const inputText = document.getElementById('input_text').value;

	fetch('/generate_notes_text', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ input_text: inputText })
	})
		.then(response => response.json())
		.then(data => {
			document.getElementById('generated_text').innerHTML = data.summary;
		})
		.catch(error => {
			console.error('Error:', error);
		});
}

