from model import *

client = generate_model()

def generate_quiz(num_questions, content, grade, format="multiple-choice"):
	prompt = f"""
    You are a quiz maker, for students of grade {grade} (Treat any grade above 12 as College Level).
    Create a quiz with {num_questions} {format} questions on: {content}. 
    
    Example formats for the quizzes are below:

     Multiple Choice:
      **Questions:**
      
        1. [Question 1]  
           a) [Answer 1]  
           b) [Answer 2]  
           c) [Answer 3]  
           d) [Answer 4]
        
        2. [Question 2]  
           a) [Answer 1]  
           b) [Answer 2]  
           c) [Answer 3]  
           d) [Answer 4]
        ......

      **Answers:**
      
        1. [Correct Answer Letter]
        2. [Correct Answer Letter]
        ......

    Free Response:
      **Questions:**
      
        1. [Question 1]
        2. [Question 2]
        ......
        
      **Answers:**
      
        1. [Example Answer 1]
        2. [Example Answer 2]
        ......

    IMPORTANT FORMATTING RULES:
    - For multiple choice, put each option (a, b, c, d) on its own line with proper indentation
    - Use 3 spaces before each option letter to ensure proper alignment
    - Leave blank lines between questions
    - Free Response questions can be any length, and example answers should be general enough
    - Any math should be in latex notation
	
    """

  # Generate the quiz using the OpenAI API and the provided prompt
	response = client.chat.completions.create(
		model = "gpt-4o-mini",
		messages = [
			{"role": "system", "content": "You are an assistant tuned to writing quizzes for students of any skill level."},
			{"role": "user", "content": prompt}
		],
		temperature = 0.7
    )

	return response.choices[0].message.content

def generate_practice_questions(num_questions, content, grade, format="multiple-choice"):
	prompt = f"""
    You are a practice question generator, for students of grade {grade}.
    Create {num_questions} {format} questions on: {content}.
	  Include Hints for each question, that will help students understand the concepts better.
    
    Example formats are below:

    Multiple Choice:
      **Questions:**
      
        1. [Question 1]  
           a) [Answer 1]  
           b) [Answer 2]  
           c) [Answer 3]  
           d) [Answer 4]
        
        2. [Question 2]  
           a) [Answer 1]  
           b) [Answer 2]  
           c) [Answer 3]  
           d) [Answer 4]
        ......
        
      **Hints:**
      
        1. [Hint 1]
        2. [Hint 2]
        ......
        
      **Answers:**
      
        1. [Correct Answer Letter]
        2. [Correct Answer Letter]
        ......

    Free Response:
      **Questions:**
      
        1. [Question 1]
        2. [Question 2]
        ......
        
      **Hints:**
      
        1. [Hint 1]
        2. [Hint 2]
        ......
        
      **Answers:**
      
        1. [Example Answer 1]
        2. [Example Answer 2]
        ......
	  

    Provide the questions and answers clearly as per the formats above. Only stick to one format, and ensure that it follows
	
    IMPORTANT FORMATTING RULES:
    - For multiple choice, put each option (a, b, c, d) on its own line with proper indentation
    - Use 3 spaces before each option letter to ensure proper alignment
    - Leave blank lines between questions for readability
    - Free Response questions can be any length, and example answers should be general enough
    - Provide the hints after the questions, and before the answers
    - Any math should be in latex notation
	
    """

	response = client.chat.completions.create(
		model = "gpt-4o-mini",
		messages = [
			{"role": "system", "content": "You are an assistant tuned to making practice questions for students of any skill level."},
			{"role": "user", "content": prompt}
		],
		temperature = 0.7
    )

	return response.choices[0].message.content