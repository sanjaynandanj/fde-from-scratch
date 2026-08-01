"""FLAGSHIP - Back-of-envelope engine: estimation with explicit error bars.

Decomp interviews and week-one scoping both run on estimates. Amateurs give
a number; professionals give a range and show the factor tree. Build a tiny
interval-arithmetic engine, then estimate a real pilot question with it:
"how much storage does one year of this hospital's HL7 feed need?"
"""


class Range:
    """A quantity known only to within [low, high]."""

    def __init__(self, low: float, high: float, label: str = ""):
        assert 0 < low <= high, f"bad range for {label}: [{low}, {high}]"
        self.low, self.high, self.label = low, high, label

    def __mul__(self, other):
        o = other if isinstance(other, Range) else Range(other, other)
        return Range(self.low * o.low, self.high * o.high)

    def __truediv__(self, other):
        o = other if isinstance(other, Range) else Range(other, other)
        return Range(self.low / o.high, self.high / o.low)

    def mid(self) -> float:
        return (self.low * self.high) ** 0.5   # geometric mean fits spans of 10x

    def spread(self) -> float:
        return self.high / self.low

    def contains(self, x: float) -> bool:
        return self.low <= x <= self.high

    def __repr__(self):
        return f"[{self.low:,.3g} .. {self.high:,.3g}]"


def main():
    # --- engine sanity ---------------------------------------------------
    a, b = Range(2, 4), Range(10, 20)
    p = a * b
    assert (p.low, p.high) == (20, 80)
    q = b / a
    assert (q.low, q.high) == (2.5, 10), "division must cross-multiply bounds"
    assert Range(9, 16).mid() == 12.0
    assert a.spread() == 2.0

    # scalars mix in
    s = a * 10
    assert (s.low, s.high) == (20, 40)

    # invalid range is rejected loudly
    try:
        Range(5, 2, "backwards")
        raise AssertionError("should reject low > high")
    except AssertionError as e:
        assert "backwards" in str(e)

    # --- the actual estimate --------------------------------------------
    # Q: storage for one year of HL7 messages at a 400-bed hospital?
    beds = Range(350, 450, "beds")
    admissions_per_bed_per_year = Range(40, 60, "admissions/bed/yr")
    messages_per_admission = Range(100, 300, "HL7 msgs/admission")
    bytes_per_message = Range(1_000, 4_000, "bytes/msg")

    total_bytes = beds * admissions_per_bed_per_year * messages_per_admission * bytes_per_message
    total_gb = total_bytes / 1e9

    # the range must bracket the "true" reference answer (~10.4 GB midpoint)
    reference_gb = 400 * 50 * 200 * 2500 / 1e9   # = 10.0
    assert total_gb.contains(reference_gb), f"{total_gb} must contain {reference_gb}"
    assert 1 < total_gb.low < total_gb.high < 100, "answer is single-digit-to-tens of GB"

    # error bars compound: 4 factors of ~1.3-3x spread => total spread 10-25x
    assert 10 < total_gb.spread() < 25

    # the punchline every interviewer wants: state the decision the number drives
    decision = "fits on one Postgres instance; no data-lake conversation needed"
    assert total_gb.high < 100, decision

    print(f"estimation-engine: all assertions passed "
          f"(1yr HL7 ~ {total_gb} GB, mid {total_gb.mid():.1f} GB -> {decision})")


if __name__ == "__main__":
    main()
