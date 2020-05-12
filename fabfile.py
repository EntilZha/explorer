from fabric import task

from qanta.log import get_logger


log = get_logger(__name__)


@task
def deploy(conn):
    with conn.cd("~/qanta-viewer"):
        log.info(conn.run("docker-compose down"))
        log.info(conn.run("git pull origin master"))
        log.info(conn.run("docker-compose up -d"))
