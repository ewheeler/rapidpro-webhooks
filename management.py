import logging
from flask.ext.script import Command
from api.v1.referrals.models import RefCode

__author__ = 'kenneth'


class UpdateFt(Command):
    def run(self):
        codes = RefCode.query.all()
        for code in codes:
            logging.info("Updating entries for code %s(%d)" % (code.name, code.id))
            if code.ft_id:
                code.update_fusion_table()


class CreateFT(Command):
    def run(self):
        codes = RefCode.get_with_no_ft_id()
        for code in codes:
            logging.info("Creating FT for %d" % code.id)
            logging.info(code.create_ft())


class CreateMainFT(Command):
    def run(self):
        logging.info("Creating Main FT")
        RefCode.create_main_ft()


class UpdateMainFT(Command):
    def run(self):
        logging.info("Updating Main FT")
        RefCode.update_main_ft()