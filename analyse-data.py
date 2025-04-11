import pandas as pd
import os
from datawrapper import Datawrapper # https://datawrapper.readthedocs.io/en/latest/user-guide/api.html
from dotenv import load_dotenv
import requests

def count_template_usages(
    excel_path: str,
    sheet_name: str = "files-templates",
    output_csv: str = "template_usage_summary.csv"
) -> pd.DataFrame:
    """
    Count how many times each template appears in the dataset and format as Markdown for Datawrapper.
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df["Template"] = df["Template"].astype(str).str.strip()
        df["TemplateURL"] = df["TemplateURL"].astype(str).str.strip()

        summary = df["Template"].value_counts().reset_index()
        summary.columns = ["Template", "Number of Uses"]

        url_map = df.drop_duplicates(subset=["Template"])[["Template", "TemplateURL"]]
        summary = summary.merge(url_map, on="Template", how="left")

        summary["Template"] = summary.apply(
            lambda row: (
                f'<a href="{row["TemplateURL"]}" target="_blank" rel="nofollow noopener">{row["Template"]}</a>'
                if pd.notnull(row["TemplateURL"]) else row["Template"]
            ),
            axis=1
        )

        summary = summary[["Template", "Number of Uses"]]
        summary["Number of Uses"] = pd.to_numeric(summary["Number of Uses"], errors="coerce")
        summary.to_csv(output_csv, index=False, encoding="utf-8", sep=";")
        print(f"✅ Template usage summary saved to: {output_csv}")
        return summary

    except Exception as e:
        print(f"❌ Error: {e}")

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

def update_and_publish_chart(dw: Datawrapper, chart_id: str, csv_path: str, title: str):
    """
    Uploads CSV data and publishes the chart using the datawrapper library.
    """
    dw_df = pd.read_csv(csv_path, sep=";")
    dw.add_data(chart_id=chart_id, data=dw_df)
    dw.update_chart(chart_id=chart_id, title=title)
    dw.publish_chart(chart_id=chart_id)
    print(f"🚀 Chart '{title}' updated and published.")

def main():
    # Fetch the API token
    load_dotenv()
    DW_API_TOKEN = os.getenv("DW_API_TOKEN")
    if not DW_API_TOKEN:
        raise ValueError("DW_API_TOKEN not found in .env file!")

    EXCEL_PATH = "Media_from_Delpher-Extracted_copyright_templates-09042025-cleaned-processed.xlsx"
    CHART_TITLE = "Media from Delpher - Copyright Template Usage Summary"
    CSV_EXPORT = "template_usage_summary.csv"
    CHART_ID_FILE = "chart_id.txt"

    dw = Datawrapper(access_token=DW_API_TOKEN)

    summary = count_template_usages(EXCEL_PATH, sheet_name="files-templates", output_csv=CSV_EXPORT)
    #summary="template_usage_summary.csv"
    if summary is not None:
        chart_id = get_or_create_chart(dw, chart_id_file=CHART_ID_FILE, title=CHART_TITLE)
        update_and_publish_chart(dw, chart_id=chart_id, csv_path=CSV_EXPORT, title=CHART_TITLE)

if __name__ == "__main__":
    main()
