import difflib
from autocorrect import Speller
import nltk
from nltk.corpus import words
from textblob import WordList
from frequentwordlist import get_word_list
nltk.download('words')

class WordSuggestor:
    def __init__(self):
        
        self.spell = Speller()
        self.word_list = set(words.words()) 

    def correct_spelling(self, word):
        """Correct the spelling of a word."""
        corrected_word = self.spell(word)
        return corrected_word

    def complete_word(self, incomplete_word):
        """Generate possible completions for an incomplete word."""
    
        possible_completions = [word for word in self.word_list if word.startswith(incomplete_word)]
        return possible_completions

    def get_similar_words(self, word):
        """Generate similar words to a given word using difflib."""
        similar_words = difflib.get_close_matches(word, self.word_list, n=10, cutoff=0.7)
        return similar_words

    def generate_suggestions(self, word):
        """Generate all possible suggestions for an incomplete or misspelled word."""
        corrected_word = self.correct_spelling(word)  # First, correct the spelling
        completions = self.complete_word(corrected_word)  # Get completions based on corrected word
        similar_words = self.get_similar_words(corrected_word)  # Get similar words for corrected word
        rawword_completions = self.complete_word(word)
        rawword_similar= self.get_similar_words(word)

        return {
            "corrected_word": corrected_word,
            "completions": completions,
            "similar_words": similar_words,
            "raw_completions": rawword_completions,
            "raw_similar": rawword_similar

        }

def main():
    
    # with open('unigram_freq.csv','r') as f:
    #     x=0
    #     r=csv.reader(f)
    #     for row in r:
    #         if x==20000:                #20000 most used english words i took 
    #             break
            
    #         if (len(row[0])<2 and row[0].lower() not in 'ai') or not row[0].isalpha():
    #             continue
    #         x+=1
    #         wordlist.append(row[0])
    
    wordlist= get_word_list()
    
    print("Length of wordlist:",len(wordlist), "hello in list:","hello" in wordlist)
    
    suggestor = WordSuggestor()
    print("Word Suggestion Program (Type 'exit' to quit)")
    
    while True:
        user_input = input("Enter a word: ").strip()
        if user_input.lower() == "exit":
            print("Exiting...")
            break
        if not user_input:
            print("Please enter a word.")
            continue

        suggestions = suggestor.generate_suggestions(user_input)
        print("Corrected word:", suggestions["corrected_word"])
      
        print("Similar words:", ", ".join(suggestions["similar_words"]))

        best_c_words=[]
        for common in wordlist:
            if common in suggestions["completions"]:
                if len(best_c_words) < 5:
                    best_c_words.append(common)
                else:
                   break
        
        best_s_words=[]
        other_s_words=[]
        for common in wordlist:
            if common in suggestions["similar_words"]:
                if len(best_s_words) < 5:
                    best_s_words.append(common)
                else:
                    break

        for word in suggestions["similar_words"]:
            if word not in best_s_words:
                other_s_words.append(word) 

        
       
          
        best_c_wordsR=[]
        for common in wordlist:
            if common in suggestions["raw_completions"]:
                if len(best_c_wordsR) < 5:
                    best_c_wordsR.append(common)
                else:
                   break
        
        best_s_wordsR=[]
        other_s_wordsR=[]
        for common in wordlist:
            if common in suggestions["raw_similar"]:
                if len(best_s_wordsR) < 5:                     
                    best_s_wordsR.append(common)
                else:
                    break

        for word in suggestions["raw_similar"]:
            if word not in best_s_wordsR:
                other_s_wordsR.append(word) 
        print("best raw completion words:",", ".join(best_c_wordsR),'\nbest raw word\'s similar words:',', '.join(best_s_wordsR),'\nother similar words of raw word:',', '.join(other_s_wordsR),'\n')
        print("best corrected completion words:",", ".join(best_c_words),'\nbest corrected word\'s similar words:',', '.join(best_s_words),'\nother similar words of corrected word:',', '.join(other_s_words))
        print("\n\nPrinted all lists:",best_c_words,best_s_words,other_s_words,best_c_wordsR,best_s_wordsR,other_s_wordsR,sep="\n")
        
def correct_word_suggestions(my_inp):
    
    #print("Length of wordlist:",len(wordlist), "hello in list:","hello" in wordlist)
    wordlist= get_word_list()
    suggestor = WordSuggestor()
    #print("Word Suggestion Program (Type 'exit' to quit)")
    
    
    user_input = my_inp
    
    if not user_input:
        #print("Please enter a word.")
        return

    suggestions = suggestor.generate_suggestions(user_input)
    #print("Corrected word:", suggestions["corrected_word"])
    
    #print("Similar words:", ", ".join(suggestions["similar_words"]))

    best_c_words=[]
    for common in wordlist:
        if common in suggestions["completions"]:
            if len(best_c_words) < 5:
                best_c_words.append(common)
            else:
                break
    
    best_s_words=[]
    other_s_words=[]
    for common in wordlist:
        if common in suggestions["similar_words"]:
            if len(best_s_words) < 5:
                best_s_words.append(common)
            else:
                break

    for word in suggestions["similar_words"]:
        if word not in best_s_words:
            other_s_words.append(word) 

    
    
        
    best_c_wordsR=[]
    for common in wordlist:
        if common in suggestions["raw_completions"]:
            if len(best_c_wordsR) < 5:
                best_c_wordsR.append(common)
            else:
                break
    
    best_s_wordsR=[]
    other_s_wordsR=[]
    for common in wordlist:
        if common in suggestions["raw_similar"]:
            if len(best_s_wordsR) < 5:                     
                best_s_wordsR.append(common)
            else:
                break

    for word in suggestions["raw_similar"]:
        if word not in best_s_wordsR:
            other_s_wordsR.append(word) 
    
    return best_c_words,best_s_words,other_s_words,best_c_wordsR,best_s_wordsR,other_s_wordsR

if __name__ == "__main__":
    main()
