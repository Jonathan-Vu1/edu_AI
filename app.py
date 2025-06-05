from flask import *
import os
import url_to_notes, quiz_maker, derivative_solver
import markdown
from transformer_model import TransformerModel
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy


# Flask start
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(12)

# SQLAlchemy setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Classes for database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), nullable=False)
    notes = db.relationship('Note', backref='user', lazy=True)
    quizzes = db.relationship('Quiz', backref='user', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()


# OAuth setup
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
googleClientId = os.getenv("GOOGLE_CLIENT_ID")
googleSecret = os.getenv("GOOGLE_CLIENT_SECRET")

oauth = OAuth(app)

oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_id=googleClientId,
    client_secret= googleSecret,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Start of the Routes

# Home page
@app.route('/')
def startPage():
    return render_template('homePage.html')

# Route for the note generator
@app.route('/noteGenerator', methods = ["GET", "POST"])
def noteGenerator():
    return render_template('generated_notes.html')

# Route used to generate notes from a URL or text input
@app.route('/generate_url', methods = ["POST"])
def summarize_url():

    # Get the URL from the request
    session['input_url'] = request.json.get('input_url')
    if session['input_url'] == '':
        return jsonify({"summary": "Please provide a valid URL."})
    
    # Use the url_to_notes module to summarize the URL
    summary = url_to_notes.summarize_url(session['input_url'], 500)
    summary = markdown.markdown(summary, extensions=['nl2br'])

    # Store the summary in the database if the user is logged in
    if 'user' in session:
        user = User.query.filter_by(google_id = session['user']['sub']).first()
        if user:
            stored_summary = f"""
            <div class="card mt-5">
                <div class="card-body">
                    {summary}
                </div>
            </div>
            """
            note = Note(content=stored_summary, user_id=user.id)
            db.session.add(note)
            db.session.commit()

    return jsonify({"summary": summary})

# Route used to generate notes from a text input
@app.route('/generate_notes_text', methods = ["POST"])
def summarize_text():
    # Get the text from the request
    session['input_text'] = request.json.get('input_text')

    summary = markdown.markdown(url_to_notes.generate_notes(session['input_text'], 500), extensions=['nl2br'])

    # Store the summary in the database if the user is logged in
    if 'user' in session:
        user = User.query.filter_by(google_id = session['user']['sub']).first()
        if user:
            stored_summary = f"""
            <div class="card mt-5">
                <div class="card-body">
                    {summary}
                </div>
            </div>
            """
            note = Note(content=stored_summary, user_id=user.id)
            db.session.add(note)
            db.session.commit()

    return jsonify({"summary": summary})

# Route for the quiz generator
@app.route('/quizMaker', methods = ["GET", "POST"])
def quizMake():
    return render_template('quiz_generator.html')

# Route used to generate a quiz based on the parameters provided by the user
@app.route('/createQuiz', methods = ["POST"])
def genQuiz():
    # Get the quiz parameters from the request
    session['difficulty'] = request.json.get('difficulty')
    session['subject'] = request.json.get('subject')
    session['checkbox'] = request.json.get('checkbox')
    session['question_type'] = request.json.get('question_type')
    session['num_questions'] = request.json.get('num_questions')
    
    # if the checkbox is checked, generate practice questions with hints and answers
    if session['checkbox']:

        raw_test = quiz_maker.generate_practice_questions(session['num_questions'], session['subject'], session['difficulty'], session['question_type'])

        # create markdown object to convert
        md = markdown.Markdown(
            extensions=['markdown.extensions.extra'],
            output_format='html5'
        )

        html = md.convert(raw_test)

        # Split the HTML into hints and answers sections, and make them collapsible via accordion

        marker_hints = '<strong>Hints:</strong>'
        marker_answer = '<strong>Answers:</strong>'

        # Initialize before, after, and answer variables
        before, after, answer = '', '', ''

        # Check if the markers are in the HTML and split accordingly
        if marker_hints in html:
            before, after = html.split(marker_hints)
            if marker_answer in after:
                after, answer = after.split(marker_answer)
            
        # Create the accordion HTML structure with the split content
        test = f"""
        <div class="accordion" id="accordQuiz">
            <div class="accordion-item">
                <h2 class="accordion-header" id="headingOne">
                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                    Questions
                </button>
                </h2>
                <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne">
                <div class="accordion-body">
                    {before}
                </div>
                </div>
            </div>
            <div class="accordion-item">
                <h2 class="accordion-header" id="headingTwo">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                    Answers
                </button>
                </h2>
                <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo">
                <div class="accordion-body">
                   {after}
                </div>
                </div>
            </div>
            <div class="accordion-item">
                <h2 class="accordion-header" id="headingThree">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                    Hints
                </button>
                </h2>
                <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree">
                <div class="accordion-body">
                    {answer}
                </div>
                </div>
            </div>
            </div>
    
        """
        
        
    else:

        # create normal quiz without hints
        raw_test = quiz_maker.generate_quiz(session['num_questions'], session['subject'], session['difficulty'], session['question_type'])
        md = markdown.Markdown(
            extensions=['markdown.extensions.extra'],
            output_format='html5'
        )

        # only split the HTML into an answer key section


        html = md.convert(raw_test)
        marker = '<strong>Answers:</strong>'

        # Initialize before and after variables
        before, after = '', ''
        if marker in html:
            before, after = html.split(marker, 1)

        # Create the accordion HTML structure with the split content
        test = f"""
        <div class="accordion" id="accordQuiz">
            <div class="accordion-item">
                <h2 class="accordion-header" id="headingOne">
                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                    Questions
                </button>
                </h2>
                <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne">
                <div class="accordion-body">
                    {before}
                </div>
                </div>
            </div>
            <div class="accordion-item">
                <h2 class="accordion-header" id="headingTwo">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                    Answers
                </button>
                </h2>
                <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo">
                <div class="accordion-body">
                   {after}
                </div>
                </div>
            </div>
        </div>
    
        """
    
    # Store the quiz in the database if the user is logged in
    if 'user' in session:
        user = User.query.filter_by(google_id = session['user']['sub']).first()
        if user:
            stored_quiz = f"""
            <div class="card mt-5">
                <div class="card-body">
                    {test}
                </div>
            </div>
            """
            note = Quiz(content=stored_quiz, user_id=user.id)
            db.session.add(note)
            db.session.commit()

    return jsonify({"test": test})

# Route for the derivative calculator
@app.route('/derivativeCalculator', methods = ["GET", "POST"])
def derivativeCalc():
    return render_template('derivative_calculator.html')

# Route used to calculate the derivative of an equation
@app.route('/calculation', methods = ["POST"])
def calculate():

    # Get the equation and order from the request
    session['equation'] = request.json.get('equation')
    session['order'] = request.json.get('order')

    # Calculate the derivative
    solution = derivative_solver.solve_derivative(session['equation'], session['order'])

    # Store the solution in the database if the user is logged in
    return jsonify({"solution": solution})

# Route for the my notes page
@app.route('/my_notes')
def my_notes():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect('/login')
    
    # Get the user's notes from the database
    user = User.query.filter_by(google_id=session['user']['sub']).first()
    notes = user.notes if user else []

    # Get the note content to return
    returned_notes = [note.content for note in notes]

    return render_template('my_notes.html', notes=returned_notes)



# Route for the my notes page
@app.route('/my_quizzes')
def my_quizzes():
    # Check if the user is logged in
    if 'user' not in session:
        return redirect('/login')
    
    # Get the user's quizzes from the database
    user = User.query.filter_by(google_id=session['user']['sub']).first()
    quizzes = user.quizzes if user else []

    # Get the quiz content to return
    returned_quizzes = [quiz.content for quiz in quizzes]

    return render_template('my_quizzes.html', quizzes=returned_quizzes)


# Route for the login page, redirects to Google OAuth
@app.route('/login')
def login():
    
    redirect_uri = url_for('auth', _external=True)
    print(redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri)

# Receives the OAuth callback and processes the user information
@app.route('/auth')
def auth():

    # Get the token from the OAuth response
    token = oauth.google.authorize_access_token()

    # Store the user information in the session
    userinfo = token['userinfo']
    session['user'] = token['userinfo']

    # Check if the user already exists in the database
    user = User.query.filter_by(google_id=userinfo['sub']).first()
    if not user:
        user = User(google_id=userinfo['sub'], email=userinfo['email'])
        db.session.add(user)
        db.session.commit()

    return redirect('/')

# Route for logging out the user
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')