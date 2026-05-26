from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

MODEL_FALLBACKS = [
    "qwen/qwen3.7-max",
    "openai/gpt-5.2",
    "anthropic/claude-sonnet-4.5",
]
DEFAULT_MAX_TOKENS = 2500


class OpenRouterCreditError(RuntimeError):
    pass


def read_env_file(project_root: Path) -> None:
    env_path = project_root / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def clean_list(value: Any, fallback: list[str], limit: int = 8) -> list[str]:
    if isinstance(value, str):
        parts = [part.strip(" -\t") for part in re.split(r"[\n;]+", value) if part.strip()]
    elif isinstance(value, list):
        parts = [str(part).strip(" -\t") for part in value if str(part).strip()]
    else:
        parts = []

    result = [part[:160] for part in parts if part]
    return (result or fallback)[:limit]


def clean_table(value: Any, fallback: list[list[str]], columns: int) -> list[list[str]]:
    if not isinstance(value, list):
        return fallback

    rows: list[list[str]] = []
    for row in value:
        if isinstance(row, dict):
            items = [str(item).strip() for item in row.values()]
        elif isinstance(row, list):
            items = [str(item).strip() for item in row]
        else:
            continue

        if len(items) < columns:
            items.extend([""] * (columns - len(items)))
        rows.append(items[:columns])

    return rows or fallback


def default_mermaid(process_steps: list[str]) -> str:
    steps = process_steps[:6] or ["Capture Requirement", "Validate Data", "Process Transaction", "Generate Report"]
    node_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    lines = ["flowchart TD", f"    {node_names[0]}([Start]) --> {node_names[1]}[{steps[0]}]"]
    for index, step in enumerate(steps[1:], start=1):
        lines.append(f"    {node_names[index]} --> {node_names[index + 1]}[{step}]")
    final_node = node_names[len(steps)]
    lines.append(f"    {final_node} --> Z([End])")
    return "\n".join(lines)


def keyword_modules(text: str) -> list[str]:
    source = text.lower()
    modules: list[str] = []
    checks = [
        ("Dashboard", ["dashboard", "status", "analytics"]),
        ("Master Data", ["master", "masters"]),
        ("Barcode Scanning", ["barcode", "scan", "scanner"]),
        ("Approval Workflow", ["approval", "approve"]),
        ("Vehicle Mapping", ["vehicle", "truck", "dispatch", "despatch"]),
        ("Mobile Receiving", ["mobile", "receiving", "trolley"]),
        ("Reports", ["report", "mis"]),
        ("Email Alerts", ["mail", "email", "alert"]),
        ("Inventory Tracking", ["inventory", "stock", "bin"]),
        ("Traceability", ["traceability", "tracking"]),
    ]

    for module, words in checks:
        if any(word in source for word in words):
            modules.append(module)

    return modules[:7] or ["Dashboard", "Transactions", "Reports", "Admin Masters"]


def build_fallback_content(
    project_code: str,
    customer_name: str,
    solution_name: str,
    requirement: str,
    proposed_solution: str,
) -> dict[str, Any]:
    source = f"{solution_name} {requirement} {proposed_solution}"
    modules = keyword_modules(source)
    process_steps = [
        "User login",
        "Capture request details",
        "Validate master data",
        "Process transaction",
        "Update dashboard",
        "Generate report",
    ]

    if "approval" in source.lower():
        process_steps.insert(3, "Approval workflow")
    if "barcode" in source.lower() or "scan" in source.lower():
        process_steps.insert(2, "Scan barcode")

    return {
        "project": {
            "project_code": project_code or "#ProjectCode",
            "customer_name": customer_name or "Customer Name",
            "solution_name": solution_name or "Solution Name",
            "solution_full_form": solution_name or "Solution Name",
        },
        "requirements": clean_list(requirement, ["Customer requires an integrated software application."]),
        "proposed_solution": clean_list(proposed_solution, ["ECOSOFT proposes an integrated web-based software solution."]),
        "technology": [
            "Front End: ASP.NET / Web Application",
            "Back End: SQL Server Database",
            "Application Server: IIS",
            "Reports: Dashboard and MIS reports",
            "Device Integration: Barcode scanner / mobile device where applicable",
        ],
        "process_steps": process_steps[:7],
        "process_mermaid": default_mermaid(process_steps),
        "solution_modules": modules,
        "ui_mockups": ["Login", "Dashboard", "Master Entry", "Transaction", "Reports"],
        "benefits": [
            "Real-time visibility of transaction status",
            "Reduced manual paperwork",
            "Improved traceability and accountability",
            "Faster reporting for users and management",
            "Configurable workflow for customer requirements",
        ],
        "prerequisites": [
            ["Server / VM", "Customer to provide required server or VM", "Before installation"],
            ["Network", "Connectivity between client machines, devices, and server", "Customer scope"],
            ["Master Data", "Customer to provide user, item, customer, and process masters", "Before UAT"],
            ["Devices", "Barcode scanners, printers, or mobile devices if applicable", "Customer scope"],
        ],
        "delivery_schedule": [
            ["1", "Requirement freeze and UI confirmation", "Customer + Ecosoft"],
            ["2-3", "Development and internal testing", "Ecosoft"],
            ["4", "UAT support and corrections", "Customer + Ecosoft"],
            ["5", "Deployment and handover", "Ecosoft"],
        ],
        "customer_scope": [
            "Provide finalized process flow and approval matrix",
            "Provide master data in agreed format",
            "Arrange server, network, device, and user access",
            "Complete UAT sign-off within agreed timeline",
        ],
        "contact_matrix": [
            ["Project Owner", "To be discussed", "Customer"],
            ["Process Owner", "To be discussed", "Customer"],
            ["Development Lead", "To be discussed", "Ecosoft"],
            ["Support Contact", "To be discussed", "Ecosoft"],
        ],
        "business_model": [
            "Project commercials, AMC, licenses, and payment milestones to be discussed and finalized separately.",
            "Any additional customization outside agreed scope will be considered as a change request.",
        ],
        "terms_conditions": [
            "Scope will be finalized after requirement sign-off.",
            "Customer will provide required infrastructure, data, and access.",
            "Delivery timeline depends on timely inputs and UAT feedback.",
            "Additional requirements after sign-off will follow change request process.",
        ],
    }


def build_user_prompt(project_code: str, customer_name: str, solution_name: str, requirement: str, proposed_solution: str) -> str:
    return f"""
Create the full BOM presentation content from this customer input.

Project code:
{project_code or "Not provided"}

Customer name:
{customer_name or "Not provided"}

Solution name:
{solution_name or "Not provided"}

Customer requirement:
{requirement}

Proposed solution:
{proposed_solution}

Return this JSON shape exactly:
{{
  "project": {{
    "project_code": "string",
    "customer_name": "string",
    "solution_name": "string",
    "solution_full_form": "string"
  }},
  "requirements": ["bullet", "bullet"],
  "proposed_solution": ["bullet", "bullet"],
  "technology": ["bullet", "bullet"],
  "process_steps": ["short step", "short step"],
  "process_mermaid": "flowchart TD...",
  "solution_modules": ["module", "module"],
  "ui_mockups": ["screen name", "screen name"],
  "benefits": ["bullet", "bullet"],
  "prerequisites": [["Category", "Customer Responsibility", "Remarks"]],
  "delivery_schedule": [["Week", "Activity", "Owner"]],
  "customer_scope": ["bullet", "bullet"],
  "contact_matrix": [["Role", "Name", "Organization"]],
  "business_model": ["bullet", "bullet"],
  "terms_conditions": ["bullet", "bullet"]
}}
""".strip()


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def call_openrouter(
    api_key: str,
    project_code: str,
    customer_name: str,
    solution_name: str,
    requirement: str,
    proposed_solution: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[1]
    system_prompt = (project_root / "prompts" / "bom_system_prompt.md").read_text(encoding="utf-8")

    payload = {
        "models": MODEL_FALLBACKS,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": build_user_prompt(project_code, customer_name, solution_name, requirement, proposed_solution),
            },
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5050",
            "X-Title": "BOM PPTX Generator",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore")
        if exc.code == 402:
            raise OpenRouterCreditError(
                "OpenRouter says this key does not have enough credits or weekly limit for the requested output size."
            ) from exc
        raise RuntimeError(f"OpenRouter HTTP {exc.code}: {details}") from exc

    data = json.loads(raw)
    message = data["choices"][0]["message"]["content"]
    return extract_json(message)


def normalize_content(
    content: dict[str, Any],
    project_code: str,
    customer_name: str,
    solution_name: str,
    requirement: str,
    proposed_solution: str,
) -> dict[str, Any]:
    fallback = build_fallback_content(project_code, customer_name, solution_name, requirement, proposed_solution)
    project = content.get("project") if isinstance(content.get("project"), dict) else {}

    process_steps = clean_list(content.get("process_steps"), fallback["process_steps"], limit=8)
    mermaid = str(content.get("process_mermaid") or "").strip()
    if not mermaid.startswith("flowchart TD"):
        mermaid = default_mermaid(process_steps)

    return {
        "project": {
            "project_code": str(project.get("project_code") or fallback["project"]["project_code"]),
            "customer_name": str(project.get("customer_name") or fallback["project"]["customer_name"]),
            "solution_name": str(project.get("solution_name") or fallback["project"]["solution_name"]),
            "solution_full_form": str(project.get("solution_full_form") or fallback["project"]["solution_full_form"]),
        },
        "requirements": clean_list(content.get("requirements"), fallback["requirements"]),
        "proposed_solution": clean_list(content.get("proposed_solution"), fallback["proposed_solution"]),
        "technology": clean_list(content.get("technology"), fallback["technology"]),
        "process_steps": process_steps,
        "process_mermaid": mermaid,
        "solution_modules": clean_list(content.get("solution_modules"), fallback["solution_modules"], limit=8),
        "ui_mockups": clean_list(content.get("ui_mockups"), fallback["ui_mockups"], limit=8),
        "benefits": clean_list(content.get("benefits"), fallback["benefits"]),
        "prerequisites": clean_table(content.get("prerequisites"), fallback["prerequisites"], 3),
        "delivery_schedule": clean_table(content.get("delivery_schedule"), fallback["delivery_schedule"], 3),
        "customer_scope": clean_list(content.get("customer_scope"), fallback["customer_scope"]),
        "contact_matrix": clean_table(content.get("contact_matrix"), fallback["contact_matrix"], 3),
        "business_model": clean_list(content.get("business_model"), fallback["business_model"]),
        "terms_conditions": clean_list(content.get("terms_conditions"), fallback["terms_conditions"]),
    }


def generate_bom_content(
    project_code: str,
    customer_name: str,
    solution_name: str,
    requirement: str,
    proposed_solution: str,
    api_key: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> tuple[dict[str, Any], str]:
    project_root = Path(__file__).resolve().parents[1]
    read_env_file(project_root)
    resolved_key = (api_key or os.getenv("OPENROUTER_API_KEY") or "").strip()

    if not resolved_key:
        content = build_fallback_content(project_code, customer_name, solution_name, requirement, proposed_solution)
        return normalize_content(content, project_code, customer_name, solution_name, requirement, proposed_solution), "fallback: no OpenRouter key provided"

    try:
        content = call_openrouter(
            resolved_key,
            project_code,
            customer_name,
            solution_name,
            requirement,
            proposed_solution,
            max_tokens=max_tokens,
        )
        status = f"ai: OpenRouter using priority models {', '.join(MODEL_FALLBACKS)}"
    except OpenRouterCreditError:
        content = build_fallback_content(project_code, customer_name, solution_name, requirement, proposed_solution)
        status = (
            "fallback: OpenRouter key has too little credit or weekly limit for full BOM generation. "
            "Generated a local rule-based BOM instead."
        )
    except Exception as exc:
        content = build_fallback_content(project_code, customer_name, solution_name, requirement, proposed_solution)
        status = f"fallback: OpenRouter failed safely. Generated a local rule-based BOM instead. Technical reason: {exc}"

    return normalize_content(content, project_code, customer_name, solution_name, requirement, proposed_solution), status
