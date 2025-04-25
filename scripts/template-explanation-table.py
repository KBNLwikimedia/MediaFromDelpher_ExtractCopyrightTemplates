"""
📊 Delpher Copyright Template Visualization Script (Datawrapper Integration)

This script automates the process of generating, updating, and publishing a Datawrapper chart
based on copyright template metadata extracted from a Delpher-sourced Excel file.

✅ **Purpose**:
- To analyze how frequently specific copyright templates are used.
- To prepare and format this data (including HTML rendering of template names).
- To upload the processed data directly into a pre-configured Datawrapper table chart.
- To update the chart's metadata, annotations, and descriptions from a separate JSON config file.
- To publish the chart and optionally retrieve the responsive embed code.

⚙️ **Workflow**:
1. Loads environment variables (for the Datawrapper API token).
2. Reads configuration settings from a JSON file.
3. Loads and processes template metadata from an Excel sheet.
4. Formats template names as clickable HTML links.
5. Filters, cleans, and sorts the data for upload.
6. Updates an existing Datawrapper chart using the Datawrapper API.
7. Publishes the chart and prints the responsive embed code.

📂 **Expected Directory Structure**:
project-root/
├── data/                # Contains the source Excel file with metadata
├── scripts/             # Contains this script and the JSON configuration file

🔒 **Requirements**:
- `.env` file containing the Datawrapper API token (`DW_API_TOKEN`).
- `pandas`, `python-dotenv`, and `datawrapper` Python packages installed.

📌 **Limitations**:
- This script assumes that the target Datawrapper chart has already been created manually.
- The configuration must match the structure expected by Datawrapper (title, metadata blocks).

🖋️ **Author**:
- Olaf Janssen, Wikimedia Coordinator @ KB, National Library of the Netherlands
- Assisted by ChatGPT
- Last updated: 25 April 2025
"""

import os
import pandas as pd
from datawrapper import Datawrapper
from dotenv import load_dotenv
from pathlib import Path
import json
from typing import Dict

def load_and_process_data(excel_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Load and process template metadata from an Excel sheet, formatting the template names as HTML links
    and preparing the data for visualization (e.g., in a Datawrapper table chart).

    The function:
    - Loads data from the specified Excel sheet.
    - Verifies the presence of required columns.
    - Cleans and formats the columns.
    - Optionally merges the 'NoCopyrightReason' column if it exists.
    - Formats the 'Template' column as an HTML hyperlink using the 'TemplateURL'.
    - Sorts the results by 'NoCopyrightReason' (A-Z) and the number of files using the template (descending).
    - Returns the processed DataFrame ready for upload or further analysis.

    Parameters:
        excel_path (str): Path to the Excel file containing the template metadata.
        sheet_name (str): Name of the sheet to process.

    Returns:
        pd.DataFrame: Processed DataFrame with the following columns:
            - 'Template' (HTML link format)
            - 'NoCopyrightReason'
            - 'Description'

    Raises:
        ValueError: If required columns are missing from the input data.
        Exception: Any unexpected error during processing is caught and logged.
    """
    try:
        # Load Excel sheet
        df = pd.read_excel(excel_path, sheet_name=sheet_name)

        # Required columns
        required_columns = [
            'Template',
            'TemplateURL',
            'Description',
            'Number of files using this template'
        ]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required column(s): {', '.join(missing_cols)}")

        # Clean columns
        df['Template'] = df['Template'].astype(str).str.strip()
        df['TemplateURL'] = df['TemplateURL'].astype(str).str.strip()
        df['Description'] = df['Description'].astype(str).str.strip()

        # Drop duplicates to create a summary
        summary_df = df[[
            'Template',
            'TemplateURL',
            'Description',
            'Number of files using this template'
        ]].drop_duplicates(subset='Template')

        # Merge NoCopyrightReason if available
        if 'NoCopyrightReason' in df.columns:
            reasons = df[['Template', 'NoCopyrightReason']].drop_duplicates()
            summary_df = pd.merge(summary_df, reasons, on='Template', how='left')
        else:
            summary_df['NoCopyrightReason'] = None

        # Format Template as HTML link
        summary_df['Template'] = summary_df.apply(
            lambda row: (
                f'<a href="{row["TemplateURL"]}" style="color:#b1bfc3;" target="_blank" rel="nofollow noopener">{row["Template"].strip("{}")}</a>'
                if pd.notnull(row["TemplateURL"]) else row["Template"]
            ),
            axis=1
        )

        # Sort by NoCopyrightReason (A-Z) and Number of files (descending)
        summary_df = summary_df.sort_values(
            by=['NoCopyrightReason', 'Number of files using this template'],
            ascending=[True, False]
        )

        # Drop column before upload
        summary_df = summary_df.drop(columns=['Number of files using this template'])

        # Final column order
        return summary_df[[
            'Template',
            'NoCopyrightReason',
            'Description',
        ]]

    except Exception as e:
        print(f"❌ Error in load_and_process_data(): {e}")
        return pd.DataFrame()


def update_datawrapper_chart(
    dw: Datawrapper,
    chart_id: str,
    data: pd.DataFrame,
    config: Dict
) -> None:
    """
    Uploads data, updates metadata and description, and publishes a Datawrapper chart.

    This function performs the following:
    - Uploads a pandas DataFrame directly into the specified Datawrapper chart.
    - Updates chart metadata using the provided configuration dictionary.
    - Sets the textual description for the chart (intro, byline, source).
    - Publishes the chart on Datawrapper.
    - Prints a confirmation message upon success.

    Parameters:
        dw (Datawrapper): An instance of the Datawrapper API client.
        chart_id (str): The ID of the chart to update.
        data (pd.DataFrame): The data to upload into the chart.
        config (dict): Chart configuration containing 'title', 'visualize', 'annotate', 'publish', and 'description' keys.

    Raises:
        RuntimeError: If any step of the chart update or publishing process fails.
    """
    try:
        # Upload data directly
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

        # Publish chart
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
        CONFIG_PATH = SCRIPT_DIR / "template-explanation-table-config.json"
        EXCEL_PATH = DATA_DIR / "Media_from_Delpher-Extracted_copyright_templates-09042025-cleaned-processed.xlsx"
        SHEET_NAME = "templates_dedup"
        CHART_ID = "PJ96v"

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
