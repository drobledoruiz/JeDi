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


def write_header(ivcf_path, ovcf_path, gzip=True):
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


def get_header(ivcf_path, gzip=True):
    ifile = gz.open(ivcf_path, "rt") if gzip else open(ivcf_path, "rt")
    with ifile:
        for line in ifile:
            if line.startswith("#CHROM"):
                vcf_names = [x for x in line.split("\t")]
                break
    return [x.split("\n")[0] for x in vcf_names]


def filter_singletons_vcf(vcf_path, out_vcf_path, singletons_path, indv_name, gzip=True):
    # Read positions to remove for the given individual
    dfs = pl.read_csv(singletons_path, separator="\t")
    positions = (
        dfs.filter(pl.col("INDV") == indv_name)
        .select([pl.col("CHROM").alias("#CHROM"), pl.col("POS")])
        .to_dicts()
    )

    # If there are no positions to remove, do nothing
    if len(positions) == 0:
        return False

    # Read header names and write sanitized header block
    names = get_header(vcf_path, gzip=gzip)
    names = [x.replace(".bam", "").split("/")[-1] for x in names]
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

    # Read into a DataFrame (avoid LazyFrame.rename segfaults)
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
        try:
            if gzip:
                with gz.open(vcf_path, "rt") as f:
                    df = pl.read_csv(f, columns=names, **read_kwargs)  # type: ignore[arg-type]
            else:
                df = pl.read_csv(vcf_path, columns=names, **read_kwargs)  # type: ignore[arg-type]
        except TypeError:
            if gzip:
                with gz.open(vcf_path, "rt") as f:
                    df = pl.read_csv(f, **read_kwargs)
            else:
                df = pl.read_csv(vcf_path, **read_kwargs)
            if len(df.columns) != len(names):
                raise MyException(
                    f"Column count mismatch between data ({len(df.columns)}) and header ({len(names)})"
                )
            df = df.rename(dict(zip(df.columns, names)))

    # Drop rows matching singleton positions for the given individual
    df = df.filter(~(pl.struct(["#CHROM", "POS"]).is_in(positions)))

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
        "-s", "--singletons", help="Singletons file path", required=True
    )  # output file path
    parser.add_argument("-n", "--name", help="Name of the individual", required=True)
    parser.add_argument(
        "-gz",
        "--gzip",
        help="Boolean to indicate whether vcf file is gunzip compressed or not (default False)",
        action="store_true",
    )

    args = vars(parser.parse_args())

    # Call the function
    if filter_singletons_vcf(
        args["vcf"], args["output"], args["singletons"], args["name"], gzip=args["gzip"]
    ):
        os.system(f"bgzip -f {args['output']}")
        os.system(f"bcftools index -c {args['output'] + '.gz'}")
    else:
        # If there are no position to remove, create symbolik link to previous vcf
        if not os.path.islink(args["output"] + ".gz"):
            os.symlink(os.path.abspath(args["vcf"]), args["output"] + ".gz")
        if not os.path.islink(args["output"] + "gz.csi"):
            os.symlink(os.path.abspath(args["vcf"] + ".csi"), args["output"] + ".gz.csi")
