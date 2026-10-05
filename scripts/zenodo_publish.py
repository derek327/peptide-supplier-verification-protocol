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
OUT = os.path.join(os.path.dirname(HERE), "out")
API = "https://zenodo.org/api"
# token 查找顺序：环境变量 → 持久目录 → 临时目录（scratch 目录闲置 24h 会被清理，不能只依赖它）
TOKEN_FILES = [
    os.path.expanduser("~/.hermes/secrets/zenodo.env"),
    os.path.expanduser("~/.hermes/cache/scratch/zen/token.env"),
]

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
    "temperature-excursion-mkt": {
        "title": "Shipment Temperature Excursion Reference Tables: MKT Profiles and Triage Matrix",
        "description": (
            "<p>Deterministic reference tables for reviewing a shipment temperature log against a "
            "declared +2 to +8&nbsp;&deg;C transport range. Two data files are provided: 24 "
            "transport profiles (each a 48&nbsp;h baseline temperature plus one excursion of "
            "stated magnitude and duration) with mean kinetic temperature computed at two "
            "activation energies, and an 18-row triage matrix mapping declared product band "
            "&times; peak temperature &times; duration outside band to a documentation action.</p>"
            "<p>Every value is computed from the published MKT formula and a stated activation "
            "energy (83.144 and 62.8&nbsp;kJ/mol) &mdash; no measured or fitted data is involved, "
            "so the tables can be regenerated exactly. Invariance checks applied before release: "
            "a constant-temperature profile returns that temperature exactly, and a hot spike "
            "raises MKT above the arithmetic mean.</p>"
            "<p>The README states plainly what the numbers do not support: MKT hides peaks, the "
            "activation energy is a modelling assumption rather than a measured property, and "
            "whether a molecule changed is an assay question that these tables cannot answer.</p>"
            "<p>The triage walkthrough and the full excursion documentation file specification: "
            "<a href=\"https://helixgmppeptides.com/coa-guide\">helixgmppeptides.com/coa-guide</a>. "
            "Catalog and shipping documentation: "
            "<a href=\"https://helixpeptidesupply.com/catalog\">helixpeptidesupply.com/catalog</a>.</p>"
        ),
        "creator": "Helix GMP Peptides",
        "affiliation": "Helix GMP Peptides (quality documentation)",
        "keywords": [
            "cold chain", "temperature excursion", "mean kinetic temperature", "MKT",
            "shipping documentation", "peptide handling", "quality documentation", "procurement",
        ],
        "related": [
            {"identifier": "https://helixgmppeptides.com/coa-guide", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
            {"identifier": "https://helixpeptidesupply.com/catalog", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
        ],
        "notes": "All values are exact functions of the stated profile and activation energy; see README formulas.",
        "version": "1.0",
        "dir": "temperature-excursion-mkt",
    },
    "purity-content-math": {
        "title": "Purity vs Peptide Content: Net-Peptide Mass and Mass-Balance Reference Tables",
        "description": (
            "<p>Deterministic reference tables for the arithmetic that relates a chromatographic "
            "purity figure (area-%) to the net peptide in a weighed research-peptide sample. Two "
            "data files and one script are provided: 12 samples at 10&nbsp;mg label mass across "
            "free-base, acetate and trifluoroacetate forms with water content, counterion content "
            "and the resulting peptide content as-is, a sensitivity table crossing fixed purity "
            "with water content from 0 to 12&nbsp;%, and a command-line calculator with a "
            "self-test.</p>"
            "<p>All values are computed from two published relations and the stated inputs "
            "&mdash; no measured or fitted data is involved, so the tables can be regenerated "
            "exactly. Invariance checks applied before release: a material at 100&nbsp;% purity "
            "with no water or counterion returns exactly 100&nbsp;% content, content falls "
            "strictly as water rises, and no row yields more peptide than the label mass, so the "
            "overstatement factor exceeds one throughout.</p>"
            "<p>The README states plainly what the numbers do not support: the multiplicative "
            "model is a review estimate rather than an assay, area-% is not content, counterion "
            "stoichiometry need not be one-to-one, and water content moves with handling.</p>"
            "<p>Quality documentation structure and the review workflow this work supports: "
            "<a href=\"https://gethelixpeptide.com/quality\">gethelixpeptide.com/quality</a>. "
            "Product-level documentation and batch records: "
            "<a href=\"https://gethelixpeptide.com/products\">gethelixpeptide.com/products</a>.</p>"
        ),
        "creator": "Helix Peptide Research",
        "affiliation": "Helix Peptide Research (research peptide documentation)",
        "keywords": [
            "peptide content", "HPLC purity", "mass balance", "Karl Fischer",
            "counterion", "trifluoroacetate", "documentation review", "procurement",
        ],
        "related": [
            {"identifier": "https://gethelixpeptide.com/quality", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
            {"identifier": "https://gethelixpeptide.com/products", "relation": "isdocumentedby",
             "resource_type": {"id": "publication-other"}},
        ],
        "notes": "All values are exact functions of the stated inputs; see README formulas.",
        "version": "1.0",
        "dir": "purity-content-math",
    },
}


def preflight(spec):
    """铁律自检：缺锚点/缺 publisher/related 格式不对，直接拒绝提交（避免白做一波）"""
    problems = []
    if not spec.get("creator"):
        problems.append("缺 creator（脚本用 creator 填 publisher，缺则 400）")
    if '<a href="' not in spec.get("description", ""):
        problems.append("description 里没有 <a href> 锚点（正文链接不会渲染）")
    for r in spec.get("related", []):
        if "relation" not in r or not isinstance(r.get("resource_type"), dict):
            problems.append(f"related_identifiers 旧格式: {r.get('identifier')}")
    if not spec.get("dir"):
        problems.append("缺 dir")
    return problems


def token():
    env = os.environ.get("ZENODO_TOKEN")
    if env:
        return env.strip()
    for path in TOKEN_FILES:
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            if line.startswith("ZENODO_TOKEN="):
                val = line.split("=", 1)[1].strip()
                if val:
                    return val
    raise SystemExit("找不到 ZENODO_TOKEN（查过环境变量与 %s）" % ", ".join(TOKEN_FILES))


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
    problems = preflight(spec)
    if problems:
        print(f"[{key}] ❌ 铁律自检未通过，拒绝提交：")
        for p in problems:
            print(f"   - {p}")
        return None
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
