"""
📊 Donut Chart Generator – Copyright Template Group Usage (Wikimedia Commons, Delpher Sources)

This script analyzes metadata from an Excel spreadsheet that documents copyright templates
applied to media files sourced from [Delpher](https://www.delpher.nl) and uploaded to
Wikimedia Commons. Its goal is to visualize how these files are categorized by the
Wikimedia community in terms of copyright status—focusing on high-level categories like
“Expired Copyright” or “No Originality”.

The script summarizes the number of files grouped by 'NoCopyrightReason' and uses the
[Datawrapper API](https://developer.datawrapper.de) to update and publish a donut chart.

🔧 Core Functionalities:
- Loads and processes Excel data with information about copyright templates.
- Aggregates the number of files by 'NoCopyrightReason'.
- Loads chart configuration (title, metadata, colors, etc.) from a local JSON config file.
- Uploads the summarized data directly into a pre-created Datawrapper donut chart.
- Updates chart metadata and textual descriptions (title, source, byline, etc.).
- Publishes the chart and prints the responsive embed code for reuse.

🧩 Technologies & Libraries Used:
- `pandas`: For data handling and transformation.
- `datawrapper`: Official API wrapper for interacting with Datawrapper.
- `dotenv`: For securely loading the API key from a `.env` file.
- `pathlib` & `json`: For modern file handling and configuration loading.

📁 Project Structure:
project-root/
├── data/
│   └── Media_from_Delpher-Extracted_copyright_templates-*.xlsx
├── scripts/
│   └── this_script.py
│   └── templategroups-usage-summary-config.json
├── .env                   # Contains DW_API_TOKEN

🌐 Output:
- Publishes an updated donut chart (e.g., https://www.datawrapper.de/_/gZqMt/).
- Logs summary statistics and prints the responsive embed code to console.

👤 Author:
- Olaf Janssen, Wikimedia Coordinator @ KB (National Library of the Netherlands)
- With scripting support from ChatGPT
- Last updated: 25 April 2025

🆓 License:
- This script is released into the public domain (CC0-style). Free to use, modify, and distribute.
"""

from datawrapper import Datawrapper #https://datawrapper.readthedocs.io/en/latest/user-guide/api.html
from dotenv import load_dotenv
import os
import json
from pathlib import Path
import pandas as pd

def count_nocopyrightreason_usage(
    excel_path: str,
    sheet_name: str
) -> pd.DataFrame:
    """
    Count the number of media files per 'NoCopyrightReason' in the provided Excel dataset.

    This function analyzes the given Excel sheet to:
    - Group the media files by their 'NoCopyrightReason' (e.g., "Copyrights expired because of age").
    - Count the number of unique files (using 'FileMid') associated with each reason.
    - Return the result as a summary DataFrame, listing the reasons and their corresponding file counts.

    This function helps provide insights into how frequently each copyright rationale
    is applied across media files in Wikimedia Commons (sourced from Delpher).

    Parameters:
        excel_path (str): Path to the Excel file containing the metadata.
        sheet_name (str): Name of the worksheet to process within the Excel file.

    Returns:
        pd.DataFrame: A summary table with two columns:
            - 'NoCopyrightReason' (the grouped reason category)
            - 'Number of files using this template' (the count of files for each reason)

    Raises:
        ValueError: If the required columns ('NoCopyrightReason' and 'FileMid') are missing from the Excel sheet.
        Exception: Other unexpected errors are caught, logged, and result in returning an empty DataFrame.
    """

    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)

        if "NoCopyrightReason" not in df.columns or "FileMid" not in df.columns:
            raise ValueError("Missing required columns 'NoCopyrightReason' and/or 'FileMid'.")

        # Group by NoCopyrightReason, count unique FileMid
        summary = df["NoCopyrightReason"].value_counts().reset_index()
        summary.columns = ["NoCopyrightReason", "Number of files using this template"]

        print("\n📊 Summary by NoCopyrightReason:")
        print(summary)

        return summary

    except Exception as e:
        print(f"❌ Error in count_nocopyrightreason_usage(): {e}")
        return pd.DataFrame()

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


def load_api_token() -> str:
    """Load the API token securely from the .env file."""
    load_dotenv()
    token = os.getenv("DW_API_TOKEN")
    if not token:
        raise ValueError("DW_API_TOKEN not found in .env file!")
    return token

def load_chart_config(config_path: Path) -> dict:
    """Load the chart configuration from the given JSON file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def authenticate_datawrapper(api_token: str) -> Datawrapper:
    """Initialize the Datawrapper client."""
    return Datawrapper(access_token=api_token)

def check_chart_exists(dw: Datawrapper, chart_id: str) -> None:
    """Check if the given chart ID exists in Datawrapper."""
    dw.get_chart(chart_id=chart_id)  # Will raise if chart does not exist

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
    Main execution for generating and publishing the donut chart (template groups summary).
    """
    try:
        # === Setup paths ===
        ROOT_DIR = Path(__file__).resolve().parent.parent
        DATA_DIR = ROOT_DIR / "data"
        SCRIPT_DIR = Path(__file__).resolve().parent
        EXCEL_PATH = DATA_DIR / "Media_from_Delpher-Extracted_copyright_templates-09042025-cleaned-processed.xlsx"
        CONFIG_PATH = SCRIPT_DIR / "templategroups-usage-summary-config.json"
        EXCEL_SHEET = "files-templates"
        CHART_ID = "gZqMt"

        # === Load environment and config ===
        api_token = load_api_token()
        config = load_chart_config(CONFIG_PATH)
        chart_title = config.get("title", "Untitled Datawrapper Chart")

        # === Init Datawrapper and validate chart ===
        dw = authenticate_datawrapper(api_token)
        check_chart_exists(dw, chart_id=CHART_ID)

        # === Print chart metadata, visualize part ===
        try:
            visualize_config = get_chart_visualize_config(dw, CHART_ID)
            print(json.dumps(visualize_config, indent=2))
        except Exception as e:
            print(e)

        # === Prepare data ===
        reason_summary_df = count_nocopyrightreason_usage(EXCEL_PATH, EXCEL_SHEET)
        if reason_summary_df is None or reason_summary_df.empty:
            raise RuntimeError("Summary DataFrame is empty. Chart will not be updated.")

        # === Update and publish chart ===
        update_and_publish_chart(
            dw=dw,
            chart_id=CHART_ID,
            data=reason_summary_df,
            config=config
        )

        # === Retrieve embed code ===
        embed_html = get_responsive_embed_code(dw, CHART_ID)
        if embed_html:
            print(f"\n📎 Responsive Embed Code:\n{embed_html}")
        else:
            print("⚠️ Chart published, but no embed code was returned.")

    except Exception as e:
        print(f"❌ An error occurred during main(): {e}")

if __name__ == "__main__":
    main()
