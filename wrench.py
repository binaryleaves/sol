import pydblite
from copy import copy
from sys import argv

class Config():
    InstanceName = "Cirno's Domain"
    InitialUsername = "autumn"
    Url = "cirnoisthe.best"
    DefaultDesc = "I'm a very mysterious person."
    CharacterLimitGeneral = 100000
    PostButtonText = "Post | Remember the human"
    DefaultPFP = "themes/default/defaultPfp.png"
    Host = "127.0.0.1"
    Port = 6969

if __name__ == "__main__":
    if argv[1] == "deleteUser":
        userdb = pydblite.Base("userdb").open()
        for r in userdb:
            print(r)
        print("Which user do you wish to modify? [name] ",end="")
        name = input()
        target = None
        for r in userdb:
            if name in r.values():
                target = r
                break
        userdb.delete(target)
        userdb.commit()
        print("User deleted!")
    if argv[1] == "kingUser":
        userdb = pydblite.Base("userdb").open()
        for r in userdb:
            print(r)
        print("Which user do you wish to modify? [name] ",end="")
        name = input()
        target = None
        for r in userdb:
            if name in r.values():
                target = r
                break
        userdb.update(r,admin=True)
        userdb.commit()
        print("User kinged!")
    if argv[1] == "modUser":
        userdb = pydblite.Base("userdb").open()
        for r in userdb:
            print(r)
        print("Which user do you wish to modify? [name] ",end="")
        name = input()
        target = None
        for r in userdb:
            if name in r.values():
                target = r
                break
        userdb.update(r,mod=True)
        userdb.commit()
        print("User modded!")

