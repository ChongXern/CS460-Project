import os

name = input("INPUT NAME: ")

input_file = f"transcripts/{name}.txt"
output_file = f"transcripts/{name}2.txt"

# Open the input file for reading and the output file for writing
with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        # Strip whitespace and check if the line is not empty
        if line.strip():
            outfile.write(line)
