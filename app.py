import json
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, ValidationError


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    mixed = "mixed"


class SummarizeRequest(BaseModel):
    reviews: list[str] | None = None


class SummaryResponse(BaseModel):
    sentiment: Sentiment
    summary: str
    complaints: list[str]


app = FastAPI(title="Product Review Summarizer")
INDEX_PATH = Path(__file__).parent / "index.html"


async def call_llm(prompt: str) -> str:
    """Mock LLM call; replace with a provider SDK when an API key is available."""
    return (
        '{"sentiment":"mixed",'
        '"summary":"Customers like the camera but complain about battery life.",'
        '"complaints":["battery drains fast","heats up"]}'
    )


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(INDEX_PATH)


@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_reviews(request: Request) -> SummaryResponse:
    try:
        payload = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise HTTPException(
            status_code=400,
            detail="Request body must be valid JSON with a non-empty reviews list.",
        ) from error

    try:
        parsed_request = SummarizeRequest.model_validate(payload)
    except ValidationError as error:
        raise HTTPException(
            status_code=400,
            detail="Request body must contain reviews as a list of strings.",
        ) from error

    reviews = [review.strip() for review in (parsed_request.reviews or []) if review.strip()]
    if not reviews:
        raise HTTPException(status_code=400, detail="Provide at least one non-empty review.")

    prompt = (
        "Analyze these customer reviews. Return JSON with sentiment (positive, negative, "
        "or mixed), a 2-3 sentence summary, and a list of top complaints.\n\n"
        + "\n".join(f"- {review}" for review in reviews)
    )
    llm_text = await call_llm(prompt)
    try:
        result = json.loads(llm_text)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=502,
            detail="The LLM returned invalid JSON. Please try again.",
        ) from error

    try:
        return SummaryResponse.model_validate(result)
    except ValidationError as error:
        raise HTTPException(
            status_code=502,
            detail="The LLM response was JSON but did not match the expected summary format.",
        ) from error
