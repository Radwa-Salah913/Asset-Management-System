import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import json
from app.schemas.risk_asset import AssetRisk
class RiskScoring:
    
    def __init__(self):
        load_dotenv()
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 0.0, google_api_key = self.GOOGLE_API_KEY)
        self.parser = JsonOutputParser()
        self.prompt = PromptTemplate(
            input_variables=["asset_json"],
            partial_variables={ "format_instructions": self.parser.get_format_instructions() },
            template=""" 
                You are a cybersecurity risk scoring engine.

                STRICT RULES:
                - You MUST follow the scoring criteria exactly as defined.
                - Do NOT invent new risk factors.
                - Do NOT change weights.
                - Do NOT use external knowledge.
                - Only use the provided asset data.

                ----------------------------------
                SCORING CRITERIA:

                1) Base score by type:
                - service: 40
                - ip_address: 30
                - domain/subdomain: 20
                - certificate: 25
                - technology: 35

                2) Status:
                - active: +20
                - stale: +10
                - archived: +0

                3) Tags:
                - internet_exposed: +30
                - critical: +25
                - internal: +5

                4) Metadata rules:

                Certificates:
                - expired: +50
                - expiring in < 7 days: +30

                Services:
                - SSH (port 22): +20
                - RDP (port 3389): +30
                - Database ports (3306, 5432): +40

                Technologies:
                - outdated version: +25
                - end-of-life: +50

                5) Recency:
                - last_seen > 30 days: +10
                - last_seen > 90 days: +20

                ----------------------------------

                TASK:

                1) Calculate the total risk score.
                2) Cap the score at 100.
                3) Assign risk level:
                - 0–20: Low
                - 21–50: Medium
                - 51–80: High
                - 81–100: Critical

                4) Return output in JSON format ONLY:
                {{
                "risk_score": number,
                "risk_level": "...",
                "reasons": [list of applied rules],
                "summary": "concise explanation"
                }}

                ----------------------------------

                INPUT:
                {asset_json}
                """)
        
        self.chain = self.prompt | self.llm | self.parser


    def _validate_output(self, result: dict) -> dict: 
     
        if not isinstance(result, dict): 
            raise ValueError("Invalid output format") 
        
        score = result.get("risk_score") 
        level = result.get("risk_level") 

        if not isinstance(score, (int, float)): 
            raise ValueError("Invalid risk_score") 
        
        if not (0 <= score <= 100): 
            raise ValueError("risk_score out of bounds") 
        
        valid_levels = ["Low", "Medium", "High", "Critical"] 
        if level not in valid_levels: 
            raise ValueError("Invalid risk_level") 
        
        return result 
    
    def cal_risk(self, asset: AssetRisk) -> dict: 
        
        try:
            result = self.chain.invoke({ "asset_json": json.dumps(asset.model_dump(mode="json"), indent=2) })
            print(result)
            validated = self._validate_output(result) 
            return validated 
        
        except Exception as e: 
            return { "error": str(e), 
                    "input_asset": asset }



