import re


def clean_node_text(value: str, fallback: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 ()/&-]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:55] or fallback


def guess_domain_steps(text: str, file_name: str) -> list[str]:
    """Create beginner-friendly default steps from PDF name/text keywords."""
    source = f"{file_name}\n{text}".lower()

    if "bin" in source:
        return [
            "User logs in",
            "Scan or select bin",
            "Validate bin and part details",
            "Update bin status",
            "Generate report",
        ]

    if "inventory" in source or "stock" in source:
        return [
            "User logs in",
            "Receive material data",
            "Check stock availability",
            "Update inventory",
            "Generate stock report",
        ]

    if "sales order" in source or "soms" in source or "invoice" in source:
        return [
            "Import sales order",
            "Validate customer and part details",
            "Create invoice",
            "Send e-invoice data",
            "Print or share invoice",
        ]

    if "dispatch" in source or "despatch" in source:
        return [
            "Create dispatch plan",
            "Scan vehicle or trolley",
            "Verify dispatch sequence",
            "Load material",
            "Complete dispatch",
        ]

    if "traceability" in source or "barcode" in source:
        return [
            "Scan barcode",
            "Capture production stage",
            "Validate traceability data",
            "Store transaction",
            "View traceability report",
        ]

    return [
        "Start process",
        "Capture input data",
        "Validate details",
        "Save transaction",
        "Generate output report",
    ]


def build_mermaid_flowchart(text: str, file_name: str) -> str:
    steps = [clean_node_text(step, f"Step {index}") for index, step in enumerate(guess_domain_steps(text, file_name), start=1)]

    lines = [
        "flowchart TD",
        f"    A([Start]) --> B[{steps[0]}]",
    ]

    current_node = "B"
    next_node_ord = ord("C")

    for step in steps[1:]:
        next_node = chr(next_node_ord)
        lines.append(f"    {current_node} --> {next_node}[{step}]")
        current_node = next_node
        next_node_ord += 1

    decision_node = chr(next_node_ord)
    success_node = chr(next_node_ord + 1)
    retry_node = chr(next_node_ord + 2)
    end_node = chr(next_node_ord + 3)

    lines.extend(
        [
            f"    {current_node} --> {decision_node}{{Data valid?}}",
            f"    {decision_node} -- Yes --> {success_node}[Save / Submit]",
            f"    {decision_node} -- No --> {retry_node}[Show error and correct data]",
            f"    {retry_node} --> B",
            f"    {success_node} --> {end_node}([End])",
        ]
    )

    return "\n".join(lines)


def build_html_preview(title: str, mermaid_code: str) -> str:
    escaped_title = title.replace("<", "&lt;").replace(">", "&gt;")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escaped_title}</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f7f7f4;
      color: #202124;
    }}
    main {{
      max-width: 1100px;
      margin: 32px auto;
      padding: 24px;
      background: #ffffff;
      border: 1px solid #deded8;
      border-radius: 8px;
    }}
    h1 {{
      font-size: 22px;
      margin: 0 0 24px;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{escaped_title}</h1>
    <pre class="mermaid">
{mermaid_code}
    </pre>
  </main>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{ startOnLoad: true, theme: "default" }});
  </script>
</body>
</html>
"""

