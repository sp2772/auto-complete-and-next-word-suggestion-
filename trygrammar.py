from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import re
  # For grammar checking (not needed right now)


class SuggestionBox:
    def __init__(self, model_name="gpt2"):
        #load the pre-trained GPT-2 model and tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
          #Initialize grammar checker

    def is_valid_word(self, word):
        """Check if a token is a valid word."""
        return re.match(r"^[a-zA-Z]+$", word)  #Only alphabetic words

    # def is_grammatically_correct(self, sentence):
    #     """Check if a sentence is grammatically correct."""
    #     matches = self.grammar_tool.check(sentence)
    #     return len(matches) == 0  #true if no grammar issues

    def get_suggestions(self, text, max_suggestions=3):
        
        suggestions = []
        texts = []
        inputs = self.tokenizer.encode(text, return_tensors="pt")
        attention_mask = torch.ones_like(inputs)  # Create attention mask

        while len(suggestions) < max_suggestions:

        # Generate predictions (not strictly limiting to only a few tokens)
            outputs = self.model.generate(
                inputs,
                attention_mask=attention_mask,
                max_length=inputs.size(1) + 25,  #allow a bit more flexibility, generating up to 20 tokens
                num_return_sequences=3,  #generate 3 different sequences
                do_sample=True,  #enable sampling
                temperature=0.8,  #adjust randomness
                top_k=50,  #Use top-k sampling for diversity
                top_p=0.9,  #nucleus sampling for balanced results
                pad_token_id=self.tokenizer.eos_token_id
            )

            for output in outputs:
                generated_text = self.tokenizer.decode(output, skip_special_tokens=True)

                # Extract next part of the text after the input text
                next_part = generated_text[len(text):].strip().split()

                if next_part:
                    #clean punctuation
                    word = next_part[0].strip(",.!?\"'")
                    if self.is_valid_word(word) and word not in suggestions:
                        suggestions.append(word)
                        texts.append(generated_text)

                #stop when enough suggestions obtained
                if len(suggestions) >= max_suggestions:
                    break

        return suggestions, texts

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
        suggestions, texts = suggestion_box.get_suggestions(user_input)
        if suggestions:
            print("Suggestions:", ", ".join(suggestions))
            print("Generated texts:(optional to print)", "\n".join(texts))
        else:
            print("No valid suggestions. Try adding more context!")

def get_input_output(my_str):
    suggestion_box = SuggestionBox()
    suggestions, texts = suggestion_box.get_suggestions(my_str)
    n=len(my_str.split())
    new_texts=[]
    for text in texts:
        if len(text.split()) - n < 4:
            new_texts.append(text)
            continue
        
        i=0
        rem_word=[]
        end=4 #take next 4 words
        for word in text.split():
            i+=1
            if i>n and i<= n+end:
                rem_word.append(word)
        new_texts.append(my_str+" "+" ".join(rem_word))
    
    return suggestions, new_texts

                
                

    

if __name__ == "__main__":
    Suggestions, sentences =get_input_output(input("Enter sentence:"))
    print("Suggested words:",", ".join(Suggestions),"\nSuggested sentences:","\n ".join(sentences))
    

    #main()
