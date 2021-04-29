from Config.Mqtt import *
from Config.Seed import seedDatabase
from time import sleep

from Infrastructure.Controller import Controller
from Infrastructure.Database import Database
from Infrastructure.TPM import TPM


def main():
    db = Database()
    tpm = TPM()
    seedDatabase(db)

    controller = Controller(db, MQTT_BROKER, MQTT_PORT, "1", MQTT_ROOT_TOPIC, tpm)
    controller.start()

    while 1:
        sleep(100)


    #Composition root, here we load all necessarry configurations and bootup the controller and ensure that the database is seeded.
    
main()
