from magma import Flows
from wrench import Config
import falcon
from wsgiref.simple_server import make_server

if __name__ == "__main__":
	booster = falcon.App()
	booster.resp_options.secure_cookies_by_default = False
	booster.add_route("/login",Flows.Login())
	booster.add_route("/",Flows.Main())
	booster.add_route("/hb",Flows.Heartbeat())
	with make_server(Config.Host,Config.Port,booster) as httpd:
		httpd.serve_forever()