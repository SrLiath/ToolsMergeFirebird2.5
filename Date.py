import os
import re

def format_dates_in_sql_files(folder_path):
    # Check if the folder path exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".sql"):
            file_path = os.path.join(folder_path, filename)

            # Read the content of the file
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Apply regular expression substitution to format dates
            modified_lines = [re.sub(r'(\d{4}-\d{2}-\d{2})', r"'\1'", line) for line in lines]

            # Write the modified lines back to the file
            with open(file_path, 'w') as file:
                file.writelines(modified_lines)

            print(f"Dates formatted in {filename}")

# Example usage
folder_path = 'output_sql/'
format_dates_in_sql_files(folder_path)
