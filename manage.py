import logging

from flask_migrate import MigrateCommand
from flask_script import Command, Manager, Server

from rapidpro_webhooks.apps.core.models import User
from rapidpro_webhooks.apps.referrals.models import RefCode
from rapidpro_webhooks.core import app


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


manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('updateft', UpdateFt())
manager.add_command('createft', CreateFT())
manager.add_command('updatecountryslug', UpdateCountrySlug())
manager.add_command('createsuperuser', CreateSuperUser())
manager.add_command('runserver', Server(port=app.config.get('SERVER_PORT')))


if __name__ == '__main__':
    manager.run()
