import os
import zipfile
import shutil
import argparse

## use example
# python unzip_json.py NEJM_case_json NEJM_case_json_unzip

# Parse command line arguments.
parser = argparse.ArgumentParser(description='unzip all the zip files from the source folder and stored them in the target folder.')
parser.add_argument('source_folder', type=str, help='path to the zip files of json.')
parser.add_argument('target_folder', type=str, help='path where the output unzip file will be saved.')
args = parser.parse_args()

# Paths to the folders
# '/Users/yuntian/Desktop/Yale/PhD/Year1/Semester2/Rotation3/DiagnosticReasoning/testDataNEJM/pdfExtract/NEJM_case_json/'
source_folder = args.source_folder
# '/Users/yuntian/Desktop/Yale/PhD/Year1/Semester2/Rotation3/DiagnosticReasoning/testDataNEJM/pdfExtract/NEJM_case_json_unzip/'
target_folder = args.target_folder


def clear_folder(folder):
    """Remove all files and folders in the given folder."""
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)  # Remove files and links
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  # Remove directories



# Clear the target folder if it is not empty
if len(os.listdir(target_folder)) > 0:
    print("Target folder is not empty. Clearing the folder.")
    clear_folder(target_folder)
else:
    print("Target folder is empty. Proceeding with extraction.")

print(f"Extracting .zip files from {source_folder} to {target_folder}.")

# Loop through all the files in the specified folder
n_extracted = 0
n_saved = 0
for filename in os.listdir(source_folder):
    if filename.endswith('.zip') and filename.startswith('nejm_case'):
        # Construct the full path to the zip file
        zip_path = os.path.join(source_folder, filename)
        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract all the contents into the folder
            zip_ref.extractall(source_folder)
            n_extracted += 1
            
            # Loop through the contents of the zip file
            for file in zip_ref.namelist():
                # Construct the full path to the extracted file
                extracted_file_path = os.path.join(source_folder, file)
                
                # Generate new filename by replacing the extracted file's extension with the zip file's name
                new_filename = os.path.splitext(filename)[0] + os.path.splitext(file)[1]
                new_file_path = os.path.join(target_folder, new_filename)
                
                # Rename the extracted file
                os.rename(extracted_file_path, new_file_path)
                n_saved += 1

        # Optionally, if you want to delete the zip file after extraction and renaming, uncomment the next line
        # os.remove(zip_path)
        #print(f'Processed and renamed files from {zip_path}')

# Make sure to replace 'path/to/your/folder' with the actual path where your .zip files are stored.
print(f"Extracted {n_extracted} zip files.")
print(f"Saved {n_saved} files to {target_folder}.")