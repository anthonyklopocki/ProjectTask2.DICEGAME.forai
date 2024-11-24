from tkinter import *
from tkinter import ttk
from random import randint

class User:
    def __init__(self, username, password, score):
        self.__username = username
        self.__password = password
        self._score = int(score)

    def getUsername(self):
        return self.__username

    def checkPassword(self, password):
        if password == self.__password:
            return True
        else:
            return False


class Game:
    def __init__(self, window, debugLogin=False, debugTie=False):
        self.__player1 = None
        self.__player2 = None
        self.__window = window
        self.__loggedinusers = []
        self.__debugLogin = debugLogin
        self.__debugTie = debugTie

    def login(self, playernumber):
        if self.__debugLogin:
            return self.fake_login(playernumber)
        else:
            return self.real_login(playernumber)

    def fake_login(self, playernumber):
        print(f"Emulating {playernumber} login attempt")
        predefined_users = {
            "admin": "admin",
            "admin2": "admin"
        }
        if playernumber == "Player 1":
            username = "admin"
            password = predefined_users["admin"]
        elif playernumber == "Player 2":
            username = "admin2"
            password = predefined_users["admin2"]
        else:
            return None

        userinstancelist = self.__window.getUserInstance()
        for user in userinstancelist:
            if user.getUsername() == username and user.checkPassword(password):
                print(f"{username} logged in successfully")
                return user, username

        print(f"{username} login failed.")
        return None

    def real_login(self, playernumber):
        while True:
            details = self.__window.makeLoginWindow(playernumber)
            if details:
                username, password = details

                if username in self.__loggedinusers:
                    print(f"{username} is already logged in.")
                    self.__window.errorWindow(f"{username} is already logged in.")
                    continue
                userinstancelist = self.__window.getUserInstance()
                for user in userinstancelist:
                    if user.getUsername() == username and user.checkPassword(password):
                        self.__loggedinusers.append(username)
                        return user, username
            else:
                print(f"{playernumber} login quit.")
            return None

    def openLB(self):
        Files = FileManager()
        LBlist = Files.get_leaderboard()
        while len(LBlist) < 5:
            LBlist.append(["N/A", "N/A"])
        pl1, s1 = LBlist[0]
        pl2, s2 = LBlist[1]
        pl3, s3 = LBlist[2]
        pl4, s4 = LBlist[3]
        pl5, s5 = LBlist[4]
        self.__window.makeLBWindow(pl1, pl2, pl3, pl4, pl5, s1, s2, s3, s4, s5)

    def createAcc(self):
        userlist = FileManager.get_usrlist()
        if len(userlist) % 3 == 0:
            userlist = [
                userlist[i:i + 3]
                for i in range(0, len(userlist), 3)
            ]
        while True:
            details = self.__window.makeCreateWindow()
            if details:
                username, password = details

                if any(user[0] == username for user in userlist):
                    print(f"{username} already exists.")
                    self.__window.errorWindow(f"{username} already exists.")
                    continue
                # else
                Files = FileManager()
                Files.Create_Account(username, password)
            else:
                print(f"Account creation quit.")
            return None

    def menu(self):
        status = 0
        menuloop = True
        while menuloop:
            status = self.__window.menuWindow(status)
            #0 leave
            #1 login
            #2 create acc
            #3 view leaderboard
            if status == 1:
                self.startGame()
            elif status == 2:
                self.createAcc()
            elif status == 3:
                self.openLB()
            elif status == 0:
                menuloop = False
            else:
                pass
            #quit

        pass
    def startGame(self):
        gamerunning = True
        player1score = 0
        player2score = 0

        self.__player1, username1 = self.login("Player 1")
        if not self.__player1:
            print("Player 1 failed to log in. Game cannot start.")
            return
        else:
            self.__player2, username2 = self.login("Player 2")
            if not self.__player2:
                print("Player 2 failed to log in. Game cannot start.")
                return

        #gameloop

        print("Both players logged in, Game started")
        usrturn = 1
        rounds = 0
        winner = None
        winscore = 0

        def finalround(username1, username2, player1score, player2score):
            equalscore = True
            gamerunning = True
            while equalscore and gamerunning:
                print("Scores are tied! Starting extra round.")

                playernumber = "Player 1"
                gamerunning, round_score = self.__window.makeFinalGameWindow(playernumber, username1, gamerunning, player1score)
                player1score += round_score
                if not gamerunning:
                    break


                playernumber = "Player 2"
                gamerunning, round_score = self.__window.makeFinalGameWindow(playernumber, username2, gamerunning, player2score)
                player2score += round_score

                if player1score != player2score:
                    equalscore = False

            return gamerunning, player1score, player2score

        if self.__debugTie:
            rounds = 5
            player1score = 30
            player2score = 30

        while gamerunning:
            if rounds >= 5:
                print("Game ended.")
                if player1score == player2score:
                    gamerunning, player1score, player2score = finalround(username1, username2, player1score, player2score)
                if player1score > player2score:
                    winner = username1
                    winscore = player1score
                else:
                    winner = username2
                    winscore = player2score
                break

            if usrturn == 1:
                playernumber = "Player 1"
                print(f"Before update: {username1}'s score: {player1score}")
                gamerunning, round_score = self.__window.makeGameWindow(playernumber, username1, gamerunning, player1score)
                player1score += round_score
                print(f"After update: {username1}'s score: {player1score}")
                usrturn = 2
                rounds += 0.5

            elif usrturn == 2:
                playernumber = "Player 2"
                print(f"Before update: {username2}'s score: {player2score}")
                gamerunning, round_score = self.__window.makeGameWindow(playernumber, username2, gamerunning, player2score)
                player2score += round_score
                print(f"After update: {username2}'s score: {player2score}")
                usrturn = 1
                rounds += 0.5
        if gamerunning:
            print(f"winner is {winner}, with score {winscore}")
            save = FileManager()
            save.Save_Protocol(winscore, winner, player1score, username1, player2score, username2)
        else:
            pass




class Window:
    def __init__(self, user_instance_list):
        self.__userinstlist = user_instance_list

    def errorWindow(self, message):
        root = Tk()
        label = ttk.Label(root, text=message, foreground="red")
        label.pack(padx=10, pady=10)
        okbutton = ttk.Button(root, text="OK", command=root.destroy)
        okbutton.pack(padx=10, pady=10)

    def makeLBWindow(self, pl1, pl2, pl3, pl4, pl5, s1, s2, s3, s4, s5):
        root = Tk()
        root.title("Leaderboard")
        root.resizable(False, False)

        def closewindow():
            root.destroy()

        Mainlabel = ttk.Label(root, text="Leaderboard")
        Mainlabel.grid(row=0, column=0, columnspan=3, sticky=N+S)

        row1 = ttk.Label(root, text="No 1.")
        row1.grid(row=1, column=0, sticky=N+S)
        row2 = ttk.Label(root, text="No 2.")
        row2.grid(row=2, column=0, sticky=N+S)
        row3 = ttk.Label(root, text="No 3.")
        row3.grid(row=3, column=0, sticky=N+S)
        row4 = ttk.Label(root, text="No 4.")
        row4.grid(row=4, column=0, sticky=N+S)
        row5 = ttk.Label(root, text="No 5.")
        row5.grid(row=5, column=0, sticky=N+S)

        LblPl1 = ttk.Label(root, text=pl1)
        LblPl1.grid(row=1, column=1, sticky=N+S)
        LblPl2 = ttk.Label(root, text=pl2)
        LblPl2.grid(row=2, column=1, sticky=N+S)
        LblPl3 = ttk.Label(root, text=pl3)
        LblPl3.grid(row=3, column=1, sticky=N+S)
        LblPl4 = ttk.Label(root, text=pl4)
        LblPl4.grid(row=4, column=1, sticky=N+S)
        LblPl5 = ttk.Label(root, text=pl5)
        LblPl5.grid(row=5, column=1, sticky=N+S)

        LblS1 = ttk.Label(root, text=s1)
        LblS1.grid(row=1, column=2, sticky=N+S)
        LblS2 = ttk.Label(root, text=s2)
        LblS2.grid(row=2, column=2, sticky=N+S)
        LblS3 = ttk.Label(root, text=s3)
        LblS3.grid(row=3, column=2, sticky=N+S)
        LblS4 = ttk.Label(root, text=s4)
        LblS4.grid(row=4, column=2, sticky=N+S)
        LblS5 = ttk.Label(root, text=s5)
        LblS5.grid(row=5, column=2, sticky=N+S)

        closebttn = ttk.Button(root, text="Close", command=closewindow)
        closebttn.grid(row=6, column=0, columnspan=3, sticky=W+E)
        root.protocol("WM_DELETE_WINDOW", closewindow)
        root.mainloop()

    def menuWindow(self, status):
        self.__status = status
        root = Tk()
        root.title("--MENU--")

        def closemenu():
            root.destroy()
            self.__status = 0
            return self.__status
        def login():
            root.destroy()
            self.__status = 1
            return self.__status
        def creatacc():
            root.destroy()
            self.__status = 2
            return self.__status
        def viewlb():
            root.destroy()
            self.__status = 3
            return self.__status
        Titlelabel = ttk.Label(root, text="Welcome to DICEGAME")
        createAccBttn = ttk.Button(root, text="Create Account", command=creatacc)
        loginAccBtn = ttk.Button(root, text="Login", command=login)
        viewLeaderboardBttn = ttk.Button(root, text="View Leaderboard", command=viewlb)

        Titlelabel.grid(row=0, column=0, columnspan=3, sticky=N+S)
        createAccBttn.grid(row=1, column=0)
        loginAccBtn.grid(row=1, column=1)
        viewLeaderboardBttn.grid(row=1, column=2)

        root.protocol("WM_DELETE_WINDOW", closemenu)
        root.mainloop()
        return self.__status



    def getUserInstance(self):
        return self.__userinstlist

    def makeCreateWindow(self):
        root = Tk()
        root.title(f"CREATE ACCOUNT")
        root.resizable(False, False)

        toplabel = Label(root, text=f"Create Account")
        toplabel.grid(column=0, row=0, columnspan=2, sticky=W+E)

        usrlabel = ttk.Label(root, text="Username")
        usrlabel.grid(column=0, row=1)

        usrpasslabel = ttk.Label(root, text="Password")
        usrpasslabel.grid(column=0, row=2)

        usrentry = ttk.Entry(root, width=40)
        usrentry.grid(column=1, row=1)

        usrpassentry = ttk.Entry(root, width=40, show="*")
        usrpassentry.grid(column=1, row=2)

        messagelabel = ttk.Label(root, text="", foreground="red")
        messagelabel.grid(row=3, column=0, columnspan=2, sticky=W+E)

        details = None
        create_success = False
        def try_create():
            nonlocal details, create_success
            username = usrentry.get()
            password = usrpassentry.get()
            if username and password:
                # Check if user already exists
                for user in self.__userinstlist:
                    if user.getUsername() == username:
                        messagelabel.config(text="Username already exists")
                        break
                details = (username, password)
                print("Account is getting Created")
                create_success = True
                root.destroy()
            else:
                messagelabel.config(text="Please enter both username and password")

        createbttn = ttk.Button(root, text="CREATE", command=try_create)
        createbttn.grid(column=0, row=4, columnspan=3, rowspan=2, sticky=N + S)

        root.mainloop()
        if create_success:
            return details
        else:
            return None

    def makeLoginWindow(self, playernumber):
        root = Tk()
        root.title(f"LOGIN - {playernumber}")
        root.resizable(False, False)

        toplabel = Label(root, text=f"{playernumber}")
        toplabel.grid(column=0, row=0, columnspan=2, sticky=W+E)

        usrlabel = ttk.Label(root, text="Username")
        usrlabel.grid(column=0, row=1)

        usrpasslabel = ttk.Label(root, text="Password")
        usrpasslabel.grid(column=0, row=2)

        usrentry = ttk.Entry(root, width=40)
        usrentry.grid(column=1, row=1)

        usrpassentry = ttk.Entry(root, width=40, show="*")
        usrpassentry.grid(column=1, row=2)

        messagelabel = ttk.Label(root, text="", foreground="red")
        messagelabel.grid(row=3, column=0, columnspan=2, sticky=W+E)

        details = None
        login_success = False
        def try_login():
            nonlocal details, login_success
            username = usrentry.get()
            password = usrpassentry.get()
            if username and password:
                for user in self.__userinstlist:
                    if user.getUsername() == username and user.checkPassword(password):
                        print(f"{username} logged in")
                        details = (username, password)
                        login_success = True
                        root.destroy()
                        return
                # Show error message without destroying the window
                messagelabel.config(text=f"{playernumber} - Username or Password incorrect")
            else:
                messagelabel.config(text="Please enter both username and password")


        enterbttn = ttk.Button(root, text="ENTER", command=try_login)
        enterbttn.grid(column=0, row=4, columnspan=3, rowspan=2, sticky=N+S)

        root.mainloop()
        if login_success:
            return details
        else:
            return None

    def makeFinalGameWindow(self, playernumber, username, gamerunning, scoreval):
        self.__turn = 0
        self.__scoreval = scoreval
        root = Tk()
        root.title("--DICEGAME--")
        root.resizable(False, False)

        mainmssg = ttk.Label(root, text=f"--DICEGAME-- {username}")
        turnlabel = ttk.Label(root, text="TURN:")
        usrturn = ttk.Label(root, text=playernumber)
        score = ttk.Label(root, text="SCORE:")
        usrscore = ttk.Label(root, text=self.__scoreval)
        frame = ttk.Frame(root)
        dinum1 = ttk.Label(frame, text='0')

        mainmssg.grid(row=0, column=0, columnspan=2, sticky=W+E)
        turnlabel.grid(row=1, column=0, sticky=W+E)
        usrturn.grid(row=1, column=1, sticky=W+E)
        score.grid(row=2, column=0, sticky=W+E)
        usrscore.grid(row=2, column=1, sticky=W+E)
        frame.grid(row=3, column=0, columnspan=2)
        dinum1.grid(row=0, column=0, rowspan=2, sticky=N+S)

        thisRoundScore = 0

        def closegame():
            nonlocal gamerunning
            gamerunning = False
            root.destroy()
            return

        def closewindow():
            root.destroy()

        def rolldice(turn):
            nonlocal thisRoundScore
            self.__turn += 1
            roll = randint(1, 6)
            dinum1.config(text=str(roll))
            thisRoundScore += roll
            usrscore.config(text=str(self.__scoreval + thisRoundScore))
            rollbttn.config(text="Next Player", command=lambda: closewindow())
            return self.__turn, thisRoundScore
        rollbttn = ttk.Button(root, text="ROLL", command=lambda: rolldice(self.__turn))
        rollbttn.grid(row=4, column=0, columnspan=2, sticky=W + E)

        if self.__turn >= 2:
            rollbttn.config(text="Next Player", command=closewindow)

        root.protocol("WM_DELETE_WINDOW", closegame)
        root.mainloop()
        return gamerunning, thisRoundScore

    def makeGameWindow(self, playernumber, username, gamerunning, scoreval):
        self.__turn = 0
        self.__scoreval = scoreval
        root = Tk()
        root.title("--DICEGAME--")
        root.resizable(False, False)

        mainmssg = ttk.Label(root, text=f"--DICEGAME-- {username}")
        turnlabel = ttk.Label(root, text="TURN:")
        usrturn = ttk.Label(root, text=playernumber)
        score = ttk.Label(root, text="SCORE:")
        usrscore = ttk.Label(root, text=self.__scoreval)
        frame = ttk.Frame(root)
        dinum1 = ttk.Label(frame, text='0')
        dinum2 = ttk.Label(frame, text ='0')

        mainmssg.grid(row=0, column=0, columnspan=2, sticky=W+E)
        turnlabel.grid(row=1, column=0, sticky=W+E)
        usrturn.grid(row=1, column=1, sticky=W+E)
        score.grid(row=2, column=0, sticky=W+E)
        usrscore.grid(row=2, column=1, sticky=W+E)
        frame.grid(row=3, column=0, columnspan=2)
        dinum1.grid(row=0, column=0, rowspan=2, sticky=N+S)
        dinum2.grid(row=0, column=1, rowspan=2, sticky=N+S)

        thisRoundScore = 0

        def closegame():
            nonlocal gamerunning
            gamerunning = False
            root.destroy()
            return

        def closewindow():
            root.destroy()

        def rolldice(turn):
            nonlocal thisRoundScore
            self.__turn += 1
            roll = randint(1, 6)
            if self.__turn == 1:
                dinum1.config(text=str(roll))
                thisRoundScore =+ roll
                usrscore.config(text=str(self.__scoreval + thisRoundScore))
                return self.__turn, thisRoundScore
            else:
                dinum2.config(text=str(roll))
                thisRoundScore += roll
                usrscore.config(text=str(self.__scoreval + thisRoundScore))
                rollbttn.config(text="Next Player", command=lambda: closewindow())
                return self.__turn, thisRoundScore
        rollbttn = ttk.Button(root, text="ROLL", command=lambda: rolldice(self.__turn))
        rollbttn.grid(row=4, column=0, columnspan=2, sticky=W + E)

        if self.__turn >= 3:
            rollbttn.config(text="Next Player", command=closewindow)

        root.protocol("WM_DELETE_WINDOW", closegame)
        root.mainloop()
        return gamerunning, thisRoundScore


class FileManager:
    __usrlist = []
    __usrinstlist = []
    __usrs = 0
    __leaderboard = []
    __lbusers = 0
    @classmethod
    def Create_Account(cls, username, password):
        score = 0
        cls.__usrlist.append([username, password, int(score)])

        if len(cls.__usrlist) % 3 == 0:
            cls.__usrlist = [
                cls.__usrlist[i:i + 3]
                for i in range(0, len(cls.__usrlist), 3)
            ]

        cls.__usrs += 1
        cls.SaveUserFile()

    @classmethod
    def SaveUserFile(cls):
        try:
            with open("USERDATA.txt", "w") as userfile:
                userfile.write(f"{str(cls.__usrs)}\n")
                for user in cls.__usrlist:
                    userfile.write(f"{user[0]} {user[1]} {user[2]}\n")
            cls.Decode_User()
        except Exception as UserSaveError:
            print(f"Error saving user data: {UserSaveError}")
    @classmethod
    def SaveLeaderboard(cls):
        try:
            with open("LEADERBOARD.txt", "w") as leaderboardfile:
                leaderboardfile.write(f"{str(cls.__lbusers)}\n")
                for leaderboard_entry in cls.__leaderboard:
                    leaderboardfile.write(f"{leaderboard_entry[0]} {leaderboard_entry[1]}\n")
            cls.Decode_Leaderboard()
        except Exception as LBSaveError:
                    print(f"Error saving leaderboard data: {LBSaveError}")

    @classmethod
    def Save_Protocol(cls, winnerscore, winnername, player1score, player1, player2score, player2):
        user_found = False
        for i in range(len(cls.__leaderboard)):
            if cls.__leaderboard[i][0] == winnername:
                if int(cls.__leaderboard[i][1]) < winnerscore:
                    cls.__leaderboard[i][1] = winnerscore
                user_found = True
                break
        if not user_found:
            cls.__leaderboard.append([winnername, winnerscore])
            cls.__lbusers += 1
        print("Debug __leaderboard:", cls.__leaderboard)

        print("Debug __usrlist:", cls.__usrlist)
        #according to the debug the list stucture is corrupted into an [a, b, c] structure instead of [[a, b, c]]
        #it needs to be reshaped
        if len(cls.__usrlist) % 3 != 0:
            print("Error: __usrlist structure is invalid and cannot be reshaped.")
        else:
            cls.__usrlist = [
                cls.__usrlist[i:i + 3]
                for i in range(0, len(cls.__usrlist), 3)
            ]
        #reshape completed
        for i in range(len(cls.__usrlist)):
            if cls.__usrlist[i][0] == player1:
                if int(cls.__usrlist[i][2]) < player1score:
                    cls.__usrlist[i][2] = player1score
                break

        for i in range(len(cls.__usrlist)):
            if cls.__usrlist[i][0] == player2:
                if int(cls.__usrlist[i][2]) < player2score:
                    cls.__usrlist[i][2] = player2score
                break
        cls.SaveUserFile()
        cls.SaveLeaderboard()

    @classmethod
    def Decode_User(cls):
        cls.__usrlist = []
        cls.__usrinstlist = []
        try:
            with open("USERDATA.txt", 'r') as file:
                cls.__usrs = int(file.readline())
                #create userlist
                for line in file:
                    try:
                        username, password, score = line.strip().split()
                        cls.__usrlist.extend([username, password, int(score)])
                        #create userinstance list
                        usrinstance = User(username,password,int(score))
                        cls.__usrinstlist.append(usrinstance)
                    except ValueError:
                           continue
        except FileNotFoundError:
            with open("USERDATA.txt", 'w') as file:
                file.write("1\nadmin admin 0\nadmin2 admin 0")
                cls.__usrs = 1
                cls.__usrlist = [["admin", "admin", 0], ["admin2", "admin", 0]]
                instance = User("admin", "admin", 0)
                instance2 = User("admin2", "admin", 0)
                cls.__usrinstlist.append(instance)
                cls.__usrinstlist.append(instance2)

    @classmethod
    def createleaderboard(cls):
        #used chat gpt to help me with the sort
        cls.__leaderboard.sort(key=lambda x: x[1], reverse=True)
        with open("LEADERBOARD.txt", 'w') as file:
            file.write(f"{cls.__lbusers}\n")
            for username, score in cls.__leaderboard:
                file.write(f"{username} {score}\n")
        # only top 5 in the list used by the other program
        cls.__leaderboard = cls.__leaderboard[:5]

    @classmethod
    def Decode_Leaderboard(cls):
        cls.__leaderboard = []
        try:
            with open("LEADERBOARD.txt", 'r') as file:
                cls.__lbusers = int(file.readline().strip())
                for line in file:
                    try:
                        username, highScore = line.strip().split()
                        cls.__leaderboard.append([username, int(highScore)])
                    except ValueError:
                        continue
        except FileNotFoundError:
            with open("LEADERBOARD.txt", 'w') as file:
                file.write("1\nadmin 0\n")
                cls.__leaderboard = [["admin", 0]]
                cls.__lbusers = 1
        cls.createleaderboard()

    @classmethod
    def get_leaderboard(cls):
        return cls.__leaderboard
    @classmethod
    def get_usrlist(cls):
        return cls.__usrlist
    @classmethod
    def get_userinstlist(cls):
        return cls.__usrinstlist

def main():
    FileManager.Decode_User()
    FileManager.Decode_Leaderboard()
    window = Window(FileManager.get_userinstlist())
    game = Game(window)
    game.menu()

def debug():
    FileManager.Decode_User()
    FileManager.Decode_Leaderboard()
    window = Window(FileManager.get_userinstlist())  # Use user instances here instead of just the (raw) list
    game = Game(window, debugLogin=True, debugTie=True)
    game.menu()

if __name__ == '__main__':
    main()
#debug()

