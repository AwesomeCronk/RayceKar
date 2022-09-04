import logging

loggingHandler = logging.StreamHandler()
loggingHandler.setLevel(logging.DEBUG)
loggingFormatter = logging.Formatter('%(name)9s %(levelname)-8s --- %(message)s')
loggingHandler.setFormatter(loggingFormatter)

viewportSize = (512 // 8 * 8, 512 // 8 * 8)
needGLVersion = (4, 4)
