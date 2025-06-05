import requests
from bs4 import BeautifulSoup
from model import *



def extract_paragraphs(url):

    # Fetch content from the URL and extract paragraphs
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, "html.parser")   

        # get all paragraphs (assumes paragraphs are what should be taken)
        paragraphs = soup.find_all('p')
        content = " ".join([para.get_text() for para in paragraphs if para.get_text()])
        return content
    
    except Exception as e:
        print(f"Failed to fetch content, error: {e}")
        return None

def generate_notes(text, length):

    client = generate_model()

    try:
        
        prompt = f"""
        Please summarize the following content into notes. 
        Make sure to keep the notes under a reasonable word limit: the output should be less than the given text.
        At the end of your notes, provide a couple bullet points with high-level takeaways from the content.

        An example output format is below:
        ### Summary Notes on []

        **[Subheading]**
        - [Notes]
        - [Notes]

        [Insert More Subheadings and Notes Here]

        ### Takeaways
        - [Takeaway]
        - [Takeaway]

        Keep the max length of the notes in mind, {length} tokens. Do not generate content that would not finish completely in the given length: all sentences, new lines, should be complete.
        Make sure that each dash is separated by a new line, and that the notes are easy to read.

        Any math should be rendered in latex notation.
        
        {text}
        """

        # Generate notes using the OpenAI API
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {"role": "system", "content": "You are an assistant tuned to providing notes for students based on content."},
                {"role": "user", "content": prompt}
            ],
            temperature = 0.7,
            max_tokens = length
        )

        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error:{e}")
        return None

def summarize_url(url, max_length=500):
    """
    Extracts content from a URL and summarizes it.
    """
    content = extract_paragraphs(url)
    if content:
        notes = generate_notes(content, max_length)
        if notes:
            return notes
        else:
            return "Failed to generate notes."
    else:
        return "Failed to fetch content."
    
# paragraphs = extract_paragraphs("https://en.wikipedia.org/wiki/Artificial_intelligence")
# print(paragraphs)
# print("---------------------------------------------")
# notes = generate_notes(paragraphs, 500)
# print(notes)
# print(summarize_url("https://en.wikipedia.org/wiki/Artificial_intelligence", 200))