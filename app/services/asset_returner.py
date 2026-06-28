import os
from dotenv import load_dotenv
from app.database.db import get_engine, get_schema
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import text
import pandas as pd

class AssetsReturner:

    # variables
    MAX_ROWS = 20
    FORBIDDEN_KEYWORDS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "MERGE", "CALL", "GRANT", "REVOKE",
    }

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not configured.")
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.0)
        self.parser = StrOutputParser()
        self.schema = get_schema()
        self.engine = get_engine()
        self.prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template="""
            You are an expert PostgreSQL SQL generator for an Asset Management System.

            Your task is to convert a user's natural language question into exactly ONE valid PostgreSQL SELECT query.

            =========================
            DATABASE SCHEMA
            =========================

            {schema}

            =========================
            RULES
            =========================

            1. Generate exactly ONE valid PostgreSQL SELECT statement.

            2. Return ONLY executable SQL.
            - Do NOT explain your answer.
            - Do NOT add comments.
            - Do NOT use Markdown.
            - Do NOT wrap the SQL inside code fences.
            - Return nothing except the SQL query.

            3. Use ONLY the tables, columns, enum values, and JSON keys provided in the schema.
            - Never invent table names.
            - Never invent column names.
            - Never invent enum values.
            - Never invent JSON keys.

            4. If the user's wording differs slightly from the schema, map it to the closest valid schema element.
            This includes:
            - Singular ↔ plural words.
            - Common synonyms.
            - Minor grammatical variations.

            Examples:
            - certificates → certificate
            - certifications → certificate
            - domains → domain
            - subdomains → subdomain
            - IPs → ip_address
            - IP addresses → ip_address
            - technologies → technology

            Never map to something that does not exist in the schema.

            5. Use PostgreSQL syntax only.

            6. Table and column names must exactly match the schema.

            7. If multiple tables are needed, generate the appropriate JOIN statements.

            8. Prefer explicit column names.
            Avoid SELECT * unless the user explicitly requests all columns.

            9. Query patterns:
            - "how many" → COUNT(*)
            - "latest" → ORDER BY ... DESC LIMIT 1
            - "oldest" → ORDER BY ... ASC LIMIT 1

            10. Text filtering rules:
            - Use ILIKE only for TEXT/VARCHAR columns.
            - Use = when the value is explicit.

            11. Enum filtering rules:
            - Columns such as type, status, and source are ENUMs.
            - Never use LIKE or ILIKE on ENUM columns.
            - Always use exact equality (=).
            - Always use one of the enum values provided in the schema.

            12. JSON rules:
            - Only use JSON keys explicitly listed in the schema.
            - Use PostgreSQL JSON operators when querying JSON columns.

            13. Unless the user explicitly requests all matching rows, append:

            LIMIT 20

            to every SELECT query.

            14. Never assume values that are not present in either:
            - the user's question, or
            - the provided schema.

            =========================
            SECURITY
            =========================

            Generate ONLY read-only SQL.

            Never generate:

            INSERT
            UPDATE
            DELETE
            DROP
            ALTER
            CREATE
            TRUNCATE
            MERGE
            CALL
            GRANT
            REVOKE

            If the request requires modifying the database, return exactly:

            INVALID_REQUEST

            If the request cannot be answered using ONLY the provided schema, return exactly:

            INVALID_REQUEST

            =========================
            USER QUESTION
            =========================

            {question}

            =========================
            OUTPUT
            =========================

            Return ONLY the SQL query.

            """
        )
        self.chain = self.prompt | self.llm | self.parser

    #------------------------------------------------------------------------
    # clean sql statement from any marks extra.
    def clean_sql(self, sql: str) -> str:
        return ( sql.replace("```sql", "").replace("```", "").strip())
    
    #-------------------------------------------------------------------------------------
    # check if statenent that llm generated valid sql .
    def validate_sql(self, sql:str):
        cleaned_sql = self.clean_sql(sql)
        
        # If the user's request is unrelated to the database.
        if cleaned_sql == "INVALID_REQUEST":
            raise ValueError(
                "The question is outside the supported Asset Management scope."
            )
        # If the user's request requires modifying the database.
        sql_upper = cleaned_sql.upper().strip()
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT statements are allowed.")
    
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in sql_upper:
                raise ValueError(
                    f"Forbidden SQL operation detected: {keyword}"
                )

        return sql
    #-----------------------------------------------------------------------------------------
    # to prevent return the entire database at one time.
    def enforce_limit(self, sql: str) -> str:
        if "LIMIT" not in sql.upper():
            sql = sql.rstrip(";")
            sql += f" LIMIT {self.MAX_ROWS};"

        return sql
    

    #----------------------------------------------------------------------------------------
    def generate_sql(self, question: str) -> str:
        print(self.schema)
        sql = self.chain.invoke({ "schema": self.schema, "question": question})
        print("\n\n",sql)
        sql = self.validate_sql(sql)
        sql = self.enforce_limit(sql)

        return sql


    #--------------------------------------------------------------------------------------------
    def run_query(self, question: str):

        query = self.generate_sql(question)
        
        # print for tracking
        print("Schema :-\n",self.schema,"\n") 
        print("SQL Query :-\n",query,"\n")

        with self.engine.connect() as conn:  
            try:
                result = conn.execute(text(query))
                rows = result.fetchmany(self.MAX_ROWS)
                # return as pandas dataframe for more structure output.
                df = pd.DataFrame(rows, columns=result.keys())

                if df.empty:
                   # explain to llm that is no matching asset to prevent hallucination.
                    return {
                        "question": question,
                        "generated_sql": query,
                        "rows": [],
                        "message": "No matching assets were found."
                    }

                return {
                    "question": question,
                    "generated_sql": query,
                    "rows": df.to_dict(orient="records")
                }
                
            
            except Exception as e:
                return{
                    "generated_sql" : query,
                    "error": str(e)
                } 