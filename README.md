# 🛡️ Smart AI Safety Guard

A comprehensive, local AI safety evaluation engine and web application built with Python and Streamlit. Features real-time heuristic safety verification, explainable risk scoring, automated batch testing, interactive analytics, and audit-ready PDF reports.

---

## 🚀 How to Run in Visual Studio Code (Windows)

### Method 1: The One-Click Key (Easiest)
1. Open this folder in **Visual Studio Code**.
2. Press **`F5`** on your keyboard (or click **Run** → **Start Debugging** in the top menu).
3. VS Code will automatically start Streamlit and open your web browser at:
   ```
   http://localhost:8501
   ```

---

### Method 2: In the VS Code Terminal
1. Open the integrated terminal in VS Code:
   - Shortcut: **`Ctrl + ~`** (or menu **Terminal** → **New Terminal**).
2. Type and run this command:
   ```powershell
   python -m streamlit run app.py
   ```
   *(Or simply run: `.\run.ps1`)*
3. Your browser will automatically open at **`http://localhost:8501`**.

> 💡 **Important Tip**: Always use `python -m streamlit run app.py` on Windows rather than `streamlit run app.py`. This ensures Windows finds Python even if system PATH variables are not configured. Also, this is a Python project, so do **not** use `npm run dev`.

---

### Method 3: Windows File Explorer (No Terminal Needed)
1. In Windows File Explorer, open the `Smart_AI_Safety_Guard` folder.
2. Double-click **`run.bat`**.
3. It will automatically check dependencies and open the website in your default browser.

---

## 📁 Project Structure

```
Smart_AI_Safety_Guard/
├── .vscode/
│   ├── launch.json     # VS Code F5 debug configuration
│   └── tasks.json      # VS Code build task configuration
├── app.py              # Main Streamlit web application & UI
├── safety_guard.py     # Rule-based safety heuristics & scoring engine
├── database.py         # SQLite relational persistence layer
├── auto_tester.py      # Automated batch testing & verdict evaluator
├── pdf_generator.py    # Audit PDF report generation (fpdf2)
├── run.bat             # Double-click launcher for Windows Explorer
├── run.ps1             # PowerShell launcher for VS Code Terminal
├── requirements.txt    # Python package dependencies
├── .env.example        # Environment configuration template
├── .gitignore          # Version control ignore rules
└── README.md           # Documentation and setup instructions
```

---

## 🌟 Key Features

1. **Interactive Safety Checker**:
   - Live scanning of user prompts and AI responses.
   - Heuristic classification into Safe, Potentially Unsafe, Unsafe, or Suspicious.
   - Explainable rule breakdown with matched patterns and confidence metrics.
   - One-click PDF download for individual safety evaluations.

2. **Analytics Dashboard**:
   - Real-time KPIs: Pass rates, risk counts, and total runs.
   - Interactive Plotly charts: Status distributions and threat category breakdowns.
   - Executive Audit Report PDF export.

3. **Analysis History**:
   - Full SQLite database audit log.
   - Search filter and status filtering.
   - CSV export and history clearing.

4. **Automated Testing Suite**:
   - Built-in benchmark test cases.
   - Progress-tracked batch execution.
   - Pass / Fail / Suspicious verdict evaluation.
