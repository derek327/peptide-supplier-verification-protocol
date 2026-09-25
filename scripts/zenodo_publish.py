#!/usr/bin/env python3
"""Zenodo 记录上传器（InvenioRDM API）

用法: python3 zenodo_publish.py --record coa-field-taxonomy [--dry-run]
token 从 ~/.hermes/cache/scratch/zen/token.env 读（不进代码、不进日志）。
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
API = "https://zenodo.org/api"
TOKEN_FILE = os.path.expanduser("~/.hermes/cache/scratch/zen/token.env")

RECORDS = {
    "coa-field-taxonomy": {
        "title": "Research Peptide Certificate of Analysis (CoA) Field Taxonomy v1.0",
        "description": (
            "<p>A machine-readable coding scheme for the fields that appear on a research-grade "
            "peptide Certificate of Analysis, together with a completeness-and-consistency scoring "
            "rule set. The taxonomy covers five sections &mdash; product identity, purity and assay, "
            "identity confirmation, residuals and safety, and storage/traceability &mdash; with 30 "
            "fields marked required or optional.</p>"
            "<p>The accompanying scoring model applies five internal-consistency penalties on top of "
            "a completeness count, because a CoA can list every field and still not be auditable "
            "(for example a declared molecular weight that disagrees with the stated sequence). "
            "Completeness minus penalties is banded into four procurement interpretations.</p>"
            "<p>Intended for normalising CoA documents before a procurement review, scoring "
            "documentation completeness across suppliers on a comparable basis, and feeding "
            "automated extraction pipelines.</p>"
            "<p>Worked review examples and the documentation workflow that this taxonomy was "
            "developed for: <a href=\"https://ketebio.com/quality\">ketebio.com/quality</a>. "
            "A GMP-oriented CoA guide using the same field set: "
            "<a href=\"https://helixgmppeptides.com/coa-guide\">helixgmppeptides.com/coa-guide</a>.</p>"
        ),
        "creator": "KeteBio",
        "affiliation": "KeteBio (research peptide documentation)",
        "keywords": [
            "certificate of analysis", "peptide analytics", "documentation review",
            "HPLC purity", "mass spectrometry", "quality documentation", "procurement",
        ],
        "related": [
            {"identifier": "https://ketebio.com/quality", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
            {"identifier": "https://helixgmppeptides.com/coa-guide", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
        ],
        "notes": "Field naming follows common pharmaceutical documentation practice.",
        "version": "1.0",
        "dir": "coa-field-taxonomy",
    },
    "reconstitution-tables": {
        "title": "Peptide Reconstitution and Unit-Conversion Reference Tables (deterministic)",
        "description": (
            "<p>Deterministic reference tables for laboratory reconstitution arithmetic: every value "
            "is computed from two inputs (vial mass, diluent volume) using the formulas documented in "
            "the README, so the tables can be regenerated exactly without any fitted or observed data.</p>"
            "<p>The main table contains 42 combinations (vial mass 2-50&nbsp;mg &times; diluent volume "
            "0.5-10&nbsp;mL) with resulting concentration and the volume required for 100, 250 and "
            "500&nbsp;&micro;g. A second file lists mass/volume unit conversions and explicitly marks "
            "the conversion that must not be attempted: IU cannot be reduced to mass without a "
            "substance-specific bioassay definition.</p>"
            "<p>The README states the limits of the tables: they are arithmetic only, assume complete "
            "dissolution, carry no clinical meaning, and say nothing about reconstituted stability.</p>"
            "<p>Catalog and product documentation: "
            "<a href=\"https://helixpeptidesupply.com/catalog\">helixpeptidesupply.com/catalog</a>. "
            "Research catalog: "
            "<a href=\"https://gethelixpeptide.com/products\">gethelixpeptide.com/products</a>.</p>"
        ),
        "creator": "Helix Peptide Supply",
        "affiliation": "Helix Peptide Supply (laboratory reagents)",
        "keywords": [
            "reconstitution", "unit conversion", "laboratory arithmetic", "peptide handling",
            "reference table", "metrology",
        ],
        "related": [
            {"identifier": "https://helixpeptidesupply.com/catalog", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
            {"identifier": "https://gethelixpeptide.com/products", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
        ],
        "notes": "Values are exact functions of the two inputs; see README formulas.",
        "version": "1.0",
        "dir": "reconstitution-tables",
    },
    "oem-documentation-handover": {
        "title": "OEM / Private-Label Peptide Documentation Handover Checklist v1.0",
        "description": (
            "<p>A checklist dataset defining the documentation a buyer should receive when a "
            "private-label or OEM peptide supply agreement ends and product is handed over: specification "
            "documents, batch records, certificates of analysis, method descriptions, artwork and "
            "labelling approvals, stability data and change-control obligations.</p>"
            "<p>Each item is coded with its stage (pre-award, first article, routine supply, handover), "
            "whether it is contractual or recommended, and the failure mode that occurs when it is "
            "missing &mdash; the practical cost of a missing item is stated so that a buyer can decide "
            "what to insist on before signature rather than after.</p>"
            "<p>OEM services and documentation flow: "
            "<a href=\"https://helixpeptideoem.com/services\">helixpeptideoem.com/services</a>. "
            "Quality documentation framework: "
            "<a href=\"https://jiepeptide.com/quality\">jiepeptide.com/quality</a>.</p>"
        ),
        "creator": "Helix Peptide OEM",
        "affiliation": "Helix Peptide OEM (private-label peptide manufacturing services)",
        "keywords": [
            "OEM", "private label", "documentation handover", "supply agreement",
            "quality agreement", "checklist", "procurement",
        ],
        "related": [
            {"identifier": "https://helixpeptideoem.com/services", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
            {"identifier": "https://jiepeptide.com/quality", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
        ],
        "notes": "Stages follow a typical private-label supply lifecycle.",
        "version": "1.0",
        "dir": "oem-documentation-handover",
    },
    "hplc-purity-reporting": {
        "title": "HPLC Purity Reporting Checklist and Coding Scheme for Research Peptides v1.0",
        "description": (
            "<p>Which fields must accompany a chromatographic purity figure before a third party can "
            "interpret, reproduce or compare it. Ten fields are enumerated, each with a typical value "
            "and the specific reason it matters, derived by asking of every datum normally printed on "
            "a purity report: if this were missing, could a different laboratory reproduce the number?</p>"
            "<p>Four comparability rules state when two purity values may be compared at all - column "
            "chemistry, wavelength, gradient and reporting threshold must match - and four common "
            "failure modes record how an omission shows up in practice, such as a purity quoted to "
            "0.1&nbsp;% while the reporting limit is 1.0&nbsp;%.</p>"
            "<p>Also states the boundary the numbers do not cross: area-% is not content, and content "
            "requires an independent assay.</p>"
            "<p>Quality documentation framework: "
            "<a href=\"https://ruitailab.com/quality\">ruitailab.com/quality</a>. Catalog and product "
            "documentation: "
            "<a href=\"https://helixpeptidesupply.com/catalog\">helixpeptidesupply.com/catalog</a>.</p>"
        ),
        "creator": "RuitaiLab",
        "affiliation": "RuitaiLab (peptide quality documentation)",
        "keywords": [
            "HPLC", "purity", "method reporting", "chromatography", "peptide analytics",
            "comparability", "quality documentation",
        ],
        "related": [
            {"identifier": "https://ruitailab.com/quality", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
            {"identifier": "https://helixpeptidesupply.com/catalog", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
        ],
        "notes": "Fields derived from the reproducibility test; see README method section.",
        "version": "1.0",
        "dir": "hplc-purity-reporting",
    },
}


def token():
    for line in open(TOKEN_FILE, encoding="utf-8"):
        if line.startswith("ZENODO_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("找不到 ZENODO_TOKEN")


def call(method, path, tok, data=None, raw=None, ctype="application/json"):
    url = path if path.startswith("http") else API + path
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read().decode()
            return resp.status, (json.loads(payload) if payload.strip().startswith(("{", "[")) else payload)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()[:600]
    except Exception as exc:  # 网络问题也要给出可读错误
        return 0, str(exc)[:300]


def publish(key, dry=False):
    spec = RECORDS[key]
    directory = os.path.join(OUT, spec["dir"])
    if not os.path.isdir(directory):
        raise SystemExit(f"目录不存在: {directory}")

    metadata = {
        "title": spec["title"],
        "description": spec["description"],
        "resource_type": {"id": "dataset"},
        "creators": [{
            "person_or_org": {"type": "organizational", "name": spec["creator"]},
            "affiliations": [{"name": spec["affiliation"]}],
        }],
        "keywords": spec["keywords"],
        "license": {"id": "cc-by-4.0"},
        "related_identifiers": [
            {"identifier": r["identifier"], "scheme": "url",
             "relation_type": {"id": r["relation"]},
             "resource_type": r["resource_type"]}
            for r in spec["related"]
        ],
        "version": spec["version"],
        "publication_date": __import__("datetime").date.today().isoformat(),
        "notes": spec["notes"],
        "publisher": spec["creator"],
    }
    files = sorted(os.listdir(directory))
    print(f"[{key}] 文件 {len(files)} 个: {', '.join(files)}")
    if dry:
        print(f"[{key}] dry-run：不提交")
        return None

    tok = token()
    code, res = call("POST", "/records", tok, data={"metadata": metadata})
    if code not in (200, 201):
        print(f"[{key}] 建草稿失败 HTTP {code}: {res}")
        return None
    rec_id = res["id"]
    draft_files = res["links"]["files"]
    print(f"[{key}] 草稿 id={rec_id}")

    for name in files:
        path = os.path.join(directory, name)
        with open(path, "rb") as fh:
            blob = fh.read()
        code, res = call("POST", f"{draft_files}", tok,
                         data=[{"key": name}], ctype="application/json")
        if code not in (200, 201, 202):
            print(f"  文件登记失败 {name}: HTTP {code} {res}")
            return None
        code, res = call("PUT", f"{draft_files}/{name}/content", tok, raw=blob,
                         ctype="application/octet-stream")
        if code not in (200, 201, 202):
            print(f"  内容上传失败 {name}: HTTP {code} {res}")
            return None
        code, res = call("POST", f"{draft_files}/{name}/commit", tok)
        if code not in (200, 201, 202):
            print(f"  提交文件失败 {name}: HTTP {code} {res}")
            return None
        print(f"  ✓ {name} ({len(blob)} B)")

    code, res = call("POST", f"/records/{rec_id}/draft/actions/publish", tok)
    if code not in (200, 201, 202):
        print(f"[{key}] 发布失败 HTTP {code}: {res}")
        return None
    print(f"[{key}] ✅ 已发布  DOI={res.get('doi')}  {res.get('links', {}).get('self_html')}")
    return {"id": rec_id, "doi": res.get("doi"), "url": res.get("links", {}).get("self_html")}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", required=True, choices=list(RECORDS))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.exit(0 if publish(args.record, args.dry_run) else 1)
