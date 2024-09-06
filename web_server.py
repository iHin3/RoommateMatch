#   This file is responsible for the web server.
#   It will be used to send data to the web server.
#   It will also be used to receive data from the web server.
import base64
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
import time
import random
import cgi
import os

hostName = ""
hostPort = 80

class SurveyWebServer(BaseHTTPRequestHandler):
    
    def _set_headers(self, content_type='text/html', length=0):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        if length > 0:
            self.send_header('Content-Length', str(length))
        self.end_headers()

    #	GET request handler
    def do_GET(self):
        print(self.path)
        mimeTypes = {
            '.html': 'text/html',
            '.htm': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif'
            # Add more MIME types as needed
        }

        filePath = "." + self.path.replace("%20", " ").split('?')[0]
        extension = os.path.splitext(filePath)[1]
        contentType = mimeTypes.get(extension, 'application/octet-stream')
        self.send_response(200)

        #this is a terrible way to handle this, but let's do it anyways!!!
        if filePath.startswith('.dynamic'):
            #safety net
            try:
                #parse dynamic params
                rawDynamicParams=self.path.split('?')[1].split('&')
                dynamicPerms={}
                for i in range(len(rawDynamicParams)):
                    rawDynamicParams[i]=rawDynamicParams[i].split('=')
                    dynamicPerms[rawDynamicParams[i][0]]=rawDynamicParams[i][1]
                #now start dynamic stuff
                if dynamicPerms['mode'] == "chat":
                    #chat stuff, let's go!
                    cookies = SimpleCookie(self.headers.get('Cookie'))
                    #use the user's email to get their ID number somehow
                    username = cookies['session'].value.split(':')[0]
                    otherChatParty=dynamicPerms['id']
                    #check if conversation between these two exist. If so, return that
                    #if not, create a new chat conversation

            #whoops, some kind of error, send them back to the main page
            except:
                with open("index.html", "r") as f:
                    webPage=f.read()
                self.wfile.write(bytes(webPage, "utf-8"))

        #handle things in a normal way
        else:
            try:
                with open(filePath, "rb") as f:
                    webPage=f.read()
                self._set_headers(content_type=contentType, length=len(webPage))
                self.wfile.write(webPage)
            except:
                with open("index.html", "r") as f:
                    webPage=f.read()
                self.wfile.write(bytes(webPage, "utf-8"))

    #	POST is for submitting data.
    def do_POST(self):
        #Handle post request body
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        tagList=False
        a=""
        # print(form)
        print(form.keys())
        cookies = SimpleCookie(self.headers.get('Cookie'))
        #Output all fields
        for i in form:
            try:
                print(form[i].value)
            except:
                print(form[i])
            
            # print(i.value)
        #handle different requests

        #demonstrate handling post requests
        if form['type'].value == "registration":
            #Setup the HTML response template
            name        =form['name'].value
            gender      =form['gender'].value
            age         =form['age'].value
            picture     =form['picture'].value
            email       =form['email'].value
            password    =form['password'].value
            classyear   =form['classyear'].value
            dorm        =form['dorm'].value
            offcampus   =form['offcampus'].value

            thisUser = createUser(name,gender,age,picture,email,password,classyear,dorm,offcampus)

            #call a function to add the user to Tyler's database, that would return true if successful, and false if not
            result=True#addUserToDatabase(email, password, thisUser)
            sessionValue=f'{email}:{password}'
            if result:
                self.respond(bytes(f'''<!DOCTYPE html>
                    <html>
                        <head>
                            <script type="text/javascript">
                                function setCookie(name, value, days) {{
                                    var expires = "";
                                    if (days) {{
                                        var date = new Date();
                                        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                                        expires = "; expires=" + date.toUTCString();
                                    }}
                                    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
                                }}

                                function setup() {{
                                    setCookie('session', '{sessionValue}', 7);
                                }}

                                window.location = prefs.html;
                            </script>
                        </head>
                        <body>
                        </body>
                    </html>''', "utf-8"))
            else:
                self.respond(bytes(f'''<!DOCTYPE html><html><head><meta http-equiv="refresh" content="2;url=register.html?warning=Error+creating+your+account.+An+account+may+already+be+associated+with+this+email+address."></head><body></body></html>''', "utf-8"))

            #return a url redirect
#             self.respond(bytes(f'''<!DOCTYPE html><html><head><meta http-equiv="refresh" content="2;url=.?value={form["value"].value}&value2={form["value2"].value}"></head><body></body></html>''', "utf-8"))

        if form['type'].value == "prefs":
            bio=            form["bio"].value
            prefGender=     form["prefGender"].value
            prefClassyear=  form["prefClassyear"].value
            interests=      ",".join(form.getlist("interests")).split(",")
            alcohol=        form["alcohol"].value
            smoke=          form["smoke"].value
            sleep=          form["sleep"].value
            wake=           form["wake"].value
            temp=           form["temp"].value
            org=            form["org"].value
            guests=         form["guests"].value
            comm=           form["comm"].value

            #call to function to update a user's preferences
            result=updatePrefs(thisUser.get("idNum"),bio,prefGender,prefClassyear,interests,alcohol,smoke,sleep,wake,temp,org,guests,comm)

            if result:
                self.respond(bytes(f'''<!DOCTYPE html><html><head><meta http-equiv="refresh" content="2;url=cardTest.html"></head><body></body></html>''', "utf-8"))
            else:
                self.respond(bytes(f'''<!DOCTYPE html><html><head><meta http-equiv="refresh" content="2;url=prefs.html?warning=Error+setting+your+preferences.+Please+ensure+you+are+logged+in+and+answered+all+the+questions."></head><body></body></html>''', "utf-8"))


        if form['type'].value == "login":
            email       =form['email1'].value
            password    =form['password1'].value
            #call a function to validate credentials
            
            #result=True#login(email,password)
            #if result:
            
            thisUser=login(email,password)
            sessionValue=f'{email}:{password}'
            if thisUser:
                self.respond(bytes(f'''<!DOCTYPE html>
                    <html>
                        <head>
                            <script type="text/javascript">
                                function setCookie(name, value, days) {{
                                    var expires = "";
                                    if (days) {{
                                        var date = new Date();
                                        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                                        expires = "; expires=" + date.toUTCString();
                                    }}
                                    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
                                }}

                                function setup() {{
                                    setCookie('session', '{sessionValue}', 7);
                                }}

                                window.location = cardTest.html;
                            </script>
                        </head>
                        <body>
                        </body>
                    </html>''', "utf-8"))
            else:
                self.respond(bytes(f'''<!DOCTYPE html><html><head><meta http-equiv="refresh" content="2;url=prefs.html?warning=Error+logging+you+in.+Please+ensure+your+email+and+password+are+correct."></head><body></body></html>''', "utf-8"))


        if form['type'].value == "swipe":
            idNum    =form['id'].value
            swipe    =form['swipe'].value
            #call a function to update user prefs
            # nextMatch=getNextMatch(thisUser)
            if swipe == "good":
                self.respond(bytes(f'''Good swipe''', "utf-8"))
            elif swipe == "bad":
                self.respond(bytes(f'''Bad swipe''', "utf-8"))
            else:
                self.respond(bytes(f'''How did you get an invalid swipe?''', "utf-8"))
            # userSwiped(thisUser,nextMatch,swipe)


        print("incomming http: ", self.path)
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        self.send_response(200)
        print(self.rfile.read())

    #Tbh, idk what this is, but I see it in other servers set up like this, so whatever.
    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)

# createUser will return a dict contaning the infromation provided by the user. - Tyler
def createUser(name,gender,age,picture,email,password,classyear,dorm,offcampus):
    userInfo = {
        "idNum": random.randint(100000, 999999), # SHOULD REMAIN HIDDEN FROM ALL OTHER USERS
        "name": name,
        "gender": gender,
        "age": age,
        "picture": picture,
        "classYear": classyear,
        "dorm": dorm,
        "offcampus": offcampus,        
        "prefs": {}
    }
    return userInfo
    
def updatePrefs(user,bio,prefGender,prefClassYear,interests,alcohol,smoke,sleep,wake,temp,org,guests,comm):
    if user.get("prefs")!={}:
        temp = user.get("prefs")
        swipedUserDict = temp.get("swipedUsers")
        swipedPrefsDict = temp.get("swipedDict")
    else:
        swipedUserDict = {}
        swipedPrefsDict = {}
    userPrefs = {
        "bio": bio,
        "prefGender": prefGender,
        "prefClassYear": prefClassYear,
        "interests": interests, #Tyler: Presumably a set? Ike: It's a list, but could probably easily be converted to a set, yeah
        "alcohol": alcohol, # 0-4
        "smoking": smoke, # 0-4
        "sleep": sleep, # 0-4
        "wake": wake, # 0-4
        "temp": temp, # 0-4
        "organized": org, # 0-4
        "guests": guests, # 0-4
        "comm": comm, # 0-4
        "swipedUsers": swipedUserDict, # SHOULD REMAIN HIDDEN FROM ALL USERS
        "swipedPrefs": swipedPrefsDict # SHOULD REMAIN HIDDEN FROM ALL USERS
    }
    user.update({"prefs": userPrefs})
    return True

# login will return w/ the user information associated w/ the provided credentials, if they exist. Otherwise, will return False. - Tyler
def login(email,password):
    # Search database for email in entry list 
        # If found, compare stored password w/ param password
            # If equal, return w/ user information
            # Otherwise, return False
        # Otherwise, return False
    return True

def userSwiped(thisUser,swipedUser,swipe):
    # Add swiped user to dict of already seen users
    userPrefs = thisUser.get("prefs")
    swipedUserDict = userPrefs.get("swipedUsers")
    swipedID = swipedUser.get("idNum")
    if swipedUserDict.get(swipedID):
        if swipe == "good":
            swipedUserDict.update(swipedID, swipedUserDict.get(swipedID)+1)
        else: #swipe == "bad"
            swipedUserDict.update(swipedID, swipedUserDict.get(swipedID)-1)
    else:
        if swipe == "good":
            swipedUserDict[swipedID] = 1
        else: #swipe == "bad"
            swipedUserDict[swipedID] = -1
    userPrefs.update("swipedUsers", swipedUserDict)

    # Add swiped user's preferences to swipedPrefsDict, with positive or negative values depending on the swipe
    swipedPrefsDict = userPrefs.get("swipedPrefs")
    swipedUserInterests = (swipedUser.get("prefs")).get("interests")
    for val in swipedUserInterests:
        if swipedPrefsDict.get(val):
            if swipe == "good":
                swipedPrefsDict.update(val, swipedPrefsDict.get(val)+0.01)
            else: #swipe == "bad"
                swipedPrefsDict.update(val, swipedPrefsDict.get(val)-0.01)
        else:
            if swipe == "good":
                swipedPrefsDict[val] = 0.01
            else: #swipe == "bad"
                swipedPrefsDict[val] = -0.01
    userPrefs.update("swipedPrefs", swipedPrefsDict)
    return True

def getNextMatch(thisUser, feed):
    # Create a set of all users from the database called userbase. See line XXX for details. - Tyler
    bestScore = -999999999
    userPrefs = thisUser.get("prefs")
    swipedUserDict = userPrefs.get("swipedUsers")
    for dataUser in userbase:
        # Reset dataScore and obtain dataUser information
        dataScore = 0
        dataUserPrefs = dataUser.get("prefs")
        dataSwipedDict = dataUserPrefs.get("swipedUsers")
        
        # =-=-=-=-=-=-=-= DATASCORE CALC BEGINS HERE =-=-=-=-=-=-=-=
        # If thisUser has already swiped dataUser before, subtract 200 from dataScore
        if swipedUserDict.get(dataUser.get("idNum")):
            dataScore - 200
        
        # If dataUser has swiped right on thisUser, add 200 to dataScore
        if dataSwipedDict.get(thisUser.get("idNum")):
            if dataSwipedDict.get(thisUser.get("idNum")) > 0:
                dataScore + 200

        # If dataUser is of preferred gender and/or classYear, add 20 to dataScore for each
        if dataUser.get("gender") == userPrefs.get("prefGender"):
            dataScore + 20
        if dataUser.get("classYear") == userPrefs.get("prefClassYear"):
            dataScore + 20
        
        # For each of the dataUser's interests, apply thisUser's swipedPrefs value (plus 5 if it's a mutual interest) to dataScore
        for val in dataUserPrefs.get("interests"):
            if val in userPrefs.get("interests"):
                dataScore + 5
            if (userPrefs.get("swipedPrefs")).get(val):
                dataScore + (userPrefs.get("swipedPrefs")).get(val)

        # Discuss how preferences on a slider should affect the score. Once done, implement here.
        # ...

        # =-=-=-=-=-=-=-= DATASCORE CALC ENDS HERE =-=-=-=-=-=-=-=

        # Compare dataScore and bestScore
        if dataScore > bestScore:
            bestScore = dataScore
            bestUser = dataUser
    return bestUser

# addUserToDatabase should return True UNLESS a user with the same email already exists, in which case it will return False. - Tyler
def addUserToDatabase(email, password, userInfo):
    # Search database for email in entry list
        # If found, return False
        # Else, add user to database and return True
            # Users should be stored as three seperate values: an email, a password, and the rest of their information, which is nested within dicts. See createUser for reference. - Tyler
    return True

#Start running the server
def run(server_class=HTTPServer, handler_class=SurveyWebServer, port=8080):
    surveyServer = HTTPServer((hostName, hostPort), SurveyWebServer)
    print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))
    try:
        surveyServer.serve_forever()
    except KeyboardInterrupt:
        pass
    surveyServer.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))


#It's being run via command line
if __name__ == '__main__':
    from sys import argv
    #Give the user the option of choosing the port
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
