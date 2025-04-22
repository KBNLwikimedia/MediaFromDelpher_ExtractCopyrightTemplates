


import os
from datawrapper import Datawrapper #https://datawrapper.readthedocs.io/en/latest/user-guide/api.html
from dotenv import load_dotenv
import pandas as pd
import json
from pathlib import Path
from typing import Tuple

def count_nocopyrightreason_usage(
    excel_path: str,
    sheet_name: str
) -> pd.DataFrame:
    """
    Summarize the number of files per 'NoCopyrightReason'.

    Parameters:
        excel_path (str): Path to the Excel file containing the data.
        sheet_name (str): Name of the sheet to process.

    Returns:
        pd.DataFrame: A DataFrame with 'NoCopyrightReason' and 'Number of files using this template'.
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

    try:
        # Load environment and API token
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
        #CSV_EXPORT = DATA_DIR / "template_usage_summary.csv"
        CONFIG_PATH = SCRIPT_DIR / "templategroups_usage_summary-config.json"
        CHART_ID = "gZqMt"  # Chart ID must exist in Datawrapper, create it via the GIU first

        # Load chart config
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load chart config from {CONFIG_PATH}: {e}")

        chart_title = config.get("title", "Untitled Datawrapper Chart")
        dw = Datawrapper(access_token=DW_API_TOKEN)

        # Generate summary and stats
        try:
            reason_summary_df = count_nocopyrightreason_usage(EXCEL_PATH, EXCEL_SHEET)
        except Exception as e:
            raise RuntimeError(f"Failed to generate template usage summary: {e}")

        if reason_summary_df is None or reason_summary_df.empty:
            raise RuntimeError("Summary DataFrame is empty. Chart will not be updated.")


        # Update and publish chart
        try:
            if not reason_summary_df.empty:
                update_and_publish_chart(
                    dw=dw,
                    chart_id=CHART_ID,
                    data=reason_summary_df,
                    config=config # Should be your donut-specific config dict
                )
            embed_html = get_responsive_embed_code(dw, CHART_ID)
            if embed_html:
                print(f"\n📎 Responsive Embed Code:\n{embed_html}")
            else:
                print("⚠️ Chart published, but no embed code was returned.")
        except Exception as e:
            raise RuntimeError(f"Failed to update and publish chart: {e}")

    except Exception as e:
        print(f"❌ An error occurred during main(): {e}")

if __name__ == "__main__":
    main()
