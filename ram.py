print("Ram started")
from bs4.element import XMLProcessingInstruction
import discord
from random import randint
import datetime
import sys
import asyncio
from lock3 import lock
import bs4
import urllib.request
import os
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process
from difflib import SequenceMatcher
import math
import cv2
import numpy
import pickle
from interp import interp
client = discord.Client()
KEY_CHARACTER = 'ram '
POST_IMAGES = False

CACHE = "./cache.pkl"
AUTO_CACHE_DELAY = 60*5

BARASU = 691843825483776100
AVERAGE_PHOTOGRAPHER_SPAM = 680843866349633568
CIVIL_DISCUSSIONS = 679005570652700688
SCREAM_CHAMBER_BOT_SPAM = 677672546145140747
AARON = 352232928224215041
KYLE = 331974513636147202

DAY = 86400

responses = []
waiters = []

class item():
    def __init__(self,type=None,content=None, messageID = None):
        self.type = type
        self.content = content

    def __getstate__(self):
        return (self.type,self.content)

    def __setstate__(self,data):
        self.type = data[0]
        self.content = data[1]

    def __str__(self):
        return "{0.type} Item: {0.content}".format(self)

    async def send(self,place):
        if self.type == "text":
            while len(self.content)>1999:
                await place.send(self.content[:2000])
                self.content = self.content[2000:]
            await place.send(self.content)
        elif self.type == "file":
            await place.send(file=discord.File(self.content))
        elif self.type == "reaction":
            pass
        elif self.type == None:
            pass


class package():
    def __init__(self,*args):
        self.items = list(args)

    def __getstate__(self):
        return self.items
    
    def __setstate__(self,data):
        self.items = data

    def __str__(self):
        out = "["
        for i in self.items:
            out+=str(i) + ' , '
        out = out[:-3]+']'
        return out

    def append(self,newItem):
        self.items.append(newItem)

    async def send(self,place):
        for i in self.items:
            await i.send(place)

class runAtSend():
    def __init__(self,function,*args):
        self.function = function
        self.args = args

    async def send(self,place):
        await self.function(*self.args).send(place)

class userPlaceholder:
    def __init__(self,id): self.id = id
    def user(self): return client.get_user(id)

class response:
    def __init__(self,textIn=None,content = None,*args,**kwargs):
        if textIn == None: textIn = ""
        self.label = "normal"
        self.inn = textIn
        self.args = args
        self.usePrefix = True
        self.user = None
        self.channel = None
        self.function = None
        self.locked = False
        self.parse = True
        self.argsOut = args
        self.takeArgs = False
        self.error = False
        self.passMessage = False
        self.format = None
        for name,value in kwargs.items():
            if name == "label":
                self.label = value
            elif name == "usePrefix":
                self.usePrefix = value
            elif name == "user":
                self.user = value
            elif name == "channel":
                self.channel = value
            elif name == "function":
                self.function = value
            elif name == "locked":
                self.locked = value
            elif name == "takeArgs":
                self.takeArgs = value
            elif name == "parse":
                self.parse = value
            elif name == "passMessage":
                self.passMessage = value
            elif name == "format":
                self.format = value
            else: print("bad kwarg")
        if isinstance(content,str):
            self.out = item("text",content)
        elif isinstance(content,list):
            for i in range(len(content)):
                if isinstance(content[i],str):
                    content[i] = item("text",content[i])
            self.out = content
        else:
            self.out = content

    def __getstate__(self):
        out = []
        out.append(self.label)
        out.append(self.inn)
        outArgs = []
        for a in self.args:
            try:
                newArg = []
                for i in a:
                    newArg.append(userPlaceholder(i.id))
                outArgs.append(newArg)
            except:
                outArgs.append(a)
        out.append(tuple(outArgs))
        out.append(self.usePrefix)
        out.append(self.user)
        out.append(self.channel)
        out.append(self.function)
        out.append(self.locked)
        out.append(self.parse)
        out.append(self.takeArgs)
        out.append(self.error)
        out.append(self.passMessage)
        out.append(self.format)
        out.append(self.out)
        return out

    def __setstate__(self,data):
        self.label = data[0]
        self.inn = data[1]
        self.args = data[2]
        asyncio.ensure_future(self.fixArgs())
        self.usePrefix = data[3]
        self.user = data[4]
        self.channel = data[5]
        self.function = data[6]
        self.locked = data[7]
        self.parse = data[8]
        self.takeArgs = data[9]
        self.error = data[10]
        self.passMessage = data[11]
        self.format = data[12]
        self.out = data[13]

    async def fixArgs(self):
        argsOut = []
        for a in self.args:
            newArg = []
            try:
                for i in range(len(a)):
                    newArg[i] = a[i].user()
                    if newArg[i] == None:
                        newArg[i] = await client.fetch_user(a[i].id)
            except:
                argsOut.append(a)
        self.args = tuple(argsOut)

    async def fetchUser(self,id,index):
        args = list(self.args)
        args[index] = await client.fetch_user(id)
        if args[index] == None:
            print("Fetch user failed on response {}:{} -> {}".format(self.label,self.inn,self.out))
        else:
            self.args = tuple(args)

    def messageIn(self,message):
        text = message.content
        if self.usePrefix:
            if text[:len(KEY_CHARACTER)].lower() == KEY_CHARACTER.lower():
                text = text[len(KEY_CHARACTER):]
            else:
                return False
        if self.user != None and message.author.id != self.user: return False
        if self.channel != None and message.channel.id != self.channel: return False
        if self.locked:
            if text[-5:] == lock():
                text = text[:-6]
            else: 
                return False
        if self.passMessage:
            args = (message,) + self.args
        else:
            args = self.args
        if self.takeArgs:
            if not isinstance(self.inn,list):
                self.inn = [self.inn]
            for i in self.inn:
                if i.lower() == text.lower()[:len(i)]:
                    try:
                        if i == "":
                            text = text[len(i):]
                        else:
                            text = text[len(i)+1:]
                        if self.format != None and not self.format(text): return False
                        if self.parse:
                            args = list(args)
                            for x in parse(text):
                                args.append(x)
                            self.argsOut = tuple(args)
                        else:
                            self.argsOut = args + (text,)
                    except Exception as e:
                        print(e)
                        self.out = item("text","error in response.messageIn:" + str(e))
                        self.error = True 
                    return True
            return False
        else:
            self.argsOut = args
            if self.inn == None: return True
            if isinstance(self.inn,list):
                for i in self.inn:
                    if i.lower() == text.lower()[:len(i)]:
                        return True
                return False
            return self.inn.lower() == text.lower()[:len(self.inn)]

    def output(self):
        if isinstance(self.out,list):
            return self.out[randint(0,len(self.out)-1)]
        elif self.function != None and self.error == False:
            return self.function(*self.argsOut)
        return self.out

    def help(self):
        return "Figure it out" 


class time(response):
    def output(self):
        time = str(datetime.datetime.now())[11:16]
        if time[0]=='0':
            time = time[1:]
        return item("text",time)


class exit(response):
    def output(self):
        print("exiting")
        sys.exit()


class waiter():
    def __init__(self,time,place,content,repeat = 0,**kwargs):
        self.label = "normal"
        self.time = time
        self.place = place
        self.catchup = False
        if isinstance(content,str):
            self.content = item("text",content)
        else:
            self.content = content
        self.repeat = repeat
        self.endtime = datetime.datetime.now()
        self.endtime = self.setEndtime()
        for name,value in kwargs.items():
            if name == "label":
                self.label = value
            elif name == "catchup":
                self.catchup = value
            else:
                print("bad kwarg in waiter")

    def setEndtime(self):
        if self.catchup:
            return datetime.timedelta(seconds = self.time) + self.endtime
        else:
            return datetime.timedelta(seconds = self.time) + datetime.datetime.now()

    def reset(self):
        self.endtime = self.setEndtime()

    def ready(self):
#       print(str(self.endtime))
#       print(str(datetime.datetime.now()))
#       print(self.endtime<datetime.datetime.now())
        return self.endtime<datetime.datetime.now()

    async def go(self):
        await self.content.send(client.get_channel(self.place))
        self.endtime = self.setEndtime()

    def keep(self):
        if self.repeat==0:
            return False
        if self.repeat>0:
            self.repeat = self.repeat-1
        return True


class dailyPoster(waiter): 
    def __init__(self,time,place,content,repeat = -1,**kwargs):
        waiter.__init__(self,time,place,content,repeat,**kwargs)

    def setEndtime(self):
        today = datetime.date.today()
        return datetime.datetime.combine(today,self.time) + datetime.timedelta(days=1)


class randDailyPoster(dailyPoster):
    def __init__(self,content,repeat = -1,**kwargs):
        dailyPoster.__init__(self,0,content,repeat,**kwargs)
        
    def setEndtime(self):
        today = datetime.date.today()
        return datetime.datetime.combine(today,datetime.time(hour = randint(0,23), minute = randint(0,59),second = randint(0,59)))+datetime.timedelta(days=1)

class removeResponse(waiter):
    def __init__(self,time,place,target,message=item(None,None),**kwargs):
        waiter.__init__(self,time,place,message,**kwargs)
        self.target = target

    async def go(self):
        await waiter.go(self)
        remove(self.target)

class dailyCleanup(dailyPoster):
    def __init__(self,time):
        self.time = time

    def go(self):
        pass
class cacheWaiter(waiter):
    def __init__(self,delayMinutes):
        waiter.__init__(self,delayMinutes*60,None,None,-1,catchup = False)

    async def go(self):
        writeCache()
        self.endtime = self.setEndtime()

class Format:
    def __init__(self):
        self.alphabet = list("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_")
        self.math = list("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_ +-()*/.")
        self.numbers = ['1','2','3','4','5','6','7','8','9','0','.']


    def ticTacToe(self,text):
        if len(text)!=2 or not text[0] in list("abcABC") or not text[1] in ['1','2','3']:
            return False
        return True

    def connectFour(self,text):
        if len(text) == 1 and  text in list("1234567"):
            return True
        return False

    def reversi(self,text):
        if len(text)!=2 or not text[0] in list("abcdefghABCDEFGH") or not text[1] in list("12345678"):
            return False
        return True
    
    def chess(self,text):
        text = text.lower()
        l = ['a','b','c','d','e','f','g','h']
        n = ['1','2','3','4','5','6','7','8']
        p = ['p','k','n','q','r','b']
        if len(text) == 5 and text[0] in l and text[1] in n and text[2] == ' ' and text[3] in l and text[4] in n:
            return True
        elif len(text) == 4:
            if text[0] in l and text[1] in n and text[2] in l and text[3] in n:
                return True
            elif text[0] in p and text[1] in l+n and text[2] in l and text[3] in n:
                return True
        elif len(text) == 3 and text[0] in p and text[1] in l and text[2] in n:
            return True
        elif len(text) == 2 and text[0] in l and text[1] in n:
            return True
        return False

    def equations(self,text):
        print(text)
        if text == None:
            return False
        text = parse(text,'\n')
        for i in text:
            if not self.matcher(i,[self.alphabet+self.numbers,[' '],['='],self.math]):
                return False
        return True

    def matcher(self,t,order):
        print(t)
        i=0
        last = self.math
        index = 0
        while index<len(order)-1 and i < len(t):
            print("t[i]: {}  i: {}  len(t): {}".format(t[i],i,len(t)))
            if t[i] in order[index]:
                i+=1
            elif t[i] in order[index+1]:
                i+=1
                index+=1
            else:
                return False
        print("{} {} {} {}".format(i,len(t),index,len(order)-1))
        if i == len(t) or index < len(order)-1:
            return False
        print("in last section")
        print("{}   {}".format(i,len(t)))
        while i < len(t):
            print("here")
            if t[i] in order[index]:
                i+=1
            else:
                return False
        return True

def redditRetrieve(number,subreddit,section='hot'):
    print("in")
    req = urllib.request.Request("https://www.reddit.com/r/{}/{}".format(subreddit,section), headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req,None,5000) as page:
        soup = bs4.BeautifulSoup(page,features="lxml")
    images = soup.find_all('img')
    #print (images)
    i=0
    while i<len(images):
        if str(images[i]).startswith('<img alt="Post image"'):
            for x in range(len(str(images[i]))-5):
                if str(images[i])[x:x+8] == "redd.it/":
                    x+=8
                    image = "https://i.redd.it/"
                    for a in str(images[i])[x:]:
                        if a != '?' and a != '"':
                            image+=a
                        else: break
                    images[i] = image
            i+=1
        else:
            images.pop(i)
    if number>len(images): number=len(images)
    counter = 0
    names = []
    ext = ""
    print(POST_IMAGES)
    if not POST_IMAGES:
        print("in not post_images")
        pack = package()
        for i in images[:number]:
            pack.append(item("text",i))
            print(pack)
        return pack
    for i in images[:number]:
        for x in range(len(i)-1,0,-1):
            if i[x] == '.':
                   ext = i[x:]
                   break
        try:
            urllib.request.urlretrieve(i,"./memes/"+str(counter)+ext)
        except:
            print("download error")
        names.append("./memes/"+str(counter)+ext)
        counter+=1
    pack = package()
    for i in names:
        pack.items.append(item("file",i))
    return pack

def gameInit(message,boardClass,inputFormat,playersMin = 2,playersMax = 2):
    if playersMin > len(message.mentions)+1 or len(message.mentions)+1 > playersMax:
        if playersMin == playersMax == 2:
            return item("text","@ one person to play with")
        return item("text","@ between {} and {} people".format(playersMin, playersMax))
    opponents = [message.author.id]
    labelCode = message.author.id
    names = message.author.display_name
    for i in message.mentions:
        opponents.append(i.id)
        labelCode += i.id
        names += ' ' + i.display_name
    board = boardClass(opponents)
    label = board.title+str(labelCode)+str(message.channel.id)
    if findResponse(label)!=None:
        return item("text","{} game with {} active in this channel, send 'ram cancel' on your turn to cancel the game".format(board.title,names))
    print("set the board")
    global responses
    responses.append(response("",None,board,inputFormat,function = game,usePrefix = False,takeArgs = True, parse = False,channel = message.channel.id,user = message.mentions[0].id,passMessage = True,format = inputFormat,label = label))
    global waiters
    waiters.append(removeResponse(board.expiration,message.channel.id,label,item("text",board.title+" game with {} has expired".format(names)),label = label))
    return package(board.initalMessage,board.out())

def game(message,board,inputFormat,move):
    #mention string
    def mention(user):
        return "<@"+str(user)+">"
    # remake label
    labelCode = 0
    for i in board.opponents: 
        labelCode += i
    label = board.title+str(labelCode)+str(message.channel.id)
    # sanatize move and unpack shorthand
    move = move.lower()
    move = board.unpackMove(move,message.author.id)
    print(move)
    if move == False:
        findWaiter(label).reset()
        return item("text","That is not a valid move shorthand.")
    legal = board.isLegal(message.author.id,move)
    if legal != True:
        findWaiter(label).reset()
        if legal == False:
            return item("text","that is not a valid move")
        else:
            return item('text',legal)
    # only valid, legal moves past this point
    # make the move
    moveInfo = board.move(message.author.id,move)
    nextPlayer = board.turnSwitch(moveInfo)
    # check for gameover
    gg = board.gameOver(message.author.id)
    if gg != None:
        losers = ""
        for i in board.opponents:
            if i == gg:
                winner = mention(i)
            else:
                losers +=  (mention(i) + ' ')
        remove(label)
        if gg == "stalemate":
            return package(item("text",losers + "\nIt's a Stalemate"),board.out())
        return package(item("text","{}\nGame over, the winner is {}".format(losers, winner)),board.out())
    # no gameover past this point, the game continues
    findWaiter(label).reset()
    global responses
    r = findResponse(label)
    responses.remove(r)
    responses.append(response("",None,board,inputFormat,function = game,usePrefix = False,takeArgs = True, parse = False,channel = message.channel.id,user = board.opponents[board.playerTurn],passMessage = True,format = inputFormat,label = label))
    outputBoard = board.out()
    if nextPlayer == message.author:
        return outputBoard
    return package(item("text",mention(nextPlayer)+" your move"),outputBoard)

class GameBoard:

    def __init__(self,opponents):
        self.opponents = opponents
        self.playerTurn = 1

    #determines the next player to move
    def turnSwitch(self,info):
        if info == None:
            self.playerTurn = (self.playerTurn + 1) % len(self.opponents)
        elif info == -1:
            pass
        elif info >-1:
            self.playerturn = info
        return self.opponents[self.playerTurn]

    def unpackMove(self,move,player):
        return move
    
    #def __getstate__(self):
    #    global userCache
    #    userCache.append(self.p1)
    #    userCache.append(self.p2)
    #    return (self.p1,self.p2,self.board)
   # 
   # def __setState__(self,data):
    #    p1 = data[0]
    #    p2 = data[1]
    #    self.__init__(p1,p2)
    #    self.board = data[2]

class TicBoard(GameBoard):
    def __init__(self,opponents):
        GameBoard.__init__(self,opponents)
        print("in ticBoard.__init__()")
        self.key = {'a':0,'b':1,'c':2,'1':0,'2':1,'3':2}
        self.p1 = opponents[0]
        self.p2 = opponents[1]
        self.board = []
        for i in range(3): self.board.append(['  ','  ','  '])
        self.title = "Tictactoe"
        self.initalMessage = item("text","Welcome to tictactoe beta\nto move type [row][column] eg: a2")
        self.expiration = DAY
        
    def out(self):
        print("in ticBoard.out()")
        out =  item("text",\
"  1    2    3\n\
a  {} |  {} | {}\n\
------------\n\
b  {} |  {} | {}\n\
------------\n\
c  {} |  {} | {}".format(self.board[0][0],self.board[0][1],self.board[0][2],self.board[1][0],self.board[1][1],self.board[1][2],self.board[2][0],self.board[2][1],self.board[2][2],))
        print("generated output")
        return out

    def isLegal(self,player,move):
        return self.board[self.key[move[0]]][self.key[move[1]]] == '  '

    def move(self,player,move): 
        if player == self.p1:
            self.board[self.key[move[0]]][self.key[move[1]]] = 'O'
        elif player == self.p2:
            self.board[self.key[move[0]]][self.key[move[1]]] = 'X'

    def gameOver(self,player):
        def winner(c):
            if c == 'O':
                return self.p1
            return self.p2
        for i in self.board:
            if '  ' != i[0] and i[0]==i[1] and i[1]==i[2]:
                return winner(i[0])
        for i in range(3): 
            if '  ' != self.board[0][i] and self.board[0][i]==self.board[1][i] and self.board[1][i]==self.board[2][i]:
                return winner(self.board[0][i])
        if '  ' != self.board[0][0] and self.board[0][0]==self.board[1][1] and self.board[1][1]==self.board[2][2]:
            return winner(self.board[0][0])
        if '  ' != self.board[0][2] and self.board[0][2]==self.board[1][1] and self.board[1][1]==self.board[2][0]:
            return winner(self.board[0][2])
        for i in self.board:
            for x in i:
                if x == '  ':
                    return None
        return "stalemate"


class ConnectFourBoard(GameBoard):
    def __init__(self,opponents):
        GameBoard.__init__(self,opponents)
        print("starting connect 4")
        self.title = "Connect Four"
        self.initalMessage = item("text","Welcome to Connect Four beta\n to move, type a number 1 through 7")
        self.p1 = opponents[0]
        self.p2 = opponents[1]
        self.board = []
        for i in range(7):
            self.board.append([])
            for x in range(6):
                self.board[i].append("   ")
        self.expiration = DAY*7

    def out(self):
        b = []
        for i in range(5,-1,-1):
            for x in range(7):
                b.append(self.board[x][i])
        b = tuple(b)
        return item("text","\
.  1    2    3    4   5    6    7\n\
| {} | {} | {} | {} | {} | {} | {} |\n\
| {} | {} | {} | {} | {} | {} | {} |\n\
| {} | {} | {} | {} | {} | {} | {} |\n\
| {} | {} | {} | {} | {} | {} | {} |\n\
| {} | {} | {} | {} | {} | {} | {} |\n\
| {} | {} | {} | {} | {} | {} | {} |\n\
|================|\n\
|                                          |".format(*b))

    def isLegal(self,player,move):
        if self.board[int(move)-1][5] == "   ":
            return True
        return False

    def move(self,player,move):
        for i in range(6):
            if self.board[int(move)-1][i] == "   ":
                if player == self.p1:
                    self.board[int(move)-1][i] = 'O'
                else:
                    self.board[int(move)-1][i] = 'X'
                break

    def gameOver(self,player):
        def winner(c):
            if c == 'O':
                return self.p1
            return self.p2
        b = self.board
        for i in b:
            for x in range(3):
                if "   "!=i[x]==i[x+1]==i[x+2]==i[x+3]:
                    return winner(i[x])
        for i in range(6):
            for x in range(4):
                if "   "!=b[x][i]==b[x+1][i]==b[x+2][i]==b[x+3][i]:
                    return winner(b[x][i])
        for  x in range(4):
            for i in range(3):
                if "   "!=b[x][i]==b[x+1][i+1]==b[x+2][i+2]==b[x+3][i+3]:
                    return winner(b[x][i])
                if "   "!=b[x+3][i]==b[x+2][i+1]==b[x+1][i+2]==b[x][i+3]:
                    return winner(b[x+3][i])
        return None

class ReversiBoard(GameBoard):
    def __init__(self,opponents):
        GameBoard.__init__(self,opponents)
        print("starting Reversi")
        self.title = "Reversi"
        self.initalMessage = item("text","Welcome to Reversi\n to move, type a number 1 through 7")
        self.key = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7,'1':0,'2':1,'3':2,'4':3,'5':4,'6':5,'7':6,'8':7,"\\_\\_":" "," ":"\\_\\_", "__X__ ":'X','X':" __X__ "," __O__ ":'O','O':" __O__ "}
        self.p1 = opponents[0]
        self.p2 = opponents[1]
        self.board = []
        for i in range(8):
            self.board.append([])
            for x in range(8):
                self.board[i].append(" ")
        self.board[3][3] = "X"
        self.board[4][4] = "X"
        self.board[3][4] = "O"
        self.board[4][3] = "O"
        self.board = self.testboard()
        self.expiration = DAY*7

    def out(self):
        b = []
        for y in range(8):
            for x in range(8):
                b.append(self.key[self.board[x][y]])
        b = tuple(b)
        return item("text","\
.  \\_\\__1_\\_\\__2_\\_\\__3_\\_\\__4_\\_\\__5_\\_\\__6_\\_\\__7_\\_\\__8_\\_\n\
A |{}|{}|{}|{}|{}|{}|{}|{}|\n\
B |{}|{}|{}|{}|{}|{}|{}|{}|\n\
C |{}|{}|{}|{}|{}|{}|{}|{}|\n\
D |{}|{}|{}|{}|{}|{}|{}|{}|\n\
E |{}|{}|{}|{}|{}|{}|{}|{}|\n\
F |{}|{}|{}|{}|{}|{}|{}|{}|\n\
G |{}|{}|{}|{}|{}|{}|{}|{}|\n\
H |{}|{}|{}|{}|{}|{}|{}|{}|".format(*b))

    def testboard(self):
        return  [list("OOOOOOO "),
                 list("OOOOOO  "),
                 list("OOOOOX  "),
                 list("OOOOOXXX"),
                 list("OOOXOOXX"),
                 list("OOXXOOOX"),
                 list("OOOOXXOO"),
                 list("XXXXXXO "),]

    def connections(self,player,moveX,moveY):
        def realSpot(x,y):
            return x>=0 and y>=0 and x<8 and y<8
        if player == self.p1:
            color = 'O'
            oppColor = 'X'
        else:
            color = 'X'
            oppColor = 'O'
        vectors = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        connections = []
        for v in vectors:
            dx = v[0]
            dy = v[1]
            x = moveX + dx
            y = moveY + dy
            if not realSpot(x,y) or not self.board[x][y] == oppColor:
                #print("rejected ({},{})".format(x,y))
                continue
            while self.board[x][y] == oppColor:
                #print("({},{})".format(x,y))
                x += dx
                y += dy
                if not realSpot(x,y) or self.board[x][y] == ' s':
                    break
                if self.board[x][y] == color:
                    connections.append((x,y,dx,dy))
        return connections

    def isLegal(self,player,move):
        x = self.key[move[1]]
        y = self.key[move[0]]
        return self.board[x][y] == ' ' and len(self.connections(player,x,y)) > 0
    
    def move(self,player,move):
        if player == self.p1:
            color = 'O'
            oppColor = 'X'
        else:
            color = 'X'
            oppColor = 'O'
        moveX = self.key[move[1]]
        moveY = self.key[move[0]]

        if player == self.p1:   
            self.board[moveX][moveY] = 'O'
        elif player == self.p2:
            self.board[moveX][moveY] = 'X'
        for cx,cy,dx,dy in self.connections(player,moveX,moveY):
            x = moveX
            y = moveY
            while x != cx or y != cy:
                x+=dx
                y+=dy
                self.board[x][y] = color

        #check for swtiching turn
        if player == self.p1:
            opponent = self.p2
        else:
            opponent = self.p1
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == ' ' and len(self.connections(opponent,x,y))>0:
                    return None
        return -1
    
        
    def gameOver(self,player):
        player = self.opponents[self.playerTurn]
        if player == self.p1:
            color = 'O'
            oppColor = 'X'
        else:
            color = 'X'
            oppColor = 'O'
        whiteScore = 0
        blackScore = 0
        for x in range(8):
            for y in range(8):
                if self.board[x][y] == 'X':
                    whiteScore += 1
                elif self.board[x][y] == 'O':
                    blackScore += 1
                elif len(self.connections(player,x,y))>0:
                    return None
        #past here the game is over
        if whiteScore>blackScore:
            return self.p2
        elif blackScore>whiteScore:
            return self.p1
        return "stalemate"
        

CHESS_HELP = "To move, type the letter for your piece and the destination square. Ex: qd6\n\
If multiple pieces of the same type can reach a square, specify by the rank or file that they do not have in common Ex: nfc3\n\
If you do not specify a piece, I will assume you mean a pawn Ex: e4 is the same as pe4\n\
To castle, move your king to its destination square Ex: kg1\n\
You can also express any move explicitly using input and output square Ex: b5 c6 or b5c6\n\
Pieces:\n\
p = pawn\n\
n = knight\n\
b = bishop\n\
r = rook\n\
q = queen\n\
k = king\n\
Games expire after one week.\n\
Have fun losing Barasu."
class ChessBoard(GameBoard):
    def __init__(self,opponents):
        GameBoard.__init__(self,opponents)
        self.fileRef = {0:'a',1:'b',2:'c',3:'d',4:'e',5:'f',6:'g',7:'h','a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
        self.pieceRef = {'wr':'white rook','wn':'white knight','wb':'white bishop','wq':'white queen','wk':'white king','wp':'white pawn',
                         'br':'black rook','bn':'black knight','bb':'black bishop','bq':'black queen','bk':'black king','bp':'black pawn'}
        print("starting chess")
        self.title = "Chess"
        self.initalMessage = item("text",'Welcome to Chess beta\n type "ram chess help" for detailed controls')
        self.p1 = opponents[0]
        self.p2 = opponents[1]
        self.board = []
        for i in range(8):
            self.board.append([])
            for x in range(8):
                self.board[i].append(None)
        self.board[0][0] = 'wr'
        self.board[7][0] = 'wr'
        self.board[1][0] = 'wn'
        self.board[6][0] = 'wn'
        self.board[2][0] = 'wb'
        self.board[5][0] = 'wb'
        self.board[3][0] = 'wq'
        self.board[4][0] = "wk"
        for i in range(8): self.board[i][1] = 'wp'
        self.board[0][7] = 'br'
        self.board[7][7] = 'br'
        self.board[1][7] = 'bn'
        self.board[6][7] = 'bn'
        self.board[2][7] = 'bb'
        self.board[5][7] = 'bb'
        self.board[3][7] = 'bq'
        self.board[4][7] = 'bk'
        for i in range(8): self.board[i][6] = 'bp'
        self.expiration = DAY*7
        self.castleWK = True
        self.castleWQ = True
        self.castleBK = True
        self.castleBQ = True
        self.enPassent = None
        self.flip = False

    def out(self):
        boardImage = cv2.imread('./chess/board.jpg')
        for rank in range(8):
            for file in range(8):
                if self.board[file][rank] == None:
                    continue
                space = cv2.imread('./chess/{}{}.jpg'.format(self.fileRef[file],rank+1))
                pieceFileName = self.pieceRef[self.board[file][rank]]
                if self.flip:
                    pieceFileName += " R"
                piece = cv2.imread('./chess/{}.jpg'.format(pieceFileName))
                reverse = cv2.bitwise_not(space)
                boardImage = cv2.bitwise_and(boardImage,reverse)
                tile = cv2.bitwise_and(piece,space)
                boardImage = cv2.bitwise_or(boardImage,tile)
        if self.flip:
            boardImage = cv2.rotate(boardImage,cv2.ROTATE_180)
        fileName = "./gameboards/chessboard{}.png".format(self.p1+self.p2)
        cv2.imwrite(fileName,boardImage)
        return item("file",fileName)

    def unpackMove(self,move,player):
        if player == self.p1:
            color = 'b'
        else:
            color = 'w'
        if len(move) == 5:
            return move
        pieces = ['p','k','n','q','r','b']
        ranks = ['1','2','3','4','5','6','7','8']
        files = ['a','b','c','d','e','f','g','h']
        if len(move) == 4:
             #checking for en passent
            if self.enPassent != None and move[0] == 'p':
                outx = self.fileRef[move[2]]
                outy = int(move[3])-1
                if self.board[outx][outy] == None and outx == self.enPassent and ((color == 'w' and outy == 5) or (color == 'b' and outy == 2)):
                    if color == 'w':
                        inRank = '5'
                    else:
                        inRank = '4'
                    return move[1] + inRank + ' ' + move[2:]
            #unpack normal move
            if move[0] in files and move[1] in ranks and move[2] in files and move[3] in ranks:
                return move[:2]+ ' ' + move[2:]
            elif move[0] in pieces and move[1] in ranks+files and move[2] in files and move[3] in ranks:
                outx = self.fileRef[move[2]]
                outy = int(move[3])-1
                i = 0
                xref = []
                yref = []
                if move[1] in files:
                    for i in range(8): xref.append(int(self.fileRef[move[1]]))
                    yref = range(8)
                else:
                    for i in range(8): yref.append(int(move[1])-1)
                    xref = range(8)
                foundMove = False
                for i in range(8):
                    x = xref[i]
                    y = yref[i]
                    if self.board[x][y] != None and self.board[x][y][0] == color and self.board[x][y][1] == move[0]:
                        if [outx,outy] in self.canSee(x,y):
                            if foundMove:
                                return False
                            else:
                                foundMove = True
                                outMove = self.fileRef[x]+chr(y+1+48)+' '+move[2:]
                if foundMove:
                    return outMove
        if len(move) == 3:
            #checking for castling
            if (move == "kg1" and self.castleWK and color == 'w'):
                return "e1 g1"
            if (move == "kc1" and self.castleWQ and color == 'w'):
                return "e1 c1"
            if (move == "kg8" and self.castleBK and color == 'b'):
                return "e8 g8"
            if (move == "kc8" and self.castleBQ and color == 'b'):
                return "e8 c8"
            #checking for en passent
            if self.enPassent != None and move[0] == 'p':
                outx = self.fileRef[move[1]]
                outy = int(move[2])-1
                if self.board[outx][outy] == None and outx == self.enPassent and ((color == 'w' and outy == 5) or (color == 'b' and outy == 2)):
                    if color == 'w':
                        inRank = '5'
                        iny = 4
                    else:
                        inRank = '4'
                        iny = 3
                    found = 0
                    if (not outx == 0) and self.board[outx-1][iny] == color + 'p':
                        found += 1
                        inx = outx-1
                    if(not outx == 7) and self.board[outx+1][inx] == color + 'p':
                        found += 1
                        inx = outx+1
                    if found == 1: 
                        return self.fileRef[inx] + inRank + ' ' + move[1:]
                    return False
            #unpack standard move
            if move[0] in pieces and move[1] in files and move[2] in ranks:
                foundMove = False
                outMove = ''
                outx = self.fileRef[move[1]]
                outy = int(move[2])-1
                for x in range(8):
                    for y in range(8):
                        if self.board[x][y] != None and self.board[x][y][0] == color and self.board[x][y][1] == move[0]:
                            if [outx,outy] in self.canSee(x,y):
                                if foundMove:
                                    return False
                                else:
                                    foundMove = True
                                    outMove = self.fileRef[x]+chr(y+1+48)+' '+move[1:]
                if foundMove:
                    return outMove
        if len(move) == 2:
            return self.unpackMove('p'+move,player)

        return False


    def canSee(self,inx,iny,board = -1):
        if board == -1: board = self.board
        piece = board[inx][iny]
        if piece == None:
            return []
        def realSpot(x,y):
            if x<0 or x>7 or y<0 or y>7:
                return False
            return True
        def check(x,y): #output in form [add space to output, check next]
            if x==inx and y==iny:
                return False,True
            if not realSpot(x,y):
                return False,False
            if board[x][y] == None:
                return True,True
            if board[x][y][0] == piece[0]:
                return False,False
            return True,False # encounters piece of different color

        output = []
        if piece[1] == 'p':
            if piece[0] == 'w':
                delta = 1
            else:
                delta = -1
            if realSpot(inx,iny+delta) and board[inx][iny+delta] == None:
                output.append([inx,iny+delta])
                if (iny-delta == 0 or iny-delta == 7) and board[inx][iny+(delta*2)] == None:
                    output.append([inx,iny+(2*delta)])                    
            if realSpot(inx+1,iny+delta) and board[inx+1][iny+delta] != None and board[inx+1][iny+delta][0] != piece[0]:
                output.append([inx+1,iny+delta])
            if realSpot(inx-1,iny+delta) and board[inx-1][iny+delta] != None and board[inx-1][iny+delta][0] != piece[0]:
                output.append([inx-1,iny+delta])
        if piece[1] == 'r' or piece[1] == 'q':
            for outx in range(inx,8):
                r = check(outx,iny)
                if r[0]: output.append([outx,iny])
                if not r[1]: break
            for outx in range(inx,-1,-1):
                r = check(outx,iny)
                if r[0]: output.append([outx,iny])
                if not r[1]: break
            for outy in range(iny,8):
                r = check(inx,outy)
                if r[0]: output.append([inx,outy])
                if not r[1]: break
            for outy in range(iny,-1,-1):
                r = check(inx,outy)
                if r[0]: output.append([inx,outy])
                if not r[1]: break
        if piece[1] == 'b' or piece[1] == 'q':
            for i in range(8):
                r = check(inx+i,iny+i)
                if r[0]: output.append([inx+i,iny+i])
                if not r[1]: break
            for i in range(8):
                r = check(inx-i,iny+i)
                if r[0]: output.append([inx-i,iny+i])
                if not r[1]: break
            for i in range(8):
                r = check(inx+i,iny-i)
                if r[0]: output.append([inx+i,iny-i])
                if not r[1]: break
            for i in range(8):
                r = check(inx-i,iny-i)
                if r[0]: output.append([inx-i,iny-i])
                if not r[1]: break
        if piece[1] == 'n' or piece[1] == 'k':
            if piece[1] == 'n':
                targets = [[inx+2,iny+1],[inx+2,iny-1],[inx+1,iny+2],[inx+1,iny-2],[inx-1,iny+2],[inx-1,iny-2],[inx-2,iny+1],[inx-2,iny-1]]
            else:
                targets = []
                for i in range(-1,2):
                    for x in range(-1,2):
                        targets.append([inx+i,iny+x])
            for i in targets:
                x = i[0]
                y = i[1]
                if realSpot(x,y) and (board[x][y] == None or board[x][y][0] != piece[0]):
                    output.append([x,y])
        return output

    def isLegal(self,player,move,decodeMove = True):
        if player == self.p2:
            color = 'w'
        else:
            color = 'b'
        if decodeMove:
            inx = self.fileRef[move[0]]
            iny = int(move[1])-1
            outx = self.fileRef[move[3]]
            outy = int(move[4])-1
        else:
            inx = move[0][0]
            iny = move[0][1]
            outx = move[1][0]
            outy = move[1][1]
        piece = self.board[inx][iny]
        if piece == None or piece[0] != color:
            return False
        exception = False
        if piece[1] == 'k' and inx == 4 and (outx == 6 or outx == 2): exception = True #castling exception
        if piece[1] == 'p' and inx != outx and self.board[outx][outy] == None:  exception = True #en passent exception
        if not (([outx,outy] in self.canSee(inx,iny)) or exception):
            return False
        #copy board
        newBoard = []
        for x in range(8):
            newBoard.append([])
            for y in range(8):
                newBoard[x].append(self.board[x][y])
        #en passent
        if piece[1] == 'p' and inx != outx and self.board[outx][outy] == None:
            if self.enPassent == outx:
                newBoard[outx][iny] = None
            else:
                return False
        #castling
        if piece[1] == 'k' and inx == 4 and outx == 6: #king's side
            if (color == 'w' and self.castleWK) or (color == 'b' and self.castleBK):
                if not (self.board[5][iny] == None and self.board[6][iny] == None):
                    return False
                newBoard[4][iny] = piece
                newBoard[5][iny] = piece
                newBoard[6][iny] = piece
                newBoard[7][iny] = None
            else:
                return False
        elif piece[1] == 'k' and inx == 4 and outx == 2: #queen's side
            if (color == 'w' and self.castleWQ) or (color == 'b' and self.castleBQ):
                if not (self.board[1][iny] == None and self.board[2][iny] == None and self.board[3][iny] == None):
                    return False
                newBoard[4][iny] = piece
                newBoard[3][iny] = piece
                newBoard[2][iny] = piece
                newBoard[0][iny] = None
            else:
                return False
        else:
            newBoard[outx][outy] = newBoard[inx][iny]
            newBoard[inx][iny] = None
        # check if the king can be attacked in projected board
        for x in range(8):
            for y in range(8):
                if newBoard[x][y] != None and newBoard[x][y][0] != color:
                    for i in self.canSee(x,y,newBoard):
                        if newBoard[i[0]][i[1]] == color+'k':
                            return "That leaves you in check"
        return True
    
    def move(self,player,move):
        inx = self.fileRef[move[0]]
        iny = int(move[1])-1
        outx = self.fileRef[move[3]]
        outy = int(move[4])-1
        color = self.board[inx][iny][0]
        # whipe en passent
        self.enPassent = None
        # check for disallow castle
        if iny == 0 and (inx == 0 or inx == 4):
            self.castleWQ = False
        if iny == 0 and (inx == 7 or inx == 4):
            self.castleWK = False
        if iny == 7 and (inx == 0 or inx == 4):
            self.castleBQ = False
        if iny == 7 and (inx == 7 or inx == 4):
            self.castleBK = False
        if self.board[inx][iny][1] == 'p': #if pawn
            if outy == 0 or outy == 7: #promotion
                self.board[inx][iny] = color + 'q'
            elif  inx != outx and self.board[outx][outy] == None: #en passent
                self.board[outx][iny] = None
            elif (outy-iny)**2 > 2: #on double move sent possible en passant
                self.enPassent = outx
        # castleing
        if self.board[inx][iny][1] == 'k':
            if inx == 4 and outx == 6: #king's side
                self.board[5][iny] = self.board[7][iny]
                self.board[7][iny] = None
            if inx == 4 and outx == 2: #queen's side
                self.board[3][iny] = self.board[0][iny]
                self.board[0][iny] = None
        self.board[outx][outy] = self.board[inx][iny]
        self.board[inx][iny] = None

    def gameOver(self,player):
        if player == self.p1:
            opponent = self.p2
            opponentColor = 'w'
        else:
            opponent = self.p1
            opponentColor = 'b'
        for x in range(8):
            for y in range(8):
                if self.board[x][y] != None and self.board[x][y][0] == opponentColor:
                    for i in self.canSee(x,y):
                        if self.isLegal(opponent,[[x,y],[i[0],i[1]]],False) == True:
                            self.flip = not self.flip
                            return None
        #there are no legal move past this point and the game is over
        for x in range(8):
            for y in range(8):
                if self.board[x][y] != None and self.board[x][y][0] != opponentColor:
                    for i in self.canSee(x,y,self.board):
                        if self.board[i[0]][i[1]] == opponentColor+'k':
                            return player
        #past here the opponent is not in check
        return "Stalemate"
        

def webwork(message,problem):
    print("in")
    problem = list(problem)
    banned = ['1','2','3','4','5','6','7','8','9','0','\n','.','/','\\',' ','{','}','∘','*','+','-']
    i=0
    while i<len(problem):
        if problem[i] in banned:
            problem.pop(i)
        else: i+=1
    for i in range(len(problem)):
        try:
            if problem[i] == '(':
                depth = 1
                while depth > 0:
                    problem.pop(i)
                    if problem[i] == '(':
                        depth+=1
                    elif problem[i] == ')':
                        depth-=1
                problem.pop(i)
        except: break
    problem = "".join(problem)
    print("here at 1")
    contents = []
    index = []
    for subdirs,dirs,files in os.walk("./webwork/webwork-open-problem-library/Contrib/LaTech"):
        for f in files:
            if f.endswith(".pg"):
                path = os.path.join(subdirs,f)
                with open(path,'r') as c:
                    string = c.read()
                start = 0
                end = 0
                for i in range(10,len(string)):
                    if string[i-10:i] == "BEGIN_TEXT":
                        start = i
                    elif string[i:i+8] == "END_TEXT":
                        end = i
                        break
                string = string[start:end]
                string = list(string)
                for i in range(len(string)):
                    try:
                        if string[i] == '$':
                            while (string[i] != ' ') and (string[i] != '\n'):
                                string.pop(i)
                        if string[i] == '(':
                            depth = 1
                            while depth > 0:
                                string.pop(i)
                                if string[i] == '(':
                                    depth+=1
                                elif string[i] == ')':
                                    depth-=1
                            string.pop(i)
                        if string[i] == '{':
                            while string[i] != '}':
                                string.pop(i)
                            string.pop(i)
                    except: break
                i=0
                while i<len(string):
                    if string[i] in banned:
                        string.pop(i)
                    else: i+=1
                string = "".join(string)
                contents.append(string)
                index.append(path)
    if contents == []:
        print("github files missing")
        return item("text","github files missing")
    best = 0
    bestScore = 0
    bestString = ""
    print(contents)
    for i in range(len(contents)):
        matcher = SequenceMatcher(None,problem,contents[i])
        match = matcher.find_longest_match(0,len(problem),0,len(contents[i]))
        longestSubstring = problem[match.a:match.a+match.size]
        score = match.size
        print("{}:  {}  {}".format(index[i],longestSubstring,score))
#        score = fuzz.ratio(problem,contents[i])
        if score > bestScore:
            best = index[i]
            bestScore = score
            bestString = contents[i]
            bestSubstring = longestSubstring
    print("problem:\n"+problem)
    print("best:\n{}   {}".format(best,score))
    print("here")
    with open(best,'r') as f:
        lines = parse(f.read(),'\n')
    problem = ""
    equations = []
    answers = []
    for i in range(len(lines)):
        if lines[i] == "BEGIN_TEXT":
            while lines[i] != "END_TEXT":
                problem+='\n'+lines[i]
                i+=1
        elif len(lines[i])>0 and lines[i][0] == '$':
            for x in range(len(lines[i])-1):
                if lines[i][x] == ' ':
                    if lines[i][x+1] == '=':
                        new = ""
                        for a in lines[i]:
                            if a!='$': new+=a
                        equations.append(new)
                    break
        elif len(lines[i])>4 and lines[i][:3] == "ANS":
            answers.append(lines[i])
    print("there")
    out = problem+'\n\n'
    for i in range(len(equations)):
        equations[i] = list(equations[i])
        x = 0
        while x < len(equations[i]):
            if equations[i][x] == '$':
                equations[i].pop(x)
            else: x+=1
        equations[i] = "".join(equations[i])
        equations[i] = equations[i][:-1]
        out+= equations[i]+'\n'
    for i in answers: out+= i+'\n'
#    out = item("text",process.extractOne(problem,contents)[0])
    print("problem:\n{}\n\nbest:\n{}\nmatch: {}".format(problem,bestString,bestSubstring))
    ans = webworkSolve(message,equations,answers)
    return package(item("text",best + '\n\n' + out + '\n\n'),ans)


def webworkSolve(message,equations,answers,new=None):
    def given(text):
        for x in range(len(text)-7):
            if text[x:x+7] == "random(" or text[x:x+8] == "random (":
                return True
        for x in range(len(text)-11):
            if text[x:x+11] == "interpVals(":
                return True
        return False
    if new != None:
        new = parse(new,'\n')
        for i in equations:
            new.append(i)
        equations = new
    try: 
        out = ""
        v = ""
        def sqrt(x):
            return x**(1/2)
        variableDict = {'v':v,'sqrt':sqrt,'ln':math.log}
        index = 0
        variables = []        
        for i in equations:
            if not given(i):
                v = ""
                variables.append(0)
                for x in i:
                    if x == ' ':
                        break
                    v+=x
                variableDict[v] = variables[index]
                print("executing: "+i)
                exec(i,variableDict)
                index+=1
                print(v+" = "+str(variableDict[v]))
        print("through exec")
        for i in answers:
            for x in range(len(i)):
                if i[x] == '$':
                    x+=1
                    var = ""
                    while i[x] != ')':
                        var+=i[x]
                        x+=1
                    out += str(variableDict[var])+ '\n'
                    break
        remove("webwork"+str(message.channel.id)+str(message.author.id))
        return item("text","answer(s):\n"+out)

    except Exception as e:
        print("except")
        label = "webwork"+str(message.channel.id)+str(message.author.id)
        global responses
        r = findResponse(label)
        if r != None:
            responses.remove(r)
        responses.append(response(None,None,equations,answers,function = webworkSolve,takeArgs = True,parse = False,user = message.author.id,channel = message.channel.id,usePrefix = False,passMessage = True,label = label,format = F.equations))
        global waiters
        w = findWaiter(label)
        if w == None:
            waiters.append(removeResponse(3600,message.channel.id,label,item("text","webwork problem expired"),label = label))
        else:
            w.reset()
        out = str(e)+"\nfind:\n"
        for i in equations:
            if given(i):
                out+=i+'\n'
        return item("text",out)


def parse(string=None,key=' '):
    out = []
    index = 0
    out.append("")
    foundOne = False
    for i in string:
        if i==key:
            foundOne = True
            index+=1
            out.append("")
        else:
            out[index]+=i
    if not foundOne:
        return [string]
    return out

def echo(*args):
    out = package()
    for i in args:
        out.append(item("text",i))
    return out


def writeCache():
    print("Writing to cache...")
    with open(CACHE, 'wb') as outFile:
        pickle.dump((responses,waiters),outFile)

async def loadCache():
    global responses
    global waiters
    with open(CACHE, 'rb') as inFile:
        cache = pickle.load(inFile)
    responses = cache[0]
    waiters = cache[1]


def remove(label):
    r = findResponse(label)
    if r != None:
        responses.remove(r)
    global waiters
    w = findWaiter(label)
    if w != None:
        waiters.remove(w)

def cancel(message):
    user = message.author.id
    actions = 0
    global responses
    global waiters
    for i in responses:
        if i.label != "normal" and i.user == user:
            w = findWaiter(i.label)
            if w != None:
                waiters.remove(w)
            responses.remove(i)
            actions+=1
    return item("text","{} actions canceled".format(actions))

def scramble():
    pass

def runAtSendTest():
    return item("text","test run")

def findResponse(label):
    for i in responses:
        if i.label == label:
            return i
    return None

def findWaiter(label):
    for i in waiters:
        if i.label == label:
            return i
    return None

def interpolate(*args):
    try:
        out = item("text",interp(*args))
    except Exception as e:

        out = item("text",str(e)+"\nenter A-low A-Hi A-target B-low B-hi")
    return out

def bakaMemes():
    global waiters
    waiters[0].endtime = waiters[0].endtime + datetime.timedelta(days = -1)


F = Format()

def reset(**kwargs):
    doResponses = True
    doWaiters = True
    for name,value in kwargs.items():
        if name == "responses":
            doResponses = value
        elif name == "waiters":
            doWaiters = value
    global responses
    global waiters
    if doResponses:
        print("doing responses")
        responses = [
            response(["cancel","stop"],passMessage = True,function = cancel),
            response(["hello ram","hi ram","ram hello","ram hi"],["Hello Barasu", "Hello", "hey"],usePrefix = False),
            response("Ping", "Pong"),
            response("Marco", "Polo",usePrefix = False),
            response(["b.rem","rem"],"Who's Rem?",usePrefix = False),
            response("flip a coin",["Heads","Tails"]),
            response(["snap?","snap"],["Death","Mercy"]),
            response("send yourself",item("file","./ram.py")),
            response("send bootstrapper",item("file","./bootstrapper.py")),
            response("send starter",item("file","./starter.py")),
            response("send backup",item("file","./rambackup.py")),
            response("send test meme",runAtSend(redditRetrieve,2,"goodanimemes","top")),
            response("help","Look I don't really know what's going on either"),
            response("send lock","nice try barasu"),
            response("runatsend test",runAtSend(runAtSendTest)),
            response("hushhush",";)",locked = True),
            response(None,["Fuck you Kyle",None,None],user = KYLE,usePrefix = False),
            response("berserk",package(
                runAtSend(redditRetrieve,4,"nukedmemes"),
                runAtSend(redditRetrieve,4,"cursedimages"),
                runAtSend(redditRetrieve,4,"goodanimemes")
            ),locked = True),
            response("echo",None,takeArgs = True,function = echo,parse = False),
            response("parse",None,takeArgs = True,function = echo),
            response("meme",None,1,function = redditRetrieve,takeArgs = True),
            response("Function test",None,"hello World",function = echo),
        #    response("30 seconds?","not yet",label = "30seconds"),
            response("webwork",function = webwork,takeArgs = True,parse = False,passMessage = True),
            response(["tictactoe","tic tac toe"],"here",TicBoard,F.ticTacToe,function = gameInit,passMessage = True),
            response(["connect four","fonnect cour","connectfour"],"here",ConnectFourBoard,F.connectFour,function = gameInit,passMessage = True), 
            response(["othello","reversi"],"here",ReversiBoard,F.reversi,function = gameInit,passMessage = True),
            response("chess","here",ChessBoard,F.chess,function = gameInit,passMessage = True),
            response("chess help",CHESS_HELP),
            response(["interpolate","interp"],None,function = interpolate,takeArgs = True),
            response("bakamemes","OK",function = bakaMemes,locked = True)
        ]

    if doWaiters:
        waiters = [
            dailyPoster(datetime.time(hour = 23),BARASU,package(
                runAtSend(redditRetrieve,5,"goodanimemes","top"),runAtSend(redditRetrieve,5,"animemes","top"))),
            randDailyPoster(SCREAM_CHAMBER_BOT_SPAM,item("text","owo daily")),
            waiter(DAY + 10,SCREAM_CHAMBER_BOT_SPAM,item("text","m.e")),
        #    waiter(15,AVERAGE_PHOTOGRAPHER_SPAM,runAtSend(redditRetrieve,2,"dankmemes","new"),4)
            waiter(10,AVERAGE_PHOTOGRAPHER_SPAM,item("text","Heartbeat"),10),
        #    removeResponse(30,AVERAGE_PHOTOGRAPHER_SPAM,"30seconds","30 seconds have passed")
        #    cacheWaiter(1)
            ]
        if waiters[0].endtime+datetime.timedelta(days = -1)>datetime.datetime.now():
            waiters[0].endtime = waiters[0].endtime + datetime.timedelta(days = -1)






@client.event
async def on_ready():
    print('Logged in as {}   {}'.format(client.user,str(datetime.datetime.now())))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == ".update "+lock():
        print("updating")
        await message.channel.send("saving file (live)")
        await message.attachments[0].save("ram.py")
    if message.content == ".reset":
        await message.channel.send("Setting default responses and waiters...")
        reset()
    if message.content == ".resetresponses":
        await message.channel.send("Setting default responses only...")
        reset(waiters = False)
    if message.content == ".cache":
        await message.channel.send("Saving to cache...")
        writeCache()
    if message.content == ".load":
        await message.channel.send("Loading from cache...")
        await loadCache()
    if message.content == ".addthing":
        await message.channel.send("adding thing")
        global responses
        responses.append(response("thing","ok",1,label = "thing"))
    try:
        if message.content == ".exit "+lock():
            await message.channel.send("bye...")
            await client.logout()
        for i in responses:
            if i.messageIn(message):
                output = i.output()
                if output != None:
                    await output.send(message.channel)
    except Exception as e:
        print("error in on_message:")
        print(e)
        await message.channel.send("error in on_message: {}".format(e))





async def iterator():
    global waiters
    now = datetime.datetime.now()
    while True:
        await asyncio.sleep(1)
        try:
            #print("looping")
            for i in waiters:
                if i.ready():
                    #print("go")
                    await i.go()
                    if not i.keep():
                        waiters.remove(i)
        except Exception as e:
            print("iterator error: {}".format(e))

async def cacheLoop():
    while True:
        try:
            await asyncio.sleep(AUTO_CACHE_DELAY)
            writeCache()
        except Exception as e:
            print("Autosave Exception: {}".format(e))

try:
    asyncio.ensure_future(loadCache())
except Exception as e:
    reset()
    print("Pickle Load Exception: {}".format(e))
mainLoop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(iterator())
    asyncio.ensure_future(cacheLoop())
    print("here")
    with open('key.txt','r') as key:
#        print(key.read())
        client.run(key.read())
except Exception as e:
    print("mainLoop error:")
    print(e)
finally:
    print("closing loop")
    writeCache()
    mainLoop.close()

