import os
from dotenv import load_dotenv
from app.database.db import get_engine, get_schema
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import text
import pandas as pd

class sqlGenerator:
    
    def __init__(self):
        load_dotenv()
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=self.GOOGLE_API_KEY, temperature=0.0)
        self.parser = StrOutputParser()
        self.schema = get_schema()
        self.engine = get_engine()
        self.prompt = PromptTemplate(
            input_variables=["schema", "question"],
            template="""
            You are an expert PostgreSQL SQL generator for an Asset Management System.

            Your job is to convert the user's natural language question into ONE valid PostgreSQL SELECT query.

            ========================
            DATABASE SCHEMA
            ========================
            {schema}

            ========================
            RULES
            ========================

            1. Generate exactly ONE PostgreSQL SELECT statement.

            2. Return ONLY executable SQL.
            - Do NOT explain your answer.
            - Do NOT add comments.
            - Do NOT use Markdown.
            - Do NOT wrap the SQL inside ```sql.
            - Do NOT return anything except the SQL query.

            3. Use ONLY the tables and columns provided in the schema.
            - Never invent table names.
            - Never invent column names.
            - Never rename columns.
            - Never rename tables.
            - Never pluralize or singularize names.
            - If the user's wording differs from the schema, map it to the closest valid column or table.

            4. Use PostgreSQL syntax only.

            5. Table names and column names MUST match the schema exactly.
            - If an identifier is mixed case, surround it with double quotes.
            - Otherwise use the identifier exactly as it appears.

            6. If multiple tables are required, generate the appropriate JOINs.

            7. Use explicit column names whenever possible.
            Avoid SELECT * unless the user explicitly requests all information.

            8. If the question asks:
            - "how many" → use COUNT().
            - "latest" → ORDER BY ... DESC LIMIT 1.
            - "oldest" → ORDER BY ... ASC LIMIT 1.

            9. When filtering text values:
            - Prefer ILIKE for partial text searches.
            - Use = only when the value is explicit.

            10. If querying JSON columns (tags or metadata_json), use PostgreSQL JSON operators.

            11. Never assume values that do not appear in the user's question.
                The example values in the schema are examples only.

            ========================
            SECURITY RULES
            ========================

            Generate ONLY read-only SQL.

            Never generate:

            - INSERT
            - UPDATE
            - DELETE
            - DROP
            - ALTER
            - CREATE
            - TRUNCATE
            - MERGE
            - CALL
            - GRANT
            - REVOKE

            If the user's request requires modifying the database, return exactly:

            INVALID_REQUEST

            If the user's request is unrelated to the database, return exactly:

            INVALID_REQUEST

            ========================
            USER QUESTION
            ========================

            {question}

            ========================
            OUTPUT
            ========================

            Return ONLY the SQL query.

            """
        )
        self.chain = self.prompt | self.llm | self.parser


    @staticmethod
    def clean_sql(sql: str) -> str:
        return ( sql.replace("```sql", "").replace("```", "").strip())
    
    
    def generate_sql(self, question: str) -> str:
        sql = self.chain.invoke({
            "schema": self.schema,
            "question": question
        })
        return self.clean_sql(sql)



    def run_query(self, question: str):
        query = self.generate_sql(question)

        print("Schema :-\n",self.schema,"\n") 
        print("SQL Query :-\n",query,"\n")

        with self.engine.connect() as conn:  
            try:
                result = conn.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
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