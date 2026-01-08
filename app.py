# app.py
import streamlit as st
from datetime import datetime
import os
import shutil

# === Project imports (must exist in your repo) ===
from agent import generate_report_with_autogen_multiagent  # optional, keep if used elsewhere
from report_generator import (
    generate_sales_performance_report,
    generate_marketing_campaign_report,
    generate_quarterly_summary_report,
    generate_product_analysis_report,
    generate_regional_analysis_report,
    generate_custom_analysis_report,
    save_report_to_file,
)
import visualizations  # must expose generate_all_charts() -> list of chart file paths
import email_sender_html
import telegram_sender
import config  # optional; contains RECIPIENT_EMAIL, TELEGRAM_PHONE, etc.

# === Streamlit page config ===
st.set_page_config(page_title="AI Sales & Marketing Report Generator", page_icon="📊", layout="wide")
st.title("🤖 AI Sales & Marketing Report Generator")
st.caption("Agentic RAG system powered by AutoGen + GROQ")

# Directories
REPORTS_DIR = "reports"
CHARTS_DIR = "charts"
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# -------------------------
# Sidebar: controls
# -------------------------
st.sidebar.header("📊 Report Controls")
report_type = st.sidebar.selectbox(
    "Select Report Type",
    [
        "Sales Performance",
        "Marketing Campaign",
        "Quarterly Summary",
        "Product Analysis",
        "Regional Analysis",
        "Custom Query",
    ],
)

# Report parameters
region = quarter = channel = product = custom_query = ""
if report_type == "Sales Performance":
    region = st.sidebar.text_input("Region (optional)", "")
    quarter = st.sidebar.text_input("Quarter (e.g. Q1 2024)", "")
elif report_type == "Marketing Campaign":
    channel = st.sidebar.text_input("Channel (e.g. Email, Social)", "")
    quarter = st.sidebar.text_input("Quarter (e.g. Q2 2024)", "")
elif report_type == "Quarterly Summary":
    quarter = st.sidebar.text_input("Quarter (required)", "Q1 2024")
elif report_type == "Product Analysis":
    product = st.sidebar.text_input("Product Name", "")
elif report_type == "Regional Analysis":
    region = st.sidebar.text_input("Region", "")
elif report_type == "Custom Query":
    custom_query = st.sidebar.text_area(
        "Enter your custom analysis question",
        height=120,
        placeholder="Example: Analyze why sales dropped in North America in Q3",
    )

st.sidebar.markdown("---")
st.sidebar.header("📈 Visualization & Delivery")
generate_charts = st.sidebar.checkbox("Generate visualizations (charts)", value=True)
chart_preview = st.sidebar.checkbox("Preview charts after generation", value=True)

# Email toggles
send_email_toggle = st.sidebar.checkbox("Enable email delivery (auto after generation)", value=False)
email_recipient_override = st.sidebar.text_input(
    "Email recipient (optional override)", value=(getattr(config, "RECIPIENT_EMAIL", "") or "")
)

# Telegram toggles
send_telegram_toggle = st.sidebar.checkbox("Enable Telegram delivery (auto after generation)", value=False)
telegram_target_override = st.sidebar.text_input(
    "Telegram phone (override)", value=(getattr(config, "TELEGRAM_PHONE", "") or "")
)

st.sidebar.markdown("---")
generate_btn = st.sidebar.button("🚀 Generate Report")

# -------------------------
# Helper functions
# -------------------------
def _save_text_report(report_text: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.txt"
    path = os.path.join(REPORTS_DIR, filename)
    # save_report_to_file in your module expects (report_text, filename=...) — keep compatibility
    try:
        save_report_to_file(report_text, filename=path)
    except TypeError:
        # fallback: if save_report_to_file expects only a filename and text, write manually
        with open(path, "w", encoding="utf-8") as f:
            f.write(report_text)
    except Exception:
        # last-resort write
        with open(path, "w", encoding="utf-8") as f:
            f.write(report_text)
    return path


def _generate_charts_wrapper() -> list:
    try:
        chart_files = visualizations.generate_all_charts()
        normalized = []
        for p in chart_files:
            abs_p = os.path.abspath(p)
            dest = os.path.join(CHARTS_DIR, os.path.basename(abs_p))
            if os.path.abspath(os.path.dirname(abs_p)) != os.path.abspath(CHARTS_DIR):
                try:
                    shutil.copyfile(abs_p, dest)
                    normalized.append(dest)
                except Exception:
                    normalized.append(abs_p)
            else:
                normalized.append(abs_p)
        return normalized
    except Exception as e:
        st.warning(f"Chart generation failed: {e}")
        return []


def _send_email(report_paths, chart_paths):
    try:
        if email_recipient_override:
            try:
                setattr(config, "RECIPIENT_EMAIL", email_recipient_override)
            except Exception:
                pass
        ok = email_sender_html.send_html_email_with_charts(report_paths, chart_paths)
        if ok:
            st.success("✅ Email sent successfully")
        else:
            st.error("✗ Email did not send successfully (check logs).")
    except Exception as e:
        st.exception(e)
        st.error("✗ Exception while sending email.")


def _send_telegram(report_paths, chart_paths):
    try:
        if telegram_target_override:
            try:
                setattr(config, "TELEGRAM_PHONE", telegram_target_override)
            except Exception:
                pass
        coro = telegram_sender.send_telegram_reports(report_paths, chart_paths)
        st.info("Sending to Telegram (may prompt for first-time login)...")
        with st.spinner("Sending via Telegram..."):
            telegram_sender.run_async(coro)
        st.success("✅ Telegram delivery attempted (check logs).")
    except Exception as e:
        st.exception(e)
        st.error("✗ Exception while sending to Telegram.")


# -------------------------
# Main generate flow (explicit calls)
# -------------------------
if generate_btn:
    with st.spinner("Generating report... this may take a few seconds ⏳"):
        try:
            # Explicitly call correct generator signatures to avoid wrong kwarg names.
            if report_type == "Sales Performance":
                report_text = generate_sales_performance_report(region=region or None, quarter=quarter or None)
            elif report_type == "Marketing Campaign":
                report_text = generate_marketing_campaign_report(channel=channel or None, quarter=quarter or None)
            elif report_type == "Quarterly Summary":
                report_text = generate_quarterly_summary_report(quarter)
            elif report_type == "Product Analysis":
                report_text = generate_product_analysis_report(product)
            elif report_type == "Regional Analysis":
                report_text = generate_regional_analysis_report(region)
            elif report_type == "Custom Query":
                # IMPORTANT: call with positional arg (your function appears to expect the custom query as positional)
                report_text = generate_custom_analysis_report(custom_query)
            else:
                st.error("Invalid report type selected")
                report_text = None

            if not report_text:
                st.error("Report generator returned empty result.")
            else:
                st.success("✅ Report Generated Successfully")
                st.markdown("## 📄 Generated Report")
                st.code(report_text, language="text")

                # Save to file
                saved_report_path = _save_text_report(report_text)
                st.info(f"Saved report to: `{saved_report_path}`")
                st.download_button(
                    label="⬇️ Download Report",
                    data=report_text,
                    file_name=os.path.basename(saved_report_path),
                    mime="text/plain",
                )

                # Generate charts
                chart_files = []
                if generate_charts:
                    with st.spinner("Generating visualizations..."):
                        chart_files = _generate_charts_wrapper()
                        if chart_files:
                            st.success(f"✓ Generated {len(chart_files)} chart(s).")
                        else:
                            st.warning("No charts were generated.")

                # Preview charts
                if chart_preview and chart_files:
                    st.markdown("## 🖼️ Chart Previews")
                    cols = st.columns(2)
                    for i, cf in enumerate(chart_files):
                        try:
                            caption = os.path.basename(cf).rsplit(".", 1)[0].replace("_", " ").title()
                            cols[i % 2].image(cf, caption=caption, use_column_width=True)
                        except Exception as e:
                            st.write(f"Could not render image {cf}: {e}")

                # Let user pick which charts to send
                selected_charts = []
                if chart_files:
                    selected_charts = st.multiselect(
                        "Select charts to attach / send",
                        options=chart_files,
                        default=chart_files,
                        format_func=lambda p: os.path.basename(p),
                    )

                # Delivery buttons
                st.markdown("---")
                st.markdown("### 📬 Delivery")
                col1, col2, col3 = st.columns([1, 1, 2])
                send_email_now = col1.button("📧 Send Email with attachments")
                send_telegram_now = col2.button("💬 Send to Telegram")
                col3.write("Use sidebar toggles to auto-send after generation.")

                if send_email_now:
                    _send_email([saved_report_path], selected_charts)
                if send_telegram_now:
                    _send_telegram([saved_report_path], selected_charts)

                # Auto-send if toggles enabled
                if send_email_toggle:
                    _send_email([saved_report_path], selected_charts)
                if send_telegram_toggle:
                    _send_telegram([saved_report_path], selected_charts)

        except Exception as e:
            st.exception(e)
            st.error("❌ Report generation failed")

# -------------------------
# Footer & recent files
# -------------------------
st.markdown("---")
st.caption("Built by Ayush Kumar Shaw | AutoGen • RAG • GROQ • Streamlit")

def _list_recent(dirpath, n=6):
    if not os.path.isdir(dirpath):
        return []
    files = sorted(
        [os.path.join(dirpath, f) for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))],
        key=os.path.getmtime,
        reverse=True,
    )
    return files[:n]

st.sidebar.markdown("### Recent files")
recent_reports = _list_recent(REPORTS_DIR)
recent_charts = _list_recent(CHARTS_DIR)
if recent_reports:
    st.sidebar.markdown("**Recent Reports**")
    for r in recent_reports:
        st.sidebar.write(os.path.basename(r))
if recent_charts:
    st.sidebar.markdown("**Recent Charts**")
    for c in recent_charts:
        st.sidebar.write(os.path.basename(c))
