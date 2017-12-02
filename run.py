import os
from flask_script import Manager
from flask_migrate import MigrateCommand
from app import create_app


config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)
manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()