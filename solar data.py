import pandas as pd
import ollama
import fitz
import re


# Step 1: Read PDF and extract text

pdf_file = "Report_First_Page_Dummy_Names.pdf"

doc = fitz.open(pdf_file)
all_text = ""
for page in doc:
    all_text += page.get_text("text") + "\n"


# Step 2: Extract fields using regex

def extract(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

data = {
    "Module Name": extract(r"Module Name\s+([^\n]+)", all_text),
    "Module Number": extract(r"Module Number\s+([^\n]+)", all_text),
    "PRN number": extract(r"PRN number\s+([^\n]+)", all_text),
    "Module Description": extract(r"Module Description\s+([\s\S]*?)\nModule", all_text),
    "Module Section": extract(r"Module Section\s+([^\n]+)", all_text),
    "Module sub-section": extract(r"Module sub-section\s+([^\n]+)", all_text),
    "Project Section": extract(r"Project Section\s+([^\n]+)", all_text),
    "Module Owner 1": extract(r"Module Owner 1\s*([^\n]*)", all_text),
    "Module Owner 2": extract(r"Module owner 2\s*([^\n]*)", all_text),
    "Module Owner 3": extract(r"Module owner 3\s*([^\n]*)", all_text),
    "Module Owner 4": extract(r"Module owner 4\s*([^\n]*)", all_text),
    "Module Owner 5": extract(r"Module owner 5\s*([^\n]*)", all_text),
    "Category": extract(r"Category\s+([^\n]+)", all_text),
    "Start date": extract(r"Start date\s+([^\n]+)", all_text),
    "Due date": extract(r"Due date\s+([^\n]+)", all_text),
}


# Step 3: Save into CSV

df = pd.DataFrame([data])
df.to_csv("main_data.csv", index=False)
print("Data extracted and saved into main_data.csv")
print(df.head())

# Step 4: Q&A loop with Mistral

while True:
    question = input("\nAsk a question about the main_data (or type 'exit' to quit): ")

    if question.lower() == "exit":
        print("Goodbye!")
        break

    data_text = df.to_json(orient="records")

    response = ollama.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions from CSV data."},
            {"role": "user", "content": f"Here is the data:\n{data_text}\n\nQuestion: {question}"}
        ]
    )

    if "message" in response:
        answer = response["message"]["content"]
    elif "messages" in response:
        answer = response["messages"][-1]["content"]
    else:
        answer = "Sorry, I couldn't parse the response."

    print("\nAnswer:", answer)
