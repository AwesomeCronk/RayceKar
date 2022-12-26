import logging, time
from math import sin

import raycekar as rk
from raycekar.coord import *
from raycekar.util import loggingHandler


frameLimit = 120
viewportSize = vec2(800, 800)
threadGroupSize = vec2(8, 4)
fpsCountInterval = 200


### Main section ###
if __name__ == '__main__':
    log = logging.getLogger('main')
    log.setLevel(logging.DEBUG)
    log.addHandler(loggingHandler)

    rk.ui.initialize()

    with rk.ui.createWindow('Window title', viewportSize):
        rk.gl.initialize(viewportSize, threadGroupSize)

        # Scene setup
        scene = rk.env.scene()
        camera = rk.env.camera(vec3(0, -5, 0), quat.fromAxisAngle(vec4(1, 0, 0, deg(0))), deg(70))
        sphere0 = rk.env.sphere(vec3(-3, 0, 0), 0.5)
        sphere1 = rk.env.sphere(vec3(-1, 0, 0), 0.5)
        sphere2 = rk.env.sphere(vec3(1, 0, 0), 0.5)
        sphere3 = rk.env.sphere(vec3(3, 0, 0), 0.5)
        scene.addCamera(camera)
        scene.addShape(sphere0)
        scene.addShape(sphere1)
        scene.addShape(sphere2)
        scene.addShape(sphere3)

        for i in range(10):
            scene.addShape(rk.env.sphere(vec3(0, i + 1, 0), 0.5))

        def closeWindow(action):
            # log.info('Window close event triggered (action: {})'.format(action))
            rk.ui.closeWindow()

        rk.ui.keys.setEvent(rk.ui.keys.ESCAPE, closeWindow)

        # Main loop
        frame = -1
        frameTimes = []
        renderTimes = []
        endTime = time.perf_counter()

        while not rk.ui.flags.shouldClose:
            frame += 1
            startTime = endTime

            sphere0.move(vec3(-3, 0, 2 * sin(rad(deg(frame)))))
            sphere1.move(vec3(-1, 0, 2 * sin(rad(deg(frame + 90)))))
            sphere2.move(vec3(1, 0, 2 * sin(rad(deg(frame + 180)))))
            sphere3.move(vec3(3, 0, 2 * sin(rad(deg(frame + 270)))))

            rk.gl.compileScene(scene)
            renderStart = time.perf_counter()
            rk.gl.paintScene()
            renderStop = time.perf_counter()
            rk.gl.blitBuffers()
            rk.ui.updateWindow()

            # FPS limiting
            # time.sleep(max(0, (1 / frameLimit) - (time.perf_counter() - startTime)))
            endTime = time.perf_counter()

            # FPS counting
            frameTimes.append(endTime - startTime)
            renderTimes.append(renderStop - renderStart)
            if len(frameTimes) == fpsCountInterval:
                print('Stats for {} frames:'.format(fpsCountInterval))
                print('FPS: {}'.format(round(fpsCountInterval / sum(frameTimes), 6)))
                print('Frame time: {}'.format(round(sum(frameTimes) / fpsCountInterval, 6)))
                print('  Render time: {}'.format(round(sum(renderTimes) / fpsCountInterval, 6)))
                print('  CPU time: {}'.format(round((sum(frameTimes) - sum(renderTimes)) / fpsCountInterval, 6)))
                frameTimes = []
                renderTimes = []
