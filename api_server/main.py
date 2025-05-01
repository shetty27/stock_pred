from fastapi import FastAPI, WebSocket
import asyncio
import json
from firebase_handler import get_realtime_db
from datetime import datetime

app = FastAPI()

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

async def fetch_ltp_for_all():
    from fetcher.stock_data_manager import load_stock_symbols, get_ltp
    symbols = load_stock_symbols()
    ltp_data = {}
    for category, symbol, key in symbols:
        ltp = get_ltp(symbol, key)
        ltp_data[symbol] = ltp
    return ltp_data

async def ticker_broadcaster():
    while True:
        data = await fetch_ltp_for_all()
        await manager.broadcast(json.dumps(data))
        await asyncio.sleep(3)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(ticker_broadcaster())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        pass
    finally:
        manager.disconnect(websocket)

@app.get("/prediction/{category}/{symbol}")
async def get_prediction(category: str, symbol: str):
    today = datetime.now().strftime("%Y-%m-%d")
    db_root = get_realtime_db()
    path = f"predictions/7days/{category}/{symbol}/{today}"
    result = db_root.child(path).get()
    if result:
        return {"symbol": symbol, "prediction": result}
    else:
        return {"error": "No prediction found"}
