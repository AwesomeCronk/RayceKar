import logging, time
from math import sin

import env, gl, ui
from coord import *
from util import loggingHandler


frameLimit = 120


### Main section ###
if __name__ == '__main__':
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(loggingHandler)

    ui.initialize()

    with ui.createWindow('Window title'):
        gl.initialize()

        # Scene setup
        scene = env.scene()
        camera = env.camera(vec3(0, -5, 0), quat.fromAxisAngle(vec4(1, 0, 0, degToRad(0))), degToRad(70))
        sphere0 = env.sphere(vec3(-3, 0, 0), 0.5)
        sphere1 = env.sphere(vec3(-1, 0, 0), 0.5)
        sphere2 = env.sphere(vec3(1, 0, 0), 0.5)
        sphere3 = env.sphere(vec3(3, 0, 0), 0.5)
        scene.addObject(camera)
        scene.addObject(sphere0)
        scene.addObject(sphere1)
        scene.addObject(sphere2)
        scene.addObject(sphere3)

        # UI setup
        mainWidget = ui.widget(vec2(50, 20), vec2(40, 40), vec3(1, 0.388, 0.035))

        def closeWindow(action):
            # logger.info('Window close event triggered (action: {})'.format(action))
            ui.close()

        ui.setKeyEvent(ui.keys.ESCAPE, closeWindow)

        # Main loop
        frame = -1
        frameTimes = []
        endTime = time.perf_counter()

        while not ui.flags.shouldClose:
            frame += 1
            startTime = endTime

            # if ui.keyPressed(window, ui.keys.ESCAPE):
            #     ui.close(window)

            # box.move(vec3(0, 0, sin(degToRad(frame))))
            sphere0.move(vec3(-3, 0, 2 * sin(degToRad(frame))))
            sphere1.move(vec3(-1, 0, 2 * sin(degToRad(frame + 90))))
            sphere2.move(vec3(1, 0, 2 * sin(degToRad(frame + 180))))
            sphere3.move(vec3(3, 0, 2 * sin(degToRad(frame + 270))))

            gl.compile(scene)
            gl.paintScene()
            gl.compile(mainWidget)
            gl.paintUI()
            gl.blitBuffers()
            ui.update()

            # FPS limiting
            time.sleep(max(0, (1 / frameLimit) - (time.perf_counter() - startTime)))
            endTime = time.perf_counter()

            # FPS counting
            # frameTimes.append(endTime - startTime)
            # if len(frameTimes) == 100:
            #     print('Average FPS: {}'.format(round(1 / (sum(frameTimes) / len(frameTimes)), 6)))
            #     frameTimes = []
