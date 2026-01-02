def test_parse_piawka_het_writes_aggregated_table(tmp_path, load_module):
    mod = load_module("piawka_het", "sample_analysis/scripts/03_genomic_piawka_het.py")

    infile = tmp_path / "piawka_het.tsv"

    # Build minimal input with two pops and het metrics
    # Columns 1..11 (only first 9 used + two ignored strings)
    lines = [
        "locus1\t10\tPopA\tX\t10\thet\t0.2\t2\t10\tfoo\tbar\n",
        "locus2\t20\tPopA\tX\t20\thet\t0.1\t1\t20\tfoo\tbar\n",
        "locus3\t30\tPopB\tY\t30\thet\t0.3\t3\t30\tfoo\tbar\n",
        # A non-het metric row should be ignored
        "locus4\t30\tPopB\tY\t30\tpi\t0.3\t3\t30\tbaz\tbuz\n",
    ]
    infile.write_text("".join(lines))

    mod.parse_piawka_het(str(infile), "")

    out = tmp_path / "genomic_het_table.tsv"
    text = out.read_text().strip().splitlines()
    # Header expected from Polars write_csv with default header names
    # It should contain columns: pop1,numerator,denominator,het
    assert text[0].split("\t") == ["pop1", "numerator", "denominator", "het"]
    rows = {r.split("\t")[0]: r.split("\t")[1:] for r in text[1:]}
    # PopA: numerator=2+1=3, denominator=10+20=30, het=0.1
    assert rows["PopA"] == ["3.0", "30.0", "0.1"]
    # PopB: numerator=3, denominator=30, het=0.1
    assert rows["PopB"] == ["3.0", "30.0", "0.1"]
