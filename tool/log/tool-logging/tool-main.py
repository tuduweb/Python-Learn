import logging

class log(object):
    pass

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        # format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(process)d %(thread)d - %(message)s',
        format='%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(process)d %(thread)d - %(pathname)s:%(lineno)d %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S.%s+0800',
    )

    # make singleton, can make tree?
    logger = logging.getLogger("main")

    logger.debug('I love you ~')
    logger.warning('I love you too~')

    child_logger = logging.getLogger('main.child')
    child_logger.debug('I love you ~')
    child_logger.warning('I love you too~')
