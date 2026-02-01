# SSE Streaming Chat

SSE(Server-Sent Events)를 활용한 실시간 스트리밍 채팅.

FastAPI 서버가 OpenRouter API로부터 응답을 토큰 단위로 스트리밍 받아 브라우저에 실시간으로 전달.

## 기술 스택

- **Backend**: FastAPI, httpx
- **Frontend**: Vanilla HTML/JS (Fetch API + ReadableStream)
- **LLM**: OpenRouter API 

## 실행

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```