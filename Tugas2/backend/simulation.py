import time
import threading
import random
import uuid
import json
import warnings
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Dict

import os

# Wajib Menggunakan Paho MQTT (Harus di-install)
try:
    import paho.mqtt.client as mqtt_module
except ImportError:
    raise ImportError("Library paho-mqtt tidak ditemukan. Jalankan: pip install paho-mqtt")

# ─── Konfigurasi Koneksi MQTT (Harus ada broker) ───
MQTT_HOST      = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT      = int(os.environ.get("MQTT_PORT", 1883))
MQTT_KEEPALIVE = 60

MQTT_RR_REQUEST  = "rr/request"
MQTT_RR_RESPONSE = "rr/response"
MQTT_PS_PREFIX   = "ps"

# ──────────────────────────────────────────────────────────────────────────────
#  SKENARIO DUNIA NYATA
#
#  Request-Response: Simulasi pemesanan makanan via aplikasi (seperti GoFood)
#    - "pelanggan-A" & "pelanggan-B"  →  mengirim ORDER ke  "restoran-padang"
#    - "restoran-padang" membalas konfirmasi pesanan
#
#  Publish-Subscribe: Simulasi siaran peringatan bencana BMKG
#    - "bmkg-pusat" & "sensor-lapangan"  →  mempublikasikan ke broker
#    - Broker meneruskan ke "MetroTV", "RRI-Radio", "AplikasiWarga"
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_TOPICS = ["gempa/peringatan", "cuaca/ekstrem"]

# Contoh payload realistis untuk RR (order makanan)
RR_PAYLOADS = [
    "ORDER: Nasi Padang + Rendang x2",
    "ORDER: Ayam Geprek + Es Teh x1",
    "ORDER: Soto Ayam + Nasi x3",
    "ORDER: Mie Ayam Bakso x2",
    "ORDER: Gado-Gado + Kerupuk x1",
    "ORDER: Nasi Goreng Spesial x2",
    "ORDER: Pecel Lele + Lalapan x1",
]

# Contoh payload realistis untuk PS (siaran BMKG)
PS_PAYLOADS = {
    "gempa/peringatan": [
        "M 5.8 @ 120km BaratDaya Ternate, kedalaman 10km",
        "M 6.2 @ Kalimantan Timur, kedalaman 15km — WASPADA",
        "M 4.9 @ Flores, NTT, kedalaman 33km",
        "M 7.1 @ Laut Banda, TSUNAMI POTENTIAL — SEGERA EVAKUASI",
    ],
    "cuaca/ekstrem": [
        "PERINGATAN: Hujan lebat + petir di Jabodetabek (18:00–22:00 WIB)",
        "SIAGA: Gelombang tinggi 3–4m Selat Karimata",
        "INFO: Angin kencang >60 km/jam Wilayah Sulawesi Tengah",
        "WASPADA: Banjir rob pesisir Semarang & Demak",
    ]
}

# =============================================================================
#  HELPER & DATA CLASSES
# =============================================================================

def _make_mqtt_client(client_id: str = "") -> "mqtt_module.Client":
    """Membuat client kompatibel dengan paho-mqtt v1 & v2."""
    try:
        return mqtt_module.Client(
            callback_api_version=mqtt_module.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )
    except AttributeError:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return mqtt_module.Client(client_id=client_id, clean_session=True)

class MessageType(Enum):
    REQUEST   = "REQUEST"
    RESPONSE  = "RESPONSE"
    PUBLISH   = "PUBLISH"
    BROADCAST = "BROADCAST"

@dataclass
class Message:
    msg_id:      str          = field(default_factory=lambda: str(uuid.uuid4())[:8])
    msg_type:    MessageType  = MessageType.REQUEST
    sender_id:   str          = ""
    receiver_id: str          = ""
    topic:       str          = ""
    payload:     str          = ""
    timestamp:   float        = field(default_factory=time.time)
    latency_ms:  float        = 0.0

@dataclass
class MetricsRecord:
    timestamp:  float
    model:      str
    event:      str
    msg_id:     str
    latency_ms: float

# =============================================================================
#  MQTT NODE CLASSES (Murni Jaringan Paho MQTT)
# =============================================================================

class RRServer:
    """
    Skenario: Server Restoran Padang yang menerima & mengkonfirmasi pesanan.
    """
    def __init__(self, node_id: str = "restoran-padang"):
        self.node_id = node_id
        self._client = None
        self.on_request_done: Optional[Callable] = None

    def start(self):
        threading.Thread(target=self._serve, daemon=True).start()

    def stop(self):
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception: pass

    def _serve(self):
        self._client = _make_mqtt_client("mqtt-rr-server")
        
        def on_connect(c, u, f, r, *a): c.subscribe(MQTT_RR_REQUEST)
        
        def on_message(client, ud, mqtt_msg):
            try: data = json.loads(mqtt_msg.payload.decode())
            except: return
            
            req = Message(
                msg_id=data.get("msg_id", ""), msg_type=MessageType.REQUEST,
                sender_id=data.get("sender_id", ""), receiver_id=self.node_id, payload=data.get("payload", "")
            )
            time.sleep(0.04) # delay proses dapur
            # Balas dengan konfirmasi pesanan
            order_summary = req.payload.replace("ORDER: ", "")
            resp = Message(
                msg_type=MessageType.RESPONSE, sender_id=self.node_id, 
                receiver_id=req.sender_id,
                payload=f" DIKONFIRMASI: {order_summary} | ETA: {random.randint(15,30)} menit"
            )
            
            client.publish(f"{MQTT_RR_RESPONSE}/{req.sender_id}", json.dumps({
                "corr_id": data.get("corr_id", ""), "msg_id": resp.msg_id, "payload": resp.payload,
            }))
            if self.on_request_done: self.on_request_done(req, resp)

        self._client.on_connect, self._client.on_message = on_connect, on_message
        try:
            self._client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
            self._client.loop_forever()
        except Exception: pass

class RRClient:
    """
    Skenario: Pelanggan yang memesan makanan lewat aplikasi.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._client = None
        self._pending, self._lock = {}, threading.Lock()
        self._connected = threading.Event()

    def connect(self):
        self._client = _make_mqtt_client(f"rr-client-{self.node_id}-{uuid.uuid4().hex[:4]}")
        def on_connect(c, u, f, r, *a):
            c.subscribe(f"{MQTT_RR_RESPONSE}/{self.node_id}")
            self._connected.set()

        def on_message(c, u, msg):
            try:
                data = json.loads(msg.payload.decode())
                corr = data.get("corr_id", "")
                with self._lock:
                    if corr in self._pending:
                        self._pending[corr][0].append(data)
                        self._pending[corr][1].set()
            except: pass

        self._client.on_connect, self._client.on_message = on_connect, on_message
        self._client.connect_async(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        self._client.loop_start()
        self._connected.wait(5.0)

    def disconnect(self):
        if self._client:
            self._client.loop_stop(); self._client.disconnect()

    def send_request(self, payload: str, delay_ms: float) -> Message:
        corr_id, resp_list, evt = str(uuid.uuid4()), [], threading.Event()
        with self._lock: self._pending[corr_id] = (resp_list, evt)
        
        req = Message(msg_type=MessageType.REQUEST, sender_id=self.node_id, receiver_id="restoran-padang", payload=payload)
        sent_at = time.time()
        time.sleep(delay_ms / 2000.0) # net delay simul
        
        self._client.publish(MQTT_RR_REQUEST, json.dumps({
            "msg_id": req.msg_id, "corr_id": corr_id, "sender_id": self.node_id, "payload": payload,
        }))
        evt.wait(10.0)
        with self._lock: self._pending.pop(corr_id, None)
        
        return Message(
            msg_type=MessageType.RESPONSE, sender_id="restoran-padang", receiver_id=self.node_id,
            payload=resp_list[0].get("payload", "TIMEOUT") if resp_list else "TIMEOUT",
            latency_ms=(time.time() - sent_at) * 1000
        )

class Publisher:
    """
    Skenario: BMKG / Sensor lapangan yang mempublikasikan data bencana.
    """
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._client = None

    def connect(self):
        self._client = _make_mqtt_client(f"pub-{self.node_id}-{uuid.uuid4().hex[:4]}")
        self._client.connect_async(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
        self._client.loop_start()

    def disconnect(self):
        if self._client:
            self._client.loop_stop(); self._client.disconnect()

    def publish(self, topic: str, payload: str, msg_id: str):
        self._client.publish(f"{MQTT_PS_PREFIX}/{topic}", json.dumps({
            "msg_id": msg_id, "topic": topic, "payload": payload, "sender_id": self.node_id,
        }))

class Subscriber:
    """
    Skenario: Media & aplikasi publik yang berlangganan siaran BMKG.
    """
    def __init__(self, node_id: str, topics: List[str]):
        self.node_id, self.topics = node_id, topics
        self._client = None
        self.on_message: Optional[Callable] = None

    def start(self):
        threading.Thread(target=self._consume, daemon=True).start()

    def stop(self):
        if self._client:
            self._client.loop_stop(); self._client.disconnect()

    def _consume(self):
        self._client = _make_mqtt_client(f"sub-{self.node_id}-{uuid.uuid4().hex[:4]}")
        def on_connect(c, u, f, r, *a):
            for t in self.topics: c.subscribe(f"{MQTT_PS_PREFIX}/{t}")
        
        def on_message(c, u, msg):
            try: data = json.loads(msg.payload.decode())
            except: return
            m = Message(
                msg_id=data.get("msg_id", ""), msg_type=MessageType.BROADCAST,
                sender_id="broker-mqtt",
                receiver_id=self.node_id,
                topic=data.get("topic", ""), payload=data.get("payload", "")
            )
            if self.on_message: self.on_message(m)

        self._client.on_connect, self._client.on_message = on_connect, on_message
        try:
            self._client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE)
            self._client.loop_forever()
        except Exception: pass

# =============================================================================
#  SIMULATION MANAGER
# =============================================================================

class SimulationManager:
    def __init__(self):
        # Nodes — RR: Aplikasi Pesan Makanan
        self.rr_server = RRServer("restoran-padang")
        self.rr_clients = [RRClient("pelanggan-A"), RRClient("pelanggan-B")]
        
        # Nodes — PS: Siaran Peringatan Bencana BMKG
        self.ps_publishers = [Publisher("bmkg-pusat"), Publisher("sensor-lapangan")]
        self.ps_subscribers = [
            Subscriber("MetroTV", DEFAULT_TOPICS),
            Subscriber("RRI-Radio", DEFAULT_TOPICS),
            Subscriber("AplikasiWarga", DEFAULT_TOPICS),
        ]
        
        # State
        self.broker_connected = False
        self.broker_mode = "Menginisialisasi MQTT Broker..."
        self.metrics: List[MetricsRecord] = []
        self._metrics_lock = threading.Lock()
        
        # Callbacks
        self.on_metric_update = None
        self.on_animation = None
        self.on_broker_status_change = None

        threading.Thread(target=self._init_mqtt, name="MQTTInit", daemon=True).start()

    def _init_mqtt(self):
        time.sleep(0.5)
        tester = _make_mqtt_client("tester")
        try:
            tester.connect(MQTT_HOST, MQTT_PORT, 5)
            tester.disconnect()
            
            self.rr_server.on_request_done = lambda req, resp: self._log("RR", "request+response", resp)
            self.rr_server.start()
            for c in self.rr_clients: c.connect()
            for p in self.ps_publishers: p.connect()
            
            for s in self.ps_subscribers:
                s.on_message = lambda msg, sn=s: self._handle_broadcast(msg, sn)
                s.start()
                
            self.broker_connected = True
            self.broker_mode = f"Terhubung ke MQTT Broker ({MQTT_HOST}:{MQTT_PORT})"
            if self.on_broker_status_change:
                self.on_broker_status_change(True, self.broker_mode)
        except Exception as e:
            self.broker_connected = False
            self.broker_mode = "Mosquitto Offline. Jalankan Docker Compose."
            if self.on_broker_status_change:
                self.on_broker_status_change(False, self.broker_mode)

    def _handle_broadcast(self, msg: Message, subscriber: Subscriber):
        if self.on_animation:
            self.on_animation("broadcast", type('o', (), {'node_id': 'broker-mqtt'})(), type('o', (), {'node_id': subscriber.node_id})(), msg, "ps")
        if subscriber.node_id == "MetroTV":
            self._log("PS", "broadcast", msg)

    def trigger_rr(self, client_idx: int, payload: str, delay_ms: float):
        if not self.broker_connected: return
        client = self.rr_clients[client_idx % len(self.rr_clients)]
        def _run():
            # Gunakan payload realistis
            if not payload or payload.startswith("GET /data") or payload.startswith("stress-"):
                real_payload = random.choice(RR_PAYLOADS)
            else:
                real_payload = payload
            req = Message(msg_type=MessageType.REQUEST, sender_id=client.node_id, receiver_id="restoran-padang", payload=real_payload)
            if self.on_animation:
                self.on_animation("req_send", type('o', (), {'node_id': client.node_id})(), type('o', (), {'node_id': 'restoran-padang'})(), req, "rr")
            resp = client.send_request(real_payload, delay_ms)
            if self.on_animation:
                self.on_animation("res_recv", type('o', (), {'node_id': 'restoran-padang'})(), type('o', (), {'node_id': client.node_id})(), resp, "rr")
            self._log("RR", "request+response", resp)
        threading.Thread(target=_run, daemon=True).start()

    def trigger_ps(self, publisher_idx: int, topic: str, payload: str, delay_ms: float):
        if not self.broker_connected: return
        pub = self.ps_publishers[publisher_idx % len(self.ps_publishers)]
        def _run():
            # Gunakan payload realistis sesuai topik
            if not payload or payload.startswith("event:") or payload.startswith("stress-"):
                real_topic = topic if topic in PS_PAYLOADS else random.choice(DEFAULT_TOPICS)
                real_payload = random.choice(PS_PAYLOADS.get(real_topic, PS_PAYLOADS["gempa/peringatan"]))
            else:
                real_topic = topic
                real_payload = payload
            msg = Message(msg_type=MessageType.PUBLISH, sender_id=pub.node_id, receiver_id="broker-mqtt", topic=real_topic, payload=real_payload)
            if self.on_animation:
                self.on_animation("pub_send", type('o', (), {'node_id': pub.node_id})(), type('o', (), {'node_id': 'broker-mqtt'})(), msg, "ps")
            time.sleep(delay_ms / 2000.0)
            pub.publish(real_topic, real_payload, msg.msg_id)
        threading.Thread(target=_run, daemon=True).start()

    def run_stress_test(self, model: str, count: int, delay_ms: float):
        if not self.broker_connected: return
        def _stress():
            for i in range(count):
                if model == "rr":
                    self.trigger_rr(i % 2, random.choice(RR_PAYLOADS), delay_ms)
                else:
                    topic = random.choice(DEFAULT_TOPICS)
                    self.trigger_ps(i % 2, topic, random.choice(PS_PAYLOADS[topic]), delay_ms)
                time.sleep(max(0.2, delay_ms / 2000.0))
        threading.Thread(target=_stress, daemon=True).start()

    def _log(self, model: str, event: str, msg: Message):
        record = MetricsRecord(time.time(), model, event, msg.msg_id, msg.latency_ms)
        with self._metrics_lock:
            self.metrics.append(record)
        if self.on_metric_update: self.on_metric_update(record)

    def get_summary(self) -> dict:
        with self._metrics_lock:
            def calc(model_name):
                recs = [m for m in self.metrics if m.model == model_name]
                if not recs: return {"count": 0, "total_msgs": 0, "avg_lat": 0.0, "throughput": 0.0}
                lats = [m.latency_ms for m in recs]
                avg_l = sum(lats)/len(lats)
                t_min = min(m.timestamp for m in recs)
                t_max = max(m.timestamp for m in recs)
                dur = max(t_max - t_min, 0.001)
                msgs = len(recs) * (4 if model_name == "PS" else 2)
                return {"count": len(recs), "total_msgs": msgs, "avg_lat": avg_l, "throughput": msgs/dur}
            return {"rr": calc("RR"), "ps": calc("PS")}

    # Alias untuk kompatibilitas
    def get_metrics_summary(self) -> dict:
        return self.get_summary()

    def reconnect(self):
        if self.broker_connected: return
        self.shutdown()
        self.__init__()

    def reset(self):
        with self._metrics_lock: self.metrics.clear()
        if self.on_metric_update:
            dummy = MetricsRecord(time.time(), "SYS", "reset", "---", 0.0)
            self.on_metric_update(dummy)

    def shutdown(self):
        self.rr_server.stop()
        for c in self.rr_clients: c.disconnect()
        for p in self.ps_publishers: p.disconnect()
        for s in self.ps_subscribers: s.stop()
