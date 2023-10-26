import pytest

import settings as cfg

# from Logic import StyleConfig
from Logic import (
    ConfigParser,
    NoStyleNameError,
    PluginConfigError,
    StyleNameError,
    StyleTracksConfigError,
)


@pytest.fixture
def style_fixture():
    return ConfigParser().build_style_data(cfg.STYLE)


def test_validate(style_fixture):
    assert style_fixture.validate()


def test_validate_name(style_fixture):
    del style_fixture.name
    with pytest.raises(NoStyleNameError):
        style_fixture.validate()
    style_fixture.name = None
    with pytest.raises(StyleNameError):
        style_fixture.validate()


@pytest.mark.parametrize("track_type", [dict(), set(), 1])
def test_validate_tracks_bad(style_fixture, track_type):
    style_fixture.tracks = track_type
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()


def test_validate_tracks_bad2(style_fixture):
    del style_fixture.tracks
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()


#
@pytest.mark.parametrize("track_paste", [list(), set(), 1, "s"])
def test_validate_tracks_internal(style_fixture, track_paste):
    assert style_fixture.validate()
    for i, _ in enumerate(style_fixture.tracks):
        style_fixture.tracks[i] = track_paste
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()


@pytest.mark.parametrize("track_paste", [list(), set(), 1, "s"])
def test_validate_tracks_internal(style_fixture, track_paste):
    # assert style_fixture.validate()
    for i, _ in enumerate(style_fixture.tracks):
        style_fixture.tracks[i] = track_paste
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()


# @pytest.mark.parametrize('track_paste', [list(), set(), 1, 's'])
def test_validate_tracks_internal2(style_fixture):
    del style_fixture.tracks[0]["plugins"]
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()

    del style_fixture.tracks[0]["track_name"]
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()
    # del style_fixture.track_name
    # with pytest.raises(StyleTracksConfigError):
    #     style_fixture.validate()


@pytest.mark.parametrize("wrong_type", [set("2"), {"a": 1}, "str", 1])
def test_validate_plugins_type_bad(style_fixture, wrong_type):
    style_fixture.tracks[0]["plugins"] = wrong_type
    with pytest.raises(PluginConfigError):
        style_fixture.validate()


def test_validate_plugins_internal_bad(style_fixture):
    del style_fixture.tracks[0]["plugins"][0]["pluginName"]
    with pytest.raises(PluginConfigError):
        style_fixture.validate()
