def test_fasta2bed_edge_cases(tmp_path, load_module):
    """Test fasta2bed with various strand/position combinations."""
    import gzip

    mod = load_module("fasta2bed", "sample_analysis/scripts/01_fasta2bed.py")
    fasta_path = tmp_path / "input.fa.gz"

    content = (
        ">seq1 pos=chr1:100+\nACGT\n"
        ">seq2 pos=chr2:50-\nAAG\n"
        ">seq3 pos=chr3:200\nAT\n"  # No strand specified
    )
    with gzip.open(fasta_path, "wt") as f:
        f.write(content)

    output_path = tmp_path / "out.bed"
    mod.fasta2bed(str(fasta_path), str(output_path))

    lines = output_path.read_text().strip().splitlines()
    assert len(lines) == 3

    # + strand: start=pos-1, end=pos+len(seq)
    assert lines[0] == "chr1\t99\t104"

    # - strand: start=pos-len(seq), end=pos+1
    assert lines[1] == "chr2\t47\t51"

    # No strand (default +): start=pos-1, end=pos+len(seq)
    assert lines[2] == "chr3\t199\t202"


def test_fasta2bed_empty_input(tmp_path, load_module):
    """Test fasta2bed with empty gzip file."""
    import gzip

    mod = load_module("fasta2bed", "sample_analysis/scripts/01_fasta2bed.py")
    fasta_path = tmp_path / "empty.fa.gz"

    with gzip.open(fasta_path, "wt") as f:
        f.write("")

    output_path = tmp_path / "out.bed"
    mod.fasta2bed(str(fasta_path), str(output_path))

    lines = output_path.read_text().strip().splitlines()
    assert len(lines) == 0


def test_fasta2bed_single_base(tmp_path, load_module):
    """Test fasta2bed with single-base sequence."""
    import gzip

    mod = load_module("fasta2bed", "sample_analysis/scripts/01_fasta2bed.py")
    fasta_path = tmp_path / "single.fa.gz"

    content = ">seq1 pos=chr1:100+\nG\n"
    with gzip.open(fasta_path, "wt") as f:
        f.write(content)

    output_path = tmp_path / "out.bed"
    mod.fasta2bed(str(fasta_path), str(output_path))

    lines = output_path.read_text().strip().splitlines()
    assert lines[0] == "chr1\t99\t101"
