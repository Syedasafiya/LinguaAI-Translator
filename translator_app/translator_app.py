"""
Language Translation Tool — CodeAlpha Internship Task 1
Uses deep-translator (Google Translate) with a tkinter GUI
No API key required!
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import tkinter.font as tkfont

try:
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import LanguageNotSupportedException
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator"])
    from deep_translator import GoogleTranslator
    from deep_translator.exceptions import LanguageNotSupportedException

# ── Language list ──────────────────────────────────────────────────────────────
LANGUAGES = {
    "Auto Detect": "auto",
    "Afrikaans": "af", "Albanian": "sq", "Amharic": "am",
    "Arabic": "ar", "Armenian": "hy", "Azerbaijani": "az",
    "Basque": "eu", "Belarusian": "be", "Bengali": "bn",
    "Bosnian": "bs", "Bulgarian": "bg", "Catalan": "ca",
    "Cebuano": "ceb", "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW", "Corsican": "co",
    "Croatian": "hr", "Czech": "cs", "Danish": "da",
    "Dutch": "nl", "English": "en", "Esperanto": "eo",
    "Estonian": "et", "Finnish": "fi", "French": "fr",
    "Frisian": "fy", "Galician": "gl", "Georgian": "ka",
    "German": "de", "Greek": "el", "Gujarati": "gu",
    "Haitian Creole": "ht", "Hausa": "ha", "Hawaiian": "haw",
    "Hebrew": "he", "Hindi": "hi", "Hmong": "hmn",
    "Hungarian": "hu", "Icelandic": "is", "Igbo": "ig",
    "Indonesian": "id", "Irish": "ga", "Italian": "it",
    "Japanese": "ja", "Javanese": "jv", "Kannada": "kn",
    "Kazakh": "kk", "Khmer": "km", "Korean": "ko",
    "Kurdish": "ku", "Kyrgyz": "ky", "Lao": "lo",
    "Latin": "la", "Latvian": "lv", "Lithuanian": "lt",
    "Luxembourgish": "lb", "Macedonian": "mk", "Malagasy": "mg",
    "Malay": "ms", "Malayalam": "ml", "Maltese": "mt",
    "Maori": "mi", "Marathi": "mr", "Mongolian": "mn",
    "Nepali": "ne", "Norwegian": "no", "Nyanja": "ny",
    "Odia": "or", "Pashto": "ps", "Persian": "fa",
    "Polish": "pl", "Portuguese": "pt", "Punjabi": "pa",
    "Romanian": "ro", "Russian": "ru", "Samoan": "sm",
    "Serbian": "sr", "Shona": "sn", "Sindhi": "sd",
    "Sinhala": "si", "Slovak": "sk", "Slovenian": "sl",
    "Somali": "so", "Spanish": "es", "Sundanese": "su",
    "Swahili": "sw", "Swedish": "sv", "Tagalog": "tl",
    "Tajik": "tg", "Tamil": "ta", "Telugu": "te",
    "Thai": "th", "Turkish": "tr", "Ukrainian": "uk",
    "Urdu": "ur", "Uyghur": "ug", "Uzbek": "uz",
    "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh",
    "Yiddish": "yi", "Yoruba": "yo", "Zulu": "zu",
}

LANG_NAMES = list(LANGUAGES.keys())

# ── Color palette ──────────────────────────────────────────────────────────────
BG        = "#0F1117"
CARD      = "#1A1D27"
ACCENT    = "#6C63FF"
ACCENT2   = "#A89CFF"
TEXT      = "#E8E8F0"
SUBTEXT   = "#8888AA"
BORDER    = "#2E2E45"
SUCCESS   = "#4CAF7D"
INPUT_BG  = "#13151F"


class TranslatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LinguaAI — Language Translator")
        self.geometry("900x680")
        self.minsize(750, 580)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._build_fonts()
        self._build_ui()
        self._tts_available = self._check_tts()

    # ── Fonts ──────────────────────────────────────────────────────────────────
    def _build_fonts(self):
        self.f_title  = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.f_sub    = tkfont.Font(family="Segoe UI", size=10)
        self.f_label  = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.f_text   = tkfont.Font(family="Segoe UI", size=12)
        self.f_btn    = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.f_small  = tkfont.Font(family="Segoe UI", size=9)

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=CARD, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🌐  LinguaAI", bg=CARD, fg=TEXT,
                 font=self.f_title).pack()
        tk.Label(hdr, text="Powered by Google Translate · CodeAlpha Internship Task",
                 bg=CARD, fg=SUBTEXT, font=self.f_sub).pack()

        # Separator
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

        # Main body
        body = tk.Frame(self, bg=BG, padx=20, pady=16)
        body.pack(fill="both", expand=True)

        # ── Language selectors row ─────────────────────────────────────────────
        sel_row = tk.Frame(body, bg=BG)
        sel_row.pack(fill="x", pady=(0, 12))

        # Source
        src_frame = tk.Frame(sel_row, bg=BG)
        src_frame.pack(side="left", fill="x", expand=True)
        tk.Label(src_frame, text="SOURCE LANGUAGE", bg=BG, fg=SUBTEXT,
                 font=self.f_small).pack(anchor="w")
        self.src_var = tk.StringVar(value="Auto Detect")
        self.src_combo = self._combo(src_frame, self.src_var)
        self.src_combo.pack(fill="x", pady=(4, 0))

        # Swap button
        mid = tk.Frame(sel_row, bg=BG, padx=12)
        mid.pack(side="left", pady=(14, 0))
        tk.Button(mid, text="⇄", bg=ACCENT, fg=TEXT, font=self.f_btn,
                  relief="flat", cursor="hand2", padx=10, pady=6,
                  command=self._swap_languages,
                  activebackground=ACCENT2, activeforeground=TEXT
                  ).pack()

        # Target
        tgt_frame = tk.Frame(sel_row, bg=BG)
        tgt_frame.pack(side="left", fill="x", expand=True)
        tk.Label(tgt_frame, text="TARGET LANGUAGE", bg=BG, fg=SUBTEXT,
                 font=self.f_small).pack(anchor="w")
        self.tgt_var = tk.StringVar(value="Hindi")
        self.tgt_combo = self._combo(tgt_frame, self.tgt_var)
        self.tgt_combo.pack(fill="x", pady=(4, 0))

        # ── Text areas row ─────────────────────────────────────────────────────
        areas = tk.Frame(body, bg=BG)
        areas.pack(fill="both", expand=True)
        areas.columnconfigure(0, weight=1)
        areas.columnconfigure(1, weight=1)
        areas.rowconfigure(1, weight=1)

        # Input label + char counter
        in_top = tk.Frame(areas, bg=BG)
        in_top.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 4))
        tk.Label(in_top, text="ENTER TEXT", bg=BG, fg=SUBTEXT,
                 font=self.f_small).pack(side="left")
        self.char_lbl = tk.Label(in_top, text="0 / 5000", bg=BG,
                                 fg=SUBTEXT, font=self.f_small)
        self.char_lbl.pack(side="right")

        # Output label
        out_top = tk.Frame(areas, bg=BG)
        out_top.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 4))
        tk.Label(out_top, text="TRANSLATION", bg=BG, fg=SUBTEXT,
                 font=self.f_small).pack(side="left")

        # Input box
        self.input_txt = tk.Text(areas, bg=INPUT_BG, fg=TEXT, font=self.f_text,
                                  relief="flat", bd=0, wrap="word",
                                  insertbackground=ACCENT2,
                                  selectbackground=ACCENT,
                                  padx=14, pady=12, undo=True)
        self.input_txt.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.input_txt.bind("<KeyRelease>", self._on_key)
        self._add_border(areas, row=1, col=0, padx=(0, 8))

        # Output box
        self.output_txt = tk.Text(areas, bg=INPUT_BG, fg=SUCCESS, font=self.f_text,
                                   relief="flat", bd=0, wrap="word",
                                   state="disabled", padx=14, pady=12,
                                   selectbackground=ACCENT)
        self.output_txt.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        self._add_border(areas, row=1, col=1, padx=(8, 0))

        # ── Action buttons ─────────────────────────────────────────────────────
        btn_row = tk.Frame(body, bg=BG, pady=14)
        btn_row.pack(fill="x")

        self._btn(btn_row, "🔄  Translate", self._translate, ACCENT).pack(side="left")
        self._btn(btn_row, "📋  Copy", self._copy, BORDER).pack(side="left", padx=(10, 0))
        self._btn(btn_row, "🔊  Speak", self._speak, BORDER).pack(side="left", padx=(10, 0))
        self._btn(btn_row, "🗑  Clear", self._clear, BORDER).pack(side="left", padx=(10, 0))

        self.status = tk.Label(btn_row, text="Ready", bg=BG, fg=SUBTEXT, font=self.f_small)
        self.status.pack(side="right")

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _combo(self, parent, var):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
                         fieldbackground=INPUT_BG,
                         background=CARD,
                         foreground=TEXT,
                         selectbackground=ACCENT,
                         selectforeground=TEXT,
                         arrowcolor=ACCENT2,
                         bordercolor=BORDER,
                         lightcolor=BORDER,
                         darkcolor=BORDER)
        cb = ttk.Combobox(parent, textvariable=var, values=LANG_NAMES,
                          style="Dark.TCombobox", state="readonly",
                          font=self.f_text)
        return cb

    def _btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=TEXT, font=self.f_btn,
                         relief="flat", cursor="hand2",
                         padx=16, pady=8,
                         activebackground=ACCENT2,
                         activeforeground=BG)

    def _add_border(self, parent, row, col, padx):
        """Draws a 1px border frame behind each text area."""
        f = tk.Frame(parent, bg=BORDER, bd=1, relief="solid")
        # We raise the text widget on top; border achieved via background frame
        # (simple approach: configure text widget with highlightthickness)
        # Actually set highlightbackground directly:
        widget = parent.grid_slaves(row=row, column=col)[0]
        widget.configure(highlightthickness=1,
                         highlightbackground=BORDER,
                         highlightcolor=ACCENT)

    def _check_tts(self):
        try:
            import pyttsx3
            return True
        except ImportError:
            return False

    # ── Events ─────────────────────────────────────────────────────────────────
    def _on_key(self, event=None):
        text = self.input_txt.get("1.0", "end-1c")
        count = len(text)
        self.char_lbl.config(text=f"{count} / 5000",
                             fg=TEXT if count <= 5000 else "#FF5555")

    def _swap_languages(self):
        src = self.src_var.get()
        tgt = self.tgt_var.get()
        if src == "Auto Detect":
            return
        self.src_var.set(tgt)
        self.tgt_var.set(src)
        # Swap text too
        src_text = self.input_txt.get("1.0", "end-1c")
        out_text = self.output_txt.get("1.0", "end-1c")
        self.input_txt.delete("1.0", "end")
        self.input_txt.insert("1.0", out_text)
        self._set_output(src_text)

    def _translate(self):
        text = self.input_txt.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("No Input", "Please enter text to translate.")
            return
        if len(text) > 5000:
            messagebox.showerror("Too Long", "Text exceeds 5000 character limit.")
            return

        src_name = self.src_var.get()
        tgt_name = self.tgt_var.get()
        src_code = LANGUAGES[src_name]
        tgt_code = LANGUAGES[tgt_name]

        if tgt_name == "Auto Detect":
            messagebox.showwarning("Invalid", "Please select a target language.")
            return

        self.status.config(text="Translating…", fg=ACCENT2)
        self.update_idletasks()
        threading.Thread(target=self._do_translate,
                         args=(text, src_code, tgt_code), daemon=True).start()

    def _do_translate(self, text, src, tgt):
        try:
            result = GoogleTranslator(source=src, target=tgt).translate(text)
            self.after(0, self._set_output, result)
            self.after(0, self.status.config, {"text": "✓ Translation complete", "fg": SUCCESS})
        except Exception as e:
            self.after(0, messagebox.showerror, "Error", f"Translation failed:\n{e}")
            self.after(0, self.status.config, {"text": "Error", "fg": "#FF5555"})

    def _set_output(self, text):
        self.output_txt.config(state="normal")
        self.output_txt.delete("1.0", "end")
        self.output_txt.insert("1.0", text)
        self.output_txt.config(state="disabled")

    def _copy(self):
        text = self.output_txt.get("1.0", "end-1c")
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status.config(text="✓ Copied to clipboard!", fg=SUCCESS)
        else:
            messagebox.showinfo("Nothing to copy", "Translate something first.")

    def _speak(self):
        if not self._tts_available:
            try:
                import subprocess, sys
                subprocess.check_call([sys.executable, "-m", "pip",
                                       "install", "pyttsx3"])
                self._tts_available = True
            except Exception:
                messagebox.showinfo("TTS Unavailable",
                    "Install pyttsx3:\n  pip install pyttsx3")
                return
        text = self.output_txt.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showinfo("Nothing to speak", "Translate something first.")
            return
        threading.Thread(target=self._do_speak, args=(text,), daemon=True).start()

    def _do_speak(self, text):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            self.after(0, messagebox.showerror, "TTS Error", str(e))

    def _clear(self):
        self.input_txt.delete("1.0", "end")
        self._set_output("")
        self.char_lbl.config(text="0 / 5000", fg=SUBTEXT)
        self.status.config(text="Ready", fg=SUBTEXT)


if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
