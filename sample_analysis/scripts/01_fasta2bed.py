#!/usr/bin/python3

# Author: Diana Robledo-Ruiz
# Date: 2024.06.12

import csv
import gzip
import re
from sys import argv


def fasta2bed(fasta_file, output_file):
    table = []
    with gzip.open(fasta_file, "rt") as f:
        lines = f.readlines()
        for i in range(0, len(lines), 2):
            header = lines[i].strip()
            sequence = lines[i + 1].strip()

            # Extract 'chro' from the header
            chr_match = re.search(r"pos=(.*?):", header)
            chro = chr_match.group(1)

            # Extract 'pos' from the header
            pos_match = re.search(r":(\d+)", header)
            pos = int(pos_match.group(1))

            # Extract strand symbol at end of header (e.g., '+', '-')
            symbol_match = re.search(r"([+-])$", header)
            symbol = symbol_match.group(1) if symbol_match else "+"

            # Calculate sequence length
            seq_length = len(sequence)

            # Set 'start' and 'end' based on 'symbol'
            if symbol == "+":
                start = pos - 1
                end = pos + seq_length
            elif symbol == "-":
                start = pos - seq_length
                end = pos + 1

            # Append to the table
            table.append((chro, start, end))

    # Export table to a tab-separated text file
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter="\t")
        for row in table:
            writer.writerow(row)


if __name__ == "__main__":
    fasta_file = argv[1]
    output_file = argv[2]
    fasta2bed(fasta_file, output_file)
