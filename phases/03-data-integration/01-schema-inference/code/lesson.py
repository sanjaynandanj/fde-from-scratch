"""FLAGSHIP - Schema inference from scratch: types, nulls, and lies.

Customer exports never come with a data dictionary. Infer per-column type,
nullability, and uniqueness from string samples - and survive the lies:
thousands separators, N/A-style nulls, leading-zero IDs that are NOT ints,
and three date formats in one column.
"""

from datetime import datetime

NULL_TOKENS = {"", "n/a", "na", "null", "none", "-", "nil", "#n/a"}
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y", "%Y/%m/%d"]


def is_null(v: str) -> bool:
    return v.strip().lower() in NULL_TOKENS


def try_int(v: str):
    s = v.strip().replace(",", "")
    if s.startswith("0") and len(s) > 1:
        return None  # leading zero => identifier, not a number
    try:
        return int(s)
    except ValueError:
        return None


def try_float(v: str):
    s = v.strip().replace(",", "")
    if s.startswith("0") and len(s) > 1 and s[1] != ".":
        return None  # same leading-zero rule: 00042 is an ID, 0.5 is a number
    try:
        return float(s)
    except ValueError:
        return None


def try_date(v: str):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(v.strip(), fmt).date()
        except ValueError:
            continue
    return None


def try_bool(v: str):
    m = {"true": True, "false": False, "yes": True, "no": False, "y": True, "n": False}
    return m.get(v.strip().lower())


def infer_column(name: str, values: list[str]) -> dict:
    non_null = [v for v in values if not is_null(v)]
    null_count = len(values) - len(non_null)
    checks = [
        ("bool", lambda v: try_bool(v) is not None),
        ("int", lambda v: try_int(v) is not None),
        ("float", lambda v: try_float(v) is not None),
        ("date", lambda v: try_date(v) is not None),
    ]
    inferred = "string"
    for type_name, check in checks:
        if non_null and all(check(v) for v in non_null):
            inferred = type_name
            break
    return {
        "name": name,
        "type": inferred,
        "nullable": null_count > 0,
        "null_rate": round(null_count / len(values), 3) if values else 0.0,
        "unique": len(set(v.strip() for v in non_null)) == len(non_null),
    }


def infer_schema(header: list[str], rows: list[list[str]]) -> list[dict]:
    cols = list(zip(*rows)) if rows else [[] for _ in header]
    return [infer_column(h, list(col)) for h, col in zip(header, cols)]


def main():
    header = ["emp_id", "name", "salary", "hired", "active", "dept_code", "bonus"]
    rows = [
        ["101", "Ada Lovelace", "1,250.50", "2021-03-15", "yes", "00042", "N/A"],
        ["102", "Grace Hopper", "2,100.00", "15/07/2020", "no", "00042", "500"],
        ["103", "Alan Turing", "1,800.75", "03-01-2022", "yes", "00108", ""],
        ["104", "Mary Jackson", "1,950.00", "12-Mar-2019", "yes", "00042", "750"],
    ]
    schema = {c["name"]: c for c in infer_schema(header, rows)}

    assert schema["emp_id"]["type"] == "int" and schema["emp_id"]["unique"]
    assert schema["name"]["type"] == "string"
    assert schema["salary"]["type"] == "float", "commas must not break numerics"
    assert schema["hired"]["type"] == "date", "must survive 4 date formats"
    assert schema["active"]["type"] == "bool"
    assert schema["dept_code"]["type"] == "string", "leading zeros mean identifier"
    assert not schema["dept_code"]["unique"]
    assert schema["bonus"]["type"] == "int" and schema["bonus"]["nullable"]
    assert schema["bonus"]["null_rate"] == 0.5

    # int column with one stray string must degrade to string, not crash
    degraded = infer_column("qty", ["1", "2", "TBD", "4"])
    assert degraded["type"] == "string"

    # all-null column stays string and nullable
    empty = infer_column("notes", ["", "N/A", "null"])
    assert empty["type"] == "string" and empty["nullable"] and empty["null_rate"] == 1.0

    print("schema-inference: all assertions passed (7 columns + 2 edge cases)")


if __name__ == "__main__":
    main()
