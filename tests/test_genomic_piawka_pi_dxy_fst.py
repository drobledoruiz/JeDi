def parse_tsv(path):
    lines = [line for line in path.read_text().splitlines() if line]
    header = lines[0].split("\t")
    rows = [dict(zip(header, r.split("\t"))) for r in lines[1:]]
    return header, rows


def test_parse_piawka_dxy_outputs_tables_and_matrices(tmp_path, load_module):
    mod = load_module(
        "piawka_dxy",
        "population_analysis/scripts/04_genomic_piawka_pi_dxy_fst.py",
    )

    infile = tmp_path / "piawka.tsv"
    # Build small dataset covering pi, Dxy and Fst_HUD
    rows = [
        # pi metrics for PopA
        "l1\t10\tPopA\tX\t10\tpi\t0.1\t2\t20\t5\t0\n",
        "l2\t10\tPopA\tX\t10\tpi\t0.1\t1\t10\t5\t0\n",
        # Dxy metrics for PopA/PopB
        "l3\t10\tPopA\tPopB\t10\tDxy\t0.1\t4\t40\t5\t0\n",
        "l4\t10\tPopA\tPopB\t10\tDxy\t0.1\t6\t60\t5\t0\n",
        # Fst metrics for PopA/PopB
        "l5\t10\tPopA\tPopB\t10\tFst_HUD\t0.2\t0\t0\t5\t0\n",
        "l6\t10\tPopA\tPopB\t10\tFst_HUD\t0.4\t0\t0\t5\t0\n",
    ]
    infile.write_text("".join(rows))

    mod.parse_piawka_dxy(str(infile))

    pi = tmp_path / "genomic_pi_table.tsv"
    dxy = tmp_path / "genomic_dxy_table.tsv"
    dxyM = tmp_path / "genomic_dxy_matrix.tsv"
    fst = tmp_path / "genomic_fst_table.tsv"
    fstM = tmp_path / "genomic_fst_matrix.tsv"

    assert pi.exists() and dxy.exists() and dxyM.exists() and fst.exists() and fstM.exists()

    # Check PI table
    _, pi_rows = parse_tsv(pi)
    assert len(pi_rows) == 1
    row = pi_rows[0]
    assert row["pop1"] == "PopA"
    assert row["diffs"] == "3.0" and row["comps"] == "30.0"
    assert float(row["pi"]) == 0.1

    # Check DXY table and matrix
    _, dxy_rows = parse_tsv(dxy)
    assert len(dxy_rows) == 1
    row = dxy_rows[0]
    assert row["pop1"] == "PopA" and row["pop2"] == "PopB"
    assert row["diffs"] == "10.0" and row["comps"] == "100.0"
    assert abs(float(row["dxy"]) - 0.1) < 1e-9

    header, matrix_rows = parse_tsv(dxyM)
    # header includes index name followed by columns for pop2 values
    assert "PopB" in header
    # Find PopA row
    mrow = next(r for r in matrix_rows if r[header[0]] == "PopA")
    assert abs(float(mrow["PopB"]) - 0.1) < 1e-9

    # Check FST table and matrix
    _, fst_rows = parse_tsv(fst)
    row = fst_rows[0]
    assert row["pop1"] == "PopA" and row["pop2"] == "PopB"
    assert abs(float(row["avg_fst"]) - 0.3) < 1e-9
    # Sample std of [0.2,0.4] = sqrt(0.02)
    assert abs(float(row["std_fst"]) - (0.02) ** 0.5) < 1e-9

    h2, fstM_rows = parse_tsv(fstM)
    assert "PopB" in h2
    mrow = next(r for r in fstM_rows if r[h2[0]] == "PopA")
    assert abs(float(mrow["PopB"]) - 0.3) < 1e-9
