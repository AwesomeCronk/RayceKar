import contextlib, logging, glfw, sys
from dataclasses import dataclass

import events
from util import loggingHandler, needGLVersion, viewportSize


logger = logging.getLogger('rk.ui')
logger.addHandler(loggingHandler)
logger.setLevel(logging.DEBUG)

@dataclass
class flags():
    initialized = False
    shouldClose = False

flags = flags()


### GLFW management ###
def initialize():
    logger.info('Initializing GLFW')
    flags.initialized = glfw.init()
    if not flags.initialized:
        logger.error('Failed to initialize GLFW')
        sys.exit(1)

@contextlib.contextmanager
def createWindow(title):
    try:
        logger.info('Requiring OpenGL {}.{} core or higher'.format(*needGLVersion))
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, needGLVersion[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, needGLVersion[1])
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.DOUBLEBUFFER, False)
        glfw.window_hint(glfw.RESIZABLE, False)
        
        window = glfw.create_window(*viewportSize, title, None, None)
        if not window: logger.error('Failed to open GLFW window'); sys.exit(1)
        glfw.make_context_current(window)
        
        glfw.set_key_callback(window, keyCallback)
        
        yield window

    finally:
        logger.info('Terminating GLFW')
        glfw.terminate()

def close(window):
    glfw.set_window_should_close(window, True)


# Matches https://www.glfw.org/docs/3.3/group__keys.html
class keys:
    # keys.keyName -> keyCode: int
    def __getattribute__(self, name: str):
        _names = {
            'UNKNOWN':          -1,
            'SPACE':            32,
            'APOSTROPHE':       39,
            'COMMA':            44,
            'MINUS':            45,
            'PERIOD':           46,
            'SLASH':            47,
            'K0':               48,
            'K1':               49,
            'K2':               50,
            'K3':               51,
            'K4':               52,
            'K5':               53,
            'K6':               54,
            'K7':               55,
            'K8':               56,
            'K9':               57,
            'SEMICOLON':        59,
            'EQUAL':            61,
            'A':                65,
            'B':                66,
            'C':                67,
            'D':                68,
            'E':                69,
            'F':                70,
            'G':                71,
            'H':                72,
            'I':                73,
            'J':                74,
            'K':                75,
            'L':                76,
            'M':                77,
            'N':                78,
            'O':                79,
            'P':                80,
            'Q':                81,
            'R':                82,
            'S':                83,
            'T':                84,
            'U':                85,
            'V':                86,
            'W':                87,
            'X':                88,
            'Y':                89,
            'Z':                90,
            'LEFT_BRACKET':     91,
            'BACKSLASH':        92,
            'RIGHT_BRACKET':    93,
            'GRAVE_ACCENT':     96,
            'WORLD_1':          161,
            'WORLD_2':          162,
            'ESCAPE':           256,
            'ENTER':            257,
            'TAB':              258,
            'BACKSPACE':        259,
            'INSERT':           260,
            'DELETE':           261,
            'RIGHT':            262,
            'LEFT':             263,
            'DOWN':             264,
            'UP':               265,
            'PAGE_UP':          266,
            'PAGE_DOWN':        267,
            'HOME':             268,
            'END':              269,
            'CAPS_LOCK':        280,
            'SCROLL_LOCK':      281,
            'NUM_LOCK':         282,
            'PRINT_SCREEN':     283,
            'PAUSE':            284,
            'F1':               290,
            'F2':               291,
            'F3':               292,
            'F4':               293,
            'F5':               294,
            'F6':               295,
            'F7':               296,
            'F8':               297,
            'F9':               298,
            'F10':              299,
            'F11':              300,
            'F12':              301,
            'F13':              302,
            'F14':              303,
            'F15':              304,
            'F16':              305,
            'F17':              306,
            'F18':              307,
            'F19':              308,
            'F20':              309,
            'F21':              310,
            'F22':              311,
            'F23':              312,
            'F24':              313,
            'F25':              314,
            'KP_0':             320,
            'KP_1':             321,
            'KP_2':             322,
            'KP_3':             323,
            'KP_4':             324,
            'KP_5':             325,
            'KP_6':             326,
            'KP_7':             327,
            'KP_8':             328,
            'KP_9':             329,
            'KP_DECIMAL':       330,
            'KP_DIVIDE':        331,
            'KP_MULTIPLY':      332,
            'KP_SUBTRACT':      333,
            'KP_ADD':           334,
            'KP_ENTER':         335,
            'KP_EQUAL':         336,
            'LEFT_SHIFT':       340,
            'LEFT_CONTROL':     341,
            'LEFT_ALT':         342,
            'LEFT_SUPER':       343,
            'RIGHT_SHIFT':      344,
            'RIGHT_CONTROL':    345,
            'RIGHT_ALT':        346,
            'RIGHT_SUPER':      347,
            'MENU':             348,
            'LAST':             348
        }

        if name == '_names': return _names
        else: return _names[name]

    # keys[keyCode: int] -> keyName: str
    # keys[keyName: str] -> keyCode: int
    def __getitem__(self, index):
        if isinstance(index, int): return list(self._names.keys())[list(self._names.values()).index(index)]
        elif isinstance(index, str): return self._names[index]

keys = keys()


def keyCallback(window, keyCode, scanCode, action, modBits):
    actionNames = {glfw.PRESS: 'press', glfw.REPEAT: 'repeat', glfw.RELEASE: 'release'}
    logger.debug('keyCallback for "{}" ({})'.format(keys[keyCode], actionNames[action]))
    eventName = 'key_{}'.format(keys[keyCode])
    event = events.getEventByName(eventName)
    if not event is None:
        event.fire(args=(action,))

def setKeyEvent(window, keyCode, function):
    keyName = keys[keyCode]
    eventName = 'key_{}'.format(keys[keyCode])
    event = events.getEventByName(eventName)
    if function is None:
        logger.debug('Removing event for key "{}"'.format(keyName))
        if not event is None: event.deactivate()

    else:
        logger.debug('Setting up event for key "{}"'.format(keyName))
        if event is None:
            event = events.event(eventName, function)
        event.activate()

def keyPressed(window, keyCode): return glfw.get_key(window, keyCode) == glfw.PRESS


### UI functions ###


# update cuntains *everything* related to the UI that may need updated each frame
def update(window):
    flags.shouldClose = glfw.window_should_close(window)

    # GLFW housekeeping
    glfw.swap_buffers(window)
    glfw.poll_events()
