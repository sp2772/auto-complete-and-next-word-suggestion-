from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import re
from typing import Tuple, List
import time

class SuggestionBox:
    def __init__(self, model_name="gpt2"):
        # Load model and tokenizer with better defaults
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Set model to evaluation mode for faster inference
        self.model.eval()

    def is_valid_word(self, word: str) -> bool:
        """Check if a token is a valid word."""
        return bool(re.match(r"^[a-zA-Z]+$", word))

    def get_next_word_probabilities(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Get the most likely next words and their probabilities."""
        with torch.no_grad():  # Disable gradient calculation for faster inference
            inputs = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
            
            outputs = self.model(inputs)
            next_token_logits = outputs.logits[0, -1, :]
            
            # Get top k probabilities and indices
            probs = torch.nn.functional.softmax(next_token_logits, dim=0)
            top_k_probs, top_k_indices = torch.topk(probs, top_k)
            
            # Convert to words
            words_and_probs = []
            for prob, idx in zip(top_k_probs, top_k_indices):
                word = self.tokenizer.decode([idx]).strip()
                if self.is_valid_word(word):
                    words_and_probs.append((word, prob.item()))
            
            return words_and_probs

    def get_suggestions(self, text: str, max_suggestions: int = 3) -> Tuple[List[str], List[str]]:
        """Get suggestions for the next word and complete sentences."""
        # Get probable next words
        word_probs = self.get_next_word_probabilities(text, top_k=20)
        
        suggestions = []
        texts = []
        
        
        
        # If we need more suggestions, generate them with a small max_length
        while len(suggestions) < max_suggestions:
            with torch.no_grad():
                inputs = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
                attention_mask = torch.ones_like(inputs)
                outputs = self.model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_length=inputs.size(1) + 10,  # Limit generation length
                    num_return_sequences=max_suggestions - len(suggestions),
                    do_sample=True,
                    temperature=0.7,
                    top_k=50,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                for output in outputs:
                    generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
                    next_part = generated_text[len(text):].strip().split()
                    
                    if next_part:
                        word = next_part[0].strip(",.!?\"'")
                        if self.is_valid_word(word) and word not in suggestions:
                            suggestions.append(word)
                            texts.append(generated_text)
            if len(suggestions) >= max_suggestions:
                break
        return suggestions, texts

def get_input_output(my_str: str) -> Tuple[List[str], List[str]]:
    suggestion_box = SuggestionBox()
    return suggestion_box.get_suggestions(my_str)

if __name__ == "__main__":
    while True:
        broken=input("Enter a sentence:")
        start_time = time.time()
        suggestions, sentences = get_input_output(broken)
        print("Suggested words:", ", ".join(suggestions))
        print("Suggested sentences:", "\n".join(sentences))
        print(f"Time taken: {time.time() - start_time:.2f} seconds")
        