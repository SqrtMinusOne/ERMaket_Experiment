import logging

import click

from ermaket.api.config import Config
from ermaket.cli import db, system, hierarchy, scripts


@click.group()
@click.option('--log/--no-log', default=True, is_flag=True)
@click.option('--sql-log/--no-sql-log', default=False, is_flag=True)
def cli(log, sql_log):
    if sql_log:
        logger = logging.getLogger('sqlalchemy.engine')
        logger.setLevel(logging.INFO)

    if log:
        config = Config()
        logging.basicConfig(
            level=logging.DEBUG,
            format=config.Logging['formatters']['single-line']['format'],
            datefmt='%I:%M:%S'
        )


cli.add_command(db)
cli.add_command(hierarchy)
cli.add_command(system)
cli.add_command(scripts)

if __name__ == "__main__":
    cli()
