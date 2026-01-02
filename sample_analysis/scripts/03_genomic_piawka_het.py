import argparse

import polars as pl


def parse_piawka_het(input_filename, pop_filename):
    # Name output files
    wdir = "/".join(input_filename.split("/")[:-1])
    if "/" in input_filename:
        wdir += "/"
    output_het_filename = wdir + "genomic_het_table.tsv"

    names = [
        "locus",
        "nSites",
        "pop1",
        "pop2",
        "nUsed",
        "metric",
        "value",
        "numerator",
        "denominator",
    ]
    cols = [
        "column_1",
        "column_2",
        "column_3",
        "column_4",
        "column_5",
        "column_6",
        "column_7",
        "column_8",
        "column_9",
    ]

    schema = {
        "column_1": pl.String,
        "column_2": pl.Int32,
        "column_3": pl.String,
        "column_4": pl.String,
        "column_5": pl.Int32,
        "column_6": pl.String,
        "column_7": pl.Float64,
        "column_8": pl.Float64,
        "column_9": pl.Float64,
        "column_10": pl.String,
        "column_11": pl.String,
    }

    # Read data into a DataFrame (avoid LazyFrame.rename segfaults)
    try:
        df = pl.read_csv(
            input_filename,
            separator="\t",
            has_header=False,
            schema=schema,
            ignore_errors=True,
            new_columns=names,
        )
    except TypeError:
        df = pl.read_csv(
            input_filename,
            separator="\t",
            has_header=False,
            schema=schema,
            ignore_errors=True,
        ).rename(dict(zip(cols, names)))

    # Filters per metric and aggregate without group_by to avoid segfaults
    df_het_rows = (
        df.filter(pl.col("metric") == "het").select(["pop1", "numerator", "denominator"]).to_dicts()
    )
    agg = {}
    for r in df_het_rows:
        p = r["pop1"]
        agg.setdefault(p, {"numerator": 0.0, "denominator": 0.0})
        agg[p]["numerator"] += float(r["numerator"]) if r["numerator"] is not None else 0.0
        agg[p]["denominator"] += float(r["denominator"]) if r["denominator"] is not None else 0.0

    out_rows = []
    for p in sorted(agg.keys()):
        num = agg[p]["numerator"]
        den = agg[p]["denominator"] or 0.0
        het = (num / den) if den else 0.0
        out_rows.append({"pop1": p, "numerator": num, "denominator": den, "het": het})

    pl.DataFrame(out_rows).write_csv(output_het_filename, separator="\t")
    del df
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Python script to reduce a pixy Het dataframe.")
    parser.add_argument("filename", help="The path of the dataframe")  # positional argument
    parser.add_argument("-p", "--pop", help="Population Dataframe", default="")
    args = vars(parser.parse_args())
    parse_piawka_het(args["filename"], args["pop"])
