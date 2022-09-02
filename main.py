import logging, sys, time
from OpenGL import GL as gl
import glfw
import env
from coord import *


### Logging setup ###
logger = None
glfwLogger = None
glLogger = None

def setupLogging():
    global logger
    global glfwLogger
    global glLogger
    loggingHandler = logging.StreamHandler()
    loggingHandler.setLevel(logging.DEBUG)
    loggingFormatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    loggingHandler.setFormatter(loggingFormatter)

    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(loggingHandler)
    glfwLogger = logging.getLogger('glfw')
    glfwLogger.addHandler(loggingHandler)
    glfwLogger.setLevel(logging.DEBUG)
    glLogger = logging.getLogger('gl')
    glLogger.addHandler(loggingHandler)
    glLogger.setLevel(logging.DEBUG)


### Global values ###
# Constants
viewportSize = (1000, 1000)
needGLVersion = (4, 4)

# Variables
scene = None

renderShaderSource = ""
renderShader = None
renderProgram = None

framebuffer = None

typeStorageBuffer = None
intStorageBuffer = None
floatStorageBuffer = None


### GLFW event flags / callbacks ###
# This one is left as an example of how to set up future callbacks in a nice fashion
# glfwWindowResize = False
# 
# def windowResizeCallback(window, width, height):
#     global flagWindowResize
#     glfwWindowResize = True
#     glfwLogger.debug('callback windowResize ({}, {})'.format(width, height))


### GL functions ###
def initializeGL():
    global renderShaderSource, renderShader, renderProgram
    global framebuffer
    global typeStorageBuffer, intStorageBuffer, floatStorageBuffer    
    glLogger.info('Using OpenGL version {}'.format(gl.glGetString(gl.GL_VERSION).decode()))

    gl.glViewport(0, 0, *viewportSize)

    # Render shader source
    with open('render.glsl', 'r') as sourceFile:
        renderShaderSource = sourceFile.read()

    # Render shader
    renderShader = gl.glCreateShader(gl.GL_COMPUTE_SHADER)
    gl.glShaderSource(renderShader, renderShaderSource)
    gl.glCompileShader(renderShader)
    if not gl.glGetShaderiv(renderShader, gl.GL_COMPILE_STATUS):
        glLogger.error('renderShader problem\n{}'.format(gl.glGetShaderInfoLog(renderShader).replace(b'\\n', b'\n').decode()))
        sys.exit(1)

    # Render program
    renderProgram = gl.glCreateProgram()
    gl.glAttachShader(renderProgram, renderShader)
    gl.glLinkProgram(renderProgram)
    if not gl.glGetProgramiv(renderProgram, gl.GL_LINK_STATUS):
        glLogger.error('renderProgram problem\n{}'.format(gl.glGetProgramInfoLog(renderProgram).replace(b'\\n', b'\n').decode()))
        sys.exit(1)

    # Shader cleanup
    # glDeleteShader(renderShader)
    
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
    typeStorageBuffer = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, typeStorageBuffer)
    gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 1, typeStorageBuffer)

    intStorageBuffer = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, intStorageBuffer)
    gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 2, intStorageBuffer)

    floatStorageBuffer = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, floatStorageBuffer)
    gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 3, floatStorageBuffer)


def paintGL():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    # Dispatch render program
    gl.glUseProgram(renderProgram)
    gl.glDispatchCompute(*viewportSize, 1)
    gl.glMemoryBarrier(gl.GL_ALL_BARRIER_BITS)
    status = gl.glGetError()
    if status != gl.GL_NO_ERROR: glLogger.error('code {} after dispatching renderProgram'.format(status)); sys.exit(1)

    # Copy data to default framebuffer's backbuffer
    gl.glBlitFramebuffer(
        0, 0, *viewportSize,
        0, 0, *viewportSize,
        gl.GL_COLOR_BUFFER_BIT, gl.GL_LINEAR
    )
    status = gl.glGetError()
    if status != gl.GL_NO_ERROR: glLogger.error('code {} after blitting framebuffers'.format(status)); sys.exit(1)


def updateSceneGL():
    # Update scene data
    typeData, intData, floatData = scene.compileBufferData()
    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, typeStorageBuffer)
    gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, len(typeData) * 4, typeData, gl.GL_DYNAMIC_DRAW)

    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, intStorageBuffer)
    gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, len(intData) * 4, intData, gl.GL_DYNAMIC_DRAW)

    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, floatStorageBuffer)
    gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, len(floatData) * 4, floatData, gl.GL_DYNAMIC_DRAW)

    gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, 0)


### Main section ###
if __name__ == '__main__':
    setupLogging()
    if not glfw.init(): logger.error('failed to initialize GLFW'); sys.exit(1)

    try:
        ### Initialization sequence ###
        logger.info('requiring OpenGL {}.{} core or higher'.format(*needGLVersion))
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, needGLVersion[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, needGLVersion[1])
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, False)

        window = glfw.create_window(*viewportSize, 'OpenGL Testing', None, None)
        if not window: logger.error('failed to open GLFW window.'); sys.exit(1)
        glfw.make_context_current(window)
        initializeGL()

        # Set up GLFW callbacks
        # glfw.set_window_size_callback(window, windowResizeCallback)

        # Scene setup
        scene = env.scene()
        camera = env.camera(vec3(0, -5, 2), quat.fromAxisAngle(vec4(1, 0, 0, degToRad(-10))), degToRad(70))
        sphere = env.sphere(vec3(0, 0, 0), 0.5)
        cameraID = scene.addObject(camera)
        sphereID = scene.addObject(sphere)
        # sceneBufferData = scene.compileBufferData()

        # Main loop
        frameTimes = []
        endTime = time.perf_counter_ns()
        while not glfw.window_should_close(window):
            startTime = endTime

            # Handle GLFW events
            if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(window, True)

            # if glfwWindowResize:
            #     resizeGL(*glfw.get_framebuffer_size(window))
            #     glfwWindowResize = False

            updateSceneGL()
            paintGL()
            glfw.swap_buffers(window)
            glfw.poll_events()

            # FPS counting
            endTime = time.perf_counter_ns()
            frameTimes.append(endTime - startTime)
            if len(frameTimes) == 100:
                print('Average FPS: {}'.format(round(1 / (sum(frameTimes) / len(frameTimes) / 1000000000), 6)))
                frameTimes = []
                sphere.move(vec3(0, 0, 1) - sphere.pos)
        
        logger.info('Main loop broke')

    finally:
        glfw.terminate()
