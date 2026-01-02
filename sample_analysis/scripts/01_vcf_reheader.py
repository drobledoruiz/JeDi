import argparse
import gzip as gz
import os

import polars as pl


class MyException(Exception):
    pass


def _count_lines(ivcf_path, gzip=True):
    f = gz.open(ivcf_path, "rt") if gzip else open(ivcf_path, "rt")
    with f:
        return sum(1 for _ in f)


def write_header(
    ivcf_path,
    ovcf_path,
    gzip=True,
):
    nl = _count_lines(ivcf_path, gzip=gzip)
    ifile = gz.open(ivcf_path, "rt") if gzip else open(ivcf_path, "rt")
    ofile = open(ovcf_path, "wt")
    counter = 0
    with ifile:
        with ofile:
            for line in ifile:
                counter += 1
                if line.startswith("#CHROM"):
                    vcf_names = [x for x in line.split("\t")]
                    ofile.write(line)
                    if nl == counter:
                        return []
                    break
                else:
                    ofile.write(line)
    return [x.split("\n")[0] for x in vcf_names]


def get_header(
    ivcf_path,
    gzip=True,
):
    ifile = gz.open(ivcf_path, "rt") if gzip else open(ivcf_path, "rt")
    counter = 0
    with ifile:
        for line in ifile:
            counter += 1
            if line.startswith("#CHROM"):
                vcf_names = [x for x in line.split("\t")]
                break
    return [x.split("\n")[0] for x in vcf_names]


def reheader_vcf(vcf_path, out_vcf_path, gzip=True):
    # Read header names
    names = get_header(
        vcf_path,
        gzip=gzip,
    )
    inds = names[names.index("FORMAT") + 1 :]
    if any(".bam" not in s for s in inds):
        return False
    # Sanitize sample names
    names = [x.replace(".bam", "").split("/")[-1] for x in names]

    # Write meta header lines and sanitized #CHROM line
    ifile = gz.open(vcf_path, "rt") if gzip else open(vcf_path, "rt")
    with ifile:
        with open(out_vcf_path, "wt") as ofile:
            for line in ifile:
                if line.startswith("#CHROM"):
                    ofile.write("\t".join(names))
                    if not names[-1].endswith("\n"):
                        ofile.write("\n")
                    break
                else:
                    ofile.write(line)

    read_kwargs = dict(
        comment_prefix="#",
        separator="\t",
        has_header=False,
        ignore_errors=True,
    )
    try:
        if gzip:
            with gz.open(vcf_path, "rt") as f:
                df = pl.read_csv(f, new_columns=names, **read_kwargs)
        else:
            df = pl.read_csv(vcf_path, new_columns=names, **read_kwargs)
    except TypeError:
        # Fallback for older Polars versions
        if gzip:
            with gz.open(vcf_path, "rt") as f:
                df = pl.read_csv(f, **read_kwargs)
        else:
            df = pl.read_csv(vcf_path, **read_kwargs)
        df = df.rename(dict(zip(df.columns, names)))

    with open(out_vcf_path, "at") as ofile:
        df.write_csv(ofile, separator="\t", include_header=False)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A Python script to remove single/doubletons from individual vcf files"
    )
    parser.add_argument(
        "-v", "--vcf", help="VCF Dataframe", required=True
    )  # VCF file to be mergedd)
    parser.add_argument(
        "-o", "--output", help="Output file path", required=True
    )  # output file path
    parser.add_argument(
        "-gz",
        "--gzip",
        help="Boolean to indicate whether vcf file is gunzip compressed or not (default False)",
        action="store_true",
    )

    args = vars(parser.parse_args())

    # Call the function
    if reheader_vcf(args["vcf"], args["output"], gzip=args["gzip"]):
        os.system(f"bgzip -f {args['output']}")
    else:
        # If reheader is not needed creates symbolik link to previous vcf
        if not os.path.islink(args["output"] + ".gz"):
            os.symlink(os.path.abspath(args["vcf"]), args["output"] + ".gz")
