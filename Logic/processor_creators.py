from pathlib import Path

import numpy as np

# from Exceptions import WrongDawDreamerProcessor  # DSPNotFoundError
from Exceptions import DSPNotFoundError, PluginNotFoundError, \
    PresetNotFoundError, PresetLoadError
from logger import logger_VST


def delay_creator(func, config, global_name):
    """
    This functions covers creation of the Delay processors and initial
    setup for it.
    """
    logger_VST.error('Delay creator not implemented!')
    pass


def faust_creator(func, config, global_name):
    """
    This functions covers creation of the Faust processors and initial
    setup for it.
    """
    # TODO: convert to '.get' with default to handle the errors of JSON
    logger_VST.debug('FAUST IS CREATING')
    dsp_path = config['dspPath']
    check_dsp_path(dsp_path)
    logger_VST.debug(f'{global_name=}')
    logger_VST.debug(f'{dsp_path=}')
    # TODO: check for files, etc...
    processor = func(global_name)
    processor.set_dsp(dsp_path)
    processor.compile()
    return processor


def check_dsp_path(path):
    p = Path(path)
    if not p.exists():
        raise DSPNotFoundError(f'DSP Preset doesn\'t exist:{path}')


def check_plugin_path(path):
    p = Path(path)
    if not p.exists():
        raise PluginNotFoundError(f'Plugin path doesn\'t exist:{path}')


def check_preset_path(path):
    p = Path(path)
    if not p.exists():
        raise PresetNotFoundError(f'Plugin preset doesn\'t exist:{path}')


def vst_creator(func, config, global_name):
    """
    This functions covers creation of the VST processors and initial
    setup for it.
    """
    plugin_path = config['pluginPath']
    plugin_name = config['pluginName']
    check_plugin_path(plugin_path)
    logger_VST.debug(f'{global_name=}')
    logger_VST.info(f'{plugin_path=}')
    processor = func(global_name, plugin_path)
    if any([s in plugin_name.lower() for s in ['ample', 'kont', 'ad2', 'ak']]):
        processor.open_editor()
    else:
        # processor.open_editor()
        preset_path = config['fxpPresetPath']
        check_preset_path(preset_path)
        logger_VST.debug(f'{preset_path=}')
        try:
            processor.load_vst3_preset(preset_path)
            logger_VST.info('VST3 preset loaded')
        except Exception as e1:
            logger_VST.error(f'Error during VST3 preset load {e1}')
            try:
                processor.load_preset(preset_path)
                logger_VST.info('VST2 preset loaded instead of VST3')
            except Exception as e2:
                logger_VST.error(f'Error during VST2 preset load {e2}')
                raise PresetLoadError('BAD LOAD OF THE PRESET: '
                                      f'\n\t{e1}, \n\t{e2}')
        # processor.open_editor()
    # logger_VST.debug('Processor has created')
    return processor


def pb_creator(func, config, global_name):
    """
    Creates PlayBack processor
    """
    empty_data = np.zeros([2, 1], dtype='float32')
    processor = func(global_name, empty_data)
    # processor.set_options(
    #     daw.PlaybackWarpProcessor.option.OptionTransientsSmooth |
    #     daw.PlaybackWarpProcessor.option.OptionPitchHighQuality |
    #     daw.PlaybackWarpProcessor.option.OptionChannelsTogether
    # )
    logger_VST.info(f'playback processor has created with name {global_name}')
    return processor


def processor_creator(func, config, track_name):
    """
    With configuration from Json creates the plugins for one track
    :param func: method of RenderEngine, which creates the processor
    :param config: config for the one processor (VST)
    :param track_name: track to which processor refers to.
    :return: instance of dawdreamer.processor class.

    """
    processor_type = config.get('type', 'vst')
    processor_name = config['pluginName']
    name_global = f'{track_name}_{processor_name}'

    if processor_type == 'faust':
        try:
            return faust_creator(func, config, name_global)
        except DSPNotFoundError as dspe:
            logger_VST.error(dspe)
            return False

    elif processor_type == 'vst':
        try:
            return vst_creator(func, config, name_global)
        except PluginNotFoundError as ple:
            logger_VST.error(ple)
            return False
        except PresetNotFoundError as pre:
            logger_VST.error(pre)
            return False
        except PresetLoadError as preset_load:
            logger_VST.error(preset_load)
            return False
    elif processor_type == 'pb':
        try:
            return pb_creator(func, config, name_global)
        except Exception as e:
            logger_VST.error(e)
    else:
        logger_VST.waring(f'Unknown type: {processor_type} for '
                          f'{processor_name}')
        # raise WrongDawDreamerProcessor
        return False
