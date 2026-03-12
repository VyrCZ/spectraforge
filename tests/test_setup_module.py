from modules.setup import Setup, SetupType


def test_setup_from_json_2d_sets_z_to_zero():
    setup = Setup.from_json("tree", {"type": SetupType.TWO_DIMENSIONAL, "coordinates": [[1, 2, 9], [3, 4, 7]]})
    assert setup.name == "tree"
    assert setup.coords == [[1, 2, 0], [3, 4, 0]]


def test_setup_from_json_3d_keeps_coordinates():
    setup = Setup.from_json("tree", {"type": SetupType.THREE_DIMENSIONAL, "coordinates": [[1, 2, 9]]})
    assert setup.coords == [[1, 2, 9]]


def test_get_formatted_name_normalizes_special_characters():
    setup = Setup("My / Fancy\\Setup", SetupType.TWO_DIMENSIONAL, [])
    assert setup.get_formatted_name() == "my___fancy_setup"