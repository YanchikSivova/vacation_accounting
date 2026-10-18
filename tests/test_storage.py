import json
from datetime import date

from models import VACATION_TYPES, User
from models.vacations import create_vacation_request
from storage import load_vacation_requests, save_vacation_requests


def test_load_legacy_request_as_paid_vacation(tmp_path):
    filename = tmp_path / "vacations.json"
    filename.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "user_id": 1,
                    "start_date": "2026-09-15",
                    "end_date": "2026-09-25",
                    "duration": 11,
                    "status": "cancelled",
                }
            ]
        ),
        encoding="utf-8",
    )
    user = User(1, "Сивова Яна", 28, 28)

    requests = load_vacation_requests(str(filename), [user])

    assert len(requests) == 1
    assert requests[0].vacation is VACATION_TYPES[0]


def test_save_and_load_vacation_request(tmp_path):
    filename = tmp_path / "vacations.json"
    user = User(1, "Сивова Яна", 28, 28)
    request = create_vacation_request(
        [],
        user,
        VACATION_TYPES[3],
        date(2026, 9, 15),
        date(2026, 9, 20),
    )
    assert request is not None

    save_vacation_requests(str(filename), [request])
    loaded_requests = load_vacation_requests(str(filename), [user])

    assert len(loaded_requests) == 1
    assert loaded_requests[0].vacation is VACATION_TYPES[3]
