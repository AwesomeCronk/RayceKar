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

    with ui.createWindow('Window title') as window:
        gl.initialize()


        # Scene setup
        scene = env.scene()
        camera = env.camera(vec3(0, -5, 0), quat.fromAxisAngle(vec4(1, 0, 0, degToRad(0))), degToRad(70))
        sphere0 = env.sphere(vec3(-3, 0, 0), 0.5)
        sphere1 = env.sphere(vec3(1, 0, 0), 0.5)
        sphere2 = env.sphere(vec3(1, 0, 0), 0.5)
        sphere3 = env.sphere(vec3(3, 0, 0), 0.5)
        # box = env.box(vec3(0, 0, 0), quat.fromAxisAngle(vec4(0, 0, 1, 0)), vec3(1, 1, 1))
        cameraID = scene.addObject(camera)
        sphere0ID = scene.addObject(sphere0)
        sphere1ID = scene.addObject(sphere1)
        sphere2ID = scene.addObject(sphere2)
        sphere3ID = scene.addObject(sphere3)
        # boxID = scene.addObject(box)
        # sceneBufferData = scene.compileBufferData()

        def closeWindow(action):
            logger.info('Window close event triggered (action: {})'.format(action))
            ui.close(window)

        ui.setKeyEvent(window, ui.keys.ESCAPE, closeWindow)

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

            gl.updateScene(scene)
            gl.paint()
            ui.update(window)

            # FPS limiting
            time.sleep(max(0, (1 / frameLimit) - (time.perf_counter() - startTime)))

            # FPS counting
            endTime = time.perf_counter()
            frameTimes.append(endTime - startTime)
            if len(frameTimes) == 100:
                print('Average FPS: {}'.format(round(1 / (sum(frameTimes) / len(frameTimes)), 6)))
                frameTimes = []
        
        logger.info('Main loop broke')

