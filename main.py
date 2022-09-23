import logging, time
from math import sin

import raycekar as rk
from raycekar.coord import *
from raycekar.util import loggingHandler


frameLimit = 120


### Main section ###
if __name__ == '__main__':
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(loggingHandler)

    rk.ui.initialize()

    with rk.ui.createWindow('Window title', (800, 800)):
        rk.gl.initialize((800, 800))

        # Scene setup
        scene = rk.env.scene()
        camera = rk.env.camera(vec3(0, -5, 0), quat.fromAxisAngle(vec4(1, 0, 0, deg(0))), deg(70))
        sphere0 = rk.env.sphere(vec3(-3, 0, 0), 0.5)
        sphere1 = rk.env.sphere(vec3(-1, 0, 0), 0.5)
        sphere2 = rk.env.sphere(vec3(1, 0, 0), 0.5)
        sphere3 = rk.env.sphere(vec3(3, 0, 0), 0.5)
        scene.addObject(camera)
        scene.addObject(sphere0)
        scene.addObject(sphere1)
        scene.addObject(sphere2)
        scene.addObject(sphere3)

        # UI setup
        mainWidget = rk.ui.widget(vec2(50, 20), vec2(40, 40), vec4(1, 0.388, 0.035, 1))

        def closeWindow(action):
            # logger.info('Window close event triggered (action: {})'.format(action))
            rk.ui.closeWindow()

        # def moveBox(action):
        #     mainWidget.move(rk.ui.mouse.pos)

        rk.ui.keys.setEvent(rk.ui.keys.ESCAPE, closeWindow)
        # rk.ui.mouse.setEvent(rk.ui.mouse.LEFT, moveBox)

        # Main loop
        frame = -1
        frameTimes = []
        endTime = time.perf_counter()

        while not rk.ui.flags.shouldClose:
            frame += 1
            startTime = endTime

            # if rk.ui.keys.pressed(rk.ui.keys.ESCAPE):
            #    rk.ui.closeWindow()

            if rk.ui.keys.pressed(rk.ui.keys.X):
                mainWidget.move(rk.ui.mouse.pos)

            if rk.ui.mouse.pressed(rk.ui.mouse.LEFT):
                mainWidget.move(rk.ui.mouse.pos)

            sphere0.move(vec3(-3, 0, 2 * sin(rad(deg(frame)))))
            sphere1.move(vec3(-1, 0, 2 * sin(rad(deg(frame + 90)))))
            sphere2.move(vec3(1, 0, 2 * sin(rad(deg(frame + 180)))))
            sphere3.move(vec3(3, 0, 2 * sin(rad(deg(frame + 270)))))

            # print(rk.ui.mouse.pos)
            # mainWidget.move(rk.ui.mouse.pos)

            rk.gl.compile(scene)
            rk.gl.paintScene()
            rk.gl.compile(mainWidget)
            rk.gl.paintUI()
            rk.gl.blitBuffers()
            rk.ui.updateWindow()

            # FPS limiting
            time.sleep(max(0, (1 / frameLimit) - (time.perf_counter() - startTime)))
            endTime = time.perf_counter()

            # FPS counting
            # frameTimes.append(endTime - startTime)
            # if len(frameTimes) == 100:
            #     print('Average FPS: {}'.format(round(1 / (sum(frameTimes) / len(frameTimes)), 6)))
            #     frameTimes = []
