import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

app = FastAPI()

# 클라이언트가 서버에게 보내는 JSON body 구조 정의
class ChatRequest(BaseModel):
    prompt: str

# openrouter API에서 토큰을 하나씩 받아 SSE 형식으로 변환해서 넘겨주는 파이프라인
async def stream_openrouter(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}", # api 인증
        "Content-Type": "application/json",
    }
    payload = {
        "model": "upstage/solar-pro-3:free",
        "stream": True, # stream을 true로 설정해야 토큰 단위로 쪼개서 보내줌
        "messages": [{"role": "user", "content": prompt}],
    }

    # 스트리밍 요청
    async with httpx.AsyncClient() as client:
        # 청크 단위로 비동기 수신
        async with client.stream(
            "POST", OPENROUTER_URL, json=payload, headers=headers, timeout=60.0
        ) as response:
            # 줄 단위로 파싱해주는 것
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue

                data = line[len("data: "):]

                # done 나오면 스트림 종료
                if data.strip() == "[DONE]":
                    yield "data: [DONE]\n\n"
                    return
                
                # json 파싱
                try:
                    chunk = json.loads(data)
                    content = chunk["choices"][0]["delta"].get("content", "")
                    if content:
                        yield f"data: {content}\n\n"
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue


@app.post("/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(
        stream_openrouter(req.prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/")
async def root():
    html = Path("index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
