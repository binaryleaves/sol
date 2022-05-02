from wrench import Config
from time import time_ns, time
from hashlib import md5
from uuid import uuid4
import jinja2, falcon, pydblite

class Flows():
	class Main():
		def on_get(self,req,resp):
			if not req.cookies:
				raise falcon.HTTPMovedPermanently("/login")
			else:
				if not req.cookies["auth"]:
					raise falcon.HTTPMovedPermanently("/login")
				else:
					print(req.cookies["auth"])
					ubase = pydblite.Base("userdb").open()
					for r in ubase:
						if req.cookies["auth"] == r["password"]	+str(md5(r["name"].encode()).digest()):
							pass
	class Heartbeat():
		def on_get(self,req,resp):
			resp.text = f"timeMs {str(int(time_ns()//1000000))} timeSec {str(int(time()))}"
	class Login():
		def on_get(self,req,resp):
			if req.cookies:
				if req.cookies["auth"]:
					raise falcon.HTTPMovedPermanently("/")
			with open("themes/default/loginpage.j2") as f:
				resp.content_type = falcon.MEDIA_HTML
				resp.text = jinja2.Template(f.read()).render(instanceTitle=Config.InstanceName)
		def on_post(self,req,resp):
			ubase = pydblite.Base("userdb").open()
			for r in ubase:
				if req.media["usr"] in r["name"]:
					if str(md5(req.media["pwd"].encode()).digest()) == r["password"]:
						print("Login success")
						resp.set_cookie("auth", str(md5(req.media["pwd"].encode()).digest())+str(md5(req.media["usr"].encode()).digest()))
					else:
						raise falcon.HTTPMovedPermanently("/login")
			ubase.insert(
			req.media["usr"]+"@"+Config.Url,
			str(md5(req.media["pwd"].encode()).digest()),
			False,
			Config.DefaultDesc,
			False,
			False,
			False,
			True
			)
			ubase.commit()
			raise falcon.HTTPMovedPermanently("/login")
			
if __name__ == "__main__":
	pbase = pydblite.Base("postdb")
	ubase = pydblite.Base("userdb")
	if not pbase.exists():
		pbase.create("content","attachmentPointers","user","federated","local","featured",mode="overwrite")
	if not ubase.exists():
		pwd = str(uuid4())
		ubase.create("name","password","pfpPointer","desc","admin","mod","federated","local",mode="overwrite")
		ubase.insert(
		Config.InitialUsername+"@"+Config.Url,
		str(md5(pwd.encode()).digest()),
		False,
		Config.DefaultDesc,
		True,
		False,
		False,
		True
		)
		ubase.commit()
		print("Your password is %s"%pwd)