import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

language = input("Enter the language you want to translate the subtitles to: ")

def generateResponse(subLines):
    # Prompt enhanced via ChatGPT
    response = model.generate_content(
        f"""
    You are tasked with translating movie subtitle dialogue into the target language: {language}. 
    Please follow these instructions very carefully. It is extremely important that you do exactly what is described here, and do not add anything else.

    1. Translate the subtitle dialogue using natural-sounding language appropriate for movies. Do not use overly literal or generic phrasing. 
    The goal is to produce translations that feel like they were originally written for a movie in the target language, 
    with idiomatic, fluent, and emotionally appropriate expressions.

    2. Do NOT add any explanations, notes, or extra commentary of any kind. 
    Just give the translated subtitles only. Nothing else should appear in the output.

    3. Do NOT add any labels like "Sentence 1", "Translation:", "Line:", or numbers. Only the translated lines should appear.

    4. Each translated subtitle line should appear on a new line, with a single newline character separating each one. 
    There should be no extra blank lines, no paragraph breaks, and no formatting. Just one translated sentence per line.

    Here are the subtitle lines to be translated:
    {subLines}
    """
    )

    return response

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


with open("subtitle.srt", "r", encoding="utf-8") as file:
    subtitles = file.read() + "\n"
    
subtitlesList = subtitles.split("\n")

counter = 1
subLines = ""
subIndices = []
for i in range(len(subtitlesList)):
    print("Progress: " + str(round((i + 1)*100/(len(subtitlesList)), 2)) + "%")

    if (counter <= 5) and (i + 1 < len(subtitlesList)):
        
    
        if ("-->" in subtitlesList[i]) or ("-->" in subtitlesList[i+1]) or (subtitlesList[i] == ''):
            continue
        else:
            subLines += "Sentence " + str(counter) + ": " + subtitlesList[i] + "\n"
            subIndices.append(i)
            counter+=1
    else:
        model = genai.GenerativeModel('gemma-3-27b-it')
        
        response = "temp"

        while response == "temp":
            try:
                response = generateResponse(subLines)
            except Exception:
                print("API Rate-limit reached. Retrying in 15 seconds...")
                time.sleep(15)
        
        responseLines = response.text.split("\n")

        for j in range(len(subIndices)):
            currentIndex = subIndices[j]
            subtitlesList[currentIndex] = responseLines[j]
        counter = 1
        subIndices.clear()
        
subTranslated = "\n".join(subtitlesList)

with open(language + "_translated_subtitle.srt", "w", encoding="utf-8") as file:
    file.write(subTranslated)

