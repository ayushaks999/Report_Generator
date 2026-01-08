#!/usr/bin/env python3
"""
report_generator.py - convenience wrappers and CLI around agent + RAG.

This file imports `generate_report_with_rag` (backwards-compatible wrapper) from agent.py.
"""
from typing import Optional, Dict
import logging
import json
from datetime import datetime
import argparse
import re
import os

# Import the agent wrapper expected by this module
try:
    from agent import generate_report_with_rag, generate_custom_report
except Exception as e:
    raise RuntimeError("Failed to import agent module. Ensure agent.py is present and importable.") from e

# Optional direct RAG preview
try:
    from rag_retrieval import retrieve_combined_data
except Exception:
    retrieve_combined_data = None

# Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# -------------------------
# Report helpers
# -------------------------
def generate_sales_performance_report(region: Optional[str] = None, quarter: Optional[str] = None) -> str:
    query_parts = ["Analyze sales performance"]
    if region:
        query_parts.append(f"in {region}")
    if quarter:
        query_parts.append(f"for {quarter}")
    query = " ".join(query_parts)
    logger.info("Generating sales performance report — Query: %s", query)
    try:
        return generate_report_with_rag(query, report_type="sales", n_results=8)
    except Exception as e:
        logger.exception("Failed to generate sales performance report: %s", e)
        return f"ERROR: Failed to generate report — {e}"


def generate_marketing_campaign_report(channel: Optional[str] = None, quarter: Optional[str] = None) -> str:
    query_parts = ["Analyze marketing campaign performance"]
    if channel:
        query_parts.append(f"for {channel} channel")
    if quarter:
        query_parts.append(f"in {quarter}")
    query = " ".join(query_parts)
    logger.info("Generating marketing campaign report — Query: %s", query)
    try:
        return generate_report_with_rag(query, report_type="marketing", n_results=8)
    except Exception as e:
        logger.exception("Failed to generate marketing campaign report: %s", e)
        return f"ERROR: Failed to generate report — {e}"


def generate_quarterly_summary_report(quarter: str) -> str:
    query = f"Provide a comprehensive summary of sales and marketing performance for {quarter}"
    logger.info("Generating quarterly summary report — Query: %s", query)
    try:
        return generate_report_with_rag(query, report_type="combined", n_results=10)
    except Exception as e:
        logger.exception("Failed to generate quarterly summary report: %s", e)
        return f"ERROR: Failed to generate report — {e}"


def generate_product_analysis_report(product_name: str) -> str:
    query = f"Analyze the performance and marketing of {product_name}"
    logger.info("Generating product analysis report — Query: %s", query)
    try:
        return generate_report_with_rag(query, report_type="combined", n_results=8)
    except Exception as e:
        logger.exception("Failed to generate product analysis report: %s", e)
        return f"ERROR: Failed to generate report — {e}"


def generate_regional_analysis_report(region: str) -> str:
    query = f"Analyze sales and marketing performance in {region}"
    logger.info("Generating regional analysis report — Query: %s", query)
    try:
        return generate_report_with_rag(query, report_type="combined", n_results=8)
    except Exception as e:
        logger.exception("Failed to generate regional analysis report: %s", e)
        return f"ERROR: Failed to generate report — {e}"


def generate_custom_analysis_report(custom_query: str) -> str:
    logger.info("Generating custom analysis report — Query: %s", custom_query)
    try:
        # you can call generate_custom_report if you want single-step behavior
        return generate_report_with_rag(custom_query, report_type="combined", n_results=8)
    except Exception as e:
        logger.exception("Failed to generate custom analysis report: %s", e)
        return f"ERROR: Failed to generate report — {e}"


# -------------------------
# File utilities
# -------------------------
def _sanitize_filename(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    safe = re.sub(r"_+", "_", safe)
    return safe.strip("._")


def save_report_to_file(report: str, filename: Optional[str] = None, folder: Optional[str] = None) -> str:
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.txt"
    basename = _sanitize_filename(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, basename)
    else:
        path = basename
    try:
        with open(path, "w", encoding="utf-8") as f:
            if isinstance(report, (dict, list)):
                json.dump(report, f, indent=2, ensure_ascii=False)
            else:
                f.write(report)
        logger.info("Report saved to: %s", path)
        return path
    except Exception as e:
        logger.exception("Failed to save report to file: %s", e)
        raise


def get_available_report_types() -> Dict[str, str]:
    return {
        "sales_performance": "Sales performance analysis by region/quarter",
        "marketing_campaign": "Marketing campaign performance analysis",
        "quarterly_summary": "Comprehensive quarterly summary",
        "product_analysis": "Product-specific performance analysis",
        "regional_analysis": "Regional sales and marketing analysis",
        "custom": "Custom analysis based on your query",
    }


# -------------------------
# CLI
# -------------------------
def _build_report(args) -> str:
    t = args.type
    if t == "sales_performance":
        return generate_sales_performance_report(region=args.region, quarter=args.quarter)
    if t == "marketing_campaign":
        return generate_marketing_campaign_report(channel=args.channel, quarter=args.quarter)
    if t == "quarterly_summary":
        if not args.quarter:
            raise ValueError("quarter is required for quarterly_summary")
        return generate_quarterly_summary_report(args.quarter)
    if t == "product_analysis":
        if not args.product:
            raise ValueError("product is required for product_analysis")
        return generate_product_analysis_report(args.product)
    if t == "regional_analysis":
        if not args.region:
            raise ValueError("region is required for regional_analysis")
        return generate_regional_analysis_report(args.region)
    if t == "custom":
        if not args.query:
            raise ValueError("query is required for custom report")
        return generate_custom_analysis_report(args.query)
    raise ValueError(f"Unknown report type: {t}")


def _cli():
    p = argparse.ArgumentParser(description="Generate reports using agent + RAG")
    p.add_argument("--type", required=True, choices=list(get_available_report_types().keys()), help="Report type")
    p.add_argument("--region", help="Region (for sales/regional reports)")
    p.add_argument("--quarter", help="Quarter string (e.g. 'Q1 2024')")
    p.add_argument("--channel", help="Marketing channel (for marketing report)")
    p.add_argument("--product", help="Product name (for product analysis)")
    p.add_argument("--query", help="Custom query (for custom report)")
    p.add_argument("--out", help="Output filename (optional)")
    p.add_argument("--out-folder", help="Output folder (optional)")
    args = p.parse_args()

    try:
        report = _build_report(args)
        print("\n" + "=" * 80)
        print("REPORT OUTPUT:")
        print("=" * 80 + "\n")
        print(report)
        # Save if requested
        if args.out or args.out_folder:
            filename = args.out or f"report_{args.type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            saved_path = save_report_to_file(report, filename=filename, folder=args.out_folder)
            print(f"\nSaved report to: {saved_path}")
    except Exception as e:
        logger.exception("Report generation failed: %s", e)
        print("ERROR:", e)


if __name__ == "__main__":
    _cli()