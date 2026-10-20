"""Protect the scientific report from mixed meshes, data and meanings."""

import hashlib
import io
import json
import zipfile

import numpy as np
from pypdf import PdfReader
import pytest

import study_data
from build_submission import build_package
from study_data import load_studies, study_rows


def test_completed_studies_preserve_selected_mesh_and_flux_definitions():
    selected, cases, profiles, manifest = load_studies()
    assert len(cases) == 19
    assert cases.n_outer.eq(96).all() and cases.n_inner.eq(128).all()
    for row in cases.itertuples():
        q = profiles[profiles.case.eq(row.case)]
        np.testing.assert_allclose(q.deviation_percent, 100*(q.flux_w_m2-row.mean_inner_flux_w_m2)/abs(row.mean_inner_flux_w_m2), atol=1e-10)
        assert row.heat_inner_w_m == pytest.approx(2*np.pi*row.r*row.mean_inner_flux_w_m2, rel=1e-10)


def test_temperature_scales_absolute_flux_without_changing_relative_shape():
    _, cases, profiles, _ = load_studies()
    rows = study_rows(cases, "temperature")
    assert np.all(np.diff(rows.mean_inner_flux_w_m2) > 0)
    reference = profiles[profiles.case.eq(rows.iloc[0]["case"])].deviation_percent.to_numpy()
    for case in rows.case:
        np.testing.assert_allclose(profiles[profiles.case.eq(case)].deviation_percent, reference, atol=1e-8)
    assert rows.max_deviation_percent.max()-rows.max_deviation_percent.min() < 1e-8


def test_centered_reference_is_uniform_and_offset_study_is_eccentric_elsewhere():
    _, cases, _, _ = load_studies()
    rows = study_rows(cases, "offset")
    assert rows.iloc[0].d == 0
    assert rows.iloc[0].max_deviation_percent < 1e-8
    assert (rows.iloc[1:].d > 0).all()
    assert np.all(np.diff(rows.max_deviation_percent) > 0)


def test_pdf_report_was_built_from_the_current_markdown_report():
    report = PdfReader(study_data.ROOT/"docs"/"REPORT.pdf")
    assert report.metadata["/ReportSourceSHA256"] == study_data.text_hash(study_data.ROOT/"docs"/"REPORT.md")
    assert len(report.pages) > 10


def test_altered_profile_data_are_rejected(tmp_path, monkeypatch):
    for name in ("cases.csv", "profiles.csv", "manifest.json"):
        (tmp_path/name).write_bytes((study_data.DATA/name).read_bytes())
    with (tmp_path/"profiles.csv").open("a", encoding="utf-8") as stream:
        stream.write("altered data\n")
    monkeypatch.setattr(study_data, "DATA", tmp_path)
    with pytest.raises(ValueError, match="changed"):
        load_studies()


def test_data_integrity_survives_windows_or_linux_line_endings(tmp_path, monkeypatch):
    for name in ("cases.csv", "profiles.csv"):
        data = (study_data.DATA/name).read_bytes().replace(b"\r\n", b"\n")
        (tmp_path/name).write_bytes(data.replace(b"\n", b"\r\n"))
    (tmp_path/"manifest.json").write_bytes((study_data.DATA/"manifest.json").read_bytes())
    monkeypatch.setattr(study_data, "DATA", tmp_path)
    _, cases, profiles, _ = load_studies()
    assert len(cases) == 19 and len(profiles) == 19*128


def test_submission_contains_every_required_source_report_and_verified_data():
    with zipfile.ZipFile(io.BytesIO(build_package())) as archive:
        required = {"scripts/radiation.py", "scripts/run_assignment.py", "scripts/run_discretization.py",
                    "scripts/run_parameter_studies.py", "scripts/streamlit_app.py",
                    "docs/MODEL.md", "docs/REPORT.md", "docs/REPORT.pdf", "docs/REQUIREMENTS.md",
                    "results/studies/cases.csv", "results/studies/profiles.csv",
                    "results/studies/offset_study.png", "results/studies/radius_study.png", "results/studies/temperature_study.png"}
        assert required.issubset(archive.namelist())
        assert not any("secrets" in name or name.startswith(("tmp/", ".git/", "output/")) for name in archive.namelist())
        assert "docs/PLAN.md" not in archive.namelist()
        manifest = json.loads(archive.read("SUBMISSION_MANIFEST.json"))
        for name, fingerprint in manifest["files_sha256"].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == fingerprint
