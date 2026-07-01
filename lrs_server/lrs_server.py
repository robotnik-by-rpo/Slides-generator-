from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
import base64

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Test LRS Server", version="1.0.0")

statements_store = []

def decode_basic_auth(auth_header: str):
    """Декодирует Basic Authentication заголовок для логирования"""
    try:
        if auth_header and auth_header.startswith("Basic "):
            encoded = auth_header.split(" ")[1]
            decoded = base64.b64decode(encoded).decode("utf-8")
            username, password = decoded.split(":", 1)
            return username, password
    except Exception as e:
        logger.error(f"Failed to decode auth header: {e}")
    return None, None

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Test LRS Server is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/xAPI/statements")
async def get_statements(limit: int = 100):
    return {
        "statements": statements_store[-limit:] if limit > 0 else statements_store,
        "count": len(statements_store)
    }

@app.post("/xAPI/statements")
async def post_statement(request: Request):
    try:
        headers = dict(request.headers)
        
        logger.info("=" * 80)
        logger.info("RECEIVED REQUEST")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info(f"Method: POST /xAPI/statements")
        
        logger.info("HEADERS:")
        for key, value in headers.items():
            logger.info(f"   {key}: {value}")
        
        auth_header = headers.get("authorization")
        if auth_header:
            username, password = decode_basic_auth(auth_header)
            logger.info(f"LOGIN_LRS: {username}")
            logger.info(f"PASSWORD_LRS: {password}")
        else:
            logger.info("No Authorization header found")
        
        body = await request.body()
        data = json.loads(body)
        
        logger.info("BODY:")
        logger.info(json.dumps(data, indent=2, ensure_ascii=False))
        logger.info("=" * 80)
        
        statements_store.append({
            "timestamp": datetime.now().isoformat(),
            "headers": headers,
            "data": data
        })
        
        return JSONResponse(
            status_code=200,
            content={
                "id": f"test-{len(statements_store)}",
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON"}
        )
    except Exception as e:
        logger.error(f"Error processing statement: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.options("/xAPI/statements")
async def options_statements():
    return JSONResponse(
        status_code=200,
        headers={
            "Allow": "GET, POST, OPTIONS",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    
    response = await call_next(request)
    
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)