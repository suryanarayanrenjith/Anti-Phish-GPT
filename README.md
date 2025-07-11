# Anti‑Phish‑GPT

Anti‑Phish‑GPT offers a simple Tkinter GUI that classifies any URL as **phishing**, **normal**, or **unknown** and explains its decision in plain English. The logic is self‑contained and runs locally, the only network call is the single request to the OpenAI API.

---

## ✨ Features

| Capability             | Details                                                                                        |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| 🔑 **API‑key manager** | Prompt, verify, and store your OpenAI key in an on‑disk `config.json` (next to the app).       |
| 🌐 **URL analysis**    | Sends a deterministic prompt to GPT‑4, returns a verdict, confidence, and ≤160‑char rationale. |
| 📄 **Portable config** | Same code path works in script form *and* inside a PyInstaller‑built EXE.                      |
| 🛡️ **No browsing**    | The model reasons over the string you provide, it never fetches the live site.                 |

---

## 🚀 Quick Start (script mode)

```bash
# 1 · clone
$ git clone https://github.com/suryanarayanrenjith/Anti‑Phish‑GPT.git
$ cd Anti‑Phish‑GPT

# 2 · install deps (Python 3.11+ recommended)
$ python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
$ pip install openai

# 3 · run
$ python phish_app.py
```

On first launch click **Set API Key → Save Key**. A fresh `config.json` will be created beside the script.

---

## 🏗️ Building a single‑file Windows EXE

> Produces **one** portable `Anti-Phish-GPT.exe`; the Python runtime is packed inside.

```powershell
cd Anti-Phish-GPT
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt pyinstaller

pyinstaller phish_app.py
  --onefile
  --windowed
  --clean
  --noupx              # remove if you want UPX compression
  --name Anti-Phish-GPT
```

Result:

```
dist/Anti-Phish-GPT.exe
```

---

## 🔑 First‑Run & Everyday Use

1. **Download the app** — head to the [Releases](https://github.com/suryanarayanrenjith/Anti-Phish-GPT/releases/tag/v1.0.0) section and grab `Anti‑Phish‑GPT_Portable.zip`.
2. **Launch Anti‑Phish‑GPT** — double‑click the the packaged `Anti-Phish-GPT.exe`.
3. **Add your own OpenAI API key**

   * Click **Set API Key**.
   * Paste your key (it must start with `sk-…`).
   * The app quickly validates the key against the OpenAI endpoint and shows *Success* if it’s accepted.
4. **Save the key**

   * Click **Save Key**. A file named `config.json` is created **in the same folder as the app**. You only need to do this once per machine or whenever you rotate keys.
5. **Analyse a URL**

   * Paste any link into the **URL** field.
   * Click **Analyze**.
   * The **Verdict**, **Confidence**, and a short **Rationale** appear instantly.
6. **Start over**

   * Click **Clear** to wipe the fields and run another check.
7. **Update / Remove the key**

   * To change the key, repeat step 2 and then click **Save Key** again—`config.json` will be overwritten.
   * To run without a saved key, simply delete `config.json`.

---

## 🛠️ Development Notes

* **Deterministic model calls** → `temperature=0` for reproducible verdicts.
* **Telemetry‑free build** → add `os.environ["OPENAI_DISABLE_TELEMETRY"] = "1"` before `import openai` if corporate policy requires it.
* Tested with **Python 3.12 + OpenAI 1.26** and **PyInstaller 6.6** on Windows 11.

---

## 🤝 Contributing

Pull requests and issue reports are welcome!

---

## 📜 License

Released under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

* OpenAI for the GPT API.
* PyInstaller for single‑file packaging.
* Icons from [Heroicons](https://heroicons.com/) (MIT).
