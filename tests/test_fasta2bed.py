import gzip


def test_fasta2bed_creates_intervals(tmp_path, load_module):
    mod = load_module("fasta2bed", "sample_analysis/scripts/01_fasta2bed.py")
    fasta_path = tmp_path / "input.fa.gz"
    content = ">seq1 pos=chr1:100+\nACGT\n>seq2 pos=chr2:50-\nAAG\n"
    with gzip.open(fasta_path, "wt") as f:
        f.write(content)

    output_path = tmp_path / "out.bed"
    mod.fasta2bed(str(fasta_path), str(output_path))

    lines = output_path.read_text().strip().splitlines()
    assert lines == [
        "chr1\t99\t104",  # + strand: start=pos-1, end=pos+len(seq)
        "chr2\t47\t51",  # - strand: start=pos-len(seq), end=pos+1
    ]
