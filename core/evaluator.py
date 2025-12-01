from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate  # <--- UPDATED IMPORT
from langchain_core.output_parsers import PydanticOutputParser # <--- UPDATED IMPORT
from pydantic import BaseModel, Field
from core.config import settings

class EvaluationMetrics(BaseModel):
    faithfulness_score: float = Field(description="Score 0.0-1.0: Is answer derived from context?")
    relevance_score: float = Field(description="Score 0.0-1.0: Does answer address the query?")
    reasoning: str = Field(description="Brief explanation of the scores")

class EvaluatorService:
    def __init__(self):
        # Use Gemini Flash for the Judge as well (Free tier compatible)
        self.eval_llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=EvaluationMetrics)

    def evaluate_response(self, query: str, answer: str, context: list[str]):
        eval_template = """
        You are an expert Quality Assurance Auditor.
        
        Evaluate this interaction:
        USER QUERY: {query}
        CONTEXT: {context}
        AI ANSWER: {answer}
        
        Metrics to calculate:
        1. Faithfulness: (0.0 to 1.0) - Is the answer based ONLY on the Context?
        2. Relevance: (0.0 to 1.0) - Does it answer the user's question?
        
        {format_instructions}
        """
        
        prompt = PromptTemplate(
            template=eval_template,
            input_variables=["query", "context", "answer"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        chain = prompt | self.eval_llm | self.parser
        
        context_str = "\n".join(context)
        
        try:
            results = chain.invoke({"query": query, "context": context_str, "answer": answer})
            return results
        except Exception as e:
            return EvaluationMetrics(
                faithfulness_score=0.0, 
                relevance_score=0.0, 
                reasoning=f"Evaluation Failed: {str(e)}"
            )