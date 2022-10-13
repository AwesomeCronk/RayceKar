import contextlib, logging, glfw, sys, struct
from dataclasses import dataclass

from raycekar import events
from raycekar.util import loggingHandler
from raycekar.coord import *

log = logging.getLogger('rk.ui')
log.addHandler(loggingHandler)
log.setLevel(logging.DEBUG)

@dataclass
class _flags:
    initialized = False
    shouldClose = False

flags = _flags()

viewportSize = vec2(400, 400)
needGLVersion = (4, 4)
window = None


### Keyboard input ###
# Key codes match https://www.glfw.org/docs/3.3/group__keys.html
class _keys:
    _map = {
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

    # keys.keyName -> keyCode: int
    def __getattr__(self, name: str):
        return self._map[name]

    # keys[keyCode: int] -> keyName: str
    # keys[keyName: str] -> keyCode: int
    def __getitem__(self, index):
        if isinstance(index, int): return list(self._map.keys())[list(self._map.values()).index(index)]
        elif isinstance(index, str): return self._map[index]

    def _callback(self, window, keyCode, scanCode, action, modBits):
        # actionNames = {glfw.PRESS: 'press', glfw.REPEAT: 'repeat', glfw.RELEASE: 'release'}
        # log.debug('keyCallback for "{}" ({})'.format(self[keyCode], actionNames[action]))
        eventName = 'key_{}'.format(self[keyCode])
        event = events.getEventByName(eventName)
        if not event is None:
            event.fire(args=(action,))

    def setEvent(self, keyCode, function):
        eventName = 'key_{}'.format(self[keyCode])
        event = events.getEventByName(eventName)
        if function is None:
            if not event is None: event.deactivate()

        else:
            if event is None:
                event = events.event(eventName, function)
            event.activate()

    def pressed(self, keyCode):
        return glfw.get_key(window, keyCode) == glfw.PRESS

keys = _keys()


### Mouse input ###
class _mouse:
    _buttons = {
        'LEFT': 0,
        'RIGHT': 1,
        'MODDLE': 2
    }
    pos = vec2(0, 0)
    mode = 'normal'

    def __getattr__(self, name: str):
        return self._buttons[name]

    def __getitem__(self, index):
        if isinstance(index, int): return list(self._buttons.keys())[list(self._buttons.values()).index(index)]
        elif isinstance(index, str): return self._buttons[index]

    def _callback(self, window, button, action, modBits):
        eventName = 'mouse_{}'.format(self[button])
        event = events.getEventByName(eventName)
        if not event is None:
            event.fire(args=(action,))

    def setMode(self, mode: str):
        if mode == 'normal':
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
        elif mode == 'hidden':
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
        elif mode == 'disabled':
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        else:
            raise ValueError('Invalid cursor mode "{}"'.format(mode))
        self.mode = mode

    def getMode(self): return self.mode

    def setEvent(self, buttonCode, function):
        eventName = 'mouse_{}'.format(self[buttonCode])
        event = events.getEventByName(eventName)
        if function is None:
            if not event is None: event.deactivate()

        else:
            if event is None:
                event = events.event(eventName, function)
            event.activate()

    def pressed(self, buttonCode):
        return glfw.get_mouse_button(window, buttonCode) == glfw.PRESS

mouse = _mouse()


### UI functions ###
class widget:
    typeID = 0
    def __init__(self, pos: vec2, dim: vec2, color: vec4):
        self.pos = pos
        self.dim = dim
        self.color = color

    def move(self, newPos: vec2):
        self.pos = newPos

    def compileBufferData(self):
        typeData = struct.pack(
            'i', self.typeID
        )
        intData = struct.pack(
            'iiii',
            *self.pos,
            *self.dim
        )
        floatData = struct.pack(
            'ffff',
            *self.color
        )
        return typeData, intData, floatData


### GLFW management ###
def initialize():
    log.info('Initializing GLFW')
    flags.initialized = glfw.init()
    if not flags.initialized:
        log.error('Failed to initialize GLFW')
        sys.exit(1)

@contextlib.contextmanager
def createWindow(title, size):
    global window, viewportSize
    try:
        viewportSize = size
        log.info('Requiring OpenGL {}.{} core or higher'.format(*needGLVersion))
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, needGLVersion[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, needGLVersion[1])
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.DOUBLEBUFFER, False)
        glfw.window_hint(glfw.RESIZABLE, False)
        
        window = glfw.create_window(*viewportSize, title, None, None)
        if not window: log.error('Failed to open GLFW window'); sys.exit(1)
        glfw.make_context_current(window)
        
        glfw.set_key_callback(window, keys._callback)
        glfw.set_mouse_button_callback(window, mouse._callback)
        
        yield

    finally:
        log.info('Terminating GLFW')
        glfw.terminate()

def closeWindow():
    glfw.set_window_should_close(window, True)

def updateWindow():
    flags.shouldClose = glfw.window_should_close(window)
    rawMousePos = glfw.get_cursor_pos(window)
    mouse.pos = vec2(int(rawMousePos[0]), viewportSize[1] - int(rawMousePos[1]))   # GLFW puts <0, 0> at upper left; OpenGl, mathematics, and basic sense put it at lower left

    glfw.swap_buffers(window)
    glfw.poll_events()
