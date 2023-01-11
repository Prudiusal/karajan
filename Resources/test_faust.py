import dawdreamer as daw
from utils import load_audio_file, render


def main():
    engine = daw.RenderEngine(44100, 128)
    kick = load_audio_file("wavs_test/kick.wav", duration=8)
    bass = load_audio_file("wavs_test/bass.wav", duration=8)
    playback_kick = engine.make_playback_processor("kick", kick)
    playback_bass = engine.make_playback_processor("bass", bass)
    faust_processor = engine.make_faust_processor("faust")
    faust_processor.set_dsp('faust_dsp/sidechain.dsp')
    faust_processor.compile()
    assert(faust_processor.compiled)
    par = faust_processor.get_parameters_description()
    for p in par:
        print()
        print(p)
        print()
    exit()

    graph = [
        (playback_kick, []),
        (playback_bass, []),
        (faust_processor, [playback_bass.get_name(),
                           playback_kick.get_name()]),
        (engine.make_add_processor("add", [1., 1.]), ["faust", "kick"])
    ]

    assert(engine.load_graph(graph))

    render(engine, file_path='output/sidechain_bass_kick.wav')

    # Todo: the last sample is inaccurate by a little bit
    # So we trim the last sample and compare

    # assert(np.allclose(data, audio, atol=1e-07))


if __name__ == '__main__':
    main()
