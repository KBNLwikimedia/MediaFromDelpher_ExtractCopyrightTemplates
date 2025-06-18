"""
📊 Delpher Copyright Template Visualization Script (Datawrapper Integration)

This Python module processes an Excel dataset of Wikimedia Commons media files sourced from Delpher,
analyzes the usage of copyright templates, and visualizes the results using the Datawrapper API.

Core Features:
--------------
- Reads metadata from an Excel file in the /data directory
- Counts how often each copyright template appears
- Merges template metadata (TemplateURL, NoCopyrightReason)
- Outputs a formatted summary DataFrame, optionally saved to CSV
- Computes key usage statistics (e.g., most used template, unique file counts)
- Loads chart configuration from a JSON file in /scripts/
- Replaces placeholder variables in the config with live stats (e.g., {total_template_usages})
- Uploads the summary to Datawrapper (no need to save a CSV)
- Updates and publishes a chart, returning the responsive embed code

Directory Structure:
--------------------
project-root/
├── data/
│   └── Excel input file + optional output CSV
├── scripts/
│   ├── this script
│   ├── template_usage_summary-config.json  (chart settings)
│   └── .env                                (contains DW_API_TOKEN)

Modules Used:
-------------
- `pandas` for data manipulation
- `pathlib` for cross-platform path handling
- `dotenv` to load secure API keys
- `datawrapper` for API interaction with https://app.datawrapper.de
- `json` for configuration injection

Chart Output:
-------------
✅ Chart is updated and published on Datawrapper.
📎 Responsive embed code is printed to console for easy reuse.

Example Chart:
--------------
https://www.datawrapper.de/_/UewJt/

Author:
-------
Olaf Janssen, Wikimedia-coördinator @KB, National Library of the Netherlands
📅 Last updated: 23 April 2025
🤖 With assistance from ChatGPT (OpenAI)
📜 License: CC0 / Public domain — reuse freely
🔗 User-Agent: OlafJanssenBot/1.0
"""

import os
from datawrapper import Datawrapper #https://datawrapper.readthedocs.io/en/latest/user-guide/api.html
from dotenv import load_dotenv
import pandas as pd
import json
from pathlib import Path
from typing import Tuple

def count_template_usages(
    excel_path: str,
    sheet_name: str,
    output_csv: str = None
) -> Tuple[pd.DataFrame, dict]:
    """
    Summarize the usage of copyright templates from an Excel dataset.

    This function analyzes how often each copyright template is applied across
    Wikimedia Commons media files, based on data extracted from an Excel sheet.

    It performs the following tasks:
    - Counts how many files use each unique copyright template.
    - Builds a summary table with:
        - Template name (HTML-formatted as a clickable link),
        - Number of times this template was used,
        - Corresponding Template URL,
        - Reason for no copyright (NoCopyrightReason).
    - Sorts the output first by NoCopyrightReason (A–Z), then by template usage (highest first).
    - Optionally saves the summary table as a CSV file for use in Datawrapper charts.
    - Computes key usage statistics (e.g., total templates used, number of unique files).

    Parameters:
        excel_path (str): Path to the Excel file containing the data.
        sheet_name (str): Name of the sheet within the Excel file that contains the template usage data.
        output_csv (str, optional): File path for saving the summary CSV. If None, no file is saved.

    Returns:
        Tuple[pd.DataFrame, dict]:
            - summary_df (pd.DataFrame): A table summarizing template usage,
              including template name (HTML link), usage count, URL, and reason.
            - stats (dict): Dictionary of key usage figures, such as:
                - total_template_usages (int)
                - unique_templates_used (int)
                - total_files_with_templates (int)
                - total_unique_files (int)
                - most_used_template (str)

    Raises:
        ValueError: If required columns are missing from the input Excel file.
        Other exceptions are caught internally and will print an error message.

    """

    try:
        # Load the data
        df = pd.read_excel(excel_path, sheet_name=sheet_name)

        # Check required columns
        required_cols = {"Template", "TemplateURL", "NoCopyrightReason", "FileMid", "FileURL"}
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required column(s): {', '.join(missing_cols)}")

        # Clean string-type columns
        df["Template"] = df["Template"].astype(str).str.strip()
        df["TemplateURL"] = df["TemplateURL"].astype(str).str.strip()
        df["NoCopyrightReason"] = df["NoCopyrightReason"].astype(str).str.strip()

        # Calculate the number of files using each template
        usage_counts = df["Template"].value_counts().reset_index()
        usage_counts.columns = ["Template", "Number of times this template is used"]

        # Merge counts with TemplateURL and NoCopyrightReason (remove duplicates first)
        summary = usage_counts.merge(
            df[["Template", "TemplateURL", "NoCopyrightReason"]].drop_duplicates(subset=["Template"]),
            on="Template",
            how="left"
        )

        # Format Template as an HTML link for Datawrapper
        summary["Template"] = summary.apply(
            lambda row: (
                f'<a href="{row["TemplateURL"]}" style="color:#b1bfc3;" target="_blank" rel="nofollow noopener">{row["Template"].strip("{}")}</a>'
                if pd.notnull(row["TemplateURL"]) and row["TemplateURL"] != "" else row["Template"]
            ),
            axis=1
        )

        # Sort summary: first by NoCopyrightReason (A–Z), then by Number of files (desc)
        summary = summary.sort_values(
            by=["NoCopyrightReason", "Number of times this template is used"],
            ascending=[True, False]
        )

        # Export CSV if requested
        if output_csv:
            try:
                summary.to_csv(output_csv, index=False, encoding="utf-8", sep=";")
                print(f"✅ Template usage summary saved to: {output_csv}")
            except Exception as e:
                print(f"⚠️ Failed to save CSV: {e}")

        # Generate key statistics
        stats = generate_template_stats(df, summary)

        return summary, stats

    except Exception as e:
        print(f"❌ Error in count_template_usages(): {e}")
        return pd.DataFrame(), {}


def generate_template_stats(df: pd.DataFrame, summary: pd.DataFrame) -> dict:
    """
    Generate key usage statistics from the copyright template dataset.

    This function calculates important summary statistics based on:
    - The number of times each template is used across files,
    - The number of unique templates,
    - The number of unique media files (using either FileURL or FileMid),
    - The most frequently used template and its count.

    The function expects:
    - The full input dataset (`df`) containing detailed template usage per file,
    - The summary table (`summary`) containing pre-calculated template usage counts
      under the column 'Number of files using this template'.

    The results are printed in a human-readable format and returned as a dictionary
    for further use (e.g., formatting chart descriptions or annotations).

    Parameters:
        df (pd.DataFrame): The original full dataframe from Excel.
            Required columns: 'Template', 'FileMid', 'FileURL'.
        summary (pd.DataFrame): The summary table with template usage counts.
            Required column: 'Number of files using this template'.

    Returns:
        dict: A dictionary containing the following usage statistics:
            - total_template_usages (int): Total count of template usages (sum across all templates).
            - unique_templates_used (int): Number of unique templates used.
            - total_files_with_templates (int): Number of unique FileURL values (media files with at least one template).
            - total_unique_files (int): Number of unique FileMid values.
            - most_used_template (str): The template with the highest number of file usages (HTML-formatted label).
            - most_used_template_count (int): The usage count for the most-used template.

    Raises:
        ValueError: If required columns are missing from either the full data or the summary table.
    """

    try:
        # Check for required columns
        required_cols_df = {"Template", "FileMid", "FileURL"}
        missing_cols_df = required_cols_df - set(df.columns)
        if missing_cols_df:
            raise ValueError(f"Missing required column(s) in the main data: {', '.join(missing_cols_df)}")

        if "Number of times this template is used" not in summary.columns:
            raise ValueError("Summary data is missing 'Number of times this template is used' column.")

        # Use the provided summary table for the counts
        total_template_usages = summary["Number of times this template is used"].sum()
        unique_templates_used = df["Template"].nunique()
        total_files_with_templates = df["FileURL"].nunique()
        total_unique_files = df["FileMid"].nunique()
        most_used_template = summary.iloc[0]["Template"]
        most_used_template_count = summary.iloc[0]["Number of times this template is used"]

        stats = {
            "total_template_usages": total_template_usages,
            "unique_templates_used": unique_templates_used,
            "total_files_with_templates": total_files_with_templates,
            "total_unique_files": total_unique_files,
            "most_used_template": most_used_template,
            "most_used_template_count": most_used_template_count
        }

        # Pretty print for logging
        print("\n📊 Key Figures:")
        print(f"• Total template usages (sum of template counts): {total_template_usages:,}")
        print(f"• Unique templates used: {unique_templates_used}")
        print(f"• Unique files with templates (based on FileURL): {total_files_with_templates:,}")
        print(f"• Unique files with templates (based on FileMid): {total_unique_files:,}")
        print(f"• Most used template: {most_used_template} ({most_used_template_count:,} uses)")

        return stats

    except Exception as e:
        print(f"❌ Failed to generate key stats: {e}")
        return {}


def update_and_publish_chart(
    dw: Datawrapper,
    chart_id: str,
    data: pd.DataFrame,
    config: dict
) -> None:
    """
    Uploads data, updates metadata and description, and publishes the chart.

    This function no longer depends on reading a CSV from disk.
    Instead, it expects a pandas DataFrame directly as input.

    Parameters:
        dw (Datawrapper): Datawrapper API instance.
        chart_id (str): ID of the chart to update.
        data (pd.DataFrame): DataFrame containing the chart data.
        config (dict): Chart configuration loaded from a JSON file.

    Raises:
        Exception: Any errors that occur during the update or publishing process.
    """
    try:
        # Upload data directly from DataFrame
        dw.add_data(chart_id=chart_id, data=data)

        # Extract chart title
        title = config.get("title", "Untitled Datawrapper Chart")

        # Apply chart metadata
        dw.update_chart(
            chart_id=chart_id,
            title=title,
            metadata={
                "visualize": config.get("visualize", {}),
                "annotate": config.get("annotate", {}),
                "publish": config.get("publish", {})
            }
        )

        # Apply textual description (description block)
        desc = config.get("description", {})
        dw.update_description(
            chart_id=chart_id,
            intro=desc.get("intro", ""),
            byline=desc.get("byline", ""),
            source_name=desc.get("source-name", ""),
            source_url=desc.get("source-url", ""),
            aria_description=desc.get("aria-description", "")
        )

        # Publish chart
        dw.publish_chart(chart_id=chart_id)
        print(f"🚀 Chart '{title}' updated and published successfully.")

    except Exception as e:
        print(f"❌ Error during chart update: {e}")


def load_config(path: Path) -> dict:
    """Load and return the chart configuration from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load chart config from {path}: {e}")


def apply_stats_to_config(config: dict, stats: dict) -> None:
    """Format and insert statistics into chart config placeholders."""
    for section in ["description", "annotate"]:
        if section in config:
            config[section] = {
                k: (v.format(**stats) if isinstance(v, str) else v)
                for k, v in config[section].items()
            }

    # Handle embedded text annotations
    if "visualize" in config and "text-annotations" in config["visualize"]:
        config["visualize"]["text-annotations"] = [
            {k: (v.format(**stats) if isinstance(v, str) else v) for k, v in annotation.items()}
            for annotation in config["visualize"]["text-annotations"]
        ]

def get_chart_visualize_config(dw: Datawrapper, chart_id: str) -> dict:
    """
    Fetch the 'visualize' metadata configuration section of a Datawrapper chart.

    Parameters:
        dw (Datawrapper): An instance of the Datawrapper API client.
        chart_id (str): The ID of the chart whose configuration you want to fetch.

    Returns:
        dict: The 'visualize' configuration section of the chart metadata.

    Raises:
        RuntimeError: If the chart metadata could not be retrieved or if 'visualize' section is missing.
    """
    try:
        chart_metadata = dw.get_chart(chart_id=chart_id)
        visualize_config = chart_metadata.get("metadata", {}).get("visualize", {})

        if not visualize_config:
            raise RuntimeError(f"'visualize' section not found in chart metadata for chart ID '{chart_id}'.")

        return visualize_config

    except Exception as e:
        raise RuntimeError(f"Failed to retrieve 'visualize' config for chart '{chart_id}': {e}")

def get_responsive_embed_code(dw, chart_id: str) -> str | None:
    """
    Fetch the responsive iframe embed code for a published Datawrapper chart.

    Parameters:
        dw (Datawrapper): An instance of the Datawrapper API client.
        chart_id (str): The public or internal ID of the Datawrapper chart.

    Returns:
        str | None: The responsive embed code if available, or None if not found or an error occurred.
    """
    try:
        chart_info = dw.get_chart(chart_id)
        embed_codes = chart_info.get("metadata", {}).get("publish", {}).get("embed-codes", {})
        script_embed = embed_codes.get("embed-method-web-component", None)

        if script_embed:
            return script_embed
        else:
            print("❌ Script embed code not found. Make sure the chart is published.")
            return None

    except Exception as e:
        print(f"❌ Error retrieving embed code: {e}")
        return None


def main():
    """
    Main pipeline to process Excel data, generate summary stats,
    update a Datawrapper chart, and print the responsive embed code.
    """
    try:
        # Load environment variables
        load_dotenv()
        DW_API_TOKEN = os.getenv("DW_API_TOKEN")
        if not DW_API_TOKEN:
            raise ValueError("DW_API_TOKEN not found in .env file!")

        # Define paths
        ROOT_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = ROOT_DIR / "data"
        SCRIPT_DIR = Path(__file__).resolve().parent

        EXCEL_PATH = DATA_DIR / "Media_from_Delpher-Extracted_copyright_templates-09042025-cleaned-processed.xlsx"
        EXCEL_SHEET = "files-templates"
        CONFIG_PATH = SCRIPT_DIR / "template-usage-summary-config.json"
        CHART_ID = "UewJt"

        # Load chart config
        config = load_config(CONFIG_PATH)

        # Authenticate Datawrapper client
        dw = Datawrapper(access_token=DW_API_TOKEN)

        # === Print existing chart metadata, visualize part ===
        try:
            visualize_config = get_chart_visualize_config(dw, CHART_ID)
            print(json.dumps(visualize_config, indent=2))
        except Exception as e:
            print(e)

        # Generate summary and stats
        summary_df, stats = count_template_usages(
            excel_path=EXCEL_PATH,
            sheet_name=EXCEL_SHEET
        )

        if summary_df.empty:
            raise RuntimeError("Summary DataFrame is empty. Chart will not be updated.")

        print("\n📊 Key stats:", stats)

        # Inject stats into config (description, annotate, and text-annotations)
        apply_stats_to_config(config, stats)

        # Update and publish chart
        update_and_publish_chart(
            dw=dw,
            chart_id=CHART_ID,
            data=summary_df,
            config=config
        )

        # Print responsive embed code
        embed_html = get_responsive_embed_code(dw, CHART_ID)
        if embed_html:
            print(f"\n📎 Responsive Embed Code:\n{embed_html}")
        else:
            print("⚠️ Chart published, but no embed code was returned.")

    except Exception as e:
        print(f"❌ An error occurred during main(): {e}")


if __name__ == "__main__":
    main()
