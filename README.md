# PDF Flowchart AI Starter

This project helps you start from client PDF files and create flowcharts/diagrams using Python.

The beginner workflow is:

1. Extract text from a client PDF.
2. Convert the important process steps into Mermaid flowchart code.
3. Preview the diagram in a browser.
4. Later, connect an AI model to generate better Mermaid from the extracted text.

## Folder Meaning

- `src/extract_pdf_text.py` reads text from a PDF.
- `src/diagram_rules.py` creates a simple first flowchart from that text.
- `src/main.py` runs the full pipeline.
- `prompts/flowchart_prompt.md` is the prompt you can give to your AI model later.
- `outputs/` is where generated `.mmd` and `.html` files will be saved.

## Run In VS Code

Open this folder in VS Code:

```powershell
cd C:\Users\91902\Documents\Codex\2026-05-26\files-mentioned-by-the-user-pdfs\pdf_flowchart_ai
code .
```

Run one PDF:

```powershell
python .\src\main.py --pdf "C:\Users\91902\Documents\Codex\2026-05-26\files-mentioned-by-the-user-pdfs\client_pdfs\pdfs\#362_MEF_BIN Management System.pdf"
```

If your normal Python does not have `pypdf`, install it:

```powershell
pip install -r requirements.txt
```

After running, open the generated `.html` file from the `outputs` folder.

Example output already created:

```text
C:\Users\91902\Documents\Codex\2026-05-26\files-mentioned-by-the-user-pdfs\pdf_flowchart_ai\outputs\362_mef_bin_management_system.html
```

## What To Learn First

1. Run `src/main.py` with one PDF.
2. Open the `.txt` output and read what text came from the PDF.
3. Open the `.mmd` output and study the Mermaid syntax.
4. Open the `.html` output to see the diagram visually.
5. Edit `src/diagram_rules.py` when you want better project-specific flow steps.

## Next AI Step

When your basic flow works, send the extracted `.txt` content to your AI model using the prompt in:

```text
prompts/flowchart_prompt.md
```

The AI model should return Mermaid code, and your app can save that Mermaid code as `.mmd` and `.html`.

## Full BOM PPTX Generator

This project also includes a local web app that creates a full BOM PowerPoint from pasted requirements.

Install packages:

```powershell
cd C:\Users\91902\Documents\Codex\2026-05-26\files-mentioned-by-the-user-pdfs\pdf_flowchart_ai
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

Start the app:

```powershell
& ".\.venv\Scripts\python.exe" .\src\bom_app.py
```

Open in browser:

```text
http://127.0.0.1:5050
```

Then:

1. Paste the customer requirement.
2. Paste the proposed solution if available.
3. Paste your OpenRouter key in the page, or create a `.env` file from `.env.example`.
4. Click `Generate Full BOM PPTX`.
5. Download the PPTX, Mermaid, and JSON files.

Generated files are saved in:

```text
outputs\generated_boms
```

The app creates these 15 slides:

1. Project Title
2. Requirements / Problem Statement
3. Proposed Solution
4. Technology
5. Process Flow
6. Solution Illustration
7. UI Mockups
8. Benefits
9. Prerequisites
10. Delivery Schedule
11. Customer Scope & Importants
12. Contact Matrix
13. Business Model
14. Terms & Conditions
15. Thank You
fun change