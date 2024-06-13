#!/bin/bash

# use exmaple
# bash nejm_case_pdf2jsonzip_byyear.sh ./NEJM_case_pdf ./NEJM_case_json 2008

# Ensure exactly three arguments are provided.
if [ $# -ne 3 ]; then
    echo "Usage: $0 <INPUT_PDF_DIR> <OUTPUT_ZIP_DIR> <YEAR>"
    exit 1
fi

# Assign the directory containing the PDF files from the first argument.
INPUT_PDF_DIR=$1

# Assign the directory where the extracted JSON files will be saved from the second argument.
OUTPUT_ZIP_DIR=$2

# The third argument is the pattern to match in the filenames, such as a specific year.
YEAR=$3

# Specify the full path to the Python script that performs the extraction.
SCRIPT_PATH="extract_txt_from_pdf_adobe.py"

# Create the output directory if it doesn't already exist.
mkdir -p "$OUTPUT_ZIP_DIR"


extracted_count=0

# Find PDF files in the specified directory that contain the year pattern in their filename.
# Then, process each file.
find "$INPUT_PDF_DIR" -type f -name "*$YEAR*.pdf" | while read pdf_file; do
    echo "==============================================================="
    echo "Processing file: $pdf_file"
    
    # Extract the filename without the extension for naming the output file.
    filename=$(basename -- "$pdf_file")
    filename="${filename%.*}"
    
    # Define the full path for the output file (.zip) in the specified output directory.
    output_path="$OUTPUT_ZIP_DIR/${filename}.zip"
    
    # Execute the Python script for the PDF file, saving the output to the defined path.
    python3 "$SCRIPT_PATH" "$pdf_file" "$output_path"

    # if the extraction was successful, print the output path, and count the number of files extracted.
    # if not successful, print a message indicating the failure.
    if [ $? -eq 0 ]; then
        echo "Extraction successful. Output saved to: $output_path"
        # define a count variable and accumulate the number of files extracted.
        extracted_count=$((extracted_count + 1))
        echo "Number of PDF files extracted so far: $extracted_count"
    else
        echo "Extraction failed for file: $pdf_file"
    fi
    
done



