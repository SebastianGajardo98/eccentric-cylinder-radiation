"""Exercise the delivered report rather than a source-only checklist."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_report_navigation_and_all_required_studies_render():
    app = AppTest.from_file(Path(__file__).resolve().parents[1]/"scripts"/"streamlit_app.py", default_timeout=30).run()
    assert app.radio(key="report_section").value == "Assignment"
    assert not app.exception and not app.error
    app.button(key="next_section").click().run()
    assert app.radio(key="report_section").value == "(a) Model"
    assert not app.exception and not app.error
    app.button(key="next_section").click().run()
    for refinement in ("Outer surface A", "Inner surface B", "Integration tolerance"):
        app.get("button_group")[0].set_value(refinement).run()
        assert not app.exception and not app.error
    app.button(key="next_section").click().run()
    for study, count in (("Center distance d", 7), ("Inner radius r", 5), ("Inner temperature T_B", 6)):
        app.get("button_group")[0].set_value(study).run()
        assert not app.exception and not app.error
        assert len(app.dataframe[0].value) == count
    app.button(key="next_section").click().run()
    assert app.radio(key="report_section").value == "(c) Discussion and conclusions"
    assert not app.exception and not app.error
