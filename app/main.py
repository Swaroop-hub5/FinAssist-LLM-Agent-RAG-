from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.rag_pipeline import RAGService
from core.evaluator import EvaluatorService

app = FastAPI(title="FinAssist AI API")

# Initialize services (Singleton pattern for the demo)
rag_service = RAGService()
evaluator_service = EvaluatorService()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    context: list[str]
    evaluation: dict = None

@app.get("/")
def read_root():
    return {"status": "FinAssist API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    1. Retrieve Answer from RAG
    2. (Simulated) Evaluate the answer instantly
    """
    # 1. Get RAG Response
    try:
        rag_result = rag_service.get_answer(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Run Evaluation (In real production, this might be async/background)
    eval_result = evaluator_service.evaluate_response(
        query=request.query,
        answer=rag_result["answer"],
        context=rag_result["context"]
    )

    return {
        "answer": rag_result["answer"],
        "context": rag_result["context"],
        "evaluation": eval_result.dict()
    }