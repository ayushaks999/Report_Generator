"""
scheduler.py

Robust Scheduler for automated daily report generation and delivery.

Key behavior:
 - Generates three reports (sales, marketing, executive summary)
 - Saves reports to disk
 - Generates visualizations (PNG files)
 - Sends an HTML email with charts & attachments
 - Sends files to Telegram (tries several common function names and both sync/async)
 - Two run modes:
     python scheduler.py         -> runs scheduler (daily at SCHEDULE_TIME)
     python scheduler.py now     -> runs the full pipeline once immediately (for testing)
"""

import os
import time
import importlib
import asyncio
from datetime import datetime
import schedule
import pytz
import sys

# Project imports (these must exist in your project)
from config import SCHEDULE_TIME, TIMEZONE, RECIPIENT_EMAIL
from report_generator import (
    generate_sales_performance_report,
    generate_marketing_campaign_report,
    generate_quarterly_summary_report,
    save_report_to_file,
)
from email_sender_html import send_html_email_with_charts
from visualizations import generate_all_charts

# Try to import telegram_sender dynamically (may expose different function names)
try:
    telegram_sender = importlib.import_module("telegram_sender")
except Exception as e:
    print(f"[scheduler] Warning: could not import telegram_sender module: {e}")
    telegram_sender = None


def _call_telegram_send(report_files, chart_files):
    """
    Try to call a Telegram send function exported by telegram_sender module.
    Supports multiple candidate function names and both sync/async functions.
    Returns True if any send call succeeded, otherwise False.
    """
    if telegram_sender is None:
        print("[scheduler] telegram_sender not available; skipping Telegram delivery.")
        return False

    candidate_names = [
        "send_to_telegram",        # original sync wrapper
        "send_telegram_reports",   # alternate name (could be async)
        "send_files",              # generic
        "send_telegram",           # another possibility
        "send",                    # minimal
    ]

    for name in candidate_names:
        fn = getattr(telegram_sender, name, None)
        if fn is None:
            continue

        try:
            # If it's a coroutine function, run it via asyncio.run
            if asyncio.iscoroutinefunction(fn):
                print(f"[scheduler] Calling async telegram function: {name}()")
                asyncio.run(fn(report_files, chart_files))
            else:
                # Call sync function. It might return a coroutine (some wrappers do) -> handle that.
                print(f"[scheduler] Calling sync telegram function: {name}()")
                result = fn(report_files, chart_files)
                if asyncio.iscoroutine(result):
                    asyncio.run(result)
            return True
        except Exception as ex:
            print(f"[scheduler] Telegram function '{name}' failed with error: {ex}")
            # try next candidate
            continue

    print("[scheduler] No working Telegram send function found in telegram_sender module.")
    return False


def _ensure_folder(path):
    """Create directory if it doesn't exist and return absolute path."""
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


def generate_and_send_daily_reports():
    """Full pipeline: generate reports, charts, email, and Telegram"""
    try:
        tz = pytz.timezone(TIMEZONE)
    except Exception:
        tz = pytz.utc

    now = datetime.now(tz)
    timestamp = now.strftime("%Y%m%d")
    print("\n" + "=" * 80)
    print(f"GENERATING DAILY REPORTS - {now.strftime('%B %d, %Y %I:%M %p %Z')}")
    print("=" * 80)

    # Ensure folders
    reports_dir = _ensure_folder("reports")
    charts_dir = _ensure_folder("charts")

    report_files = []

    try:
        # 1) Sales report
        print("\n[1/3] Generating Sales Performance Report...")
        sales_report = generate_sales_performance_report()
        sales_file = os.path.join(reports_dir, f"daily_sales_report_{timestamp}.txt")
        save_report_to_file(sales_report, sales_file)
        report_files.append(os.path.abspath(sales_file))
        print(f"✓ Saved: {sales_file}")

        # 2) Marketing report
        print("\n[2/3] Generating Marketing Campaign Report...")
        marketing_report = generate_marketing_campaign_report()
        marketing_file = os.path.join(reports_dir, f"daily_marketing_report_{timestamp}.txt")
        save_report_to_file(marketing_report, marketing_file)
        report_files.append(os.path.abspath(marketing_file))
        print(f"✓ Saved: {marketing_file}")

        # 3) Executive summary
        print("\n[3/3] Generating Executive Summary...")
        summary_report = generate_quarterly_summary_report("Q3 2024")
        summary_file = os.path.join(reports_dir, f"daily_executive_summary_{timestamp}.txt")
        save_report_to_file(summary_report, summary_file)
        report_files.append(os.path.abspath(summary_file))
        print(f"✓ Saved: {summary_file}")

        print("\n" + "=" * 80)
        print("REPORTS GENERATED SUCCESSFULLY")
        print("=" * 80)

        # Generate visualizations (should save into charts_dir or return file list)
        print("\n" + "=" * 80)
        print("GENERATING VISUALIZATIONS")
        print("=" * 80)
        # Some implementations of generate_all_charts() save to cwd and return list.
        chart_files = generate_all_charts() or []
        # If generate_all_charts created files in current dir, move them to charts_dir (optional)
        # We'll convert to absolute paths and ensure they exist; don't move files automatically.
        chart_files = [os.path.abspath(c) for c in chart_files if os.path.exists(c)]
        if not chart_files:
            print("[scheduler] No charts found/returned by generate_all_charts().")
        else:
            print(f"[scheduler] Charts generated: {len(chart_files)}")

        # Send email
        print("\n" + "=" * 80)
        print("SENDING BEAUTIFUL HTML EMAIL WITH CHARTS")
        print("=" * 80)
        try:
            email_ok = send_html_email_with_charts(report_files, chart_files)
            if email_ok:
                print("\n✓ Email sent successfully!")
            else:
                print("\n[scheduler] Warning: send_html_email_with_charts returned False/None.")
        except Exception as e:
            print(f"\n✗ Error sending email: {e}")

        # Send to Telegram (best-effort)
        print("\n" + "=" * 80)
        print("SENDING TO TELEGRAM (if configured)...")
        print("=" * 80)
        try:
            tg_ok = _call_telegram_send(report_files, chart_files)
            if tg_ok:
                print("\n✓ Telegram sent successfully!")
            else:
                print("\n✗ Telegram delivery not completed.")
        except Exception as ex:
            print(f"\n✗ Telegram error: {ex}")

        print("\n" + "=" * 80)
        return True

    except Exception as main_ex:
        print(f"\n✗ Error generating reports: {main_ex}")
        return False


def start_scheduler():
    """Run schedule every day at SCHEDULE_TIME in TIMEZONE"""
    print("\n" + "=" * 80)
    print("AUTOMATED REPORT SCHEDULER")
    print("=" * 80)
    print(f"Scheduled Time: {SCHEDULE_TIME} ({TIMEZONE})")
    print(f"Recipient: {RECIPIENT_EMAIL}")
    try:
        tz = pytz.timezone(TIMEZONE)
        print(f"Current Time: {datetime.now(tz).strftime('%I:%M %p %Z')}")
    except Exception:
        print("Current Time: (could not localize timezone)")

    print("\nScheduler is running... Press Ctrl+C to stop.")
    print("=" * 80)

    schedule.every().day.at(SCHEDULE_TIME).do(generate_and_send_daily_reports)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user.")


def run_now():
    """Run the whole pipeline once immediately (testing)"""
    print("\nRunning report generation NOW (test mode)...\n")
    generate_and_send_daily_reports()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "now":
        run_now()
    else:
        start_scheduler()
