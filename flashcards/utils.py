import openai
import pdfplumber
import docx
import os
from django.conf import settings

#OPENAI_API_KEY = settings.OPENAI_API_KEY

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text+"\n"
        return text.strip()
    elif ext == ".docx":
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def generate_flashcards(file_path):
    text = extract_text_from_file(file_path)
    if not text:
        return [{"error":"No text extracted from the file."}]
    
    prompt = f"""
    Create flashcards from the following text. Cover all important topics from the given text. Make it as accurate as possible with respect to the provided text. Each flashcard should follow this format:
    Question: [A key question based on the text]
    Answer: 
    [A well-explained answer obtained from the provided text in atleast 3-4 lines]
    Text:
    {text}
    """

    #print("Using GROQ API Key:", settings.GROQ_API_KEY)
    #print("Using GROQ Base URL:", settings.GROQ_BASE_URL)

    try:
        client = openai.OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL
            )
        response = client.chat.completions.create(
            model = "llama3-8b-8192",
            messages = [{"role":"user", "content":prompt}],
            max_tokens = 1500,
            temperature = 0.7,
            #api_key = OPENAI_API_KEY
        )
        print("\nOpenAI Full Response:", response)
        output_text = response.choices[0].message.content
        print("\nGenerated Flashcards Raw Text:", output_text)
        flashcards = []
        flashcard_pairs = output_text.split("Question: ")[1:]
        for pair in flashcard_pairs:
            parts = pair.split("Answer:",1)
            if len(parts)==2:
                question = parts[0].strip()
                answer = parts[1].strip()
                flashcards.append({"question":question, "answer":answer})
        #print("\nExtracted Flashcards:", flashcards)
        return flashcards
    except Exception as e:
        print("\nOpenAI API error", str(e))
        return [{"error": f"OpenAI API Error: {str(e)}"}]