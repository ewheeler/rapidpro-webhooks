from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from server import app, db

__author__ = 'kenneth'
app.config.from_object('settings.base')

migrate = Migrate(app, db)
manager = Manager(app,)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
