import gzip
from pathlib import Path


def make_gz(path: Path, text: str):
    with gzip.open(path, "wt") as f:
        f.write(text)


def test_get_and_write_header_gz(tmp_path, load_module):
    mod = load_module("vcf_reheader", "sample_analysis/scripts/01_vcf_reheader.py")

    vcf = tmp_path / "in.vcf.gz"
    out = tmp_path / "out.vcf"

    header = (
        "##fileformat=VCFv4.2\n"
        "##source=test\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tpath/a.bam\tpath/b.bam\n"
    )
    body = "chr1\t1\t.\tA\tG\t.\t.\t.\tGT\t0/1\t1/1\n"
    make_gz(vcf, header + body)

    # get_header returns raw names from header
    names = mod.get_header(str(vcf), gzip=True)
    assert names[:9] == [
        "#CHROM",
        "POS",
        "ID",
        "REF",
        "ALT",
        "QUAL",
        "FILTER",
        "INFO",
        "FORMAT",
    ]
    assert names[-2:] == ["path/a.bam", "path/b.bam"]

    # write_header writes all header lines to out and returns names
    _ = mod.write_header(str(vcf), str(out), gzip=True)
    assert out.exists()
    # Validate output header content
    out_text = out.read_text()
    assert (
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tpath/a.bam\tpath/b.bam" in out_text
    )


def test_reheader_vcf_updates_sample_names(tmp_path, load_module):
    mod = load_module("vcf_reheader", "sample_analysis/scripts/01_vcf_reheader.py")

    vcf = tmp_path / "in.vcf.gz"
    out = tmp_path / "out.vcf"

    header = (
        "##fileformat=VCFv4.2\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsome/dir/a.bam\tsome/dir/b.bam\n"
    )
    body = "chr1\t2\t.\tC\tT\t.\t.\t.\tGT\t0/0\t0/1\n"
    make_gz(vcf, header + body)

    changed = mod.reheader_vcf(str(vcf), str(out), gzip=True)
    assert changed is True

    lines = out.read_text().splitlines()
    assert lines[0].startswith("##fileformat")
    # Header should have sample names without .bam and only basenames
    assert lines[1] == "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ta\tb"
    # Data line must be present and unchanged except for header rename
    assert lines[2] == "chr1\t2\t.\tC\tT\t.\t.\t.\tGT\t0/0\t0/1"


def test_reheader_vcf_skips_when_already_clean(tmp_path, load_module):
    mod = load_module("vcf_reheader", "sample_analysis/scripts/01_vcf_reheader.py")

    vcf = tmp_path / "in2.vcf.gz"
    out = tmp_path / "out2.vcf"

    header = "##source=test\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ta\tb\n"
    body = "chr1\t3\t.\tG\tA\t.\t.\t.\tGT\t0/1\t1/1\n"
    make_gz(vcf, header + body)

    changed = mod.reheader_vcf(str(vcf), str(out), gzip=True)
    assert changed is False
    assert not out.exists()
