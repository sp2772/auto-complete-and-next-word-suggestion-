import difflib
from autocorrect import Speller
import nltk
from nltk.corpus import words
from frequentwordlist import get_word_list
from functools import lru_cache
from typing import Set, List, Dict, Tuple
import threading
import time

def ensure_nltk_resources():
    """Ensure all required NLTK resources are downloaded."""
    try:
        # Try to access words to check if they're downloaded
        words.words()
    except LookupError:
        print("Downloading required NLTK resources...")
        nltk.download('words', quiet=True)
        print("Download complete!")
        
class WordSuggestor:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WordSuggestor, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        ensure_nltk_resources()
        # Initialize only once
        self.spell = Speller()
        
        # Pre-load and cache word lists
        self.word_list = set(words.words())
        self.frequent_words = set(get_word_list())
        
        # Create prefix dictionary for faster completion lookups
        self.prefix_dict = {}
        for word in self.word_list:
            for i in range(1, len(word) + 1):
                prefix = word[:i]
                if prefix not in self.prefix_dict:
                    self.prefix_dict[prefix] = set()
                self.prefix_dict[prefix].add(word)
                
        self._initialized = True

    @lru_cache(maxsize=1000)
    def correct_spelling(self, word: str) -> str:
        """Cache-enabled spelling correction."""
        return self.spell(word)

    def complete_word(self, incomplete_word: str) -> Set[str]:
        """Optimized word completion using prefix dictionary."""
        return self.prefix_dict.get(incomplete_word, set())

    @lru_cache(maxsize=1000)
    def get_similar_words(self, word: str) -> List[str]:
        """Cache-enabled similar word generation."""
        return difflib.get_close_matches(word, self.word_list, n=10, cutoff=0.7)

    def generate_suggestions(self, word: str) -> Dict[str, any]:
        """Generate all suggestions with parallel processing for longer words."""
        corrected_word = self.correct_spelling(word)
        print("Corrected word:",corrected_word)
        # Get completions and similar words in parallel for longer words
        if len(word) > 3:
            completions = set()
            similar_words = []
            raw_completions = set()
            raw_similar = []
            
            def get_completions():
                nonlocal completions
                completions = self.complete_word(corrected_word)
                
            def get_similar():
                nonlocal similar_words
                similar_words = self.get_similar_words(corrected_word)
                
            def get_raw_completions():
                nonlocal raw_completions
                raw_completions = self.complete_word(word)
                
            def get_raw_similar():
                nonlocal raw_similar
                raw_similar = self.get_similar_words(word)
            
            threads = [
                threading.Thread(target=get_completions),
                threading.Thread(target=get_similar),
                threading.Thread(target=get_raw_completions),
                threading.Thread(target=get_raw_similar)
            ]
            
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        else:
            
            completions = self.complete_word(corrected_word)
            similar_words = self.get_similar_words(corrected_word)
            raw_completions = self.complete_word(word)
            raw_similar = self.get_similar_words(word)

        return {
            "corrected_word": corrected_word,
            "completions": completions,
            "similar_words": similar_words,
            "raw_completions": raw_completions,
            "raw_similar": raw_similar
        }

def get_best_matches(words: Set[str], frequent_words: Set[str], limit: int) -> List[str]:
    """Get best matches based on frequency list."""
    return [word for word in frequent_words if word in words][:limit]

def correct_word_suggestions(my_inp: str) -> Tuple[List[str], List[str], List[str], List[str], List[str], List[str]]:
    if not my_inp:
        return [], [], [], [], [], []
    
    # Use singleton instance
    suggestor = WordSuggestor()
    suggestions = suggestor.generate_suggestions(my_inp)
    
    # Get best matches efficiently
    best_c_words = get_best_matches(suggestions["completions"], suggestor.frequent_words, 5)
    best_s_words = get_best_matches(set(suggestions["similar_words"]), suggestor.frequent_words, 5)
    best_c_wordsR = get_best_matches(suggestions["raw_completions"], suggestor.frequent_words, 5)
    best_s_wordsR = get_best_matches(set(suggestions["raw_similar"]), suggestor.frequent_words, 5)
    other_s_words = [word for word in suggestions["similar_words"] if word not in best_s_words]
    other_s_wordsR = [word for word in suggestions["raw_similar"] if word not in best_s_wordsR]
    
    return best_c_words, best_s_words, other_s_words, best_c_wordsR, best_s_wordsR, other_s_wordsR
    
    

if __name__ == "__main__":
    while True:
        joke=input("type:")
        start_time = time.time()
        result = correct_word_suggestions(joke)
        print(f"Time taken: {time.time() - start_time:.2f} seconds")
        print("Results:", result)