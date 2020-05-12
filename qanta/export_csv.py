import json
import typer
import pandas as pd


app = typer.Typer()


@app.command()
def main(output: str):
    with open("data/qanta.mapped.2018.04.18.json") as f:
        questions = [q for q in json.load(f)["questions"] if q["page"] is not None]

    grouped = {}
    for q in questions:
        if q["page"] not in grouped:
            grouped[q["page"]] = []
        qdb_id = q["qdb_id"]
        if qdb_id is None:
            qdb_id = -1

        proto_id = q["proto_id"]
        if proto_id is None:
            proto_id = -1
        grouped[q["page"]].append(
            [q["qanta_id"], qdb_id, proto_id, q["page"], q["answer"],]
        )

    rows = []
    for page, batch in grouped.items():
        rows.extend(batch)
    df = pd.DataFrame(
        rows, columns=["qanta_id", "qdb_id", "proto_id", "answer", "raw_answer"]
    )
    print(df.head())
    df.to_csv(output)


if __name__ == "__main__":
    app()
