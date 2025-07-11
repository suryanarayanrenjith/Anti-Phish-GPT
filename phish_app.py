import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import openai

BASE_DIR = os.path.dirname(
    sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


class PhishApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Anti-Phish-GPT")
        self.geometry("600x260")
        self.resizable(False, False)

        self.api_key: str | None = None

        self._load_config()
        self._create_widgets()

    def _load_config(self) -> None:
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                maybe_key = cfg.get("api_key")
                if maybe_key and self._validate_key_format(maybe_key):
                    self.api_key = maybe_key
                    openai.api_key = self.api_key
            except Exception:
                pass

    def _save_config(self) -> None:
        if not self.api_key:
            messagebox.showwarning("Missing Key", "No API key to save.")
            return
        if not self._validate_key_format(self.api_key):
            messagebox.showerror("Invalid Format", "Current key does not look valid (must start with 'sk').")
            return
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"api_key": self.api_key}, f, indent=2)
            messagebox.showinfo("Success", "API key saved.")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save API key: {exc}")

    def _create_widgets(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=5)
        ttk.Button(top, text="Set API Key", command=self._set_api_key).pack(side="left")
        ttk.Button(top, text="Save Key", command=self._save_config).pack(side="left", padx=5)

        url_frame = ttk.Frame(self)
        url_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(url_frame, text="URL:").pack(side="left")
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Analyze", command=self._analyze).pack(side="right")
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side="right", padx=5)

        res_frame = ttk.LabelFrame(self, text="Result")
        res_frame.pack(fill="both", expand=True, padx=10, pady=5)
        res_frame.columnconfigure(1, weight=1)

        self.verdict_var = tk.StringVar()
        self.conf_var = tk.StringVar()
        self.rat_var = tk.StringVar()

        ttk.Label(res_frame, text="Verdict:").grid(row=0, column=0, sticky="w", padx=(5, 0), pady=2)
        ttk.Label(res_frame, textvariable=self.verdict_var).grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(res_frame, text="Confidence:").grid(row=1, column=0, sticky="w", padx=(5, 0), pady=2)
        ttk.Label(res_frame, textvariable=self.conf_var).grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(res_frame, text="Rationale:").grid(row=2, column=0, sticky="nw", padx=(5, 0), pady=2)
        ttk.Label(res_frame, textvariable=self.rat_var, wraplength=480, justify="left").grid(
            row=2, column=1, sticky="w", pady=2
        )

    @staticmethod
    def _validate_key_format(key: str) -> bool:
        return key.startswith("sk")

    @staticmethod
    def _online_key_check() -> bool:
        try:
            openai.Model.list()
            return True
        except openai.error.AuthenticationError:
            return False
        except Exception:
            return False

    def _set_api_key(self) -> None:
        key = simpledialog.askstring("API Key", "Enter your OpenAI API key:", show="*")
        if not key:
            return
        key = key.strip()
        if not self._validate_key_format(key):
            messagebox.showerror("Invalid Format", "API key must start with 'sk'.")
            return
        self.config(cursor="watch")
        self.update()
        openai.api_key = key
        ok = self._online_key_check()
        self.config(cursor="")
        if not ok:
            messagebox.showerror("Authentication Failed", "The API key was rejected by OpenAI.")
            return
        self.api_key = key
        messagebox.showinfo("Success", "API key set and verified. Click 'Save Key' to persist.")

    def _analyze(self) -> None:
        if not self.api_key:
            messagebox.showwarning("Missing Key", "Please set your API key first.")
            return
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a URL to analyze.")
            return
        result = self._detect_phishing(url)
        self.verdict_var.set(result.get("verdict", ""))
        self.conf_var.set(f"{result.get('confidence', 0):.2f}")
        self.rat_var.set(result.get("rationale", ""))

    def _detect_phishing(self, url: str) -> dict[str, str | float]:
        system_prompt = """
You are **“Anti-Phish-GPT”**, a senior SOC (Security-Operations-Center) analyst.

╔════════ 1. TASK ═════════╗
Given one URL plus any optional evidence the caller appends
(e.g. WHOIS record, HTTP headers, HTML snippet, screenshot reference),
decide whether the URL is **phishing**, **normal**, or **unknown**.

╔════════ 2. OUTPUT ═════════╗
Return **ONLY** valid JSON, no prose before or after, in exactly this schema:
{
  "verdict": "phishing" | "normal" | "unknown",
  "confidence": 0-1  // float with two decimals, 1.00 = certain
  "rationale": "<≤160-char sentence for auditors>"
}

╔════════ 3. DECISION HEURISTICS (non-exhaustive) ═════════╗
A. DOMAIN & REGISTRATION
  • Brand-look-alike, homoglyph, or punycode domain? → phishing↑  
  • Newly registered (≤180 days) or short-lived certificate? → phishing↑  
B. URL STRUCTURE
  • IP-address host, excessive sub-domains, or typosquatting? → phishing↑  
  • Query/path hints: “login”, “verify”, “reset”, “update-account”, base64 blobs? → phishing↑  
C. CONTENT & INTENT (when HTML/screenshot given)
  • Fake login/payment forms, blurred logos, urgency banners, or mismatched favicon? → phishing↑  
D. CONTEXTUAL SIGNALS
  • Positive reputation scores, age > 2 years, canonical brand domain, no credential forms → benign↑  
E. INSUFFICIENT DATA
  • If evidence is conflicting or minimal, return "unknown" with confidence ≤ 0.40.

╔════════ 4. RULES OF ENGAGEMENT ═════════╗
  • **Determinism:** Set `temperature=0`. Think step-by-step **internally** but expose ONLY the JSON.  
  • **No actions:** Never fetch or “click” the link; reason only over supplied evidence.  
  • **JSON police:** If the verdict is “phishing”, confidence **must** be ≥ 0.50.  
  • Escape any quotes in `rationale`; keep it single-line.

╔════════ 5. EXAMPLE RESPONSE (for auditors only) ═════════╗
{
  "verdict": "phishing",
  "confidence": 0.96,
  "rationale": "Homoglyph domain imitates paypal.com; WHOIS age 3 days; URL contains /login/verify."
}

--- END OF SYSTEM PROMPT ---
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps({"url": url, "evidence": None})},
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=messages,
                temperature=0,
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {"verdict": "error", "confidence": 0.00, "rationale": "Invalid JSON response."}
        except Exception as exc:
            return {"verdict": "error", "confidence": 0.00, "rationale": str(exc)}

    def _clear(self) -> None:
        self.url_entry.delete(0, tk.END)
        self.verdict_var.set("")
        self.conf_var.set("")
        self.rat_var.set("")


if __name__ == "__main__":
    PhishApp().mainloop()