from magma import Flows
from wrench import Config
import falcon
from wsgiref.simple_server import make_server

if __name__ == "__main__":
    booster = falcon.App()
    booster.resp_options.secure_cookies_by_default = False
    booster.add_route("/login",Flows.Auth.Login())
    booster.add_route("/attachments/{user}/{attch}",Flows.Attachments())
    booster.add_route("/signout",Flows.Auth.Signout())
    booster.add_route("/",Flows.Main())
    booster.add_route("/hb",Flows.Heartbeat())
    booster.add_route("/mkpo",Flows.CreatePost())
    booster.add_route("/edpr",Flows.EditProfile())
    booster.add_route("/mode",Flows.Moderation())
    with make_server(Config.Host,Config.Port,booster) as httpd:
        print("Rocket has lifted off at %s:%i"%(Config.Host,Config.Port))
        httpd.serve_forever()
