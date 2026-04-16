import sys

with open("main.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Themes
theme_old = """# ─────────────────────────────────────────────
#  TEMA & WARNA
# ─────────────────────────────────────────────
BG_DARK        = "#0d1117"   # latar utama
BG_PANEL       = "#161b22"   # panel samping
BG_CARD        = "#1f2937"   # kartu metriks
BORDER_COLOR   = "#30363d"   # garis tepi

ACCENT_BLUE    = "#58a6ff"   # Request-Response
ACCENT_GREEN   = "#3fb950"   # Publish-Subscribe / ok
ACCENT_ORANGE  = "#e3b341"   # highlight / broker
ACCENT_PURPLE  = "#bc8cff"   # subscriber
ACCENT_RED     = "#f85149"   # error / alert

TEXT_PRIMARY   = "#e6edf3"
TEXT_SECONDARY = "#8b949e"
TEXT_DIM       = "#484f58"

NODE_RADIUS = 30
MSG_RADIUS  = 7
MSG_TTL_MS  = 1000           # berapa lama partikel pesan hidup di kanvas (ms)

FONT_TITLE  = ("Helvetica Neue", 13, "bold")
FONT_BODY   = ("Helvetica Neue", 10)
FONT_SMALL  = ("Helvetica Neue", 9)
FONT_MONO   = ("Courier", 10)
FONT_HUGE   = ("Helvetica Neue", 22, "bold")
FONT_MED    = ("Helvetica Neue", 14, "bold")"""

theme_new = """# ─────────────────────────────────────────────
#  TEMA & WARNA (MODERN LIGHT)
# ─────────────────────────────────────────────
BG_DARK        = "#F7F9FC"   # latar utama kanvas (sangat terang, biru abu-abu sedikit)
BG_PANEL       = "#FFFFFF"   # background panel list/kotak
BG_CARD        = "#FFFFFF"   # kartu/button
BORDER_COLOR   = "#E2E8F0"   # garis batas terang

ACCENT_BLUE    = "#6366F1"   # Indigo modern (Primary)
ACCENT_GREEN   = "#10B981"   # Emerald green
ACCENT_ORANGE  = "#F59E0B"   # Orange amber
ACCENT_PURPLE  = "#8B5CF6"   # Purple lembut
ACCENT_RED     = "#EF4444"   # Rose red

TEXT_PRIMARY   = "#1E293B"   # Slate dark
TEXT_SECONDARY = "#64748B"   # Slate medium
TEXT_DIM       = "#94A3B8"   # Slate light

# Palet warna terang (pastel tones) seperti di image
CARD_PASTEL_1  = "#EDFAFA"   # light cyan
CARD_PASTEL_2  = "#FEF2F2"   # light pink
CARD_PASTEL_3  = "#F3E8FF"   # light purple
CARD_PASTEL_4  = "#FFFBEA"   # light orange/yellow

NODE_RADIUS = 32
MSG_RADIUS  = 7
MSG_TTL_MS  = 1000

FONT_TITLE  = ("Segoe UI", 12, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10, "bold")
FONT_HUGE   = ("Segoe UI", 22, "bold")
FONT_MED    = ("Segoe UI", 11, "bold")"""
code = code.replace(theme_old, theme_new)

# 2. Update Metrics render (using pastel colors)
metrics_old = """        for r, (label, rr_var, ps_var) in enumerate(rows, start=1):
            tk.Label(
                tbl, text=label, font=FONT_SMALL,
                bg=BG_PANEL, fg=TEXT_SECONDARY, anchor="w", width=11,
            ).grid(row=r, column=0, sticky="w", padx=2, pady=1)

            rr_lbl = tk.Label(
                tbl, textvariable=rr_var, font=FONT_MONO,
                bg=BG_CARD, fg=ACCENT_BLUE, anchor="center", width=8,
                relief="flat",
            )
            rr_lbl.grid(row=r, column=1, sticky="ew", padx=2, pady=1)

            ps_lbl = tk.Label(
                tbl, textvariable=ps_var, font=FONT_MONO,
                bg=BG_CARD, fg=ACCENT_GREEN, anchor="center", width=8,
                relief="flat",
            )
            ps_lbl.grid(row=r, column=2, sticky="ew", padx=2, pady=1)"""

metrics_new = """        pastels = [CARD_PASTEL_1, CARD_PASTEL_4, CARD_PASTEL_3, CARD_PASTEL_2]
        for r, (label, rr_var, ps_var) in enumerate(rows, start=1):
            bg_color = pastels[(r-1) % 4]
            tk.Label(
                tbl, text=label, font=FONT_SMALL,
                bg=BG_PANEL, fg=TEXT_SECONDARY, anchor="w", width=11,
            ).grid(row=r, column=0, sticky="w", padx=2, pady=4)

            rr_lbl = tk.Label(
                tbl, textvariable=rr_var, font=FONT_MONO,
                bg=bg_color, fg=ACCENT_BLUE, anchor="center", width=8,
                relief="flat", pady=6,
            )
            rr_lbl.grid(row=r, column=1, sticky="ew", padx=2, pady=4)

            ps_lbl = tk.Label(
                tbl, textvariable=ps_var, font=FONT_MONO,
                bg=bg_color, fg=ACCENT_GREEN, anchor="center", width=8,
                relief="flat", pady=6,
            )
            ps_lbl.grid(row=r, column=2, sticky="ew", padx=2, pady=4)"""
code = code.replace(metrics_old, metrics_new)

# 3. Update Status Bar
status_old = """        # ── Broker Status Bar ──
        self._status_bar = tk.Frame(self, bg="#0c1e0c", pady=4)
        self._status_bar.pack(fill="x")
        self._broker_dot = tk.Label(
            self._status_bar, text="●",
            font=("Helvetica Neue", 10),
            bg="#0c1e0c", fg=ACCENT_ORANGE,
        )
        self._broker_dot.pack(side="left", padx=(14, 4))
        self._broker_lbl = tk.Label(
            self._status_bar,
            text="Broker: Menginisialisasi...",
            font=FONT_SMALL,
            bg="#0c1e0c", fg=TEXT_SECONDARY,
        )
        self._broker_lbl.pack(side="left")
        self._reconnect_btn = tk.Button(
            self._status_bar,
            text="↻ Reconnect",
            bg="#0c1e0c", fg=TEXT_DIM,
            font=("Helvetica Neue", 8),
            relief="flat", cursor="hand2",
            activebackground=BG_CARD, activeforeground=TEXT_PRIMARY,
            command=self._do_reconnect,
        )
        self._reconnect_btn.pack(side="right", padx=14)
        self._mq_ui_lbl = tk.Label(
            self._status_bar,
            text="",
            font=("Helvetica Neue", 8),
            bg="#0c1e0c", fg=TEXT_DIM,
        )"""

status_new = """        # ── Broker Status Bar ──
        self._status_bar = tk.Frame(self, bg=CARD_PASTEL_4, pady=6)
        self._status_bar.pack(fill="x")
        self._broker_dot = tk.Label(
            self._status_bar, text="●",
            font=("Segoe UI", 12),
            bg=CARD_PASTEL_4, fg=ACCENT_ORANGE,
        )
        self._broker_dot.pack(side="left", padx=(14, 4))
        self._broker_lbl = tk.Label(
            self._status_bar,
            text="Broker: Menginisialisasi...",
            font=FONT_SMALL,
            bg=CARD_PASTEL_4, fg=TEXT_PRIMARY,
        )
        self._broker_lbl.pack(side="left")
        self._reconnect_btn = tk.Button(
            self._status_bar,
            text="↻ Reconnect",
            bg=CARD_PASTEL_4, fg=TEXT_SECONDARY,
            font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2",
            activebackground=BG_CARD, activeforeground=ACCENT_BLUE,
            command=self._do_reconnect,
            bd=0
        )
        self._reconnect_btn.pack(side="right", padx=14)
        self._mq_ui_lbl = tk.Label(
            self._status_bar,
            text="",
            font=("Segoe UI", 9),
            bg=CARD_PASTEL_4, fg=TEXT_DIM,
        )"""
code = code.replace(status_old, status_new)

# 4. _update_status_bar function body
update_old = """    def _update_status_bar(self, connected: bool, info: str):
        if connected:
            color     = ACCENT_GREEN
            bg_color  = "#0c2010"
            dot_color = ACCENT_GREEN
            mq_text   = "  |  Web UI: http://localhost:15672  (user: guest / pass: guest)"
        else:
            color     = ACCENT_ORANGE
            bg_color  = "#1e1a0c"
            dot_color = ACCENT_ORANGE
            mq_text   = ""
            if "pika" in info.lower():
                dot_color = ACCENT_RED
                bg_color  = "#1e0c0c"

        self._status_bar.configure(bg=bg_color)
        self._broker_dot.configure(bg=bg_color, fg=dot_color)
        self._broker_lbl.configure(
            bg=bg_color, fg=color,
            text=f"Broker: {self.sim.broker_mode}  |  {info}",
        )
        self._mq_ui_lbl.configure(bg=bg_color, text=mq_text, fg=TEXT_DIM)
        self._reconnect_btn.configure(bg=bg_color)"""

update_new = """    def _update_status_bar(self, connected: bool, info: str):
        if connected:
            color     = ACCENT_GREEN
            bg_color  = CARD_PASTEL_1
            dot_color = ACCENT_GREEN
            mq_text   = "  |  Web UI: localhost:15672" if "rabbit" in info.lower() else ""
        else:
            color     = ACCENT_ORANGE
            bg_color  = CARD_PASTEL_4
            dot_color = ACCENT_ORANGE
            mq_text   = ""
            if "pika" in info.lower() or "paho" in info.lower():
                dot_color = ACCENT_RED
                color     = ACCENT_RED
                bg_color  = CARD_PASTEL_2

        self._status_bar.configure(bg=bg_color)
        self._broker_dot.configure(bg=bg_color, fg=dot_color)
        self._broker_lbl.configure(
            bg=bg_color, fg=color,
            text=f"Broker: {self.sim.broker_mode}  |  {info}",
        )
        self._mq_ui_lbl.configure(bg=bg_color, text=mq_text, fg=TEXT_DIM)
        self._reconnect_btn.configure(bg=bg_color)"""
code = code.replace(update_old, update_new)

# 5. Buttons Styling
btn_old = """self.btn_single = tk.Button(
            btn_frame,
            text="▶  Kirim 1 Pesan",
            bg=ACCENT_BLUE, fg="white",
            font=FONT_BODY, relief="flat", cursor="hand2",
            activebackground="#79b8ff", activeforeground="white",
            command=self._send_single,
        )
        self.btn_single.pack(fill="x", pady=3)

        self.btn_stress = tk.Button(
            btn_frame,
            text="⚡  Stress Test",
            bg=ACCENT_GREEN, fg="white",
            font=FONT_BODY, relief="flat", cursor="hand2",
            activebackground="#56d364", activeforeground="white",
            command=self._send_stress,
        )
        self.btn_stress.pack(fill="x", pady=3)

        self.btn_reset = tk.Button(
            btn_frame,
            text="↺  Reset Simulasi",
            bg=BG_CARD, fg=TEXT_SECONDARY,
            font=FONT_BODY, relief="flat", cursor="hand2",
            activebackground=BORDER_COLOR, activeforeground=TEXT_PRIMARY,
            command=self._reset,
        )
        self.btn_reset.pack(fill="x", pady=3)"""

btn_new = """self.btn_single = tk.Button(
            btn_frame,
            text="▶  Kirim 1 Pesan",
            bg=ACCENT_BLUE, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            activebackground="#4F46E5", activeforeground="white",
            command=self._send_single,
            pady=4, bd=0
        )
        self.btn_single.pack(fill="x", pady=4)

        self.btn_stress = tk.Button(
            btn_frame,
            text="⚡  Stress Test",
            bg=ACCENT_GREEN, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            activebackground="#059669", activeforeground="white",
            command=self._send_stress,
            pady=4, bd=0
        )
        self.btn_stress.pack(fill="x", pady=4)

        self.btn_reset = tk.Button(
            btn_frame,
            text="↺  Reset Simulasi",
            bg="#F1F5F9", fg=TEXT_SECONDARY,
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            activebackground="#E2E8F0", activeforeground=TEXT_PRIMARY,
            command=self._reset,
            pady=4, bd=0
        )
        self.btn_reset.pack(fill="x", pady=4)"""
code = code.replace(btn_old, btn_new)

# 6. Canvas Nodes Draw Map
draw_old = """    def _draw_node(self, canvas, nid, x, y, positions):
        color  = NODE_COLORS.get(nid, TEXT_DIM)
        icon   = NODE_ICONS.get(nid, "?")
        r      = NODE_RADIUS

        # Glow ring
        canvas.create_oval(
            x - r - 6, y - r - 6,
            x + r + 6, y + r + 6,
            outline=color, width=1,
            fill="", stipple="gray25",
            tags=("topology", f"node_glow_{nid}"),
        )

        # Lingkaran utama
        canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=BG_CARD, outline=color, width=2,
            tags=("topology", f"node_{nid}"),
        )

        # Icon
        canvas.create_text(
            x, y - 6,
            text=icon, font=("Helvetica Neue", 14),
            fill=color, tags=("topology", f"icon_{nid}"),
        )"""

draw_new = """    def _draw_node(self, canvas, nid, x, y, positions):
        color  = NODE_COLORS.get(nid, TEXT_DIM)
        icon   = NODE_ICONS.get(nid, "?")
        r      = NODE_RADIUS

        # Drop shadow tipis (simulasi tumpukan)
        canvas.create_oval(
            x - r + 3, y - r + 5, x + r + 4, y + r + 5,
            fill="#CBD5E1", outline="",
            tags=("topology", f"node_shadow_{nid}")
        )

        # Glow ring tipis (dash line)
        canvas.create_oval(
            x - r - 8, y - r - 8,
            x + r + 8, y + r + 8,
            outline=color, width=1,
            fill="", dash=(4, 4),
            tags=("topology", f"node_glow_{nid}"),
        )

        # Lingkaran utama
        canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=BG_CARD, outline=color, width=3,
            tags=("topology", f"node_{nid}"),
        )

        # Icon
        canvas.create_text(
            x, y - 4,
            text=icon, font=("Segoe UI", 16),
            fill=color, tags=("topology", f"icon_{nid}"),
        )"""
code = code.replace(draw_old, draw_new)

# 7. Update ttk.Scrollbar & TScale
ttk_old = """    # Konfigurasi ttk Scale style agar lebih gelap
    style = ttk.Style(app)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(
        "Horizontal.TScale",
        background=BG_PANEL,
        troughcolor=BG_CARD,
        sliderlength=16,
        sliderrelief="flat",
    )
    style.configure(
        "Vertical.TScrollbar",
        background=BG_CARD,
        troughcolor=BG_DARK,
        bordercolor=BG_DARK,
        arrowcolor=TEXT_DIM,
    )"""

ttk_new = """    # Konfigurasi ttk Scale style
    style = ttk.Style(app)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(
        "Horizontal.TScale",
        background=BG_PANEL,
        troughcolor="#E2E8F0",
        sliderlength=18,
        sliderrelief="flat",
    )
    style.configure(
        "Vertical.TScrollbar",
        background="#F1F5F9",
        troughcolor=BG_PANEL,
        bordercolor=BG_PANEL,
        arrowcolor=TEXT_SECONDARY,
    )"""
code = code.replace(ttk_old, ttk_new)

# Replace any remnants of Helvetica Neue to Segoe UI to match modern windows/web vibe
code = code.replace('"Helvetica Neue"', '"Segoe UI"')
# Update event log text background
code = code.replace('log_frame = tk.Frame(parent, bg=BG_DARK, padx=1, pady=1)', 'log_frame = tk.Frame(parent, bg=BORDER_COLOR, padx=1, pady=1)')
code = code.replace('bg=BG_DARK, fg=TEXT_SECONDARY,', 'bg="#F8FAFC", fg=TEXT_PRIMARY,')

with open("main.py", "w", encoding="utf-8") as f:
    f.write(code)

print("done")
