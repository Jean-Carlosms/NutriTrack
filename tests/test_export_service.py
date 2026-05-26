from app.services.export_service import (
    FOOD_HEADERS,
    MEASUREMENT_HEADERS,
    export_foods,
    export_measurements,
)


def test_export_foods_with_header_only():
    csv_content = export_foods([])

    assert csv_content.splitlines()[0] == ",".join(FOOD_HEADERS)
    assert len(csv_content.splitlines()) == 1


def test_export_measurements_with_header_only():
    csv_content = export_measurements([])

    assert csv_content.splitlines()[0] == ",".join(MEASUREMENT_HEADERS)
    assert len(csv_content.splitlines()) == 1
