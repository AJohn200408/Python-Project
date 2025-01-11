import tkinter as tk # class for display, positioning and control of widgets.
import re           #Python's regular expression module, used for sentence splitting and cleaning.
import sys          #provides Python system interaction tools.         
sys.path.append(r"C:/Users/ashis/anaconda3/lib/site-packages")
from spellchecker import SpellChecker
import language_tool_python  # For grammar checking

# Initialize the grammar checking tool
tool = language_tool_python.LanguageTool('en-US')  # You can specify other languages like 'en-GB', 'fr', etc.

# Function to highlight misspelled words and grammar errors
def highlight_errors():  
    text = text_input.get("1.0", tk.END).strip()
    text_input.tag_remove("misspelled", "1.0", tk.END)  # Clear previous highlights for misspelled words
    text_input.tag_remove("grammar_error", "1.0", tk.END)  # Clear previous highlights for grammar errors

    if not text:
        result_label.config(text="")
        return

    # Spell checking
    spell = SpellChecker()
    words = text.split()
    misspelled_words = spell.unknown(words) # unknown used to identify words not in dictionary.

    # Highlight misspelled words and collect spelling corrections
    spelling_corrections = []
    start_index = "1.0"
    for word in words:
        if word in misspelled_words:
            spelling_corrections.append(f"{word} -> {spell.correction(word)}")
            start_index = text_input.search(word, start_index, tk.END)
            if start_index:
                end_index = f"{start_index}+{len(word)}c"
                text_input.tag_add("misspelled", start_index, end_index)
                start_index = end_index

    # Grammar checking by sentences
    grammar_corrections = []
    sentences = re.split(r'(?<=\w[.?!;])\s*', text)  # Split by punctuation marks (.?!,;)

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            # Remove ending punctuation for grammar checking
            cleaned_sentence = re.sub(r'[.?!,;]$', '', sentence)

            # Exclude misspelled words from the grammar check
            cleaned_sentence_words = cleaned_sentence.split()
            filtered_words = [word for word in cleaned_sentence_words if word not in misspelled_words]
            filtered_sentence = " ".join(filtered_words)

            # Check for grammar errors
            matches = tool.check(filtered_sentence)
            if matches:  # If there are grammar errors in the sentence
                # Highlight the entire sentence in blue
                start_index = text.find(sentence)
                end_index = start_index + len(sentence)
                text_input.tag_add("grammar_error", f"1.0+{start_index}c", f"1.0+{end_index}c")

                # Collect grammar corrections
                for match in matches:
                    error = match.context[match.offset:match.offset + match.errorLength]
                    suggestions = ", ".join(match.replacements)
                    grammar_corrections.append(f"{error} -> {suggestions}")

    # Update result label with corrections
    result_label.config(
        text=(
            "Spelling Corrections:\n" + "\n".join(spelling_corrections) +
            "\n\nGrammar Corrections:\n" + "\n".join(grammar_corrections)
        ) if spelling_corrections or grammar_corrections else "All text is correct!"
    )

def clear_text():
    text_input.delete("1.0", tk.END)
    result_label.config(text="")
    text_input.tag_remove("misspelled", "1.0", tk.END)
    text_input.tag_remove("grammar_error", "1.0", tk.END)

# Set up the main application window
root = tk.Tk()
root.title("Real-Time Spell and Grammar Checker")
root.geometry("800x700")  # window size
root.config(bg="#f0f0f0")  # background color

# Define text styles
text_input = tk.Text(root, height=15, width=80, wrap=tk.WORD, font=("Open Sans", 16), bg="#ffffff", fg="#333", insertbackground="blue")
text_input.pack(pady=20, fill=tk.X)  # Increased padding

text_input.tag_config("misspelled", foreground="red")  # Orange color for misspelled words
text_input.tag_config("grammar_error", foreground="orange")  # Cyan color for grammar errors
text_input.bind("<KeyRelease>", lambda event: highlight_errors())

# Thin line to separate text input and output
separator = tk.Frame(root, height=2, bg="#cccccc")
separator.pack(fill=tk.X, padx=10, pady=10)

# Label to display corrections
result_label = tk.Label(root, text="", justify=tk.LEFT, wraplength=700, bg="#ffffff", fg="#333", font=("Open Sans", 14), anchor="nw")
result_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Clear button at bottom right
clear_button = tk.Button(root, text="Clear", command=clear_text, bg="#e74c3c", fg="white", font=("Open Sans", 14), padx=10, pady=5)
clear_button.pack(side=tk.BOTTOM, anchor=tk.NE, padx=10, pady=10)  # Positioned at the bottom right corner

# Run the application
root.mainloop()
