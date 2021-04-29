#This seeds the database to the initial state

from Domain.User import User
from Domain.Message import Message
from Domain.Role import Role
from Domain.Channel import Channel, GroupChannel

def seedDatabase(db):

    user1 = User("USER-1", "user1","Name1", ["ROLE-3", "ROLE-5"], [])
    user2 = User("USER-2", "Brad123", "Brad McBradface", ["ROLE-1", "ROLE-4"], [])
    user3 = User("USER-3", "Team5", "Jon Pedersen", ["ROLE-4"], [])

    role1 = Role("ROLE-1", "Manager")
    role2 = Role("ROLE-2", "Doctor")
    role3 = Role("ROLE-3", "Receptionist")
    role4 = Role("ROLE-4", "Nurse")
    role5 = Role("ROLE-5", "Brain surgeron")

    channel1 = GroupChannel("CHANNEL-1", [], "Intensivavdeling", ["ROLE-1", "ROLE-3"])
    channel2 = GroupChannel("CHANNEL-2", [], "Akutmottak", ["ROLE-4"])

    db.addRole(role1)
    db.addRole(role2)
    db.addRole(role3)
    db.addRole(role4)
    db.addRole(role5)


    db.addUser(user1)
    db.addUser(user2)

    db.addChannel(channel1)
    db.addChannel(channel2)