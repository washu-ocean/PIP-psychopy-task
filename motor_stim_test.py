#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.1.5),
    on Mon Jul 29 13:16:44 2024
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import prefs
prefs.hardware['audioLib'] = 'ptb'
prefs.hardware['audioLatencyMode'] = '3'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware

import os  # handy system and path functions
import sys  # to get file system encoding
from air_device import AirDevice
from utils import *
import serial


# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2024.1.5'
expName = 'motor_stim_test'  # from the Builder filename that created this script
# information about this experiment

hand_trial = 'H'
foot_trial = 'F'
none_trial = 'N'

presentation_times = {
    hand_trial: 10,
    foot_trial: 10,
    none_trial: 10
}

fiber_optic_threshold = 610
air_sample_rate = 0.1 # seconds

channel_a = {
    "channel_name": "A",
    "flexT": 1.25,
    "extT": 1.25,
    "intensity": 50,
    "reps": int(presentation_times[hand_trial]/2.5),
    "fiber_sample_rate": air_sample_rate,
    "fiber_threshold": fiber_optic_threshold
}

channel_b = {
    "channel_name": "B",
    "flexT": 1.25,
    "extT": 1.25,
    "intensity": 50,
    "reps": int(presentation_times[foot_trial]/2.5),
    "fiber_sample_rate": air_sample_rate,
    "fiber_threshold": fiber_optic_threshold
}

trial_list = ["H", "F", "H", "F", "H", "F", "H", "F"]

expInfo = {
    'participant': '',
    'session': '01',
    'comPort' : [p.device for p in serial.tools.list_ports.comports() if 'Bluetooth' not in p.device],
    'testMode':False,
    'date|hid': data.getDateStr(format='%Y-%m-%d_%Hh%M-%S-%f'),
    'expName|hid': expName,
    'psychopyVersion|hid': psychopyVersion,
}


# --- Define some variables which will change depending on pilot mode ---
'''
To run in pilot mode, either use the run/pilot toggle in Builder, Coder and Runner, 
or run the experiment with `--pilot` as an argument. To change what pilot 
#mode does, check out the 'Pilot mode' tab in preferences.
'''
# work out from system args whether we are running in pilot mode
PILOTING = core.setPilotModeFromArgs()
# start off with values from experiment settings
_fullScr = True
_winSize = [1440, 900]
_loggingLevel = logging.getLevel('debug')
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']
    # override logging level
    _loggingLevel = logging.getLevel(
        prefs.piloting['pilotLoggingLevel']
    )


def create_routines_and_run(expInfo, thisExp, win, globalClock=None):
    
    arduino = connectSerial(expInfo["comPort"])

    air_deviceA = AirDevice(name="air_channel_A",
                            serial_device=arduino,
                            **channel_a)
    air_deviceB = AirDevice(name="air_channel_B", 
                            serial_device=arduino,
                            **channel_b)
    
    clear_serial_buffer = lambda : arduino.reset_input_buffer() or arduino.readline()
    get_arduino_time = lambda : air_deviceA.data_from_message(air_deviceA.read(flush=True))[0]

    # Wait for scanner message
    wait_text = visual.TextStim(win=win, name='wait_text',
        text='Waiting for MRI scanner....',
        font='Arial',
        pos=(0,-0.3), height=0.03, wrapWidth=None, ori=0.0, 
        color=[-1.0000, -1.0000, -1.0000], colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0)

    background_block = visual.Rect(
        win=win, name='control_block',
        width=2, height=2,
        ori=0.0, pos=(0, 0), anchor='center',
        lineWidth=1.0,     colorSpace='rgb',  lineColor=[1,1,1], fillColor=[1,1,1],
        opacity=None, depth=1.0, interpolate=True)
    
    fixation = visual.ShapeStim(
        win=win, name='fixation_cross', vertices='cross',
        size=(0.1, 0.1),
        ori=0.0, pos=(0, 0), anchor='center',
        lineWidth=1.0,     colorSpace='rgb',  lineColor=[-1.0000, -1.0000, -1.0000], fillColor=[-1.0000, -1.0000, -1.0000],
        opacity=None, depth=0.0, interpolate=True)

    # -- Create routines with there components 
    routines = {}

    none_routine = {
        ROUTINE_NAME: none_trial,
        COMPONENTS:[
            {
                OBJ:fixation,
                TRIAL_START_TIME:0.0,
                TRIAL_END_TIME:presentation_times[none_trial],
                STIM_TYPE:STIM_DRAW
            }
        ],
        ROUTINE_DURATION:presentation_times[none_trial]
    }
    routines[none_routine[ROUTINE_NAME]] = none_routine

    hand_routine = {
        ROUTINE_NAME:hand_trial,
        COMPONENTS:[
            {
                OBJ:fixation,
                TRIAL_START_TIME:0.0,
                TRIAL_END_TIME:presentation_times[hand_trial],
                STIM_TYPE:STIM_DRAW
            },
            {
                OBJ:air_deviceA,
                TRIAL_START_TIME:0.0,
                TRIAL_END_TIME:presentation_times[hand_trial],
                STIM_TYPE:STIM_AIR
            }
        ],
        ROUTINE_DURATION:presentation_times[hand_trial]
    }
    routines[hand_routine[ROUTINE_NAME]] = hand_routine

    foot_routine = {
        ROUTINE_NAME:foot_trial,
        COMPONENTS:[
            {
                OBJ:fixation,
                TRIAL_START_TIME:0.0,
                TRIAL_END_TIME:presentation_times[foot_trial],
                STIM_TYPE:STIM_DRAW
            },
            {
                OBJ:air_deviceB,
                TRIAL_START_TIME:0.0,
                TRIAL_END_TIME:presentation_times[foot_trial],
                STIM_TYPE:STIM_AIR
            }
        ],
        ROUTINE_DURATION:presentation_times[foot_trial]
    }
    routines[foot_routine[ROUTINE_NAME]] = foot_routine

    win.backgroundImage = background_block

   # run the experiment
    run(
        expInfo=expInfo,
        thisExp=thisExp,
        win=win,
        globalClock=globalClock,
        trials=trial_list,
        routines=routines,
        mri_wait_stim=wait_text,
        mri_wait_callback=clear_serial_buffer,
        air_stim_clock_time=get_arduino_time,
        pre_loop_callback=clear_serial_buffer,
        run_loop_callback=clear_serial_buffer,
        post_loop_callback=arduino.close
    )
    


# if running this experiment as a script...
if __name__ == '__main__':
    # call all functions in order
    expInfo = showExpInfoDlg(expInfo=expInfo)
    _filename = f'{expInfo["participant"]}_{expInfo["session"]}_{expName}_{expInfo["date|hid"]}'
    thisExp = setupData(expInfo=expInfo, filename=_filename)
    logFile = setupLogging(filename=thisExp.dataFileName, loggingLevel=_loggingLevel)
    logging.info(f"expInfo = {expInfo}")
    logging.info(f"presentation_times = {presentation_times}")
    logging.info(f"scanner_keys = {SCANNER_KEYS}")
    logging.info(f"scanner_pulses_needed = {SCANNER_PULSES_NEEDED}")
    win = setupWindow(expInfo=expInfo, winSize=_winSize, fullScr=_fullScr)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    create_routines_and_run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='float'
    )
    # saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
