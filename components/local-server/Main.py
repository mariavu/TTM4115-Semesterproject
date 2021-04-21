from Config.Mqtt import *
from Config.Seed import seedDatabase

from Infrastructure.Controller import Controller
from Infrastructure.Database import Database


def main():
    db = Database()
    seedDatabase(db)

    controller = Controller(MQTT_BROKER, MQTT_PORT, "LOCAL-SERVER-1", MQTT_ROOT_TOPIC)
    controller.start()


    #Composition root, here we load all necessarry configurations and bootup the controller and ensure that the database is seeded.
    
main()
