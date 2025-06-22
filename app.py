from flask import Flask, render_template, request
import spacy

# Initialize Flask app
app = Flask(__name__)  # ✅ Fixed here

# Load SpaCy's English model
nlp = spacy.load("en_core_web_sm")

# Function to generate enhanced questions
def generate_enhanced_questions(text):
    doc = nlp(text)
    qa_pairs = []

    for sent in doc.sents:
        sentence = sent.text.strip()
        sent_doc = nlp(sentence)
        added = False

        for ent in sent_doc.ents:
            if ent.label_ == "PERSON":
                qa_pairs.append((f"Who is mentioned in the sentence: '{sentence}'?", ent.text))
                added = True
            elif ent.label_ == "GPE":
                qa_pairs.append((f"What place is referred to in: '{sentence}'?", ent.text))
                added = True
            elif ent.label_ in ["DATE", "TIME"]:
                qa_pairs.append((f"When does the action take place in: '{sentence}'?", ent.text))
                added = True
            elif ent.label_ == "ORG":
                qa_pairs.append((f"Which organization is highlighted in: '{sentence}'?", ent.text))
                added = True
            elif ent.label_ == "EVENT":
                qa_pairs.append((f"What event is referenced in: '{sentence}'?", ent.text))
                added = True

        if not added:
            nouns = [token.text for token in sent_doc if token.pos_ == "NOUN"]
            verbs = [token.text for token in sent_doc if token.pos_ == "VERB"]

            if verbs:
                qa_pairs.append((f"What action is performed in: '{sentence}'?", verbs[0]))
            elif nouns:
                qa_pairs.append((f"What is the main subject in: '{sentence}'?", nouns[0]))
            else:
                qa_pairs.append((f"What is implied in: '{sentence}'?", sentence.split()[0]))

    return list(set(qa_pairs))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        paragraph = request.form['paragraph']
        if not paragraph.strip():
            return "Please enter a valid paragraph."

        qa_pairs = generate_enhanced_questions(paragraph)
        return render_template('result.html', qa_pairs=qa_pairs, paragraph=paragraph)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':  # ✅ Fixed here
    app.run(debug=True)
