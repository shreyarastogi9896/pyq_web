import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")
        self.parser = JsonOutputParser()
    def extract_metadata(self,page_text):
        prompt = PromptTemplate.from_template("""
        Extract metadata from the following question paper page.

        Return this exact JSON format:
        {{
        "subject": "...",
        "course_code": "...",
        "semester": "...",
        "year": "..."
        }}

        If any field is missing, use null.

        Text:
        \"\"\"
        {page_text}
        \"\"\"
        """)
        chain_extract = prompt| self.llm
        res = chain_extract.invoke(input={"page_text": page_text})
        try:
            chain_extract = prompt | self.llm
            res = chain_extract.invoke({"page_text": page_text})
            return res.content
        except OutputParserException:
            return {"error": "Failed to parse output due to large context or bad format."}
        except Exception as e:
            return {"error": str(e)}
if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))