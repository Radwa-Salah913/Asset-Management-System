import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from app.utils.rule_engine import*
from app.schemas.enrichment_output import EnrichmentOutput
from app.schemas.enrich_asset import EnrichAsset

class Enrichment:
    def __init__(self):
        load_dotenv()
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 0.0, google_api_key = self.GOOGLE_API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=EnrichmentOutput)
        self.prompt = PromptTemplate(
            input_variables=["asset", "classification"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template="""
            You are a senior cybersecurity asset analyst.

            Your task is NOT to reclassify everything.

            Some fields are already classified by deterministic rules.

            Only complete fields whose value is Unknown.

            Never modify fields that already have a value.

            Use the following guidance.

            Environment:

            Production
            Development
            Staging
            Testing
            Unknown

            Category:

            Website
            API
            Database
            Certificate
            Mail Server
            VPN
            DNS
            Cloud Resource
            IP Address
            Unknown
            
            Criticality:

            Critical:
            - Payment systems
            - Identity providers
            - Authentication
            - Admin portals

            High:
            - Public APIs
            - VPN
            - Production databases

            Medium:
            - Internal APIs
            - Monitoring
            - Internal services

            Low:
            - Blogs
            - Documentation
            - Development assets
                     
            --------------------------------------
            Generate:

            tags

            description

            Return ONLY valid JSON.
            {format_instructions}
      
            -----------------------------------------
            Original Asset:

            {asset}
            -----------------------------------------
            Current Classification:

            {classification}

            Complete only Unknown fields.
            """
        )
        self.chain = self.prompt | self.llm | self.parser


    def run_rule_engine(self, asset: EnrichAsset):

        value = asset.value

        return {
        "environment": detect_environment(value),
        "category": detect_category(value),
        "criticality": detect_criticality(value)
        }
    

    def enrich_asset(self, asset):

        rule_result = self.run_rule_engine(asset)
        print("Rule Results:\n", rule_result)
        classification = f"""
            Environment: {rule_result["environment"]["value"]}
            Category: {rule_result["category"]["value"]}
            Criticality: {rule_result["criticality"]["value"]}
            """
        llm_result = self.chain.invoke({"asset":asset, "classification": classification})
        print("LLM Results:\n", llm_result)

        final = {
         "environment":
             rule_result["environment"]["value"] if rule_result["environment"]["value"] != "Unknown" else llm_result.environment,
        "category":
            rule_result["category"]["value"] if rule_result["category"]["value"] != "Unknown" else llm_result.category,
        "criticality":
            rule_result["criticality"]["value"] if rule_result["criticality"]["value"] != "Unknown" else llm_result.criticality,
        "tags": llm_result.tags,
        "description": llm_result.description
        }
        
        asset_dict = asset.model_dump()
        asset_dict.update(final)
        return asset_dict
