"""
PDF Report Generator for Smart AI Safety Guard.
Uses fpdf2 to produce professional, audit-ready safety reports with
clean visual styling, executive summaries, and risk breakdowns.
"""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
from fpdf import FPDF


def sanitize_text_for_pdf(text: Any) -> str:
    """
    Sanitizes arbitrary text to ensure safe encoding in standard FPDF Helvetica font (Latin-1).
    Replaces common Unicode punctuation and symbols with ASCII equivalents.
    """
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
        "\u2022": "*",
        "\u2192": "->",
        "\u2190": "<-",
        "\u2713": "[PASS]",
        "\u2717": "[FAIL]",
        "\u26a0": "[WARN]",
        "\u00a0": " ",
        "\t": "    ",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    # Strip any remaining characters outside latin-1
    return s.encode("latin-1", errors="replace").decode("latin-1")


class SafetyReportPDF(FPDF):
    """Custom FPDF class with styled header and footer."""
    def __init__(self, title_text: str = "Smart AI Safety Guard Report"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = title_text
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Header banner
        self.set_fill_color(15, 23, 42)  # Dark slate
        self.rect(0, 0, 210, 20, "F")
        self.set_font("helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(190, 10, sanitize_text_for_pdf(self.report_title), 0, 0, "L")
        self.ln(18)

    def footer(self):
        self.set_y(-12)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        page_str = f"Page {self.page_no()} | Smart AI Safety Guard Audit Report"
        self.cell(0, 8, sanitize_text_for_pdf(page_str), 0, 0, "C")


def generate_single_analysis_pdf(data: Dict[str, Any]) -> bytes:
    """
    Generates a single-page or multi-page executive safety evaluation PDF for an individual prompt/response check.
    """
    pdf = SafetyReportPDF("Smart AI Safety Guard - Safety Analysis Report")
    pdf.add_page()

    # Title & Metadata Card
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "AI Content Safety Verification", ln=True)

    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(100, 116, 139)
    timestamp = data.get("Timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 5, sanitize_text_for_pdf(f"Report Generated: {timestamp} | Mode: Explainable Heuristic Guard"), ln=True)
    pdf.ln(4)

    # Status Badge / Banner Box
    status = data.get("status", data.get("Status", "Unknown"))
    risk_score = float(data.get("risk_score", data.get("Risk_Score", 0.0)))
    category = data.get("category", data.get("Category", "General"))
    confidence = data.get("confidence", data.get("Confidence", "Medium"))

    # Color coding
    if status == "Safe":
        pdf.set_fill_color(220, 252, 231)  # Soft green
        pdf.set_text_color(22, 101, 52)     # Dark green
        badge_text = f"SAFETY VERDICT: {status.upper()} (Risk Score: {risk_score:.2f})"
    elif status == "Unsafe":
        pdf.set_fill_color(254, 226, 226)  # Soft red
        pdf.set_text_color(153, 27, 27)    # Dark red
        badge_text = f"SAFETY VERDICT: {status.upper()} (Risk Score: {risk_score:.2f} - High Risk)"
    else:
        pdf.set_fill_color(254, 243, 199)  # Soft amber
        pdf.set_text_color(146, 64, 14)    # Dark amber
        badge_text = f"SAFETY VERDICT: {status.upper()} (Risk Score: {risk_score:.2f} - Caution)"

    pdf.set_font("helvetica", "B", 11)
    pdf.cell(190, 9, sanitize_text_for_pdf(badge_text), border=1, ln=True, align="C", fill=True)
    pdf.ln(4)

    # Key Metrics Grid
    pdf.set_text_color(30, 41, 59)
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(47, 7, "Risk Score", border=1, fill=True)
    pdf.cell(47, 7, "Safety Category", border=1, fill=True)
    pdf.cell(47, 7, "Confidence Level", border=1, fill=True)
    pdf.cell(49, 7, "Compliance State", border=1, fill=True, ln=True)

    pdf.set_font("helvetica", "", 9)
    pdf.cell(47, 7, f"{risk_score * 100:.0f}%", border=1)
    pdf.cell(47, 7, sanitize_text_for_pdf(category[:25]), border=1)
    pdf.cell(47, 7, sanitize_text_for_pdf(str(confidence)), border=1)
    pdf.cell(49, 7, "Compliant" if status == "Safe" else "Requires Review", border=1, ln=True)
    pdf.ln(5)

    # Section 1: Analyzed Prompt (if present)
    prompt_text = data.get("prompt") or data.get("Prompt") or ""
    if prompt_text:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 6, "Input Prompt:", ln=True)
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(51, 65, 85)
        pdf.set_fill_color(248, 250, 252)
        pdf.multi_cell(190, 5, sanitize_text_for_pdf(prompt_text), border=1, fill=True)
        pdf.ln(3)

    # Section 2: Analyzed Response Text
    response_text = data.get("response_text") or data.get("Response_Text") or data.get("AI_Response") or ""
    if response_text:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 6, "AI Output / Content Analyzed:", ln=True)
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(51, 65, 85)
        pdf.set_fill_color(248, 250, 252)
        pdf.multi_cell(190, 5, sanitize_text_for_pdf(response_text), border=1, fill=True)
        pdf.ln(3)

    # Section 3: Safety Findings & Explanation
    warning = data.get("warning") or data.get("Warning") or ""
    if warning:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(180, 40, 40)
        pdf.cell(0, 6, sanitize_text_for_pdf(f"Warning: {warning}"), ln=True)
        pdf.ln(2)

    reasons = data.get("reasons") or data.get("Reasons") or []
    if isinstance(reasons, str):
        reasons = [r.strip() for r in reasons.split(";") if r.strip()]

    if reasons:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 6, "Explainability Breakdown & Flagged Triggers:", ln=True)
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(71, 85, 105)
        for r in reasons:
            pdf.multi_cell(190, 4.5, sanitize_text_for_pdf(f"- {r}"))
        pdf.ln(2)

    # Section 4: Recommended Remediation
    remediation = data.get("remediation")
    if not remediation:
        if status == "Safe":
            remediation = "Text is compliant with standard safety guidelines. No intervention needed."
        elif status == "Suspicious":
            remediation = "Flag for manual auditor review before user presentation or automated API execution."
        elif status == "Potentially Unsafe":
            remediation = "Block automated display. Enforce system prompt boundary or trigger verification."
        else:
            remediation = "Immediate refusal required. Do not echo hazardous or adversarial content."

    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "Remediation Guidance:", ln=True)
    pdf.set_font("helvetica", "I", 9)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(190, 5, sanitize_text_for_pdf(remediation), border=1)
    pdf.ln(4)

    # Disclaimer note
    pdf.set_font("helvetica", "I", 7.5)
    pdf.set_text_color(148, 163, 184)
    pdf.multi_cell(190, 4, sanitize_text_for_pdf(
        "Notice: This report is an automated diagnostic assessment generated by the Smart AI Safety Guard engine. "
        "Intended for audit, compliance monitoring, and continuous integration evaluation."
    ))

    return bytes(pdf.output())


def generate_audit_report_pdf(metrics: Dict[str, Any], test_history_df: pd.DataFrame) -> bytes:
    """
    Generates a multi-page audit report summarizing total executions,
    safety breakdown, pass/fail metrics, and recent test results.
    """
    pdf = SafetyReportPDF("Smart AI Safety Guard - Executive Audit Report")
    pdf.add_page()

    # Title & Metadata
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "AI Safety & Testing Executive Audit", ln=True)

    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(100, 116, 139)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 5, sanitize_text_for_pdf(f"Audit Timestamp: {now_str} | Generated by: Smart AI Safety Guard Engine"), ln=True)
    pdf.ln(5)

    # KPI Metrics Table
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(47, 7, "Total Test Executions", border=1, fill=True)
    pdf.cell(47, 7, "Pass Rate", border=1, fill=True)
    pdf.cell(47, 7, "Unsafe Flagged", border=1, fill=True)
    pdf.cell(49, 7, "Safe Verified", border=1, fill=True, ln=True)

    total_exec = metrics.get("total_executions", 0)
    passed = metrics.get("passed", 0)
    failed = metrics.get("failed", 0)
    pass_rate = f"{(passed / total_exec * 100):.1f}%" if total_exec > 0 else "N/A"
    unsafe_cnt = metrics.get("unsafe_count", 0)
    safe_cnt = metrics.get("safe_count", 0)

    pdf.set_font("helvetica", "", 9)
    pdf.cell(47, 7, str(total_exec), border=1)
    pdf.cell(47, 7, pass_rate, border=1)
    pdf.cell(47, 7, str(unsafe_cnt), border=1)
    pdf.cell(49, 7, str(safe_cnt), border=1, ln=True)
    pdf.ln(6)

    # Test Outcomes Breakdown
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "Execution Verdict Summary", ln=True)
    pdf.set_font("helvetica", "", 9)
    pdf.cell(63, 6, f"Passed Tests: {passed}", border=1)
    pdf.cell(63, 6, f"Failed Tests: {failed}", border=1)
    pdf.cell(64, 6, f"Suspicious Flags: {metrics.get('suspicious', 0)}", border=1, ln=True)
    pdf.ln(6)

    # Detailed Results Table (top 20 entries)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 6, "Recent Test Records (Top 20)", ln=True)

    if not test_history_df.empty:
        pdf.set_font("helvetica", "B", 8)
        pdf.set_fill_color(241, 245, 249)
        pdf.cell(20, 6, "Test ID", border=1, fill=True)
        pdf.cell(38, 6, "Category", border=1, fill=True)
        pdf.cell(68, 6, "Prompt Excerpt", border=1, fill=True)
        pdf.cell(24, 6, "Expected", border=1, fill=True)
        pdf.cell(24, 6, "Actual", border=1, fill=True)
        pdf.cell(16, 6, "Status", border=1, fill=True, ln=True)

        pdf.set_font("helvetica", "", 7.5)
        records = test_history_df.head(20).to_dict(orient="records")
        for r in records:
            test_id = str(r.get("Test_ID", ""))[:10]
            cat = str(r.get("Test_Category", r.get("Category", "")))[:20]
            prompt = str(r.get("Prompt", ""))[:42]
            exp = str(r.get("Expected_Result", ""))[:12]
            act = str(r.get("Actual_Result", r.get("Actual_Safety_Status", "")))[:12]
            status = str(r.get("Test_Status", ""))[:8]

            # Highlight fails
            if status == "FAIL":
                pdf.set_text_color(180, 20, 20)
            elif status == "PASS":
                pdf.set_text_color(20, 120, 40)
            else:
                pdf.set_text_color(50, 50, 50)

            pdf.cell(20, 5.5, sanitize_text_for_pdf(test_id), border=1)
            pdf.cell(38, 5.5, sanitize_text_for_pdf(cat), border=1)
            pdf.cell(68, 5.5, sanitize_text_for_pdf(prompt), border=1)
            pdf.cell(24, 5.5, sanitize_text_for_pdf(exp), border=1)
            pdf.cell(24, 5.5, sanitize_text_for_pdf(act), border=1)
            pdf.cell(16, 5.5, sanitize_text_for_pdf(status), border=1, ln=True)

        pdf.set_text_color(30, 41, 59)
    else:
        pdf.set_font("helvetica", "I", 9)
        pdf.cell(0, 6, "No test execution records found in database.", ln=True)

    pdf.ln(6)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(190, 4, sanitize_text_for_pdf(
        "Confidentiality & Compliance Note: This audit report was compiled from recorded SQLite database entries. "
        "Review safety gaps with engineering teams to adjust prompt injection safeguards and classification heuristics."
    ))

    return bytes(pdf.output())
