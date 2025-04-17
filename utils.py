#!/usr/bin/env python  
# -*- coding: utf-8 -*- 

from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
prefs.hardware['audioLib'] = 'ptb'
prefs.hardware['audioLatencyMode'] = '3'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard
import serial
from pathlib import Path

# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2024.1.5'
    

SCANNER_KEYS = ['5', 't']
SCANNER_PULSES_NEEDED = 1

TRIAL_PARAM= "Trial"
ITI_PARAM = "ITI"

STIM_DRAW = "draw"
STIM_PLAY = "play"
STIM_MOVIE = "movie"
STIM_AIR = "air"

ROUTINE_NAME = "routine_name"
TRIAL_NAME = "trial_name"
COMPONENTS = "components"
OBJ = "obj"
TRIAL_START_TIME = "trial_start_time"
TRIAL_END_TIME = "trial_end_time"
STIM_TYPE = "stim_type"
ROUTINE_DURATION = "routine_duration"

FIBER_QUEUE_SIZE = 3
FIBER_OUT_OF_BOUNDS_MAX = 1

def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # show participant info dialog
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expInfo["expName|hid"], alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # return expInfo
    return expInfo


def setupData(expInfo, filename, dataDir=None):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    dataDir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # remove dialog-specific syntax from expInfo
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    expName = expInfo["expName"]
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    # filename = u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
    # filename = Path('data') / f'{expInfo["participant"]}_{expInfo["session"]}_{expName}_order-{expInfo["stimOrder"]}_{expInfo["date"]}'
    filename = Path('data') / f"sub-{expInfo['participant']}_ses-{expInfo['session']}" / filename
    filename = str(filename)
    # make sure filename is relative to dataDir
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        # originPath='/Users/agardr/Desktop/python_code/becca_py_task/define-roi.py',
        originPath=Path(__file__).resolve(),
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp


def setupLogging(filename, loggingLevel):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # this outputs to the screen, not a file
    logging.console.setLevel(logging.ERROR)
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename+'.log', level=loggingLevel)
    
    return logFile


def setupWindow(expInfo=None, win=None, winSize=None, fullScr=True, piloting=False):
    """
    Setup the Window
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    win : psychopy.visual.Window
        Window to setup - leave as None to create a new window.
    
    Returns
    ==========
    psychopy.visual.Window
        Window in which to run this experiment.
    """
    if piloting:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        # if not given a window to setup, make one
        win = visual.Window(
            size=winSize, fullscr=fullScr, screen=0,
            winType='pyglet', allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height', 
            checkTiming=False  # we're going to do this ourselves in a moment
        )
    else:
        # if we have a window, just set the attributes which are safe to set
        win.color = [0,0,0]
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        # get/measure frame rate if not already in expInfo
        if win._monitorFrameRate is None:
            win.getActualFrameRate(infoMsg='Attempting to measure frame rate of screen, please wait...')
        expInfo['frameRate'] = win._monitorFrameRate
    win.mouseVisible = False
    win.hideMessage()
    # show a visual indicator if we're in piloting mode
    if piloting and prefs.piloting['showPilotingIndicator']:
        win.showPilotingIndicator()
    
    return win


def setupDevices(expInfo, thisExp, win):
    """
    Setup whatever devices are available (mouse, keyboard, speaker, eyetracker, etc.) and add them to 
    the device manager (deviceManager)
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window in which to run this experiment.
    Returns
    ==========
    bool
        True if completed successfully.
    """
    # --- Setup input devices ---
    ioConfig = {}
    
    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    
    ioSession = '1'
    if 'session' in expInfo:
        ioSession = str(expInfo['session'])
    ioServer = io.launchHubServer(window=win, **ioConfig)
    # store ioServer object in the device manager
    deviceManager.ioServer = ioServer
    
    # create a default keyboard (e.g. to check for escape)
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='iohub'
        )
    # create speaker 'violet_sound'
    deviceManager.addDevice(
        deviceName='stim_speaker',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    # return True if completed successfully
    return True

def waitForScanner(win, message_stim, keylist=SCANNER_KEYS, loop_callback=None, is_movie=False):
    pulse_count = 0
    message_stim.setAutoDraw(True)
    if is_movie:
        message_stim.play()
    while pulse_count < SCANNER_PULSES_NEEDED:
        win.flip()
        if callable(loop_callback):
            loop_callback()
        keys = event.getKeys(keylist)
        if len(keys) > 0:
            pulse_count += 1
            logging.info("Received a scanner pulse")
    message_stim.setAutoDraw(False)
    if is_movie:
        message_stim.stop()

def connectSerial(com_port):
    if not com_port:
        RuntimeError("communication port for connecting to the arduino is not defined")
    ser = serial.Serial(com_port, 115200, timeout=0.100)
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    return ser

def pauseExperiment(thisExp, win=None, timers=[], playbackComponents=[]):
    """
    Pause this experiment, preventing the flow from advancing to the next routine until resumed.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    timers : list, tuple
        List of timers to reset once pausing is finished.
    playbackComponents : list, tuple
        List of any components with a `pause` method which need to be paused.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # pause any playback components
    for comp in playbackComponents:
        comp.pause()
    # prevent components from auto-drawing
    win.stashAutoDraw()
    # make sure we have a keyboard
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='ioHub',
        )
    # run a while loop while we wait to unpause
    while thisExp.status == PAUSED:
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        # flip the screen
        win.flip()
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    for comp in playbackComponents:
        comp.play()
    # restore auto-drawn components
    win.retrieveAutoDraw()
    # reset any timers
    for timer in timers:
        timer.reset()

def run(expInfo, thisExp, win, 
        trials,
        routines,
        mri_wait_stim,
        wait_is_movie=False,
        mri_wait_callback=None,
        air_stim_clock_time=None,
        pre_loop_callback=None,
        run_loop_callback=None,
        post_loop_callback=None,
        globalClock=None, 
        thisSession=None):
    """
    Run the experiment flow.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    psychopy.visual.Window
        Window in which to run this experiment.
    globalClock : psychopy.core.clock.Clock or None
        Clock to get global time from - supply None to make a new one.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    # mark experiment as started
    thisExp.status = STARTED
    # make sure variables created by exec are available globally
    exec = environmenttools.setExecEnvironment(globals())
    # get device handles from dict of input devices
    ioServer = deviceManager.ioServer
    # get/create a default keyboard (e.g. to check for escape)
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ioHub'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    # make sure we're running in the directory for this experiment
    os.chdir(_thisDir)
    # get filename from ExperimentHandler for convenience
    filename = thisExp.dataFileName
    frameTolerance = 0.001  # how close to onset before 'same' frame
    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    # get frame duration from frame rate in expInfo
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess

    # global clock to track the time since experiment started
    if globalClock is None:
        # create a clock if not given one
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        # if given a string, make a clock accoridng to it
        if globalClock == 'float':
            # get timestamps as a simple value
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            # get timestamps in ISO format
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            # get timestamps in a custom format
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock) 
    
    if isinstance(trials, str) or isinstance(trials, Path):
        trials = data.importConditions(trials)
    elif not isinstance(trials, list):
        raise TypeError("'trials' parameter must be of types 'str' or 'Path' or 'list'. Input was not any of the expected types.")

    # set up handler to look after randomisation of conditions etc
    trials = data.TrialHandler(nReps=1.0, method='sequential', 
        extraInfo=expInfo, originPath=-1,
        trialList=trials,
        seed=None, name='trials')
    thisExp.addLoop(trials)  # add the loop to the experiment
    thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
    currentLoop = trials

    has_loop_callback = callable(run_loop_callback)

    # Test if communication with air control device is working as expected
    try:
        air_stim_clock_time()
    except ValueError as e:
        print(e)
        raise RuntimeError(f"""---- CRITICAL ----\nDid not receive any data from the Air-Control Box.\nRestart the Air-Control Box before retrying this task""")

    # wait for the mri scanner then 
    # store the exact time the global clock started
    if not expInfo['testMode']:
        waitForScanner(win=win, 
                       message_stim=mri_wait_stim, 
                       loop_callback=mri_wait_callback,
                       is_movie=wait_is_movie)
    
    globalClock.reset()
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    thisExp.addData('exp.clock.going', globalClock.getTime(format='float'))
    win.flip()  # flip window to reset last flip timer

    air_clock_start = air_stim_clock_time()
    logging.info(f"Serial start: {air_clock_start}")

    thisExp.timestampOnFlip(win, 'exp.clock.offset')
    thisExp.addData("serial.wait.time", globalClock.getTime(format='float'))

    if callable(pre_loop_callback):
        pre_loop_callback()

    # routine timer to track time remaining of each (possibly non-slip) routine
    routineTimer = core.Clock()
    logging.info(f"routine timer: {routineTimer.getTime()}")

    print("\n\n----- STARTING THE TASK -----\n")

    for thisTrial in trials:
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
        )
        
        print(f"Starting trial:  {thisTrial[TRIAL_PARAM]}")

        continueRoutine = True

        current_routine = routines[thisTrial[TRIAL_PARAM]]
        current_components = current_routine[COMPONENTS]
        fiber_check_queue = {}
        fiber_out_of_bounds_count = {}
        did_report_air_component_error = {}
        air_component_obj = None
        last_sample_time = {}

        for thisComponent in current_components:
            thisComponentObj = thisComponent[OBJ]
            thisComponentObj.tStart = None
            thisComponentObj.tStop = None
            thisComponentObj.tStartRefresh = None
            thisComponentObj.tStopRefresh = None
            if hasattr(thisComponentObj, 'status'):
                thisComponentObj.status = NOT_STARTED
            if thisComponent[STIM_TYPE] == STIM_AIR:
                air_component_obj = thisComponentObj
                last_sample_time[air_component_obj.name] = -current_routine[ROUTINE_DURATION]
                fiber_check_queue[thisComponentObj.name] = []
                fiber_out_of_bounds_count[thisComponentObj.name] = 0
                did_report_air_component_error[thisComponentObj.name] = False
        
        if air_component_obj:
            serial_time = air_component_obj.data_from_message(
                air_component_obj.read(flush=True)
                )[0] - air_clock_start
            logging.info(f"serial time: {serial_time}")   

        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1

        # log the start of the routine
        thisExp.timestampOnFlip(win, f'{current_routine[ROUTINE_NAME]}.started')
        total_duration = current_routine[ROUTINE_DURATION]
        if ITI_PARAM in thisTrial and thisTrial[ITI_PARAM]:
            total_duration += float(thisTrial[ITI_PARAM])/1000 
        while routineTimer.getTime() < current_routine[ROUTINE_DURATION]:

            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1

            # is it time to end the Routine? (based on local clock)
            if tThisFlip > current_routine[ROUTINE_DURATION]:
                continueRoutine = False

            for thisComponent in current_components:
                thisComponentObj = thisComponent[OBJ]

                # If this component is starting this frame
                if thisComponentObj.status == NOT_STARTED and tThisFlip >= thisComponent[TRIAL_START_TIME]-frameTolerance:
                    thisComponentObj.frameNStart = frameN
                    thisComponentObj.tStart = t # local t and not account for scr refresh
                    thisComponentObj.tStartRefresh = tThisFlipGlobal # on global time
                    win.timeOnFlip(thisComponentObj, 'tStartRefresh') # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, f'{thisComponentObj.name}.started')
                    if thisComponent[STIM_TYPE] == STIM_DRAW:
                        thisComponentObj.setAutoDraw(True)
                    elif thisComponent[STIM_TYPE] == STIM_PLAY:
                        thisComponentObj.play(loops=1, when=win)
                    elif thisComponent[STIM_TYPE] == STIM_MOVIE:
                        thisComponentObj.setAutoDraw(True)
                        thisComponentObj.play()
                    elif thisComponent[STIM_TYPE] == STIM_AIR:
                        start_t_millis = thisComponentObj.start()
                        logging.info(f"{thisComponentObj.name}-serial-start: {start_t_millis - air_clock_start}")
                        thisExp.addData(f"{thisComponentObj._channel_name}.serial.started", globalClock.getTime(format='float'))
                    thisComponentObj.status = STARTED

                elif thisComponentObj.status == STARTED:
                    if tThisFlip >= thisComponent[TRIAL_END_TIME]-frameTolerance:
                        thisComponentObj.tStop = t
                        thisComponentObj.tStopRefresh = tThisFlipGlobal
                        thisComponentObj.frameNStop = frameN
                        thisExp.timestampOnFlip(win, f'{thisComponentObj.name}.stopped')
                        if thisComponent[STIM_TYPE] == STIM_DRAW:
                            thisComponentObj.setAutoDraw(False)
                        elif thisComponent[STIM_TYPE] == STIM_PLAY:
                            thisComponentObj.stop()
                        elif thisComponent[STIM_TYPE] == STIM_MOVIE:
                            thisComponentObj.setAutoDraw(False)
                            thisComponentObj.stop()
                        elif thisComponent[STIM_TYPE] == STIM_AIR:
                            stop_t_millis, channel_duration = thisComponentObj.stop()
                            logging.info(f"{thisComponentObj.name}-serial-stop: {stop_t_millis - air_clock_start}")
                            logging.info(f"{thisComponentObj.name}-serial-duration(secs): {channel_duration}")
                            thisExp.addData(f"{thisComponentObj._channel_name}.serial.stopped", globalClock.getTime(format='float'))
                        thisComponentObj.status = FINISHED

                # flush the serial buffer to keep data 'live'
                if has_loop_callback:
                    run_loop_callback()

                # update sound and air components status according to whether it's playing
                if thisComponent[STIM_TYPE] == STIM_PLAY:
                    if thisComponentObj.isPlaying:
                        thisComponentObj.status = STARTED
                    elif thisComponentObj.isFinished:
                        thisComponentObj.status = FINISHED
                elif thisComponent[STIM_TYPE] == STIM_AIR and thisComponentObj.status == STARTED:
                    if t >= last_sample_time[thisComponentObj.name] + thisComponentObj.fiber_sample_rate:
                        last_sample_time[thisComponentObj.name] = t
                        in_range, fiber_value, serial_time_from_start = thisComponentObj.check_fiber_value()
                        fiber_check_queue[thisComponentObj.name].append(not in_range)
                        msg = f"Fiber Optic readout is not in the expected range for the current time. "
                        msg += f"Component:{thisComponentObj.name}, Time from trial_start:{serial_time_from_start}, Fiber Value:{fiber_value}"
                        if not in_range:
                            logging.warning(msg)
                        if len(fiber_check_queue[thisComponentObj.name]) >= FIBER_QUEUE_SIZE:
                            fiber_check_queue[thisComponentObj.name] = fiber_check_queue[thisComponentObj.name][-FIBER_QUEUE_SIZE:]
                            if all(fiber_check_queue[thisComponentObj.name]):
                                fiber_out_of_bounds_count[thisComponentObj.name] += 1 
                                if not did_report_air_component_error[thisComponentObj.name] and fiber_out_of_bounds_count[thisComponentObj.name] >= FIBER_OUT_OF_BOUNDS_MAX: 
                                    logging.warning("Fiber value warning presented") 
                                    print(f"------------- WARNING -------------\n{msg}\n------------------------------------------")
                                    did_report_air_component_error[thisComponentObj.name] = True


            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
                break
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineForceEnded = True
                break
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        for thisComponent in current_components:
            thisComponentObj = thisComponent[OBJ]
            if thisComponentObj.status != FINISHED:
                if thisComponent[STIM_TYPE] == STIM_DRAW:
                    thisComponentObj.setAutoDraw(False)
                elif thisComponent[STIM_TYPE] == STIM_PLAY:
                    thisComponentObj.stop()
                elif thisComponent[STIM_TYPE] == STIM_MOVIE:
                    thisComponentObj.setAutoDraw(False)
                    thisComponentObj.stop()
                elif thisComponent[STIM_TYPE] == STIM_AIR:
                    stop_t_millis, channel_duration = thisComponentObj.stop()
                    logging.info(f"{thisComponentObj.name}-serial-stop: {stop_t_millis - air_clock_start}")
                    logging.info(f"{thisComponentObj.name}-serial-duration(secs): {channel_duration}")
                    thisExp.addData(f"{thisComponentObj._channel_name}.serial.stopped", globalClock.getTime(format='float'))

        # log the end of the routine
        thisExp.timestampOnFlip(win, f'{current_routine[ROUTINE_NAME]}.stopped')

        if thisExp.status == FINISHED:
            win.flip()
            break

        # If there is time inbetween the end of the routine and the start of the next 
        while routineTimer.getTime() < total_duration:
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            if tThisFlip >= total_duration:
                break
            win.flip()
        

        # using non-slip timing so subtract the expected duration of this Routine
        routineTimer.addTime(-total_duration)

        thisExp.nextEntry()
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()

    # completed 1.0 repeats of 'trials'
    
    if callable(post_loop_callback):
        post_loop_callback()

    print("\n----- ENDING THE TASK -----\n\n")

    # mark experiment as finished
    endExperiment(thisExp, win=win)


def endExperiment(thisExp, win=None):

    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    """

    thisExp.timestampOnFlip(win, 'exp.clock.stop')
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed
        win.flip()
    # mark experiment handler as finished
    thisExp.status = FINISHED
    # shut down eyetracker, if there is one
    if deviceManager.getDevice('eyetracker') is not None:
        deviceManager.removeDevice('eyetracker')
    logging.flush()


def quit(thisExp, win=None, thisSession=None):
    """
    Fully quit, closing the window and ending the Python process.
    
    Parameters
    ==========
    win : psychopy.visual.Window
        Window to close.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()  # or data files will save again on exit
    # make sure everything is closed down
    if win is not None:
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed before quitting
        win.flip()
        win.close()
    # shut down eyetracker, if there is one
    if deviceManager.getDevice('eyetracker') is not None:
        deviceManager.removeDevice('eyetracker')
    logging.flush()
    if thisSession is not None:
        thisSession.stop()
    # terminate Python process
    core.quit()


def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='auto')
    thisExp.saveAsPickle(filename)