# Product review summarizer

A small HTML/JavaScript frontend served by FastAPI. The frontend sends reviews to the backend; any LLM API key belongs in the backend environment and must never be added to browser code. The backend currently uses a fixed mock response, so no API key is required, but the sample response does not analyze the submitted review text.

## Run the FastAPI backend

Python and the dependencies in `requirements.txt` are required to run the backend.

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000> (do not open `index.html` directly). The API is available at `POST /api/summarize` with a JSON body such as:

```json
{"reviews": ["Great picture quality.", "The battery drains too quickly."]}
```

The response includes `sentiment`, `summary`, and `complaints`. Missing or blank reviews return HTTP 400; malformed or unexpected LLM output returns HTTP 502 with an error message.
