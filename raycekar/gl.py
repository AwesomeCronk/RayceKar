import logging, sys, pathlib, struct
from OpenGL import GL as gl
from raycekar import util
from raycekar.coord import *

log = logging.getLogger('rk.gl')
log.addHandler(util.loggingHandler)
log.setLevel(logging.DEBUG)

viewportSize = vec2(400, 400)

class _contacts:
    scene = ()
    ui = ()
contacts = _contacts()

def _glDebugMessageCallback(source, messageType, messageID, severity, length, message, user):
    log.error('Source: {}; Message type: {}; Message ID: {}; Severity: {}; Length: {}; Message: {}; User: {};'.format(source, messageType, messageID, severity, length, message, user))

def _createRenderProgram(shaderSource):
    log.debug('Creating render program from "{}"'.format(shaderSource))
    # Render shader source
    with open(shaderSource, 'r') as sourceFile:
        renderShaderSource = sourceFile.read()

    # Render shader
    renderShader = gl.glCreateShader(gl.GL_COMPUTE_SHADER)
    gl.glShaderSource(renderShader, renderShaderSource)
    gl.glCompileShader(renderShader)
    if not gl.glGetShaderiv(renderShader, gl.GL_COMPILE_STATUS):
        log.error('renderShader problem\n{}'.format(gl.glGetShaderInfoLog(renderShader).replace(b'\\n', b'\n').decode()))
        sys.exit(1)

    # Render program
    renderProgram = gl.glCreateProgram()
    gl.glAttachShader(renderProgram, renderShader)
    gl.glLinkProgram(renderProgram)
    if not gl.glGetProgramiv(renderProgram, gl.GL_LINK_STATUS):
        log.error('renderProgram problem\n{}'.format(gl.glGetProgramInfoLog(renderProgram).replace(b'\\n', b'\n').decode()))
        sys.exit(1)

    # Shader cleanup
    # glDeleteShader(renderShader)
    
    return renderProgram

def _createStorageBuffer(bindPoint):
    log.debug('Creating storage buffer at bind point {}'.format(bindPoint))
    storageBuffer = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, storageBuffer)
    gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, bindPoint, storageBuffer)
    return storageBuffer


def initialize(size):
    global sceneRenderProgram, uiRenderProgram
    global framebuffer
    global typeStorageBuffer, intStorageBuffer, floatStorageBuffer
    global contactStorageBuffer
    global viewportSize
    viewportSize = size

    log.info('Initializing OpenGL')
    log.info('Using OpenGL {}'.format(gl.glGetString(gl.GL_VERSION).decode()))
    gl.glDebugMessageCallback(gl.GLDEBUGPROC(_glDebugMessageCallback), None)

    gl.glViewport(0, 0, *viewportSize)

    sceneRenderProgram = _createRenderProgram(pathlib.Path(__file__).parent.joinpath('renderScene.glsl'))
    uiRenderProgram = _createRenderProgram(pathlib.Path(__file__).parent.joinpath('renderUI.glsl'))

    # Texture to render to
    screenTex = gl.glGenTextures(1)
    gl.glActiveTexture(gl.GL_TEXTURE0)
    gl.glBindTexture(gl.GL_TEXTURE_2D, screenTex)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)    # Set min filter to linear instead of mipmap

    # Allow the render shader to write to the texture
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA32F, *viewportSize, 0, gl.GL_RGBA, gl.GL_FLOAT, None)
    gl.glBindImageTexture(0, screenTex, 0, gl.GL_FALSE, 0, gl.GL_WRITE_ONLY, gl.GL_RGBA32F)

    # https://stackoverflow.com/a/58043489
    # Generate a framebuffer and attach the texture to it
    framebuffer = gl.glGenFramebuffers(1)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, screenTex, 0)
    gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, framebuffer)
    gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)

    # Shader storage buffers for scene objects
    typeStorageBuffer = _createStorageBuffer(1)
    intStorageBuffer = _createStorageBuffer(2)
    floatStorageBuffer = _createStorageBuffer(3)

    # Shader storage buffer to hold contact ID output
    contactStorageBuffer = _createStorageBuffer(4)
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, contactStorageBuffer)
    dataSize = viewportSize[0] * viewportSize[1] * 4
    gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, dataSize, b'\x00' * dataSize, gl.GL_DYNAMIC_READ)


def compile(scene):
    # Compile scene/ui data
    typeData, intData, floatData = scene.compileBufferData()
    if not typeData is None:
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, typeStorageBuffer)
        gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, len(typeData), typeData, gl.GL_DYNAMIC_DRAW)

    if not intData is None:
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, intStorageBuffer)
        gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, len(intData), intData, gl.GL_DYNAMIC_DRAW)

    if not floatData is None:
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, floatStorageBuffer)
        gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, len(floatData), floatData, gl.GL_DYNAMIC_DRAW)

    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, 0)

def paintScene():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    # Dispatch render program
    gl.glUseProgram(sceneRenderProgram)
    gl.glDispatchCompute(viewportSize[0] // 8, viewportSize[1] // 8, 1)
    gl.glMemoryBarrier(gl.GL_ALL_BARRIER_BITS)

    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, contactStorageBuffer)
    contacts.scene = struct.unpack('i' * viewportSize[0] * viewportSize[1], gl.glGetBufferSubData(gl.GL_SHADER_STORAGE_BUFFER, 0, viewportSize[0] * viewportSize[1] * 4))

def paintUI():
    gl.glUseProgram(uiRenderProgram)
    gl.glDispatchCompute(viewportSize[0] // 8, viewportSize[1] // 8, 1)
    gl.glMemoryBarrier(gl.GL_ALL_BARRIER_BITS)

    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, contactStorageBuffer)
    contacts.ui = struct.unpack('i' * viewportSize[0] * viewportSize[1], gl.glGetBufferSubData(gl.GL_SHADER_STORAGE_BUFFER, 0, viewportSize[0] * viewportSize[1] * 4))

def blitBuffers():
    # Copy data to default framebuffer's backbuffer
    gl.glBlitFramebuffer(
        0, 0, *viewportSize,
        0, 0, *viewportSize,
        gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR
    )
