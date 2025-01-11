import sys  # Provides Python system interaction tools.
sys.path.append(r"C:/Users/ashis/anaconda3/lib/site-packages")
import flet as ft
from spellchecker import SpellChecker
import language_tool_python  # For grammar checking
import re


# Initialize the grammar checking tool
tool = language_tool_python.LanguageTool('en-US')  # Specify the language


def main(page: ft.Page):
    page.title = "Real-Time Spell and Grammar Checker"
    page.padding = 20
    page.scroll = "adaptive"
    page.bgcolor = "black"  # Set background color to black

    # Function to tokenize text and filter out punctuation
    def tokenize_text(text):
        return [word for word in re.findall(r'\b\w+\b', text)]

    # Function to highlight text in real time
    def highlight_text(e):
        text = text_input.value.strip()
        if not text:
            result_container.controls.clear()
            page.update()
            return

        # Tokenize the text
        words = tokenize_text(text)

        # Spell checking
        spell = SpellChecker()
        misspelled_words = spell.unknown(words)

        # Grammar checking
        sentences = re.split(r'(?<=[.!?])\s+', text)
        grammar_errors = []
        capitalization_errors = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check capitalization of the first word
            first_word = sentence.split()[0]
            if first_word[0].islower() and first_word not in misspelled_words:
                capitalization_errors.append(first_word)

            # Grammar checking using language_tool_python
            matches = tool.check(sentence)
            for match in matches:
                error = match.context[match.offset:match.offset + match.errorLength]
                grammar_errors.append(error)

        # Build highlighted text
        highlighted_controls = []
        for word in text.split():
            if word in misspelled_words:
                highlighted_controls.append(ft.Text(word + " ", color="red"))
            elif word in capitalization_errors:
                highlighted_controls.append(ft.Text(word + " ", color="orange"))
            elif word in grammar_errors:
                highlighted_controls.append(ft.Text(word + " ", color="orange"))
            else:
                highlighted_controls.append(ft.Text(word + " ", color="white"))  # Set normal text to white

        # Update the result container
        result_container.controls.clear()
        result_container.controls.extend(highlighted_controls)
        page.update()

    # Function to correct text when "Correct" button is clicked
    def correct_text(e):
        text = text_input.value.strip()
        if not text:
            return

        # Correct misspelled words
        spell = SpellChecker()
        words = tokenize_text(text)
        corrected_text = text
        for word in spell.unknown(words):
            corrected_text = corrected_text.replace(word, spell.correction(word))

        # Correct grammar and capitalization
        sentences = re.split(r'(?<=[.!?])\s+', corrected_text)
        corrected_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            matches = tool.check(sentence)
            for match in matches:
                error = match.context[match.offset:match.offset + match.errorLength]
                if match.replacements:
                    sentence = sentence.replace(error, match.replacements[0])

            # Capitalize the first letter after punctuation
            if sentence and sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]
            corrected_sentences.append(sentence)

        corrected_text = " ".join(corrected_sentences)

        # Update the text input with corrected text
        text_input.value = corrected_text
        highlight_text(e)  # Re-highlight the corrected text
        page.update()

    # Clear text function
    def clear_text(e):
        text_input.value = ""
        result_container.controls.clear()
        page.update()

    # UI Elements
    text_input = ft.TextField(
        label="Enter Text",
        multiline=True,
        expand=True,
        height=200,
        on_change=highlight_text,
        bgcolor="black",  # Match background color for consistency
    )

    correct_button = ft.ElevatedButton("Correct", on_click=correct_text)
    clear_button = ft.ElevatedButton("Clear", on_click=clear_text)

    result_container = ft.Row(wrap=True, expand=True)  # For dynamic highlighting

    # Add components to the page
    page.add(
        ft.Column([
            text_input,
            ft.Row([correct_button, clear_button], alignment="end"),
            ft.Divider(),
            result_container,
        ])
    )


# Run the Flet app
ft.app(target=main)
