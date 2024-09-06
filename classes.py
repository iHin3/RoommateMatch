import time

class Person:
	def __init__(self,idNum,name,gender,age,picture,email,password,classyear,dorm,offcampus):
		self.idNum		=idNum
		self.name		=name
		self.gender		=gender
		self.age		=age
		self.picture	=picture
		self.email		=email
		self.password	=password
		self.classyear	=classyear
		self.dorm		=dorm
		self.offcampus	=offcampus
		self.prefs		={
					        "bio": 				None,
					        "prefGender": 		None,
					        "prefClassYear": 	None,
					        "interests": 		None,
					        "alcohol": 			None,
					        "smoking": 			None,
					        "sleep": 			None,
					        "wake": 			None,
					        "temp": 			None,
					        "organized": 		None,
					        "guests": 			None,
					        "comm": 			None,
					        "swipedUsers": 		{},
					        "swipedPrefs": 		{}
					    }

	def updateAttribute(self,attr,newValue):
		eval(f'self.{attr}={newValue}')

	def updatePref(self,pref,newValue):
		self.prefs[f"{pref}"]=newValue

	def updateSwipedUsers(self,swipedUser,newValue):
		self.prefs["swipedUsers"].[f"{swipedUser}"]=newValue

	def updateSwipedPrefs(self,swipedPref,newValue):
		self.prefs["swipedPrefs"].[f"{swipedPref}"]=newValue

class Message:
	def __init__(self,author,content):
		self.time=int(time.time())
		self.author=author
		self.content=content

class ChatConversation:
	def __init__(self,userA,userB):
		#prevent issues of having conversation(0,1) and conversation(1,0) being counted as different
		userA,userB=sort(userA,userB)
		self.userA=userA
		self.userB=userB
		self.messages=[]

	def addNewMessage(self,message):
		self.messages.append(message)
