class item():
    def __init__(self,type=None,content=None):
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
                outArgs.append(userPlaceholder(a.id))
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
        args = []
        for i in range(len(data[2])):
            try:
                args.append(data[2][i].user())
                if args[i] == None:
                    asyncio.ensure_future(self.fetchUser(data[2][i].id,i))
            except:
                args.append(data[2][i])
        self.args = tuple(args)
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