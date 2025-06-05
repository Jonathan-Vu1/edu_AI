document.addEventListener("DOMContentLoaded", function () {

	console.log("DOM fully loaded and parsed")

	document.getElementById("derivative_form").addEventListener("submit", function (event) {
		event.preventDefault();
		fetchData();
	});

});

function fetchData() {

	const equation = document.getElementById('equation').value;
	const order = document.getElementById('order').value;

	console.log("Equation: " + equation);
	console.log("Order: " + order);

	fetch('/calculation', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ equation: equation, order: order })
	})
		.then(response => response.json())
		.then(data => {
			document.getElementById('generated_text').innerHTML = data.solution;
		})
		.catch(error => {
			console.error('Error:', error);
		});
}
