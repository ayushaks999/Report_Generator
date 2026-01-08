# telegram_sender.py
"""
Telegram bot for sending reports and charts.

Usage:
  python telegram_sender.py             -> auto: looks in ./reports/, ./charts/, then current dir; sends files if found, otherwise sends a test message
  python telegram_sender.py --test      -> send only a test message
  python telegram_sender.py --send      -> force send files (scan reports/charts/cwd)
  python telegram_sender.py rpt1.txt rpt2.txt --charts ch1.png ch2.png
"""

import os
import sys
from datetime import datetime
from telethon import TelegramClient, errors
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact

# Load configuration from config.py in same folder
try:
    from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
except Exception as e:
    raise SystemExit(
        "Missing config.py or variables in it. Create config.py with TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE"
    ) from e

SESSION_NAME = "sudhreport123_session"
client = TelegramClient(SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)

# File type heuristics
REPORT_EXTS = {".txt", ".csv", ".pdf", ".xlsx", ".xls", ".docx", ".doc"}
CHART_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


# -------------------------
# Helpers
# -------------------------
def list_files_in_dir(dirpath):
    if not os.path.isdir(dirpath):
        return []
    files = [
        os.path.join(dirpath, f)
        for f in sorted(os.listdir(dirpath))
        if os.path.isfile(os.path.join(dirpath, f))
    ]
    return files


def find_files_auto():
    """
    Priority:
      1) files in ./reports/ and ./charts/
      2) if none, scan cwd for charts and reports by extension
    Returns (reports_list, charts_list)
    """
    reports = list_files_in_dir("reports")
    charts = list_files_in_dir("charts")

    if reports or charts:
        return reports, charts

    # fallback: scan cwd
    cwd_files = [f for f in sorted(os.listdir(".")) if os.path.isfile(f)]
    for f in cwd_files:
        ext = os.path.splitext(f)[1].lower()
        if ext in REPORT_EXTS:
            reports.append(os.path.abspath(f))
        elif ext in CHART_EXTS:
            charts.append(os.path.abspath(f))
    return reports, charts


async def ensure_client_started():
    if not client.is_connected():
        await client.connect()
    if not await client.is_user_authorized():
        await client.start()


async def resolve_entity(phone: str):
    """
    Resolve phone to an entity usable by send_message / send_file.
    If Telethon cannot find it, import the phone as a contact and retry.
    """
    try:
        return await client.get_input_entity(phone)
    except (ValueError, errors.RPCError):
        try:
            contact = InputPhoneContact(client_id=0, phone=phone, first_name="Report", last_name="Recipient")
            await client(ImportContactsRequest([contact]))
            return await client.get_input_entity(phone)
        except Exception as e:
            raise RuntimeError(f"Could not resolve or import contact {phone}: {e}") from e


# -------------------------
# Core message functions
# -------------------------
async def send_header(peer):
    today = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
    header = (
        "📊 **Daily Sales & Marketing Report**\n\n"
        f"Generated: {today}\n"
        "Data: 1000 sales + 1000 marketing records\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await client.send_message(peer, header)


async def send_footer(peer):
    footer = "✅ All reports delivered successfully!\n\n🤖 Powered by AI • Generated with Python + AutoGen + RAG"
    await client.send_message(peer, footer)


async def send_files(peer, reports, charts):
    # send header
    try:
        await send_header(peer)
        print("✓ Sent header")
    except Exception as e:
        print("Header send error:", e)

    # charts
    for chart in charts or []:
        if not chart:
            continue
        if os.path.exists(chart):
            try:
                name = os.path.basename(chart).rsplit(".", 1)[0].replace("_", " ").title()
                await client.send_file(peer, chart, caption=f"📈 {name}")
                print(f"✓ Sent chart: {os.path.basename(chart)}")
            except Exception as e:
                print(f"Error sending chart {chart}: {e}")
        else:
            print(f"Chart not found, skipping: {chart}")

    # reports
    for rpt in reports or []:
        if not rpt:
            continue
        if os.path.exists(rpt):
            try:
                name = os.path.basename(rpt).rsplit(".", 1)[0].replace("_", " ").title()
                await client.send_file(peer, rpt, caption=f"📄 {name}")
                print(f"✓ Sent report: {os.path.basename(rpt)}")
            except Exception as e:
                print(f"Error sending report {rpt}: {e}")
        else:
            print(f"Report not found, skipping: {rpt}")

    # footer
    try:
        await send_footer(peer)
        print("✓ Sent footer")
    except Exception as e:
        print("Footer send error:", e)


async def test_telegram():
    await ensure_client_started()
    try:
        peer = await resolve_entity(TELEGRAM_PHONE)
    except RuntimeError as e:
        print("ERROR: Could not prepare recipient:", e)
        return
    try:
        await client.send_message(peer, "🚀 Test Message from Report System!\n\nIf you see this, Telegram integration is working! ✅")
        print("✅ Test message sent successfully!")
    except Exception as e:
        print("Test message error:", e)


async def send_telegram_reports(reports, charts):
    await ensure_client_started()

    try:
        peer = await resolve_entity(TELEGRAM_PHONE)
    except RuntimeError as e:
        print("ERROR: Could not prepare recipient:", e)
        return

    if (not reports) and (not charts):
        print("No files provided to send.")
        return

    print("\n" + "=" * 60)
    print("SENDING TO TELEGRAM:", TELEGRAM_PHONE)
    print("=" * 60)

    await send_files(peer, reports, charts)
    print("\n✓ All done.\n")


# -------------------------
# CLI parsing & run
# -------------------------
def run_async(coro):
    with client:
        return client.loop.run_until_complete(coro)


def parse_args(argv):
    """
    returns dict: {mode: 'test'|'send', reports: [], charts: []}
    """
    if len(argv) <= 1:
        # auto mode
        reports, charts = find_files_auto()
        if reports or charts:
            return {"mode": "send", "reports": reports, "charts": charts}
        else:
            return {"mode": "test", "reports": [], "charts": []}

    args = argv[1:]
    if "--test" in args:
        return {"mode": "test", "reports": [], "charts": []}
    if "--send" in args:
        reports, charts = find_files_auto()
        return {"mode": "send", "reports": reports, "charts": charts}

    # explicit file listing
    reports = []
    charts = []
    if "--charts" in args:
        i = args.index("--charts")
        reports = [os.path.abspath(p) for p in args[:i]]
        charts = [os.path.abspath(p) for p in args[i + 1 :]]
    else:
        reports = [os.path.abspath(p) for p in args]
    return {"mode": "send", "reports": reports, "charts": charts}


if __name__ == "__main__":
    parsed = parse_args(sys.argv)

    if parsed["mode"] == "test":
        print("Mode: TEST")
        print(f"Target: {TELEGRAM_PHONE}")
        run_async(test_telegram())
    else:
        print("Mode: SEND")
        print(f"Target: {TELEGRAM_PHONE}")
        print(f"Reports found: {len(parsed['reports'])}, Charts found: {len(parsed['charts'])}")
        if parsed["reports"]:
            print("Reports to send:")
            for r in parsed["reports"]:
                print("  ", os.path.basename(r))
        if parsed["charts"]:
            print("Charts to send:")
            for c in parsed["charts"]:
                print("  ", os.path.basename(c))

        run_async(send_telegram_reports(parsed["reports"], parsed["charts"]))
