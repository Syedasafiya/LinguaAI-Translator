"""
LinguaAI — Professional Language Translator
project
Premium UI: canvas art · gradient header · flag emoji · illustrated empty state
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import threading, tempfile, os, time, math

# ── Auto-install ───────────────────────────────────────────────────────────────
def _ensure(*pkgs):
    import subprocess, sys, importlib
    for pkg, imp in pkgs:
        try: importlib.import_module(imp)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

_ensure(("deep-translator","deep_translator"), ("gtts","gtts"), ("pygame","pygame"))
from deep_translator import GoogleTranslator

# ── Languages ──────────────────────────────────────────────────────────────────
LANGUAGES = {
    "Auto Detect":"auto","Afrikaans":"af","Albanian":"sq","Arabic":"ar",
    "Armenian":"hy","Azerbaijani":"az","Bengali":"bn","Bosnian":"bs",
    "Bulgarian":"bg","Catalan":"ca","Chinese (Simplified)":"zh-CN",
    "Chinese (Traditional)":"zh-TW","Croatian":"hr","Czech":"cs",
    "Danish":"da","Dutch":"nl","English":"en","Estonian":"et",
    "Finnish":"fi","French":"fr","Galician":"gl","Georgian":"ka",
    "German":"de","Greek":"el","Gujarati":"gu","Hebrew":"he","Hindi":"hi",
    "Hungarian":"hu","Icelandic":"is","Indonesian":"id","Irish":"ga",
    "Italian":"it","Japanese":"ja","Kannada":"kn","Korean":"ko",
    "Latvian":"lv","Lithuanian":"lt","Macedonian":"mk","Malay":"ms",
    "Malayalam":"ml","Maltese":"mt","Marathi":"mr","Mongolian":"mn",
    "Nepali":"ne","Norwegian":"no","Persian":"fa","Polish":"pl",
    "Portuguese":"pt","Punjabi":"pa","Romanian":"ro","Russian":"ru",
    "Serbian":"sr","Sinhala":"si","Slovak":"sk","Slovenian":"sl",
    "Somali":"so","Spanish":"es","Swahili":"sw","Swedish":"sv",
    "Tagalog":"tl","Tamil":"ta","Telugu":"te","Thai":"th","Turkish":"tr",
    "Ukrainian":"uk","Urdu":"ur","Uzbek":"uz","Vietnamese":"vi",
    "Welsh":"cy","Zulu":"zu",
}
LANG_NAMES = list(LANGUAGES.keys())

# Language → flag emoji mapping (best-effort)
LANG_FLAGS = {
    "English":"🇬🇧","Hindi":"🇮🇳","French":"🇫🇷","German":"🇩🇪","Spanish":"🇪🇸",
    "Italian":"🇮🇹","Portuguese":"🇧🇷","Russian":"🇷🇺","Japanese":"🇯🇵",
    "Korean":"🇰🇷","Chinese (Simplified)":"🇨🇳","Chinese (Traditional)":"🇹🇼",
    "Arabic":"🇸🇦","Turkish":"🇹🇷","Dutch":"🇳🇱","Polish":"🇵🇱",
    "Swedish":"🇸🇪","Danish":"🇩🇰","Norwegian":"🇳🇴","Finnish":"🇫🇮",
    "Greek":"🇬🇷","Hebrew":"🇮🇱","Thai":"🇹🇭","Vietnamese":"🇻🇳",
    "Indonesian":"🇮🇩","Malay":"🇲🇾","Bengali":"🇧🇩","Urdu":"🇵🇰",
    "Tamil":"🇱🇰","Telugu":"🇮🇳","Kannada":"🇮🇳","Malayalam":"🇮🇳",
    "Gujarati":"🇮🇳","Marathi":"🇮🇳","Punjabi":"🇮🇳","Ukrainian":"🇺🇦",
    "Czech":"🇨🇿","Romanian":"🇷🇴","Hungarian":"🇭🇺","Croatian":"🇭🇷",
    "Slovak":"🇸🇰","Bulgarian":"🇧🇬","Serbian":"🇷🇸","Persian":"🇮🇷",
    "Swahili":"🇰🇪","Afrikaans":"🇿🇦","Auto Detect":"🌐",
}

MAX_CHARS = 5000

# ── Palette ────────────────────────────────────────────────────────────────────
# Header gradient stops (drawn with canvas)
GRAD_TOP    = "#1A0533"   # deep purple-black
GRAD_BOT    = "#3B0F6B"   # rich violet

CHROME      = "#13002B"   # lang-bar background
CHROME_LINE = "#2D1052"   # border on dark
ACCENT      = "#A855F7"   # bright violet
ACCENT_DARK = "#7C3AED"
ACCENT_GLOW = "#C084FC"
ACCENT_SOFT = "#F3E8FF"   # very pale violet — output panel tint

PANEL_L     = "#FAFAFA"
PANEL_R     = "#F8F4FF"
DIVIDER     = "#E5E7EB"

TEXT_LIGHT  = "#F9FAFB"
TEXT_NAV    = "#E2D9F3"
TEXT_DARK   = "#1E1B2E"
TEXT_MID    = "#6B7280"
TEXT_FAINT  = "#9CA3AF"

GREEN       = "#10B981"
AMBER       = "#F59E0B"
RED_ERR     = "#EF4444"

SEL_BG      = "#DDD6FE"
CURSOR_CLR  = ACCENT

# ── App ────────────────────────────────────────────────────────────────────────
class LinguaAI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LinguaAI — Language Translator")
        self.geometry("1080px" if False else "1080x700")
        self.geometry("1080x700")
        self.minsize(860, 560)
        self.configure(bg=CHROME)
        self.resizable(True, True)

        self._speaking        = False
        self._translating     = False
        self._translated_txt  = ""
        self._has_placeholder = True
        self._placeholder     = "Start typing or paste your text here…"
        self._anim_id         = None
        self._dot_count       = 0

        self._build_fonts()
        self._build_ui()
        self._style_combos()
        self.bind_all("<Control-Return>", lambda e: self._translate())

    # ── Fonts ──────────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.f_logo    = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.f_tagline = tkfont.Font(family="Segoe UI", size=9)
        self.f_badge   = tkfont.Font(family="Segoe UI", size=8, weight="bold")
        self.f_label   = tkfont.Font(family="Segoe UI", size=8, weight="bold")
        self.f_lang    = tkfont.Font(family="Segoe UI", size=11)
        self.f_flag    = tkfont.Font(family="Segoe UI Emoji", size=18)
        self.f_text    = tkfont.Font(family="Segoe UI", size=13)
        self.f_out     = tkfont.Font(family="Segoe UI", size=13)
        self.f_small   = tkfont.Font(family="Segoe UI", size=9)
        self.f_btn     = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.f_counter = tkfont.Font(family="Segoe UI", size=9)
        self.f_empty   = tkfont.Font(family="Segoe UI", size=28)
        self.f_empty_s = tkfont.Font(family="Segoe UI", size=10)
        self.f_hint    = tkfont.Font(family="Segoe UI", size=8)

    # ── Full UI ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_lang_bar()
        self._build_panels()

    # ── Header (canvas gradient + decorative art) ──────────────────────────────
    def _build_header(self):
        H = 90
        self._hdr_canvas = tk.Canvas(self, height=H, highlightthickness=0,
                                      bd=0, bg=GRAD_TOP)
        self._hdr_canvas.pack(fill="x")

        # Draw gradient by stacking thin rectangles
        steps = 40
        for i in range(steps):
            t = i / steps
            r1,g1,b1 = 0x1A,0x05,0x33
            r2,g2,b2 = 0x3B,0x0F,0x6B
            r = int(r1 + (r2-r1)*t)
            g = int(g1 + (g2-g1)*t)
            b = int(b1 + (b2-b1)*t)
            col = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(H * i / steps)
            y1 = int(H * (i+1) / steps) + 1
            self._hdr_canvas.create_rectangle(0, y0, 3000, y1,
                                               fill=col, outline=col)

        # Decorative orbiting circles (world/globe motif)
        cx, cy = 54, H//2
        # Outer ring
        self._hdr_canvas.create_oval(cx-30, cy-30, cx+30, cy+30,
                                      outline="#6D28D9", width=2)
        # Inner ring (tilted — faked with ellipse)
        self._hdr_canvas.create_oval(cx-30, cy-10, cx+30, cy+10,
                                      outline="#7C3AED", width=1)
        # Vertical axis
        self._hdr_canvas.create_line(cx, cy-30, cx, cy+30,
                                      fill="#6D28D9", width=1)
        # Horizontal equator
        self._hdr_canvas.create_line(cx-30, cy, cx+30, cy,
                                      fill="#6D28D9", width=1)
        # Globe dot glow
        self._hdr_canvas.create_oval(cx-5, cy-5, cx+5, cy+5,
                                      fill=ACCENT_GLOW, outline="")

        # Decorative dots (constellation feel, right side)
        dots = [(920,18),(960,35),(940,55),(980,22),(1010,45),
                (870,40),(850,20),(1040,30),(900,65),(1020,65)]
        for dx,dy in dots:
            r = 2
            self._hdr_canvas.create_oval(dx-r, dy-r, dx+r, dy+r,
                                          fill="#6D28D9", outline="")
        # Connecting lines (light constellation lines)
        for i in range(len(dots)-1):
            x1,y1 = dots[i]; x2,y2 = dots[i+1]
            self._hdr_canvas.create_line(x1,y1,x2,y2,
                                          fill="#3B1069", width=1)

        # Small arc decorations
        self._hdr_canvas.create_arc(980, 10, 1060, 80,
                                     start=30, extent=120,
                                     outline="#5B21B6", width=1, style="arc")
        self._hdr_canvas.create_arc(840, 30, 890, 80,
                                     start=200, extent=120,
                                     outline="#4C1D95", width=1, style="arc")

        # Logo text
        self._hdr_canvas.create_text(96, H//2 - 8, text="LinguaAI",
                                      fill="white", font=self.f_logo,
                                      anchor="w")
        self._hdr_canvas.create_text(97, H//2 + 16,
                                      text="AI-Powered Language Translation  ·  70+ Languages",
                                      fill=TEXT_NAV, font=self.f_tagline,
                                      anchor="w")

        # Badge top-right
        badge_x = 1050
        self._hdr_canvas.create_rectangle(badge_x-110, H//2-14,
                                           badge_x+2,   H//2+14,
                                           fill=ACCENT, outline="",)
        self._hdr_canvas.create_text(badge_x-54, H//2,
                                      text="project",
                                      fill="white", font=self.f_badge)

        # Bind resize to redraw gradient width
        self._hdr_canvas.bind("<Configure>", self._on_header_resize)

    def _on_header_resize(self, e):
        # Extend gradient rectangles on resize — simpler: just retag fill
        pass   # gradient is drawn wide enough at 3000px

    # ── Language bar ──────────────────────────────────────────────────────────
    def _build_lang_bar(self):
        bar = tk.Frame(self, bg=CHROME, height=60)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Bottom glow line
        tk.Frame(self, bg=ACCENT_DARK, height=2).pack(fill="x")

        inner = tk.Frame(bar, bg=CHROME)
        inner.pack(fill="both", expand=True, padx=24)

        # Source flag + combo
        self.src_flag_var = tk.StringVar(value="🇬🇧")
        self.src_flag_lbl = tk.Label(inner, textvariable=self.src_flag_var,
                                      bg=CHROME, font=self.f_flag)
        self.src_flag_lbl.pack(side="left", pady=8, padx=(0,4))

        self.src_var   = tk.StringVar(value="English")
        self.src_combo = ttk.Combobox(inner, textvariable=self.src_var,
                                       values=LANG_NAMES, state="readonly",
                                       width=20, font=self.f_lang,
                                       style="Pro.TCombobox")
        self.src_combo.pack(side="left", pady=8)
        self.src_var.trace_add("write", lambda *_: self._update_flags())

        # Swap
        swap_btn = tk.Button(inner, text="⇄", bg="#2D1052", fg=ACCENT_GLOW,
                              font=self.f_btn, relief="flat", cursor="hand2",
                              padx=14, pady=6,
                              activebackground=ACCENT, activeforeground="white",
                              command=self._swap)
        swap_btn.pack(side="left", padx=18)
        self._hover(swap_btn, ACCENT, "white", "#2D1052", ACCENT_GLOW)

        # Target flag + combo
        self.tgt_flag_var = tk.StringVar(value="🇮🇳")
        self.tgt_flag_lbl = tk.Label(inner, textvariable=self.tgt_flag_var,
                                      bg=CHROME, font=self.f_flag)
        self.tgt_flag_lbl.pack(side="left", pady=8, padx=(0,4))

        self.tgt_var   = tk.StringVar(value="Hindi")
        self.tgt_combo = ttk.Combobox(inner, textvariable=self.tgt_var,
                                       values=LANG_NAMES, state="readonly",
                                       width=20, font=self.f_lang,
                                       style="Pro.TCombobox")
        self.tgt_combo.pack(side="left", pady=8)
        self.tgt_var.trace_add("write", lambda *_: self._update_flags())

        # Translate button
        self.trans_btn = tk.Button(inner, text="  ⚡  Translate",
                                    bg=ACCENT, fg="white",
                                    font=self.f_btn, relief="flat",
                                    cursor="hand2", padx=22, pady=8,
                                    activebackground=ACCENT_DARK,
                                    activeforeground="white",
                                    command=self._translate)
        self.trans_btn.pack(side="right", pady=8)
        self._hover(self.trans_btn, ACCENT_DARK, "white", ACCENT, "white")

        # Status
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(inner, textvariable=self.status_var,
                                    bg=CHROME, fg=TEXT_FAINT, font=self.f_small)
        self.status_lbl.pack(side="right", padx=16)

    # ── Panels ─────────────────────────────────────────────────────────────────
    def _build_panels(self):
        wrap = tk.Frame(self, bg=DIVIDER)
        wrap.pack(fill="both", expand=True)
        wrap.columnconfigure(0, weight=1)
        wrap.columnconfigure(1, weight=1)
        wrap.rowconfigure(0, weight=1)

        left  = tk.Frame(wrap, bg=PANEL_L)
        right = tk.Frame(wrap, bg=PANEL_R)
        left.grid( row=0, column=0, sticky="nsew")
        tk.Frame(wrap, bg=DIVIDER, width=1).grid(row=0, column=0, sticky="nse")
        right.grid(row=0, column=1, sticky="nsew")

        for f in (left, right):
            f.rowconfigure(1, weight=1)
            f.columnconfigure(0, weight=1)

        self._build_left(left)
        self._build_right(right)

    # ── Left panel ─────────────────────────────────────────────────────────────
    def _build_left(self, p):
        # Panel header strip
        top = tk.Frame(p, bg="#F0EBF8", padx=18, pady=8)
        top.grid(row=0, column=0, sticky="ew")

        tk.Label(top, text="✏️  SOURCE TEXT", bg="#F0EBF8", fg=ACCENT_DARK,
                 font=self.f_label).pack(side="left")

        self.char_var = tk.StringVar(value="0 / 5,000")
        self.char_lbl = tk.Label(top, textvariable=self.char_var,
                                  bg="#F0EBF8", fg=TEXT_FAINT,
                                  font=self.f_counter)
        self.char_lbl.pack(side="right")

        clr = tk.Button(top, text="✕ Clear", bg="#F0EBF8", fg=TEXT_FAINT,
                         font=self.f_hint, relief="flat", cursor="hand2",
                         padx=6, activebackground=DIVIDER,
                         command=self._clear)
        clr.pack(side="right", padx=8)
        self._hover(clr, DIVIDER, TEXT_MID, "#F0EBF8", TEXT_FAINT)

        tk.Frame(p, bg=DIVIDER, height=1).grid(row=0, column=0,
                  sticky="sew", pady=(34,0))

        # Input area
        self.input_txt = tk.Text(p, bg=PANEL_L, fg=TEXT_DARK,
                                  font=self.f_text, relief="flat", bd=0,
                                  wrap="word", padx=22, pady=18,
                                  insertbackground=CURSOR_CLR,
                                  selectbackground=SEL_BG,
                                  undo=True, highlightthickness=0)
        self.input_txt.grid(row=1, column=0, sticky="nsew")
        self.input_txt.insert("1.0", self._placeholder)
        self.input_txt.config(fg=TEXT_FAINT)
        self.input_txt.bind("<FocusIn>",  self._clear_ph)
        self.input_txt.bind("<FocusOut>", self._restore_ph)
        self.input_txt.bind("<KeyRelease>", self._on_key)

        # Progress bar
        pb_frame = tk.Frame(p, bg=DIVIDER, height=4)
        pb_frame.grid(row=2, column=0, sticky="ew")
        pb_frame.pack_propagate(False)
        self._prog = tk.Frame(pb_frame, bg=ACCENT, height=4)
        self._prog.place(x=0, y=0, relheight=1, relwidth=0)

        # Bottom bar
        tk.Frame(p, bg=DIVIDER, height=1).grid(row=3, column=0, sticky="ew")
        bot = tk.Frame(p, bg=PANEL_L, padx=18, pady=8)
        bot.grid(row=4, column=0, sticky="ew")
        tk.Label(bot, text="⌨️  Ctrl+Enter to translate",
                 bg=PANEL_L, fg="#D1D5DB", font=self.f_hint).pack(side="right")

    # ── Right panel ────────────────────────────────────────────────────────────
    def _build_right(self, p):
        # Panel header strip
        top = tk.Frame(p, bg="#EDE9FE", padx=18, pady=8)
        top.grid(row=0, column=0, sticky="ew")

        tk.Label(top, text="🌐  TRANSLATION", bg="#EDE9FE", fg=ACCENT_DARK,
                 font=self.f_label).pack(side="left")

        self.out_char_var = tk.StringVar(value="")
        tk.Label(top, textvariable=self.out_char_var, bg="#EDE9FE",
                 fg=TEXT_FAINT, font=self.f_counter).pack(side="right")

        self.tgt_badge_var = tk.StringVar(value="")
        self._tgt_badge = tk.Label(top, textvariable=self.tgt_badge_var,
                                    bg=ACCENT, fg="white",
                                    font=self.f_badge, padx=8, pady=2)
        self._tgt_badge.pack(side="right", padx=10)

        tk.Frame(p, bg=DIVIDER, height=1).grid(row=0, column=0,
                  sticky="sew", pady=(34,0))

        self.output_txt = tk.Text(p, bg=PANEL_R, fg=TEXT_DARK,
                                   font=self.f_out, relief="flat", bd=0,
                                   wrap="word", padx=22, pady=18,
                                   state="disabled",
                                   selectbackground=SEL_BG,
                                   highlightthickness=0)
        self.output_txt.grid(row=1, column=0, sticky="nsew")

        # Empty state (shown when no translation yet)
        self._empty_frame = tk.Frame(p, bg=PANEL_R)
        self._empty_frame.grid(row=1, column=0, sticky="nsew")
        self._build_empty_state(self._empty_frame)

        # Bottom bar
        tk.Frame(p, bg=DIVIDER, height=1).grid(row=2, column=0, sticky="ew")
        bot = tk.Frame(p, bg=PANEL_R, padx=18, pady=8)
        bot.grid(row=3, column=0, sticky="ew")

        self._mk_action_btn(bot, "📋  Copy",  self._copy ).pack(side="left")
        self._mk_action_btn(bot, "🔊  Speak", self._speak).pack(side="left", padx=8)

    def _build_empty_state(self, parent):
        """Illustrated empty state with decorative canvas art."""
        c = tk.Canvas(parent, bg=PANEL_R, highlightthickness=0, bd=0)
        c.pack(fill="both", expand=True)

        def draw(event=None):
            c.delete("all")
            W, H = c.winfo_width(), c.winfo_height()
            if W < 2: return

            cx, cy = W//2, H//2 - 30

            # Outer decorative ring
            c.create_oval(cx-70, cy-70, cx+70, cy+70,
                           outline="#DDD6FE", width=2)
            # Middle ring
            c.create_oval(cx-48, cy-48, cx+48, cy+48,
                           outline="#C4B5FD", width=1)
            # Inner filled circle
            c.create_oval(cx-32, cy-32, cx+32, cy+32,
                           fill="#EDE9FE", outline="#A78BFA", width=2)

            # Globe lines inside inner circle (decorative)
            c.create_oval(cx-32, cy-10, cx+32, cy+10,
                           outline="#A78BFA", width=1)
            c.create_line(cx, cy-32, cx, cy+32, fill="#A78BFA", width=1)

            # Globe icon text
            c.create_text(cx, cy, text="🌐",
                           font=tkfont.Font(family="Segoe UI Emoji", size=22),
                           fill=ACCENT_DARK)

            # Small orbiting dots
            for angle_deg in range(0, 360, 45):
                angle = math.radians(angle_deg)
                dx = cx + int(58 * math.cos(angle))
                dy = cy + int(58 * math.sin(angle))
                c.create_oval(dx-4, dy-4, dx+4, dy+4,
                               fill=ACCENT if angle_deg % 90==0 else "#C4B5FD",
                               outline="")

            # Prompt text
            c.create_text(cx, cy+100,
                           text="Your translation will appear here",
                           font=tkfont.Font(family="Segoe UI", size=12),
                           fill=TEXT_MID)
            c.create_text(cx, cy+122,
                           text="Type in the left panel and press  ⚡ Translate",
                           font=tkfont.Font(family="Segoe UI", size=9),
                           fill=TEXT_FAINT)

            # Bottom language chips row
            langs = ["EN","FR","DE","HI","JP","ES","AR","ZH"]
            chip_w, chip_h, gap = 36, 20, 6
            total = len(langs)*(chip_w+gap) - gap
            sx = cx - total//2
            for i, lg in enumerate(langs):
                x0 = sx + i*(chip_w+gap)
                y0 = cy + 148
                c.create_rectangle(x0, y0, x0+chip_w, y0+chip_h,
                                    fill="#EDE9FE", outline="#C4B5FD")
                c.create_text(x0+chip_w//2, y0+chip_h//2, text=lg,
                               font=tkfont.Font(family="Segoe UI", size=8),
                               fill=ACCENT_DARK)

        c.bind("<Configure>", lambda e: draw())
        self._empty_canvas = c

    # ── Widget helpers ─────────────────────────────────────────────────────────
    def _mk_action_btn(self, parent, text, cmd):
        b = tk.Button(parent, text=text, bg=PANEL_R, fg=TEXT_MID,
                       font=self.f_small, relief="flat", cursor="hand2",
                       padx=12, pady=5,
                       activebackground=ACCENT_SOFT,
                       activeforeground=ACCENT_DARK,
                       highlightbackground=DIVIDER,
                       highlightthickness=1,
                       command=cmd)
        self._hover(b, ACCENT_SOFT, ACCENT_DARK, PANEL_R, TEXT_MID)
        return b

    def _hover(self, w, bg_in, fg_in, bg_out, fg_out):
        w.bind("<Enter>", lambda e: w.config(bg=bg_in, fg=fg_in))
        w.bind("<Leave>", lambda e: w.config(bg=bg_out, fg=fg_out))

    def _style_combos(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Pro.TCombobox",
                    fieldbackground=CHROME,
                    background="#2D1052",
                    foreground=TEXT_LIGHT,
                    selectbackground=ACCENT_DARK,
                    selectforeground="white",
                    arrowcolor=ACCENT_GLOW,
                    bordercolor=CHROME_LINE,
                    lightcolor=CHROME_LINE,
                    darkcolor=CHROME_LINE,
                    padding=(8, 6))
        s.map("Pro.TCombobox",
              fieldbackground=[("readonly", CHROME)],
              foreground=[("readonly", TEXT_LIGHT)])

    # ── Flag updater ───────────────────────────────────────────────────────────
    def _update_flags(self):
        self.src_flag_var.set(LANG_FLAGS.get(self.src_var.get(), "🏳️"))
        self.tgt_flag_var.set(LANG_FLAGS.get(self.tgt_var.get(), "🏳️"))

    # ── Placeholder ────────────────────────────────────────────────────────────
    def _clear_ph(self, e=None):
        if self._has_placeholder:
            self.input_txt.delete("1.0", "end")
            self.input_txt.config(fg=TEXT_DARK)
            self._has_placeholder = False

    def _restore_ph(self, e=None):
        if not self.input_txt.get("1.0", "end-1c").strip():
            self.input_txt.insert("1.0", self._placeholder)
            self.input_txt.config(fg=TEXT_FAINT)
            self._has_placeholder = True

    # ── Key events ─────────────────────────────────────────────────────────────
    def _on_key(self, e=None):
        if self._has_placeholder: return
        n = len(self.input_txt.get("1.0", "end-1c"))
        self.char_var.set(f"{n:,} / {MAX_CHARS:,}")
        self.char_lbl.config(fg=RED_ERR if n > MAX_CHARS else TEXT_FAINT)
        ratio = min(n / MAX_CHARS, 1.0)
        col = RED_ERR if n > MAX_CHARS else (AMBER if ratio > 0.8 else ACCENT)
        self._prog.config(bg=col)
        self._prog.place(relwidth=ratio)

    def _get_input(self):
        if self._has_placeholder: return ""
        return self.input_txt.get("1.0", "end-1c").strip()

    # ── Swap ───────────────────────────────────────────────────────────────────
    def _swap(self):
        src, tgt = self.src_var.get(), self.tgt_var.get()
        if src == "Auto Detect" or tgt == "Auto Detect":
            self._status("⚠  Can't swap with Auto Detect", AMBER); return
        self.src_var.set(tgt); self.tgt_var.set(src)
        inp = self._get_input()
        out = self.output_txt.get("1.0", "end-1c")
        self.input_txt.delete("1.0", "end")
        if out.strip():
            self.input_txt.config(fg=TEXT_DARK)
            self._has_placeholder = False
            self.input_txt.insert("1.0", out)
            self._on_key()
        self._set_output(inp)

    # ── Clear ──────────────────────────────────────────────────────────────────
    def _clear(self):
        self.input_txt.delete("1.0", "end")
        self._restore_ph()
        self._set_output("")
        self.char_var.set("0 / 5,000")
        self.char_lbl.config(fg=TEXT_FAINT)
        self._prog.place(relwidth=0)
        self.out_char_var.set("")
        self.tgt_badge_var.set("")
        self.status_var.set("")
        # Show empty state
        self._empty_frame.lift()

    # ── Translate ──────────────────────────────────────────────────────────────
    def _translate(self):
        text = self._get_input()
        if not text:
            self._status("⚠  Enter some text first", AMBER); return
        if len(text) > MAX_CHARS:
            self._status(f"⚠  Too long (max {MAX_CHARS:,})", RED_ERR); return
        tgt = self.tgt_var.get()
        if tgt == "Auto Detect":
            self._status("⚠  Pick a target language", AMBER); return

        self._status("Translating", TEXT_FAINT)
        self._start_anim()
        self.trans_btn.config(state="disabled", text="  ⏳  Working…")
        self._translating = True
        threading.Thread(target=self._do_translate,
                         args=(text, LANGUAGES[self.src_var.get()],
                               LANGUAGES[tgt]), daemon=True).start()

    def _do_translate(self, text, src, tgt):
        try:
            result = GoogleTranslator(source=src, target=tgt).translate(text)
            self.after(0, self._finish, result, None)
        except Exception as ex:
            self.after(0, self._finish, None, str(ex))

    def _finish(self, result, error):
        self._stop_anim()
        self.trans_btn.config(state="normal", text="  ⚡  Translate")
        self._translating = False
        if result:
            self._set_output(result)
            self.tgt_badge_var.set(f"  {self.tgt_var.get()}  ")
            self._status("✓  Translation complete", GREEN)
            self.output_txt.lift()   # hide empty state
        else:
            self._status(f"✗  {error}", RED_ERR)

    def _set_output(self, text):
        self._translated_txt = text
        self.output_txt.config(state="normal")
        self.output_txt.delete("1.0", "end")
        if text: self.output_txt.insert("1.0", text)
        self.output_txt.config(state="disabled")
        self.out_char_var.set(f"{len(text):,} chars" if text else "")

    # ── Status ─────────────────────────────────────────────────────────────────
    def _status(self, msg, color=None):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color or TEXT_FAINT)

    # ── Dot animation ──────────────────────────────────────────────────────────
    def _start_anim(self):
        self._dot_count = 0
        self._tick_anim()

    def _tick_anim(self):
        if not self._translating: return
        dots = "." * (self._dot_count % 4)
        self.status_var.set(f"Translating{dots:<3}")
        self._dot_count += 1
        self._anim_id = self.after(380, self._tick_anim)

    def _stop_anim(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None

    # ── Copy & Speak ───────────────────────────────────────────────────────────
    def _copy(self):
        out = self.output_txt.get("1.0", "end-1c")
        if out.strip():
            self.clipboard_clear(); self.clipboard_append(out)
            self._status("✓  Copied to clipboard", GREEN)
        else:
            self._status("Translate something first", TEXT_FAINT)

    def _speak(self):
        if self._speaking: return
        out = self._translated_txt.strip()
        if not out:
            self._status("Translate something first", TEXT_FAINT); return
        tgt_code = LANGUAGES.get(self.tgt_var.get(), "en")
        if tgt_code in ("auto","ceb","hmn","haw","ny","sm","sn","st","su","mg","xh","yo","zu"):
            tgt_code = "en"
        self._status("🔊  Speaking…", ACCENT_GLOW)
        self._speaking = True
        threading.Thread(target=self._do_speak,
                         args=(out, tgt_code), daemon=True).start()

    def _do_speak(self, text, lang):
        try:
            from gtts import gTTS
            import pygame
            tts = gTTS(text=text, lang=lang, slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tmp = f.name
            tts.save(tmp)
            pygame.mixer.init()
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): time.sleep(0.1)
            pygame.mixer.music.unload()
            os.remove(tmp)
            self.after(0, self._status, "✓  Done speaking", GREEN)
        except Exception as ex:
            self.after(0, self._status, f"✗  TTS error: {ex}", RED_ERR)
        finally:
            self._speaking = False


if __name__ == "__main__":
    app = LinguaAI()
    app.mainloop()