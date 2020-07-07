from tkinter import *
import math

class MOD:
    #var_type: 0=front 1=right-left 2=theta
    def __init__(self,a,b,c,d,var_type):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.var_type = var_type
    
    #歸屬度
    def Membership(self,value_in):
        value_out = 0
        
        if value_in >= self.a and value_in <= self.b and self.a != self.b:
            value_out = (value_in - self.a) / (self.b - self.a)
        elif value_in >= self.a and value_in <= self.b and self.a == self.b:
            value_out = 1
        elif value_in > self.b and value_in <= self.c:
            value_out = 1
        elif value_in > self.c and value_in <= self.d and self.c != self.d:
            value_out = (self.d - value_in) / (self.d - self.c)
        elif value_in > self.c and value_in <= self.d and self.c == self.d:
            value_out = 1
        else:
            value_out = 0

        return value_out

class Fuzzy:
    def __init__(self,var,interval):
        self.var = var
        self.interval = interval
        self.start = 0
        self.end = 0
        self.R = []
        self.Alpha = []
        
    #Rule and Mod
    def Rule(self):
        #Mod d1 = front d2 = right-left c = theta
        d1_1 = MOD(3,3,9,13,0)
        d1_2 = MOD(30,30,100,100,0)

        d2_1 = MOD(12,22,100,100,1)
        d2_2 = MOD(2,7,15,20,1)
        d2_3 = MOD(0,0,2,3,1)
        d2_4 = MOD(-3,-2,0,0,1)
        d2_5 = MOD(-20,-15,-7,-2,1)
        d2_6 = MOD(-100,-100,-22,-12,1)

        c_1 = MOD(0,18,22,22,2)
        c_2 = MOD(15,18,18,18,2)
        c_3 = MOD(0,0,5,10,2)
        c_4 = MOD(-10,-5,0,0,2)
        c_5 = MOD(-18,-18,-18,-15,2)
        c_6 = MOD(-22,-22,-18,0,2)
        #c_7 = MOD(-35,-30,-30,-30,2)
        
        #Rule
        R1 = [d2_1,c_1]
        R2 = [d2_2,c_2]
        R3 = [d2_6,c_6]
        R4 = [d2_5,c_5]
        R5 = [d1_2,d2_3,c_3]
        R6 = [d1_2,d2_4,c_4]
        #R7 = [d1_2,c_7]
        self.R = [R1,R2,R3,R4,R5,R6]
        
        self.start = c_1.a
        self.end = c_1.d
    #firing strength
    def FS(self):
        for i in range(len(self.R)):
            alpha = 1
            for j in range(len(self.R[i])-1):
                temp = self.R[i][j].Membership(self.var[self.R[i][j].var_type])
                alpha = min(alpha,temp)
            self.start = min(self.start,self.R[i][len(self.R[i])-1].a)
            self.end = max(self.end,self.R[i][len(self.R[i])-1].d)
            self.Alpha.append(alpha)            
    #去模糊化(重心法)
    def deFuzzy_1(self):
        Den = 0
        Mol = 0
        for i in range(self.start,self.end+self.interval,self.interval):
            ms = 0
            for j in range(len(self.R)):
                temp = min(self.R[j][len(self.R[j])-1].Membership(i),self.Alpha[j])
                ms = max(ms,temp)
            Den = Den + ms
            Mol = Mol + i * ms
            
        if Den == 0:
            ans = 0
        else:
            ans = Mol / Den
        
        return ans
            
    def Cal_FZ(self):
        self.Rule()
        self.FS()
        return self.deFuzzy_1()

class Line:
    def __init__(self,x1,y1,x2,y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.VecX = x2 - x1
        self.VecY = y2 - y1

class Car:
    def __init__(self, x , y , theta , phi):
        self.x = x
        self.y = y
        self.theta = theta
        self.phi = phi
        self.b = 6
        self.front = 0
        self.right = 0
        self.left = 0

    def xmovTo(self):
        self.x = self.x + self.cos(self.theta+self.phi) + self.sin(self.theta) * self.sin(self.phi)
        
    def ymovTo(self):
        self.y = self.y + self.sin(self.theta+self.phi) - self.sin(self.theta) * self.cos(self.phi)
        
    def nextPhi(self):
        self.phi = self.phi - math.degrees(math.asin(2 * self.sin(self.theta) / self.b))
        self.xmovTo()
        self.ymovTo()
        
    def turn(self, theta):
        self.theta = theta
        
    def distance(self,templist):
        self.front = self.Cal_distance(templist,self.phi)
        self.right = self.Cal_distance(templist,self.phi-45)
        self.left = self.Cal_distance(templist,self.phi+45)

    def Cal_distance(self,templist,ang):
        d = -1
        for count in range(len(templist)):
            if (templist[count].VecX * self.sin(ang) - templist[count].VecY * self.cos(ang)) == 0:
                continue
            # Line => (x1 + VecX * t , y1 + VecY * t)
            t = (self.sin(ang) * (self.x-templist[count].x1) - self.cos(ang) * (self.y-templist[count].y1)) / (templist[count].VecX * self.sin(ang) - templist[count].VecY * self.cos(ang))
            # Point =>  (x1 + VecX * t , y1 + VecY * t) and (x + cos(ang) * k , y + sin(ang) * k) 之交點
            if ang == 90 or ang == 270:
                k = (templist[count].VecY * t + templist[count].y1 - self.y) / self.sin(ang)
            else:
                k = (templist[count].VecX * t + templist[count].x1 - self.x) / self.cos(ang)

            if t >= 0 and t <= 1 and k > 0:
                pointX = templist[count].x1 + templist[count].VecX * t
                pointY = templist[count].y1 + templist[count].VecY * t
                temp = math.pow((math.pow(pointX-self.x,2) + math.pow(pointY-self.y,2)),0.5)
                if temp < d or d == -1:
                    d = temp
        if d == -1:
            d = 0
        return d
            
    def sin(self,ang):
        i = round(math.sin(math.radians(ang)),10)
        return i
    
    def cos(self,ang):
        i = round(math.cos(math.radians(ang)),10)
        return i


class CanvasDemo:    
    def __init__(self):
        window = Tk()
        window.title("Canvas Demo")
        window.minsize(width = 460, height = 600)
        
        self.canvas = Canvas(window, width = 560, height = 600, bg = "white")
        self.canvas.pack()

        window.title("Fuzzy Control")
    
        #line
        self.canvas.create_line(self.trans_w(-6), self.trans_h(0), self.trans_w(-6), self.trans_h(22), fill = "blue")
        self.canvas.create_line(self.trans_w(6), self.trans_h(0), self.trans_w(6), self.trans_h(10), fill = "blue")
        self.canvas.create_line(self.trans_w(-6), self.trans_h(22), self.trans_w(18), self.trans_h(22), fill = "blue")
        self.canvas.create_line(self.trans_w(6), self.trans_h(10), self.trans_w(30), self.trans_h(10), fill = "blue")
        self.canvas.create_line(self.trans_w(18), self.trans_h(22), self.trans_w(18), self.trans_h(50), fill = "blue")
        self.canvas.create_line(self.trans_w(30), self.trans_h(10), self.trans_w(30), self.trans_h(50), fill = "blue")
        self.canvas.create_line(self.trans_w(-11), self.trans_h(0), self.trans_w(11), self.trans_h(0), fill = "black")
        self.canvas.create_line(self.trans_w(18), self.trans_h(50), self.trans_w(30), self.trans_h(50), fill = "black")

        line1 = Line(-6,0,-6,22)
        line2 = Line(6,0,6,10)
        line3 = Line(-6,22,18,22)
        line4 = Line(6,10,30,10)
        line5 = Line(18,22,18,50)
        line6 = Line(30,10,30,50)
        line7 = Line(-6,0,6,0)
        line8 = Line(18,50,30,50)
        
        LineList = [line1,line2,line3,line4,line5,line6,line7,line8]

        #car
        self.canvas.create_oval(self.trans_w(-3), self.trans_h(3), self.trans_w(3), self.trans_h(-3),tags='car')
        self.canvas.create_oval(self.trans_w(-0.5), self.trans_h(0.5), self.trans_w(0.5), self.trans_h(-0.5),fill='red',tags='carcenter')
        self.canvas.create_oval(self.trans_w(23.5), self.trans_h(37.5), self.trans_w(24.5), self.trans_h(38.5),tags='finish',fill='red')
        self.canvas.create_rectangle(self.trans_w(-15),self.trans_h(53.5),self.trans_w(6),self.trans_h(42))
        self.canvas.create_line(self.trans_w(0),self.trans_h(0),self.trans_w(0),self.trans_h(5),fill = 'red',tags ='direction',width=1.5)
        self.canvas.create_text(self.trans_w(1), self.trans_h(52),text ="information",fill='blue',font=("Helvetica", "15"))

        #car's init variable
        myCar = Car(0,0,0,90)
        #information about car
        self.canvas.create_text(self.trans_w(0), self.trans_h(4),text ="({PosX},{PosY})".format(PosX = '%.2f'%myCar.x,PosY = '%.2f'%myCar.y),tags='text')
        self.canvas.create_line(self.trans_w(0),self.trans_h(0),
                                self.trans_w(10*myCar.cos(myCar.phi-45)),self.trans_h(10*myCar.sin(myCar.phi-45)),fill = 'green',tags ='directionR',width=1.5)
        self.canvas.create_line(self.trans_w(myCar.x),self.trans_h(myCar.y),
                                self.trans_w(10*myCar.cos(myCar.phi+45)),self.trans_h(10*myCar.sin(myCar.phi+45)),fill = 'yellow',tags ='directionL',width=1.5)
        self.canvas.create_text(self.trans_w(-6), self.trans_h(48),text ="{info}".format(info = self.all_info(myCar)),tags='all_info')
        myCar.distance(LineList)

        #Fuzzy grahpics
        self.canvas.create_line(self.trans_w(-14),self.trans_h(27),self.trans_w(14),self.trans_h(27))
        self.canvas.create_line(self.trans_w(0),self.trans_h(36),self.trans_w(0),self.trans_h(25))
        self.canvas.create_oval(self.trans_w(-0.01),self.trans_h(27+0.01),self.trans_w(0.01),self.trans_h(27-0.01),fill='blue',tags='msg')
        self.canvas.create_text(self.trans_w(-10), self.trans_h(38),text ="θ graphics",fill='green',font=("Helvetica", "15"))
        self.canvas.create_rectangle(self.trans_w(-15),self.trans_h(40),self.trans_w(15),self.trans_h(24))

        outfile1 = open('train4D.txt','a')
        outfile2 = open('train6D.txt','a')

        while True:

            Prex = myCar.x
            Prey = myCar.y
            
            myCar.distance(LineList)
            #Fuzzy Control
            FZ = Fuzzy([myCar.front,myCar.right-myCar.left],1)
            theta = FZ.Cal_FZ()

            if myCar.y >= 37:
                self.Summary(outfile1,outfile2,myCar)
                outfile1.close()
                outfile2.close()
                break
            #Fuzzy grahpics
            self.graphic(FZ)
            
            myCar.turn(theta)

            #update car information
            self.Summary(outfile1,outfile2,myCar)
            myCar.nextPhi()

            dx = myCar.x - Prex
            dy = myCar.y - Prey

            self.canvas.after(1000)
            self.canvas.move("carcenter", dx * 10, -dy * 10)
            self.canvas.move("car", dx * 10, -dy * 10)
            self.canvas.create_oval(self.trans_w(myCar.x-0.15), self.trans_h(myCar.y+0.15), self.trans_w(myCar.x+0.15), self.trans_h(myCar.y-0.15),fill='blue')

            myCar.distance(LineList)
            #car direction
            self.canvas.delete('direction')
            self.canvas.create_line(self.trans_w(myCar.x),self.trans_h(myCar.y),
                                    self.trans_w(myCar.x+myCar.front*myCar.cos(myCar.phi)),
                                    self.trans_h(myCar.y+myCar.front*myCar.sin(myCar.phi)),fill = 'red',tags ='direction',width=1.5)
            self.canvas.delete('directionR')
            self.canvas.create_line(self.trans_w(myCar.x),self.trans_h(myCar.y),
                                    self.trans_w(myCar.x+myCar.right*myCar.cos(myCar.phi-45)),
                                    self.trans_h(myCar.y+myCar.right*myCar.sin(myCar.phi-45)),fill = 'green',tags ='directionR',width=1.5)
            self.canvas.delete('directionL')
            self.canvas.create_line(self.trans_w(myCar.x),self.trans_h(myCar.y),
                                    self.trans_w(myCar.x+myCar.left*myCar.cos(myCar.phi+45)),
                                    self.trans_h(myCar.y+myCar.left*myCar.sin(myCar.phi+45)),fill = 'yellow',tags ='direction',width=1.5)
            self.canvas.update()
            
        window.mainloop
        
    #transformate x and y to window coordinate
    def trans_w(self,point):
        i = (point + 16) * 10
        return i
    
    def trans_h(self,point):
        j = 600 - 50 - 10 * point
        return j
    
    def all_info(self,myCar):
        return "X: {PosX} \nY: {PosY} \nFront distance: {Fd} \nRight distance: {Rd} \nLeft distance: {Ld} \nθ: {theta}".format(
                PosX = '%.7f'%myCar.x,PosY = '%.7f'%myCar.y,Fd = '%.7f'%myCar.front,Rd = '%.7f'%myCar.right,Ld = '%.7f'%myCar.left,theta = '%.7f'%myCar.theta)
    
    def graphic(self,FZ):
        i = FZ.start
        self.canvas.delete('msg')
        while i <= FZ.end:
            ms = 0
            for j in range(len(FZ.R)):
                temp = min(FZ.R[j][len(FZ.R[j])-1].Membership(i),FZ.Alpha[j])
                ms = max(ms,temp)
            self.canvas.create_oval(self.trans_w(i*0.5-0.01),self.trans_h(27+ms*8+0.01),self.trans_w(i*0.5+0.01),self.trans_h(27+ms*8-0.01),tags='msg')
            i = i + 0.1
            
    def Summary(self,outfile1,outfile2,myCar):
        self.canvas.delete('all_info')
        self.canvas.create_text(self.trans_w(-6), self.trans_h(48),text ="{info}".format(info = self.all_info(myCar)),tags='all_info')

        self.canvas.delete('text')
        self.canvas.create_text(self.trans_w(myCar.x), self.trans_h(myCar.y+4),text ="({PosX},{PosY})".format(PosX = '%.2f'%myCar.x,PosY = '%.2f'%myCar.y),tags='text')

        outfile1.write("{Fd} {Rd} {Ld} {theta}\n".format(Fd = '%.7f'%myCar.front,Rd = '%.7f'%myCar.right,Ld = '%.7f'%myCar.left,theta = '%.7f'%myCar.theta))    
        outfile2.write("{PosX} {PosY} {Fd} {Rd} {Ld} {theta}\n".format(PosX = '%.7f'%myCar.x,PosY = '%.7f'%myCar.y,
                        Fd = '%.7f'%myCar.front,Rd = '%.7f'%myCar.right,Ld = '%.7f'%myCar.left,theta = '%.7f'%myCar.theta))
              
myCanvas = CanvasDemo()
