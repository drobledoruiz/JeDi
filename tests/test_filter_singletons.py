import gzip
from pathlib import Path


def write_gz(path: Path, text: str):
    with gzip.open(path, "wt") as f:
        f.write(text)


def test_filter_singletons_removes_matching_positions(tmp_path, load_module):
    mod = load_module("filter_singletons", "sample_analysis/scripts/02_filter_singletons.py")

    vcf = tmp_path / "input.vcf.gz"
    out = tmp_path / "output.vcf"
    singletons = tmp_path / "singletons.tsv"

    header = (
        "##fileformat=VCFv4.2\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tA.bam\tB.bam\n"
    )
    rows = [
        "chr1\t10\t.\tA\tG\t.\t.\t.\tGT\t0/1\t0/0\n",
        "chr1\t20\t.\tC\tT\t.\t.\t.\tGT\t0/0\t0/1\n",
    ]
    write_gz(vcf, header + "".join(rows))

    # Singletons file indicates that INDV 'A' has a singleton at chr1:10
    singletons.write_text(
        "CHROM\tPOS\tINDV\tALLELE\tSINGLETON/DOUBLETON\nchr1\t10\tA\tG\tsingleton\n"
    )

    changed = mod.filter_singletons_vcf(str(vcf), str(out), str(singletons), "A", gzip=True)
    assert changed is True

    out_lines = out.read_text().splitlines()
    # Header preserved but with sanitized sample names
    assert out_lines[1] == "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tA\tB"
    # Row at chr1:10 removed; row at 20 remains
    assert out_lines[-1].startswith("chr1\t20\t.")


def test_filter_singletons_no_positions_returns_false(tmp_path, load_module):
    mod = load_module("filter_singletons", "sample_analysis/scripts/02_filter_singletons.py")

    vcf = tmp_path / "input2.vcf.gz"
    out = tmp_path / "output2.vcf"
    singletons = tmp_path / "singletons2.tsv"

    header = (
        "##fileformat=VCFv4.2\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tA.bam\tB.bam\n"
    )
    body = "chr1\t10\t.\tA\tG\t.\t.\t.\tGT\t0/1\t0/0\n"
    write_gz(vcf, header + body)

    singletons.write_text(
        "CHROM\tPOS\tINDV\tALLELE\tSINGLETON/DOUBLETON\n"  # no rows for INDV C
    )

    changed = mod.filter_singletons_vcf(str(vcf), str(out), str(singletons), "C", gzip=True)
    assert changed is False
    assert not out.exists()
