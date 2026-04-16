import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from backend.simulation import SimulationManager, Message, MetricsRecord

app = FastAPI(title="Distributed System Simulation API")

# Setup folder statis untuk frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Inisialisasi Simulation Manager
sim = SimulationManager()

# Simpan semua koneksi websocket yang aktif
connected_clients = set()
loop = None

@app.on_event("startup")
async def startup_event():
    global loop
    loop = asyncio.get_running_loop()
    
    # ── Hook callbacks ke WebSocket ──
    def on_metric_update(record: MetricsRecord):
        """Dipanggil dari thread lain oleh SimulationManager"""
        data = {
            "type": "metric_update",
            "summary": sim.get_summary(),
            "log": f"[{record.model}] Latency: {record.latency_ms:.1f}ms | ID: {record.msg_id}"
        }
        _broadcast_from_sync(data)

    def on_animation(event_type, src, dst, msg: Message, model: str):
        data = {
            "type": "animation",
            "event_type": event_type,
            "src": src.node_id,
            "dst": dst.node_id,
            "msg": msg.payload,
            "topic": msg.topic,
            "model": model
        }
        log_msg = f"[{model.upper()}] {src.node_id} → {dst.node_id} | {msg.payload[:60]}"
        _broadcast_from_sync({**data, "log": log_msg})

    def on_broker_status_change(is_connected: bool, status_msg: str):
        data = {
            "type": "broker_status",
            "is_connected": is_connected,
            "message": status_msg
        }
        _broadcast_from_sync(data)

    sim.on_metric_update = on_metric_update
    sim.on_animation = on_animation
    sim.on_broker_status_change = on_broker_status_change


def _broadcast_from_sync(data: dict):
    """Fungsi pembantu untuk mem-broadcast pesan dari thread sinkron ke thread asyncio"""
    if loop and connected_clients:
        asyncio.run_coroutine_threadsafe(_broadcast_async(data), loop)

async def _broadcast_async(data: dict):
    if not connected_clients:
        return
    text_data = json.dumps(data, ensure_ascii=False)
    disconnected = set()
    for client in connected_clients:
        try:
            await client.send_text(text_data)
        except Exception:
            disconnected.add(client)
    for c in disconnected:
        connected_clients.discard(c)


@app.get("/")
async def get_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("Frontend tidak ditemukan.", status_code=404)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    
    # Kirim state awal
    await websocket.send_json({
        "type": "broker_status",
        "is_connected": sim.broker_connected,
        "message": sim.broker_mode
    })
    await websocket.send_json({
        "type": "metric_update",
        "summary": sim.get_summary()
    })

    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            action = payload.get("action")
            
            if action == "trigger_rr":
                client_idx = int(payload.get("client_idx", 0))
                msg_payload = payload.get("payload", "")
                delay_ms = float(payload.get("delay", 300))
                sim.trigger_rr(client_idx, msg_payload, delay_ms)
                
            elif action == "trigger_ps":
                pub_idx = int(payload.get("pub_idx", 0))
                topic = payload.get("topic", "gempa/peringatan")
                msg_payload = payload.get("payload", "")
                delay_ms = float(payload.get("delay", 300))
                sim.trigger_ps(pub_idx, topic, msg_payload, delay_ms)
                
            elif action == "stress_test":
                model = payload.get("model", "rr")
                count = int(payload.get("count", 5))
                delay_ms = float(payload.get("delay", 300))
                sim.run_stress_test(model, count, delay_ms)
                
            elif action == "reset":
                sim.reset()
                await _broadcast_async({"type": "metric_update", "summary": sim.get_summary()})
                
            elif action == "reconnect":
                sim.reconnect()
                
    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    except Exception as e:
        connected_clients.discard(websocket)
