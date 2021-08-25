from botbasics import *

def gameInit(message,board,inputFormat):
    if len(message.mentions)!=1:
        return item("text","@ one person to play with")
    board = board(message.author.id,message.mentions[0].id)
    label = board.title+str(message.author.id+message.mentions[0].id)+str(message.channel.id)
    if findResponse(label)!=None:
        return item("text","{} game with {} active, send 'ram cancel' on your turn to cancel the game".format(board.title,message.mentions[0].display_name))
    print("set the board")
    global responses
    responses.append(response("",None,message.author,board,inputFormat,function = game,usePrefix = False,takeArgs = True, parse = False,channel = message.channel.id,user = message.mentions[0].id,passMessage = True,format = inputFormat,label = label))
    global waiters
    waiters.append(removeResponse(board.expiration,message.channel.id,label,item("text",board.title+" game between {} and {} has expired".format(message.author.display_name,message.mentions[0].display_name)),label = label))
    return package(board.initalMessage,board.out())

def game(message,opponent,board,inputFormat,move):
    # sanatize move and unpack shorthand
    move = move.lower()
    move = board.unpackMove(move,message.author.id)
    if move == False:
        return item("text","That is not a valid move shorthand.")
    label = board.title+str(message.author.id+opponent.id)+str(message.channel.id)
    legal = board.isLegal(message.author.id,move)
    if legal == True:
        board.move(message.author.id,move)
        gg = board.gameOver(message.author.id)
        if gg != None:
            remove(label)
            if gg == "stalemate":
                return package(item("text",opponent.mention+" It's a Stalemate"),board.out())
            elif gg == message.author.id:
                winner = message.author.mention
            else:
                winner = opponent.mention
            return package(item("text","Game over, the winner is "+winner),board.out())
        findWaiter(label).reset()
        global responses
        r = findResponse(label)
        responses.remove(r)
        responses.append(response("",None,message.author,board,inputFormat,function = game,usePrefix = False,takeArgs = True, parse = False,channel = message.channel.id,user = opponent.id,passMessage = True,format = inputFormat,label = label))
        outputBoard = board.out()
        return package(item("text",opponent.mention+" your move"),outputBoard)
    else: 
        findWaiter(label).reset()
        if legal == False:
            return item("text","that is not a valid move")
        else:
            return item('text',legal)

class gameBoard:
    def unpackMove(self,move):
        return move,True
    pass
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

class ticBoard(gameBoard):
    def __init__(self,player1,player2):
        print("in ticBoard.__init__()")
        self.key = {'a':0,'b':1,'c':2,'1':0,'2':1,'3':2}
        self.p1 = player1
        self.p2 = player2
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


class connectFourBoard(gameBoard):
    def __init__(self,player1,player2):
        print("starting connect 4")
        self.title = "Connect Four"
        self.initalMessage = item("text","Welcome to Connect Four beta\n to move, type a number 1 through 7")
        self.p1 = player1
        self.p2 = player2
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

CHESS_HELP = "To move, type the letter for your piece and the destination square. Ex: qd6\n\
If multiple pieces of the same type can reach a square, specify by the rank or file that they do not have in common Ex: nfc3\n\
If you do not specify a piece, I will assume you mean a pawn Ex: e4 is the same as pe4\n\
To castle, move your king to the castled square Ex: kg1\n\
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
class chessBoard(gameBoard):
    def __init__(self,player1,player2):
        self.fileRef = {0:'a',1:'b',2:'c',3:'d',4:'e',5:'f',6:'g',7:'h','a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
        self.pieceRef = {'wr':'white rook','wn':'white knight','wb':'white bishop','wq':'white queen','wk':'white king','wp':'white pawn',
                         'br':'black rook','bn':'black knight','bb':'black bishop','bq':'black queen','bk':'black king','bp':'black pawn'}
        print("starting chess")
        self.title = "Chess"
        self.initalMessage = item("text",'Welcome to Chess beta\n type "ram chess help" for detailed controls')
        self.p1 = player1
        self.p2 = player2
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
