from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .crawler.fetcher import fetch_html
from .crawler.parser import extract_content

app = FastAPI()

class URLRequest(BaseModel):
    url: str

class HTMLRequest(BaseModel):
    html: str

@app.post("/fetch")
async def fetch_html_endpoint(request: URLRequest):
    try:
        html = await fetch_html(request.url)
        return {"html": html}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract")
async def process_html_endpoint(request: HTMLRequest):
    try:
        content = extract_content(request.html)
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
