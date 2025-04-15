import os
from datawrapper import Datawrapper #https://datawrapper.readthedocs.io/en/latest/user-guide/api.html
from dotenv import load_dotenv
import pandas as pd
import json

def count_template_usages(
        excel_path: str,
        sheet_name: str,
        output_csv: str
) -> tuple[pd.DataFrame, dict]:
    """
    Count how many times each template appears in the dataset and format as HTML for Datawrapper.

    Also calculates key figures about usage frequency and file-template relationships.

    Parameters:
        excel_path (str): Path to the Excel file.
        sheet_name (str): Sheet name containing the data.
        output_csv (str): Path to output the CSV summary.

    Returns:
        tuple: (summary DataFrame, dictionary of key figures)
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df["Template"] = df["Template"].astype(str).str.strip()
        df["TemplateURL"] = df["TemplateURL"].astype(str).str.strip()

        # Count template usage
        summary = df["Template"].value_counts().reset_index()
        summary.columns = ["Template", "Number of Uses"]

        # Merge with URLs
        url_map = df.drop_duplicates(subset=["Template"])[["Template", "TemplateURL"]]
        summary = summary.merge(url_map, on="Template", how="left")

        # Format templates as HTML links
        summary["Template"] = summary.apply(
            lambda row: (
                f'<a href="{row["TemplateURL"]}" target="_blank" rel="nofollow noopener">{row["Template"].strip("{").strip("}")}</a>'
                if pd.notnull(row["TemplateURL"]) else row["Template"]
            ),
            axis=1
        )
        summary = summary[["Template", "Number of Uses"]]
        summary["Number of Uses"] = pd.to_numeric(summary["Number of Uses"], errors="coerce")

        # Save CSV
        summary.to_csv(output_csv, index=False, encoding="utf-8", sep=";")
        print(f"✅ Template usage summary saved to: {output_csv}")

        # === KEY FIGURES ===
        total_template_usages = len(df)
        unique_templates_used = df["Template"].nunique()
        total_files_with_templates = df["FileURL"].nunique() if "FileURL" in df.columns else None
        total_unique_files = df["FileMid"].nunique() if "FileMid" in df.columns else None
        most_used_template = summary.sort_values("Number of Uses", ascending=False).iloc[0]["Template"]

        stats = {
            "total_template_usages": total_template_usages,
            "unique_templates_used": unique_templates_used,
            "total_files_with_templates": total_files_with_templates,
            "total_unique_files": total_unique_files,
            "most_used_template": most_used_template
        }

        # Pretty print stats
        print("\n📊 Key Figures:")
        print(f"• Total template usages (incl. duplicates): {total_template_usages:,}")
        print(f"• Unique templates used: {unique_templates_used}")
        if total_files_with_templates is not None:
            print(f"• Unique filess with templates (based on FileURL): {total_files_with_templates:,}")
        if total_unique_files is not None:
            print(f"•  Unique files with templates (based on FileMid): {total_unique_files:,}")
        print(f"• Most used template (HTML label): {most_used_template}")

        return summary, stats

    except Exception as e:
        print(f"❌ Error: {e}")
        return pd.DataFrame(), {}


def get_or_create_chart(dw: Datawrapper, chart_id_file: str, title: str, chart_type: str = "d3-bars") -> str:
    """
    Reuse existing chart ID or create a new one using Datawrapper.
    """
    if os.path.exists(chart_id_file):
        with open(chart_id_file, "r") as f:
            chart_id = f.read().strip()
        print(f"📄 Reusing existing chart ID: {chart_id}")
        return chart_id

    chart = dw.create_chart(title=title, chart_type=chart_type)
    chart_id = chart['id']
    with open(chart_id_file, "w") as f:
        f.write(chart_id)
    print(f"✅ Created and saved new chart ID: {chart_id}")
    return chart_id


def update_and_publish_chart(dw: Datawrapper, chart_id: str, csv_path: str, config: dict):
    """
    Uploads data, updates metadata and description, and publishes the chart.
    Accepts all visual and textual chart configuration as a dictionary.

    Parameters:
        dw (Datawrapper): Datawrapper API instance
        chart_id (str): ID of the chart to update
        csv_path (str): Path to the CSV file with chart data
        config (dict): Chart configuration loaded from a JSON file
    """
    try:
        # Upload data
        dw_df = pd.read_csv(csv_path, sep=";")
        dw.add_data(chart_id=chart_id, data=dw_df)

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

        # Apply description
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
        responsive_embed = embed_codes.get("embed-method-responsive", None)

        if responsive_embed:
            return responsive_embed
        else:
            print("❌ Responsive embed code not found. Make sure the chart is published.")
            return None

    except Exception as e:
        print(f"❌ Error retrieving embed code: {e}")
        return None

def main():
    """
    Main execution pipeline for generating a Datawrapper chart.

    This function:
    - Loads API credentials from .env
    - Loads chart configuration from JSON
    - Generates a CSV summary of template usage from an Excel file
    - Updates the Datawrapper chart metadata and data
    - Publishes the chart and prints the responsive embed code

    Raises:
        ValueError: If the API token is not found
        RuntimeError: If the config file or any major step fails
    """
    try:
        # Load environment and fetch API token
        load_dotenv()
        DW_API_TOKEN = os.getenv("DW_API_TOKEN")
        if not DW_API_TOKEN:
            raise ValueError("DW_API_TOKEN not found in .env file!")

        # Define file paths
        EXCEL_PATH = "Media_from_Delpher-Extracted_copyright_templates-09042025-cleaned-processed.xlsx"
        EXCEL_SHEET = "files-templates"
        CSV_EXPORT = "template_usage_summary.csv"
        CHART_ID_FILE = "chart_id.txt"
        CONFIG_PATH = "template_usage_summary-chart-config.json"

        # Load chart config from JSON
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load chart config: {e}")

        chart_title = config.get("title", "Untitled Datawrapper Chart")
        dw = Datawrapper(access_token=DW_API_TOKEN)

        # Generate summary and stats
        summary_df, stats = count_template_usages(
            excel_path=EXCEL_PATH,
            sheet_name=EXCEL_SHEET,
            output_csv=CSV_EXPORT
        )

        print("📊 Key stats:", stats)

        # Format variables into description fields
        if "description" in config:
            config["description"] = {
                k: v.format(**stats) if isinstance(v, str) else v
                for k, v in config["description"].items()
            }

        # Update and publish chart
        if summary_df is not None and not summary_df.empty:
            chart_id = get_or_create_chart(dw, chart_id_file=CHART_ID_FILE, title=chart_title)
            update_and_publish_chart(dw, chart_id=chart_id, csv_path=CSV_EXPORT, config=config)
            embed_html = get_responsive_embed_code(dw, chart_id)
            print(f"\n📎 Responsive Embed Code:\n{embed_html}")
        else:
            print("⚠️ No summary data found — chart was not updated.")

    except Exception as e:
        print(f"❌ An error occurred during main(): {e}")


if __name__ == "__main__":
    main()
