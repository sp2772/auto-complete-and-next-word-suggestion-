from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import re

class SuggestionBox:
    def __init__(self, model_name="gpt2"):
        # Load the pre-trained GPT-2 model and tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)

    def is_valid_word(self, word):
        """Check if a token is a valid word."""
        return re.match(r"^[a-zA-Z]+$", word)  # Only alphabetic words

    def get_suggestions(self, text, max_suggestions=10):
        """
        Generate diverse word suggestions based on input text.
        
        Parameters:
        text (str): The input text.
        max_suggestions (int): Number of word suggestions to generate.
        
        Returns:
        list: List of diverse suggestions.
        """
        suggestions = []
        texts=[]
        inputs = self.tokenizer.encode(text, return_tensors="pt")
        attention_mask = torch.ones_like(inputs)  # Create attention mask

        while len(suggestions)<max_suggestions:
            outputs = self.model.generate(
                inputs,
                attention_mask=attention_mask,
                max_length=inputs.size(1) + 7,  # Generate up to 5 more tokens
                num_return_sequences=1,
                do_sample=True,  # Enable sampling
                temperature=0.8,  # Adjust randomness
                top_k=50,  # Use top-k sampling for diversity
                top_p=0.9,  # Nucleus sampling for balanced results
                pad_token_id=self.tokenizer.eos_token_id
            )

            # Decode generated text
            generated_text = self.tokenizer.decode(outputs[0])
            
            

            # Extract next part of the text
            next_part = generated_text[len(text):].strip().split()
            if next_part:
                word = next_part[0].strip(",.!?\"'")  # Clean punctuation
                if self.is_valid_word(word) and word not in suggestions:
                    suggestions.append(word)
                    texts.append(generated_text)

        return suggestions,texts

def main():
    suggestion_box = SuggestionBox()
    print("Google Keyboard-Like Suggestion Box (Type 'exit' to quit)")
    while True:
        user_input = input("Enter text: ").strip()
        if user_input.lower() == "exit":
            print("Exiting...")
            break
        if not user_input:
            print("Please enter some text.")
            continue
        suggestions,texts = suggestion_box.get_suggestions(user_input)
        if suggestions:
            print("Suggestions:", ", ".join(suggestions))
            print("Generated texts:", "\n".join(texts))
        else:
            print("No valid suggestions. Try adding more context!")

if __name__ == "__main__":
    main()
