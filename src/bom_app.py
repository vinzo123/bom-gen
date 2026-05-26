from __future__ import annotations

from pathlib import Path

from flask import Flask, abort, render_template, request, send_file

from bom_ai import DEFAULT_MAX_TOKENS, MODEL_FALLBACKS, generate_bom_content
from bom_pptx import build_bom_pptx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "generated_boms"

app = Flask(__name__, template_folder=str(PROJECT_ROOT / "templates"))


@app.get("/")
def index():
    return render_template("bom_generator.html", models=MODEL_FALLBACKS, default_max_tokens=DEFAULT_MAX_TOKENS)


@app.post("/generate")
def generate():
    project_code = request.form.get("project_code", "").strip()
    customer_name = request.form.get("customer_name", "").strip()
    solution_name = request.form.get("solution_name", "").strip()
    requirement = request.form.get("requirement", "").strip()
    proposed_solution = request.form.get("proposed_solution", "").strip()
    api_key = request.form.get("api_key", "").strip()
    try:
        max_tokens = int(request.form.get("max_tokens", DEFAULT_MAX_TOKENS))
    except ValueError:
        max_tokens = DEFAULT_MAX_TOKENS
    max_tokens = max(500, min(max_tokens, 4000))

    if not requirement:
        return render_template(
            "bom_generator.html",
            models=MODEL_FALLBACKS,
            default_max_tokens=DEFAULT_MAX_TOKENS,
            error="Please paste the customer requirement before generating the BOM.",
        )

    content, ai_status = generate_bom_content(
        project_code=project_code,
        customer_name=customer_name,
        solution_name=solution_name,
        requirement=requirement,
        proposed_solution=proposed_solution,
        api_key=api_key,
        max_tokens=max_tokens,
    )
    pptx_path, json_path, mmd_path = build_bom_pptx(content, OUTPUT_DIR)

    return render_template(
        "bom_generator.html",
        models=MODEL_FALLBACKS,
        default_max_tokens=max_tokens,
        ai_status=ai_status,
        pptx_name=pptx_path.name,
        json_name=json_path.name,
        mmd_name=mmd_path.name,
    )


@app.get("/download/<path:file_name>")
def download(file_name: str):
    target = (OUTPUT_DIR / file_name).resolve()
    if OUTPUT_DIR.resolve() not in target.parents:
        abort(404)
    if not target.exists():
        abort(404)
    return send_file(target, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
