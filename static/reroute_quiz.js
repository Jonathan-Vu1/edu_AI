document.addEventListener("DOMContentLoaded", function () {

	console.log("DOM fully loaded and parsed")

	document.getElementById("quizForm").addEventListener("submit", function (event) {
		console.log(
			"here"
		)
		event.preventDefault();
		fetchQuizData();
	});

});

function fetchQuizData() {

	const difficulty = document.getElementById('difficulty').value;
	const subject = document.getElementById('content').value;
	const checkbox = document.getElementById('checkbox').checked;
	const question_type = document.getElementById('question_type').value;
	const num_questions = document.getElementById('num_questions').value;

	fetch('/createQuiz', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ difficulty: difficulty, subject: subject, question_type: question_type, num_questions: num_questions, checkbox: checkbox }),
	})
		.then(response => response.json())
		.then(data => {
			console.log(data);

			const container = document.getElementById('generated_text');

			container.innerHTML = data.test;

			//if (window.MathJax && MathJax.typesetPromise) {
			//MathJax.typesetPromise([container])
			//	.catch(err => console.error("MathJax typeset failed:", err));
			//}

		})
		.catch(error => {
			console.error('Error:', error);
		});
}