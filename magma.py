from wrench import Config
from time import time_ns, time
from hashlib import md5
from uuid import uuid4
from os import mkdir
from mimetypes import guess_type
import jinja2, falcon, pydblite

def HashMD5(string):
    return md5(string.encode()).hexdigest()

def CustomBearerAuth(req,resp,res,gimme=False):
    done = False
    if len(req.cookies)!=1:
        if req.cookies["auth"]:
            ubase = pydblite.Base("userdb").open()
            if len(ubase) != 0:
                for r in ubase:
                    if str(req.cookies["auth"]) == str(r["password"])+str(HashMD5(r["name"])):
                        if gimme:
                            return r
                        else:
                            done = True
    if not done:
        raise falcon.HTTPMovedPermanently("/login")

class Flows():
    class Attachments():
        def on_get(self,req,resp,user,attch):
            with open(req.path[1:],"rb") as f:
                if req.path[-1:-4:-1] == "gnp":
                    resp.content_type = falcon.MEDIA_PNG
                    resp.text = f.read()
                elif req.path[-1:-4:-1] == "gpj" or req.path[-1:-4:-1] == "gep":
                    resp.content_type = falcon.MEDIA_JPEG
                    resp.text = f.read()
    class Main():
        @falcon.before(CustomBearerAuth)
        def on_get(self,req,resp):
            pbase = pydblite.Base("postdb").open()
            with open("themes/default/mainpage.j2") as f:
                resp.content_type = falcon.MEDIA_HTML
                postsUnified = ""
                user = CustomBearerAuth(req,resp,self,True) 
                if len(pbase) != 0:
                    for r in pbase:
                        postsUnified += "<br/><br/>%s"%r["user"] + "<br/><br/><img src='/%s'/><br/>"%user["pfpPointer"] + r["content"] + "<br/><br/><br/><hr/>"
                resp.text = jinja2.Template(f.read()).render(instanceTitle=Config.InstanceName,postsUnified=postsUnified)
    class CreatePost():
        @falcon.before(CustomBearerAuth)
        def on_post(self,req,resp):
            r = CustomBearerAuth(req,resp,self,True)
            print(r["name"])
            pbase = pydblite.Base("postdb").open()
            pbase.insert(req.media["post"],False,r["name"],False,True,False)
            pbase.commit()
            raise falcon.HTTPMovedPermanently("/")
        @falcon.before(CustomBearerAuth)
        def on_get(self,req,resp):
            with open("themes/default/postpage.j2") as f:
                resp.content_type = falcon.MEDIA_HTML
                resp.text = jinja2.Template(f.read()).render(instanceTitle=Config.InstanceName,characterLimitGeneral=Config.CharacterLimitGeneral,postButtonText=Config.PostButtonText)
    class EditProfile():
        @falcon.before(CustomBearerAuth)
        def on_post(self,req,resp):
            r = CustomBearerAuth(req,resp,self,True)
            media = req.get_media()
            for part in media:
                if part.name == "pfp":
                    try:
                        mkdir("attachments/%s"%r["name"])
                    except Exception as e:
                        pass
                    try:
                        with open("attachments/%s/%s"%(r["name"],part.secure_filename),"x+b") as f:
                            part.stream.pipe(f)
                            f.truncate()
                    except Exception as e:
                        pass
                    try:
                        ubase.update(r,pfpPointer="attachments/%s/%s"%(r["name"],part.secure_filename))
                        ubase.commit()
                    except Exception as e:
                        pass
                    raise falcon.HTTPMovedPermanently("/")
        @falcon.before(CustomBearerAuth)
        def on_get(self,req,resp):
            with open("themes/default/editprofilepage.j2") as f:
                resp.content_type = falcon.MEDIA_HTML
                resp.text = jinja2.Template(f.read()).render(instanceTitle=Config.InstanceName)
    class Moderation():
        @falcon.before(CustomBearerAuth)
        def on_get(self,req,resp):
            pass
    class Heartbeat():
        def on_get(self,req,resp):
            resp.text = f"timeMs {str(int(time_ns()//1000000))} timeSec {str(int(time()))}"
    class Auth():
        class Signout():
            @falcon.before(CustomBearerAuth)
            def on_get(self,req,resp):
                req.unset_cookie("auth")
        class Login():
            def on_get(self,req,resp):
                with open("themes/default/loginpage.j2") as f:
                    resp.content_type = falcon.MEDIA_HTML
                    resp.text = jinja2.Template(f.read()).render(instanceTitle=Config.InstanceName)
            def on_post(self,req,resp):
                ubase = pydblite.Base("userdb").open()
                done = False
                if len(ubase) != 0:
                    for r in ubase:
                        if req.media["usr"] in r["name"]:
                            if str(HashMD5(req.media["pwd"])) == r["password"]:
                                resp.set_cookie("auth",str(HashMD5(req.media["pwd"]))+str(HashMD5(req.media["usr"]+"@"+Config.Url)))
                                resp.set_cookie("hello",":-)")
                                done = True
                if done == False:
                    ubase.insert(
                    req.media["usr"]+"@"+Config.Url,
                    str(HashMD5(req.media["pwd"])),
                    Config.DefaultPFP,
                    Config.DefaultDesc,
                    False,
                    False,
                    True
                    )
                    ubase.commit()
                    resp.set_cookie("auth",str(HashMD5(req.media["pwd"]))+str(HashMD5(req.media["usr"]+"@"+Config.Url)))
                    resp.set_cookie("hello",":-)")
                raise falcon.HTTPMovedPermanently("/")
            
if __name__ == "__main__":
    pbase = pydblite.Base("postdb")
    ubase = pydblite.Base("userdb")
    if not pbase.exists():
        pbase.create("content","attachmentPointers","user","federated","local","featured",mode="overwrite")
    if not ubase.exists():
        ubase.create("name","password","pfpPointer","desc","admin","federated","local",mode="overwrite")
