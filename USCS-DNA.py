import pandas as pd
import requests

# Load the Excel file
file_path = 'Input.xlsx'
df = pd.read_excel(file_path)

# UCSC Table Browser URL for DNA retrieval (configured for mm10)
url = "https://genome.ucsc.edu/cgi-bin/das/mm10/dna"

# Prepare the output DataFrame
sequences = []

# Iterate through the data
for index, row in df.iterrows():
    try:
        # Extract chromosome and position
        chromosome = str(row['chr'])
        position = int(row['position'])

        # Define the range for 150 bp upstream and downstream
        start = position - 150
        end = position + 150

        # Construct the request parameters
        params = {
            "segment": f"chr{chromosome}:{start},{end}"
        }

        # Query the UCSC API
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Parse and clean up the DNA sequence
            sequence_lines = response.text.splitlines()
            sequence = "".join(sequence_lines[2:])  # Skip the header lines
            sequence_upper = sequence.upper()  # Ensure uppercase

            # Save the sequence
            sequences.append(sequence_upper)
        else:
            # If the API call fails, add an error message
            sequences.append(f"Error: HTTP {response.status_code}")
    except Exception as e:
        # Handle any processing errors
        sequences.append(f"Error: {str(e)}")

# Add the sequences to the DataFrame
df['SEQ 300 bp centered on the DM CG'] = sequences

# Save the updated DataFrame to a new Excel file
output_excel_path = "Updated_Input_with_Sequences.xlsx"
df.to_excel(output_excel_path, index=False)

# Save sequences to FASTA as well (optional)
fasta_output_path = "DNA_Sequences_API_Output.fasta"
with open(fasta_output_path, "w") as fasta_file:
    for index, sequence in enumerate(sequences):
        header = f">chr{df.iloc[index]['chr']}:{df.iloc[index]['position'] - 150}-{df.iloc[index]['position'] + 150}"
        fasta_file.write(f"{header}\n{sequence}\n")

print(f"Updated Excel file saved to {output_excel_path}")
print(f"FASTA file saved to {fasta_output_path}")