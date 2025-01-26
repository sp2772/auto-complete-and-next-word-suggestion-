import tkinter as tk
from tkinter import ttk
import difflib
from autocorrect import Speller
import nltk
from nltk.corpus import words
import csv
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import re
import threading                             #GUI IS WRONG! DONT RUN THIS. THIS IS UNDER CONSTRUCTION
import queue
from functools import partial
from usegpuword import correct_word_suggestions
from usegpusentence import get_input_output

class CombinedSuggester:
    def __init__(self):
        # Initialize word suggestion components
        self.spell = Speller()
        nltk.download('words', quiet=True)
        self.word_list = set(words.words())
        
        # Initialize GPT-2 components
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")
        
        # Load common words
        self.common_words = self.load_common_words()
        
    def load_common_words(self):
        wordlist = []
        try:
            with open('unigram_freq.csv', 'r') as f:
                reader = csv.reader(f)
                count = 0
                for row in reader:
                    if count == 20000:
                        break
                    if (len(row[0]) < 2 and row[0].lower() not in 'ai') or not row[0].isalpha():
                        continue
                    count += 1
                    wordlist.append(row[0].lower())
        except FileNotFoundError:
            print("Warning: unigram_freq.csv not found. Using limited word list.")
            wordlist = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "i"]
        return wordlist

    def get_word_suggestions(self, current_word):
        """Get suggestions for the current word being typed."""
        if not current_word:
            return [], [], []
        
        # # Get raw completions and similar words
        # completions = [word for word in self.word_list if word.startswith(current_word.lower())]
        # similar_words = difflib.get_close_matches(current_word, self.word_list, n=10, cutoff=0.6)
        
        # # Filter by common words
        # best_completions = []
        # best_similar = []
        # other_similar = []
        
        # # Get best completions
        # for word in self.common_words:
        #     if word in completions and len(best_completions) < 5:
        #         best_completions.append(word)
                
        # # Get best similar words
        # for word in self.common_words:
        #     if word in similar_words and len(best_similar) < 5:
        #         best_similar.append(word)
                
        # # Get other similar words
        # for word in similar_words:
        #     if word not in best_similar:
        #         other_similar.append(word)

        best_c_words,best_s_words,other_s_words,best_c_wordsR,best_s_wordsR,other_s_wordsR = correct_word_suggestions(current_word)
        best_completions= list(set(best_c_wordsR+best_c_words))
        best_similar= list(set(best_s_wordsR+best_s_words))
        other_similar= list(set(other_s_wordsR+other_s_words))
        
        return best_completions, best_similar, other_similar

    def get_next_word_suggestions(self, text):
        """Get suggestions for the next word using GPT-2."""
        if not text:
            return []
        
        # inputs = self.tokenizer.encode(text, return_tensors="pt")
        # attention_mask = torch.ones_like(inputs)
        
        # outputs = self.model.generate(
        #     inputs,
        #     attention_mask=attention_mask,
        #     max_length=inputs.size(1) + 5,
        #     num_return_sequences=3,
        #     do_sample=True,
        #     temperature=0.7,
        #     top_k=50,
        #     top_p=0.9,
        #     pad_token_id=self.tokenizer.eos_token_id
        # )
        
        # suggestions = []
        # for output in outputs:
        #     generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
        #     next_part = generated_text[len(text):].strip().split()
        #     if next_part:
        #         word = next_part[0].strip(",.!?\"'")
        #         if re.match(r"^[a-zA-Z]+$", word) and word not in suggestions:
        #             suggestions.append(word)

        Suggestions, sentences =get_input_output(text)
                    
        return Suggestions,sentences

class SuggestionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Word Suggester")
        
        # Initialize the suggester
        self.suggester = CombinedSuggester()
        
        # Create suggestion queue and thread
        self.suggestion_queue = queue.Queue()
        self.should_stop = False
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create text input
        self.text_input = tk.Text(main_frame, height=5, width=50, wrap=tk.WORD)
        self.text_input.grid(row=0, column=0, columnspan=2, pady=5)
        self.text_input.bind('<KeyRelease>', self.on_text_change)
        
        # Create suggestion displays
        # Next word suggestions
        next_word_frame = ttk.LabelFrame(main_frame, text="Next Word Suggestions", padding="5")
        next_word_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.next_word_vars = []
        self.next_word_labels = []
        for i in range(3):
            var = tk.StringVar()
            self.next_word_vars.append(var)
            label = ttk.Label(next_word_frame, textvariable=var, style='Suggestion.TLabel')
            label.grid(row=0, column=i, padx=5)
            label.bind('<Button-1>', partial(self.insert_suggestion, i, 'next'))
            self.next_word_labels.append(label)
            
        # Current word suggestions
        current_word_frame = ttk.LabelFrame(main_frame, text="Current Word Suggestions", padding="5")
        current_word_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Completions
        ttk.Label(current_word_frame, text="Completions:").grid(row=0, column=0, sticky=tk.W)
        self.completion_var = tk.StringVar()
        completion_label = ttk.Label(current_word_frame, textvariable=self.completion_var)
        completion_label.grid(row=0, column=1, sticky=tk.W)
        
        # Similar words
        ttk.Label(current_word_frame, text="Similar:").grid(row=1, column=0, sticky=tk.W)
        self.similar_var = tk.StringVar()
        similar_label = ttk.Label(current_word_frame, textvariable=self.similar_var)
        similar_label.grid(row=1, column=1, sticky=tk.W)
        
        # Start suggestion thread
        self.suggestion_thread = threading.Thread(target=self.process_suggestions, daemon=True)
        self.suggestion_thread.start()
        
        # Configure styles
        style = ttk.Style()
        style.configure('Suggestion.TLabel', foreground='blue', cursor='hand2')
        
    def on_text_change(self, event):
        """Handle text change events."""
        # Get current text and word
        text = self.text_input.get("1.0", "end-1c")
        current_word = text.split()[-1] if text.split() else ""
        
        # Add to suggestion queue
        self.suggestion_queue.put((text, current_word))
        
    def process_suggestions(self):
        """Process suggestions in a separate thread."""
        while not self.should_stop:
            try:
                text, current_word = self.suggestion_queue.get(timeout=0.1)
                
                # Get suggestions
                completions, similar, other = self.suggester.get_word_suggestions(current_word)
                next_words,texts = self.suggester.get_next_word_suggestions(text)
                
                # Update GUI
                self.root.after(0, self.update_suggestions,
                              completions, similar, other, next_words+texts)
                
            except queue.Empty:
                continue
            
    def update_suggestions(self, completions, similar, other, next_words):
        """Update the GUI with new suggestions."""
        # Update completion suggestions
        self.completion_var.set(", ".join(completions))
        
        # Update similar word suggestions
        similar_text = ", ".join(similar)
        if other:
            similar_text += " | " + ", ".join(other)
        self.similar_var.set(similar_text)
        
        # Update next word suggestions
        for i, var in enumerate(self.next_word_vars):
            if i < len(next_words):
                var.set(next_words[i])
            else:
                var.set("")
                
    def insert_suggestion(self, index, suggestion_type, event):
        """Insert the selected suggestion into the text input."""
        if suggestion_type == 'next':
            suggestion = self.next_word_vars[index].get()
            if suggestion:
                current_text = self.text_input.get("1.0", "end-1c")
                if current_text and not current_text.endswith(" "):
                    suggestion = " " + suggestion
                suggestion += " "
                self.text_input.insert("end", suggestion)
                self.text_input.see("end")
                
    def cleanup(self):
        """Cleanup resources before closing."""
        self.should_stop = True
        if self.suggestion_thread.is_alive():
            self.suggestion_thread.join()

def main():
    root = tk.Tk()
    app = SuggestionGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()