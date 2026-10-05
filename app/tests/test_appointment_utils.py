from app.utils.appointment_utils import has_overlap


def test_overlap():
    assert has_overlap(10, 20, 15, 25)


def test_no_overlap():
    assert not has_overlap(10, 20, 20, 30)
