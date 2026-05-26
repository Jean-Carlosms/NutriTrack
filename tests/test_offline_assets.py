from pathlib import Path

from tests.test_app import make_app, valid_profile_payload


TEMPLATE_DIR = Path("app/templates")
BLOCKED_EXTERNAL_ASSETS = [
    "cdn.jsdelivr",
    "unpkg",
    "cdnjs",
    "cloudflare",
    "https://",
    "http://",
]


def test_base_template_references_local_vendor_assets():
    content = (TEMPLATE_DIR / "base.html").read_text(encoding="utf-8")

    assert "vendor/bootstrap/css/bootstrap.min.css" in content
    assert "vendor/bootstrap/js/bootstrap.bundle.min.js" in content
    assert "vendor/chartjs/chart.umd.min.js" in content
    assert "url_for('static'" in content


def test_templates_do_not_reference_external_asset_hosts():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in TEMPLATE_DIR.glob("*.html")
    )

    for blocked in BLOCKED_EXTERNAL_ASSETS:
        assert blocked not in combined


def test_vendor_asset_files_exist():
    expected_files = [
        Path("app/static/vendor/bootstrap/css/bootstrap.min.css"),
        Path("app/static/vendor/bootstrap/js/bootstrap.bundle.min.js"),
        Path("app/static/vendor/chartjs/chart.umd.min.js"),
    ]

    for path in expected_files:
        assert path.exists()
        assert path.stat().st_size > 0


def test_core_pages_render_with_local_assets():
    app = make_app()
    client = app.test_client()
    client.post("/profile", data=valid_profile_payload())

    for path in ["/", "/weekly-report", "/exports"]:
        response = client.get(path)
        assert response.status_code == 200
