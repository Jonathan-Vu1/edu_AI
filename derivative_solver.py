import torch
import pickle
import __main__

from transformer_model import TransformerModel
import re

__main__.TransformerModel = TransformerModel

def math_tokenizer(text):

    # some patterns
    patterns = [
        (r'\*\*', 'OP'),
        (r'[\+\-\*/\^=<>]', 'OP'),
        (r'[\(\)\[\]\{\}]', 'BRACKET'),
        (r'[a-zA-Z_][a-zA-Z0-9_]*', 'VAR'),
        (r'\s+', 'SPACE'),
    ]

    tokens = []
    index = 0

    while index < len(text):
        if (text[index].isdigit() or (text[index] == '.' and index + 1 < len(text) and text[index + 1].isdigit())):

            # If number is there, match it.
            number_match = re.match(r'\d+\.\d+|\d+', text[index:])

            if number_match:

                num_str = number_match.group(0)

                for digit in num_str:
                    tokens.append(digit)

                index += len(num_str)
                continue

        # If it isn't a number, try to see if it's a knwon regex pattern
        match_found = False
        for pattern, _ in patterns:
            regex = re.compile(pattern)
            match = regex.match(text[index:])

            # if it is a known operation, add it
            if match:
                token_text = match.group(0)
                tokens.append(token_text)
                index += len(token_text)
                match_found = True
                break

        # worst case, just add the token
        if not match_found:
            tokens.append(text[index])
            index += 1

    return tokens

def load_vocab(vocab_path):
    with open(vocab_path, 'rb') as f:
    	return pickle.load(f)
     
def solve_derivative(equation, derivative):
     
	# Load the model
	device = "cuda" if torch.cuda.is_available() else "cpu"
	model = torch.load(
        "colab_files/trained_models/diff_model_3.pth",
        map_location=device
    )
	model.to(device)
	model.eval()
     

    # Prepare the input text
	input_text = f'Find the {derivative} derivative of {equation}.'
     
	vocab = load_vocab("colab_files\\trained_models\\vocab.pkl")

	
	with torch.no_grad():

        # I really don't like this, but it works for now
		src_tokens  = math_tokenizer(input_text)
		src_indices = [vocab["<start>"]] + vocab.lookup_indices(src_tokens) + [vocab["<end>"]]
		src_tensor = torch.tensor([src_indices], dtype=torch.long).to(device)

        # Add start token to question
		tgt_indices = [vocab["<start>"]]
		tgt_input = torch.tensor([tgt_indices], dtype=torch.long).to(device)

        # Generate tokens
		for _ in range(100):

            # Predict next token from model
			output = model(src_tensor, tgt_input)

			# Choose best option
			next_token = output.argmax(dim=-1)[:, -1].item()

			# Add and create iteratively
			tgt_indices.append(next_token)
			tgt_input = torch.tensor([tgt_indices], dtype=torch.long).to(device)

			# Stop if end token is predicted
			if next_token == vocab["<end>"]:
				break
		
    # Convert indices back to tokens
	input_tokens = [vocab.get_itos()[idx] for idx in src_tensor[0].cpu().numpy()]
	output_tokens = [vocab.get_itos()[idx] for idx in tgt_indices[1:-1]]

	# Get original questions
	input_question = "".join(input_tokens)
	output_answer = "".join(output_tokens)

	print(f"Input Question: {input_question}")
	print(f"Predicted Answer: {output_answer}")
     
	return output_answer
