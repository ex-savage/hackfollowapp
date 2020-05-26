import asyncio
import datetime
import logging
import signal
import sys
from asyncio.runners import _cancel_all_tasks

import aiohttp
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from hackfollow import settings
from hackfollow.watcher import check
from hackfollow.webapp import setup_routes


def init_logging():
    config = {
        'handlers': [
            {
                'sink': settings.log_file,
                'level': 'DEBUG'
            },
        ],
    }
    if settings.stdout_log:
        config['handlers'].append({
            'sink': sys.stdout,
            'level': 'DEBUG',
        })
    logger.configure(**config)

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())

    logging.getLogger().setLevel(logging.DEBUG)
    if settings.sql_log:
        logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)
    logging.getLogger().addHandler(InterceptHandler())


def run():
    def shutdown_by_signal(sig):
        logger.info(f'Got {sig} signal. Shutting down..')
        loop.stop()

    init_logging()
    logger.info('Running hackfollow service')
    loop = asyncio.get_event_loop()
    loop.set_debug(settings.debug)

    for sig_name in 'SIGINT', 'SIGTERM':
        loop.add_signal_handler(getattr(signal, sig_name), shutdown_by_signal, sig_name)

    scheduler = AsyncIOScheduler()
    app = web.Application()
    setup_routes(app)

    async def main(run_scheduler=True):
        session = aiohttp.ClientSession()  # todo close
        if run_scheduler:
            scheduler.start()
            scheduler.add_job(
                check, 'interval', (session,),
                seconds=settings.interval, next_run_time=datetime.datetime.now()
            )
        asyncio.create_task(web._run_app(app, host=settings.host, port=settings.port))

    loop.run_until_complete(main())
    loop.run_forever()
    scheduler.shutdown()
    _cancel_all_tasks(loop)
    loop.run_until_complete(loop.shutdown_asyncgens())
    logger.success('Service has been stopped')


if __name__ == '__main__':
    run()
