import pandas as pd
import pdfplumber
import os
import wget

from open_ai import extract_title_specs_features

# Define the path to the Excel file
excel_path = "Resources/MVP Group MAP-MCOP  MAY 1, 2024-Revised.xlsx"  # Correct path if necessary

# Load the data from the Excel file
df = pd.read_excel(excel_path)

# Define a new DataFrame to hold results
results_df = pd.DataFrame(
    columns=[
        "S2.Product Name",
        "S2.Description",
        "S2.PDF Text",
        "S2.Features",
        "S2.Specifications",
        "S2.Certifications",
        "S2.Warranty",
    ]
)


def download_and_extract_text():
    # Create a Downloads directory if it doesn't exist
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads")

    row_count = 0
    # Process each spec sheet URL
    for index, row in df.iterrows():
        if row_count == 5:
            break
        url = row["Spec sheet"]
        if pd.notna(url):
            try:
                # Download the PDF
                filename = wget.download(url, out="Downloads/")

                # Extract text from PDF
                all_text = []
                with pdfplumber.open(filename) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            all_text.append(page_text)
                full_text = "\n".join(all_text)

                # Extract features and specifications
                title_specs_features = extract_title_specs_features(
                    row["PRODUCT"], full_text,row.to_json()
                )

                # Populate new DataFrame
                # results_df.loc[index] = [row['PRODUCT'], row['DESCRIPTION'], full_text, features, specifications, '', '']  # Assuming Certifications and Warranty are empty for now
                results_df.loc[index] = [
                    title_specs_features.get("product_name", ""),
                    title_specs_features.get("product_description"),
                    full_text,
                    title_specs_features.get("product_features"),
                    title_specs_features.get("product_specifications", []),
                    title_specs_features.get("product_certifications"),
                    title_specs_features.get("product_warranty"),
                ]  # Assuming Certifications and Warranty are empty for now
                row_count += 1
            except Exception as e:
                print(f"Failed to process {url}: {e}")
                results_df.loc[index] = [
                    row["PRODUCT"],
                    row["DESCRIPTION"],
                    "Error extracting text",
                    "Error extracting features",
                    "Error extracting specifications",
                    "",
                    "",
                ]


# Call the function
download_and_extract_text()

# Save the new DataFrame to a CSV file
results_df.to_csv("Resources/output.csv", index=False)
