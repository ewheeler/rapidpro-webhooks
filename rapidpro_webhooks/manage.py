import logging

from flask_script import Command

from rapidpro_webhooks.api.referrals.models import RefCode, User


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


class UpdateCountrySlug(Command):
    def run(self):
        logging.info("Updating Country Slug")
        User.update_country_slug()
        RefCode.update_country_slug()


class CreateSuperUser(Command):
    def run(self):
        logging.info("Creating SuperUser")
        email = input("Email: ")
        password = input("Password: ")
        User.create_superuser(email, password)
        logging.info("Superuser created successfully")
