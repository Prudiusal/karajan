import pytest

from Logic import ConfigParser
from Logic import StyleConfig
from Logic import StyleNotFoundError, JsonNotFoundError, PluginConfigError
from Logic import NoStyleNameError, StyleTracksConfigError, StyleNameError
import settings as cfg


@pytest.fixture
def parser_fixture():
    return ConfigParser()

@pytest.fixture
def style_fixture(parser_fixture):
    return parser_fixture.build_style_data(cfg.STYLE)

def test_init(parser_fixture):
    parser_fixture.check_json(parser_fixture.default_style_config)


@pytest.mark.parametrize('style', ['PianoDrums', 'OrcheTrack', ])
def test_build_midi_data(style, parser_fixture):
    assert isinstance(parser_fixture.build_style_data(style), StyleConfig)


@pytest.mark.parametrize('style', ['SomeOther'])
def test_build_midi_data_bad(style, parser_fixture):
    with pytest.raises(StyleNotFoundError):
        parser_fixture.build_style_data(style)


@pytest.mark.parametrize('path', ['/bad/path '])
def test_check_json_bad(path, parser_fixture):
    parser_fixture.default_style_config = path
    with pytest.raises(JsonNotFoundError):
        parser_fixture.build_style_data(cfg.STYLE)


def test_validate(style_fixture):
    assert style_fixture.validate()

#
def test_validate_name(style_fixture):
    del style_fixture.name
    with pytest.raises(NoStyleNameError):
        style_fixture.validate()
    style_fixture.name = None
    with pytest.raises(StyleNameError):
        style_fixture.validate()


@pytest.mark.parametrize('track_type', [dict(), set(), 1])
def test_validate_tracks_bad(style_fixture, track_type):
    style_fixture.tracks = track_type
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()


def test_validate_tracks_bad2(style_fixture):
    del style_fixture.tracks
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()

#
@pytest.mark.parametrize('track_paste', [list(), set(), 1, 's'])
def test_validate_tracks_internal(style_fixture, track_paste):
        assert style_fixture.validate()
        for i, _ in enumerate(style_fixture.tracks):
            style_fixture.tracks[i] = track_paste
        with pytest.raises(StyleTracksConfigError):
            style_fixture.validate()


@pytest.mark.parametrize('track_paste', [list(), set(), 1, 's'])
def test_validate_tracks_internal(style_fixture, track_paste):
        # assert style_fixture.validate()
        for i, _ in enumerate(style_fixture.tracks):
            style_fixture.tracks[i] = track_paste
        with pytest.raises(StyleTracksConfigError):
            style_fixture.validate()


# @pytest.mark.parametrize('track_paste', [list(), set(), 1, 's'])
def test_validate_tracks_internal2(style_fixture):
    del style_fixture.tracks[0]['plugins']
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()

    del style_fixture.tracks[0]['track_name']
    with pytest.raises(StyleTracksConfigError):
        style_fixture.validate()
    # del style_fixture.track_name
    # with pytest.raises(StyleTracksConfigError):
    #     style_fixture.validate()


@pytest.mark.parametrize('wrong_type', [set('2'), {'a': 1}, 'str', 1])
def test_validate_plugins_type_bad(style_fixture, wrong_type):
    style_fixture.tracks[0]['plugins'] = wrong_type
    with pytest.raises(PluginConfigError):
        style_fixture.validate()


def test_validate_plugins_internal_bad(style_fixture):
    del style_fixture.tracks[0]['plugins'][0]['pluginName']
    with pytest.raises(PluginConfigError):
        style_fixture.validate()
