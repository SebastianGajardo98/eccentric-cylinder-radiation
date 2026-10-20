"""Create a self-contained code, report, figure and data package."""

import hashlib
import io
import json
import zipfile

from study_data import DATA, MESH, ROOT, SCRIPTS, load_studies

PROJECT_FILES = ("requirements.txt", "requirements-dev.txt", "pytest.ini", "README.md", ".streamlit/config.toml")
DOC_FILES = ("ASSIGNMENT.md", "MODEL.md", "GEOMETRY.md", "COMPARISON.md", "CODE_GUIDE.md", "DISCRETIZATION.md", "PARAMETERS.md", "REPORT.md", "REPORT.pdf", "REQUIREMENTS.md")


def submission_files():
    files = [ROOT / name for name in PROJECT_FILES]
    files += sorted(SCRIPTS.glob("*.py"))
    files += [ROOT / "docs" / name for name in DOC_FILES]
    files += sorted((ROOT / "tests").glob("test_*.py"))
    for pattern in ("independent_*", "qualification_96_128_*", "worst_case_*", "support_96_128_*", "selected.json", "discretization_selection.*"):
        files += sorted(MESH.glob(pattern))
    files += sorted(p for p in DATA.iterdir() if p.is_file())
    missing = [str(p.relative_to(ROOT)) for p in files if not p.is_file()]
    if missing:
        raise FileNotFoundError("Incomplete submission files: "+", ".join(missing))
    return sorted(set(files))


def build_package():
    selection, cases, profiles, evidence = load_studies()
    content = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in submission_files()}
    manifest = {
        "solver_sha256": evidence["solver_sha256"],
        "selected_mesh": [selection["n_outer"], selection["n_inner"]],
        "case_count": len(cases),
        "files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in content.items()},
        "reproduce": "python scripts/run_assignment.py",
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in content.items():
            archive.writestr(name, data)
        archive.writestr("SUBMISSION_MANIFEST.json", json.dumps(manifest, indent=2)+"\n")
    return buffer.getvalue()


def main():
    output = ROOT / "output" / "eccentric-cylinder-assignment.zip"
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(build_package())
    print(f"Submission package: {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
