"""Deterministic finding -> control mapping. Pure lookup, no LLM."""
import json
from pathlib import Path
from backend.schemas import Finding, Mapping

_ONTOLOGY = json.loads((Path(__file__).parent / "ontology.json").read_text())


def map_finding(finding: Finding) -> list[Mapping]:
    entry = _ONTOLOGY.get(finding.type, {})
    out: list[Mapping] = []
    for framework, controls in entry.items():
        for c in controls:
            out.append(Mapping(
                framework=framework,
                control_id=c["control_id"],
                title=c["title"],
            ))
    return out


if __name__ == "__main__":
    from backend.graph.parsers import load_all_findings

    findings = load_all_findings()
    sample = findings[0]
    print("Sample finding: {} / {}".format(sample.type, sample.description[:60]))
    print("Maps to:")
    for m in map_finding(sample):
        print("  {} {} -- {}".format(m.framework, m.control_id, m.title))

    print("\nMappings per finding type:")
    seen_types = set(f.type for f in findings)
    for t in sorted(seen_types):
        dummy = Finding(id="x", type=t, file="x", severity="high", description="x")
        print("  {}: {} mappings".format(t, len(map_finding(dummy))))
