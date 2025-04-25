import os
import pandas as pd
from datawrapper import Datawrapper
from dotenv import load_dotenv
from pathlib import Path
import json

def load_and_process_data(excel_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Load and filter data from the Excel file for templates with 'Copyrights expired because of age'.

    Returns a DataFrame ready for upload to Datawrapper, with the Template column formatted as HTML.
    """
    try:
        # Load the Excel sheet
        df = pd.read_excel(excel_path, sheet_name=sheet_name)

        # Required columns
        required_columns = [
            'Template',
            'TemplateURL',
            'Number of files using this template',
            'NoCopyrightReason',
            'Years after death of author',
            'Years after first publication',
            'Years after creation',
            'Remarks'
        ]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required column(s): {', '.join(missing_cols)}")

        # Filter only rows where NoCopyrightReason == 'Copyrights expired because of age'
        filtered_df = df[df['NoCopyrightReason'] == 'Copyrights expired because of age'].copy()

        # Format Template as HTML link
        filtered_df['Template'] = filtered_df.apply(
            lambda row: (
                f'<a href="{row["TemplateURL"]}" style="color:#b1bfc3;" target="_blank" rel="nofollow noopener">{row["Template"].strip("{}")}</a>'
                if pd.notnull(row["TemplateURL"]) and row["TemplateURL"] != "" else row["Template"]
            ),
            axis=1
        )

        # Select and order columns
        final_df = filtered_df[[
            'Template',
            'Number of files using this template',
            'Years after death of author',
            'Years after first publication',
            'Years after creation',
            'Remarks'
        ]]

        return final_df

    except Exception as e:
        print(f"❌ Error in load_and_process_data(): {e}")
        return pd.DataFrame()


def update_datawrapper_chart(dw: Datawrapper, chart_id: str, data: pd.DataFrame, config: dict):
    dw.add_data(chart_id=chart_id, data=data)

    dw.update_chart(
        chart_id=chart_id,
        title=config.get("title", "Datawrapper Table"),
        metadata={
            "visualize": config.get("visualize", {}),
            "annotate": config.get("annotate", {}),
            "publish": config.get("publish", {})
        }
    )

    desc = config.get("description", {})
    dw.update_description(
        chart_id=chart_id,
        intro=desc.get("intro", ""),
        byline=desc.get("byline", ""),
        source_name=desc.get("source-name", ""),
        source_url=desc.get("source-url", ""),
        aria_description=desc.get("aria-description", "")
    )

    dw.publish_chart(chart_id=chart_id)
    print(f"✅ Chart '{config.get('title', 'Datawrapper Table')}' updated and published successfully.")


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
