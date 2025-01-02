import pandas as pd
import requests
import re

# Load the Excel file
file_path = 'Input.xlsx'
df = pd.read_excel(file_path)

# UCSC Table Browser URL for DNA retrieval (configured for mm10)
url = "https://genome.ucsc.edu/cgi-bin/das/mm10/dna"

# Prepare the output column
fasta_sequences = []

# Regex to clean XML tags
xml_tag_pattern = r"<.*?>"

# Iterate through the data
for index, row in df.iterrows():
    try:
        # Extract chromosome and position
        chromosome = str(row['chr'])
        position = int(row['position'])

        # Define the range for 150 bp upstream and downstream
        start = position - 150
        end = position + 149

        # Construct the request parameters
        params = {
            "segment": f"chr{chromosome}:{start},{end}"
        }

        # Query the UCSC API
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Parse and clean up the DNA sequence
            sequence_lines = response.text.splitlines()
            raw_sequence = "".join(sequence_lines[2:])  # Skip the first two header lines

            # Remove XML tags using regex
            sequence_cleaned = re.sub(xml_tag_pattern, "", raw_sequence).strip()

            # Ensure uppercase DNA sequence
            sequence_upper = sequence_cleaned.upper()

            # Format the sequence in FASTA style
            fasta_header = f">Sequence_{index+1} | chr{chromosome}:{start}-{end} strand=+"
            formatted_sequence = "\n".join([sequence_upper[i:i+60] for i in range(0, len(sequence_upper), 60)])
            fasta_format = f"{fasta_header}\n{formatted_sequence}"
            fasta_sequences.append(fasta_format)
        else:
            # If the API call fails, add an error message
            fasta_sequences.append(f"Error: HTTP {response.status_code}")
    except Exception as e:
        # Handle any processing errors
        fasta_sequences.append(f"Error: {str(e)}")

# Add the FASTA-formatted sequences to the DataFrame
df['SEQ 300 bp centered on the DM CG'] = fasta_sequences

# Save the updated DataFrame to a new Excel file
output_excel_path = "MethylData.xlsx"
df.to_excel(output_excel_path, index=False)

# Save sequences to FASTA as well (optional)
fasta_output_path = "MethylCleanedData.fasta"
with open(fasta_output_path, "w") as fasta_file:
    for fasta_entry in fasta_sequences:
        fasta_file.write(f"{fasta_entry}\n")

print(f"Updated Excel file with FASTA sequences saved to {output_excel_path}")
print(f"Cleaned FASTA file saved to {fasta_output_path}")