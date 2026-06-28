import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ReportGenerator:

    def __init__(self):

        load_dotenv()

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0,google_api_key=os.getenv("GOOGLE_API_KEY"))
        self.parser = StrOutputParser()
        self.prompt = PromptTemplate(
            input_variables=["question","assets", "risk_results"],
            template="""
            You are a senior cybersecurity reporting assistant.

            The user requested:

            {question}

            Below are the matching assets 

            {assets}

            and their risk assessments.

            {risk_results}

            Generate a professional report.

            The report must contain:

            1. Executive Summary

            2. Inventory Summary

            3. Key Risk Findings

            4. Recommendations

            Rules:

            - Do NOT invent information.
            - Base the report ONLY on the provided assets.
            - Use Markdown.
            - Keep the report concise.
            """
            )

        self.chain = self.prompt | self.llm | self.parser


    def generate(self, question, assets, risk_results):

        return self.chain.invoke({
            "question": question,
            "assets" : assets,
            "risk_results": risk_results
        })