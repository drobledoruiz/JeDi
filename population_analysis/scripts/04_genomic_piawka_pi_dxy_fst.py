import argparse

import polars as pl


def parse_piawka_dxy(
    input_filename,
):
    # Name output files
    wdir = "/".join(input_filename.split("/")[:-1])
    if "/" in input_filename:
        wdir += "/"
    output_pi_filename = wdir + "genomic_pi_table.tsv"
    output_dxy_filename1 = wdir + "genomic_dxy_table.tsv"
    output_dxy_filename2 = wdir + "genomic_dxy_matrix.tsv"
    output_fst_filename1 = wdir + "genomic_fst_table.tsv"
    output_fst_filename2 = wdir + "genomic_fst_matrix.tsv"

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
        "column_10": pl.Int32,
        "column_11": pl.Int32,
    }

    names = [
        "locus",
        "nSites",
        "pop1",
        "pop2",
        "nUsed ",
        "metric",
        "value",
        "numerator",
        "denominator",
        "nGenotypes",
        "nMissing",
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
        "column_10",
        "column_11",
    ]

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

    # Filters per metric (as dict rows)
    rows_pi = (
        df.filter(pl.col("metric") == "pi").select(["pop1", "numerator", "denominator"]).to_dicts()
    )
    rows_dxy = (
        df.filter(pl.col("metric") == "Dxy")
        .select(["pop1", "pop2", "numerator", "denominator"])
        .to_dicts()
    )
    rows_fst = df.filter(pl.col("metric") == "Fst_HUD").select(["pop1", "pop2", "value"]).to_dicts()

    # --------------------------------------------------
    # PI Table
    agg_pi = {}
    for r in rows_pi:
        p = r["pop1"]
        agg_pi.setdefault(p, {"diffs": 0.0, "comps": 0.0})
        agg_pi[p]["diffs"] += float(r["numerator"]) if r["numerator"] is not None else 0.0
        agg_pi[p]["comps"] += float(r["denominator"]) if r["denominator"] is not None else 0.0
    pi_rows = []
    for p in sorted(agg_pi.keys()):
        diffs = agg_pi[p]["diffs"]
        comps = agg_pi[p]["comps"]
        pi_rows.append(
            {"pop1": p, "diffs": diffs, "comps": comps, "pi": (diffs / comps) if comps else 0.0}
        )
    pl.DataFrame(pi_rows).write_csv(
        output_pi_filename,
        separator="\t",
    )

    # --------------------------------------------------
    # DXY Table
    agg_dxy = {}
    pops2 = set()
    for r in rows_dxy:
        key = (r["pop1"], r["pop2"])
        pops2.add(r["pop2"])
        agg_dxy.setdefault(key, {"diffs": 0.0, "comps": 0.0})
        agg_dxy[key]["diffs"] += float(r["numerator"]) if r["numerator"] is not None else 0.0
        agg_dxy[key]["comps"] += float(r["denominator"]) if r["denominator"] is not None else 0.0
    dxy_rows = []
    for p1, p2 in sorted(agg_dxy.keys()):
        diffs = agg_dxy[(p1, p2)]["diffs"]
        comps = agg_dxy[(p1, p2)]["comps"]
        dxy_rows.append(
            {
                "pop1": p1,
                "pop2": p2,
                "diffs": diffs,
                "comps": comps,
                "dxy": (diffs / comps) if comps else 0.0,
            }
        )
    pl.DataFrame(dxy_rows).write_csv(output_dxy_filename1, separator="\t")

    # DXY Matrix manual pivot
    pops1 = sorted({p1 for (p1, _p2) in agg_dxy.keys()})
    pops2_sorted = sorted(pops2)
    with open(output_dxy_filename2, "w") as f:
        f.write("pop1\t" + "\t".join(pops2_sorted) + "\n")
        for p1 in pops1:
            row = [p1]
            for p2 in pops2_sorted:
                diffs = agg_dxy.get((p1, p2), {}).get("diffs", 0.0)
                comps = agg_dxy.get((p1, p2), {}).get("comps", 0.0)
                row.append(str((diffs / comps) if comps else 0.0))
            f.write("\t".join(row) + "\n")

    # --------------------------------------------------
    # FST Table
    agg_fst = {}
    pops2_fst = set()
    for r in rows_fst:
        key = (r["pop1"], r["pop2"])
        pops2_fst.add(r["pop2"])
        agg_fst.setdefault(key, [])
        agg_fst[key].append(float(r["value"]))

    def mean_std(vals):
        n = len(vals)
        if n == 0:
            return 0.0, 0.0
        m = sum(vals) / n
        if n == 1:
            return m, 0.0
        var = sum((x - m) ** 2 for x in vals) / (n - 1)
        return m, var**0.5

    fst_rows = []
    for p1, p2 in sorted(agg_fst.keys()):
        m, s = mean_std(agg_fst[(p1, p2)])
        fst_rows.append({"pop1": p1, "pop2": p2, "avg_fst": m, "std_fst": s})
    pl.DataFrame(fst_rows).write_csv(output_fst_filename1, separator="\t")

    # FST Matrix manual pivot
    pops1_fst = sorted({p1 for (p1, _p2) in agg_fst.keys()})
    pops2_fst_sorted = sorted(pops2_fst)
    with open(output_fst_filename2, "w") as f:
        f.write("pop1\t" + "\t".join(pops2_fst_sorted) + "\n")
        for p1 in pops1_fst:
            row = [p1]
            for p2 in pops2_fst_sorted:
                m, _s = mean_std(agg_fst.get((p1, p2), []))
                row.append(str(m))
            f.write("\t".join(row) + "\n")
    del df
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Python script to reduce a pixy PI dataframe.")
    parser.add_argument("filename", help="The path of the dataframe")  # positional argument
    args = vars(parser.parse_args())
    parse_piawka_dxy(
        args["filename"],
    )
