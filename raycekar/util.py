import logging

loggingHandler = logging.StreamHandler()
loggingHandler.setLevel(logging.DEBUG)
loggingFormatter = logging.Formatter('%(name)9s %(levelname)-8s --- %(message)s')
loggingHandler.setFormatter(loggingFormatter)
