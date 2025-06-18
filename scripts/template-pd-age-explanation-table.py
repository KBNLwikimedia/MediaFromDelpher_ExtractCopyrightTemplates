"""
📊 Datawrapper Chart Automation Script: Public Domain Template Overview

This script automates the process of generating and publishing a Datawrapper table chart that summarizes
public domain copyright templates used in Wikimedia Commons for media sourced from Delpher.

The script performs the following steps:
1. Loads an Excel dataset containing template metadata.
2. Filters the data to include only templates with the reason 'Copyrights expired because of age'.
3. Formats the template names as HTML hyperlinks for clean integration into Datawrapper.
4. Loads chart configuration from a JSON file.
5. Updates an existing Datawrapper chart (using its chart ID) with the prepared data and metadata.
6. Publishes the chart and retrieves the responsive embed code.

🧩 Key Components:
- Data loading and processing with pandas.
- Datawrapper API interaction for updating chart data, metadata, and descriptions.
- Configuration handling via JSON.
- Secure API token management via a `.env` file.

📁 Expected Folder Structure:
project-root/
├── data/                  # Contains the Excel source file
├── scripts/               # Contains this script and the config JSON

🔐 Requirements:
- A `.env` file with your `DW_API_TOKEN`.
- The target Datawrapper chart must already exist (create manually via the GUI beforehand).

👤 Author:
- Olaf Janssen, Wikimedia Coordinator @ KB, National Library of the Netherlands
- Supported by ChatGPT

📅 Last updated: 25 April 2025

💼 License:
- Released into the public domain (CC0-style). Free to reuse, adapt, and distribute.
"""

import os
from dotenv import load_dotenv
from pathlib import Path
import json
from typing import Dict
from datawrapper import Datawrapper
import pandas as pd

def load_and_process_data(excel_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Load, filter, and format data from an Excel file for use in a Datawrapper chart.

    This function:
    - Loads data from the specified Excel sheet.
    - Checks for the required columns.
    - Filters the dataset to only include rows where 'NoCopyrightReason' is
      'Copyrights expired because of age'.
    - Formats the 'Template' column as an HTML hyperlink using the 'TemplateURL'.
    - Returns a cleaned and ordered DataFrame ready for Datawrapper upload.

    Parameters:
        excel_path (str): Path to the Excel file containing the data.
        sheet_name (str): Name of the sheet within the Excel file to process.

    Returns:
        pd.DataFrame: Filtered and formatted DataFrame with the following columns:
            - 'Template' (HTML link format)
            - 'Number of times this template is used'
            - 'Years after death of author'
            - 'Years after first publication'
            - 'Years after creation'
            - 'Remarks'

    Raises:
        ValueError: If required columns are missing.
        Other exceptions are caught and logged, and an empty DataFrame is returned.
    """
    try:
        # Load the Excel sheet
        df = pd.read_excel(excel_path, sheet_name=sheet_name)

        # Define required columns
        required_columns = [
            'Template',
            'TemplateURL',
            'Number of times this template is used',
            'NoCopyrightReason',
            'Years after death of author',
            'Years after first publication',
            'Years after creation',
            'Remarks'
        ]

        # Check for missing columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required column(s): {', '.join(missing_cols)}")

        # Filter for specific NoCopyrightReason
        filtered_df = df[df['NoCopyrightReason'] == 'Copyrights expired because of age'].copy()

        # Format 'Template' column as HTML links
        filtered_df['Template'] = filtered_df.apply(
            lambda row: (
                f'<a href="{row["TemplateURL"]}" style="color:#b1bfc3;" target="_blank" rel="nofollow noopener">{row["Template"].strip("{}")}</a>'
                if pd.notnull(row["TemplateURL"]) and row["TemplateURL"] != "" else row["Template"]
            ),
            axis=1
        )

        # Final column order selection
        final_df = filtered_df[[
            'Template',
            'Number of times this template is used',
            'Years after death of author',
            'Years after first publication',
            'Years after creation',
            'Remarks'
        ]]

        return final_df

    except ValueError as ve:
        print(f"❌ ValueError in load_and_process_data(): {ve}")
        return pd.DataFrame()

    except Exception as e:
        print(f"❌ Unexpected error in load_and_process_data(): {e}")
        return pd.DataFrame()


def update_datawrapper_chart(
    dw: Datawrapper,
    chart_id: str,
    data: pd.DataFrame,
    config: Dict
) -> None:
    """
    Uploads data to a Datawrapper chart, updates its metadata and description, and publishes it.

    This function:
    - Uploads the provided pandas DataFrame directly into the specified Datawrapper chart.
    - Updates chart metadata such as visualization options, annotations, and publishing settings using the provided config.
    - Updates the chart's textual description (intro, byline, source info, aria description).
    - Publishes the updated chart.
    - Prints a success message upon successful publishing.

    Parameters:
        dw (Datawrapper): An authenticated Datawrapper API client instance.
        chart_id (str): The ID of the chart to update and publish.
        data (pd.DataFrame): The data to upload into the chart (must match chart structure).
        config (dict): Chart configuration containing keys like 'title', 'visualize',
                       'annotate', 'publish', and 'description'.

    Raises:
        RuntimeError: If any of the steps (data upload, chart update, description update, or publish) fail.
    """
    try:
        # Upload data
        dw.add_data(chart_id=chart_id, data=data)

        # Update chart metadata
        title = config.get("title", "Datawrapper Table")
        dw.update_chart(
            chart_id=chart_id,
            title=title,
            metadata={
                "visualize": config.get("visualize", {}),
                "annotate": config.get("annotate", {}),
                "publish": config.get("publish", {})
            }
        )

        # Update chart description
        desc = config.get("description", {})
        dw.update_description(
            chart_id=chart_id,
            intro=desc.get("intro", ""),
            byline=desc.get("byline", ""),
            source_name=desc.get("source-name", ""),
            source_url=desc.get("source-url", ""),
            aria_description=desc.get("aria-description", "")
        )

        # Publish the chart
        dw.publish_chart(chart_id=chart_id)
        print(f"✅ Chart '{title}' updated and published successfully.")

    except Exception as e:
        raise RuntimeError(f"❌ Error while updating and publishing chart '{chart_id}': {e}")


def load_api_token() -> str:
    """Load the Datawrapper API token from .env."""
    load_dotenv()
    token = os.getenv("DW_API_TOKEN")
    if not token:
        raise ValueError("DW_API_TOKEN not found in environment variables.")
    return token

def load_config(config_path: Path) -> dict:
    """Load chart configuration from JSON file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def init_datawrapper(api_token: str) -> Datawrapper:
    """Initialize the Datawrapper API client."""
    return Datawrapper(access_token=api_token)

def get_chart_visualize_config(dw: Datawrapper, chart_id: str) -> dict:
    """
    Fetch the 'visualize' configuration section of a Datawrapper chart.

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
    Main execution pipeline for generating and publishing a Datawrapper chart.
    Streamlined error handling using helper functions.
    """
    try:
        # === Setup paths ===
        ROOT_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = ROOT_DIR / "data"
        SCRIPT_DIR = Path(__file__).resolve().parent
        CONFIG_PATH = SCRIPT_DIR / "template-pd-age-explanation-table-config.json"
        EXCEL_PATH = DATA_DIR / "Media_from_Delpher-Extracted_copyright_templates-09042025-cleaned-processed.xlsx"
        SHEET_NAME = "templates_dedup"
        CHART_ID = "2NsXE"

        # === Load config and initialize ===
        api_token = load_api_token()
        config = load_config(CONFIG_PATH)
        dw = init_datawrapper(api_token)

        # === Load and process data ===
        df = load_and_process_data(EXCEL_PATH, sheet_name=SHEET_NAME)
        if df.empty:
            raise ValueError("Processed DataFrame is empty. Check the source Excel data.")

        # === Optional: Check chart exists ===
        chart_metadata = dw.get_chart(chart_id=CHART_ID)

        # === Print chart metadata, visualize part ===
        try:
            visualize_config = get_chart_visualize_config(dw, CHART_ID)
            print(json.dumps(visualize_config, indent=2))
        except Exception as e:
            print(e)

        # === Update chart ===
        update_datawrapper_chart(dw, chart_id=CHART_ID, data=df, config=config)

        # === Embed code ===
        embed_html = get_responsive_embed_code(dw, CHART_ID)
        if embed_html:
            print(f"\n📎 Responsive Embed Code:\n{embed_html}")
        else:
            print("⚠️ Embed code not available (chart may not be published yet).")

    except Exception as e:
        print(f"❌ An error occurred in main(): {e}")


if __name__ == "__main__":
    main()
