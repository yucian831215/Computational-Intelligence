from tkinter import *
from tkinter import messagebox
import os
import math
import random
import numpy as np

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
            d = 30
        return d
            
    def sin(self,ang):
        i = round(math.sin(math.radians(ang)),10)
        return i
    
    def cos(self,ang):
        i = round(math.cos(math.radians(ang)),10)
        return i
    

class RBFN:
    def __init__(self,p,J):
        self.p = p
        self.J = J
        self.theta = 0
        self.W = np.zeros(self.J)
        self.M = np.zeros((self.J,self.p))
        self.sigma = np.zeros(self.J)       

    #x為一維向量 M是二維向量
    def calOutput(self,x):
        out = 0
        for i in range(self.J):
            out += self.W[i] * math.exp(-self.dist(x,self.M[i]) / (2 * math.pow(self.sigma[i],2)))
        out += self.theta
        return out
        
    def dist(self,x,y):
        distance = 0
        for i in range(self.p):
            distance += math.pow((x[i]-y[i]),2)
        return distance
    

class Individual:
    def __init__(self,p,J,rbf):
        self.p = p
        self.J = J
        self.rbf = rbf
        self.fit = -1
        self.best_history_fit = -1
        self.behavior = np.zeros((1 + (2 + self.p) * self.J))
        self.velocity = np.zeros((1 + (2 + self.p) * self.J))
        self.best_history_behavior = np.zeros((1 + (2 + self.p) * self.J))
        self.maxVlen = 30 * math.sqrt(self.p * self.J) / 2

    def init_individual(self):
        #theta
        self.behavior[0] = random.uniform(0,1)
        #W
        for i in range(1,1 + self.J):
            self.behavior[i] = random.uniform(0,1)
        #M
        for i in range(1 + self.J,1 + self.J + self.J * self.p):
            self.behavior[i] = random.randint(0,30)
        #sigma
        for i in range(1 + self.J + self.J * self.p,1 + self.J + self.J * self.p + self.J):
            self.behavior[i] = random.randint(0,10)

    def setRBFN(self):
        #set theta
        self.rbf.theta = min(max(self.behavior[0],0),1)
        self.behavior[0] = self.rbf.theta
        #set W
        for i in range(self.J):
            self.rbf.W[i] = min(max(self.behavior[1 + i],0),1)
            self.behavior[1 + i] = self.rbf.W[i]
        #set M
        for i in range (1 + self.J,1 + self.J + self.J * self.p):
            self.rbf.M[(i - 1 - self.J) // self.p][(i - 1 - self.J) % self.p] = min(max(self.behavior[i],0),30)
            self.behavior[i] = self.rbf.M[(i - 1 - self.J) // self.p][(i - 1 - self.J) % self.p]            
        #set sigma
        for i in range(self.J):
            self.rbf.sigma[i] = min(max(self.behavior[(1 + self.p) * self.J + 1 + i],1e-7),10)
            self.behavior[(1 + self.p) * self.J + 1 + i] = self.rbf.sigma[i]

    def set_history_best(self):
        if self.best_history_fit > self.fit or self.best_history_fit == -1:
            self.best_history_fit = self.fit
            self.best_history_behavior = self.behavior.copy()

    def change_velocity(self,best_group_behavior,phi1,phi2):
        self.velocity = self.velocity + phi1 * (self.best_history_behavior - self.behavior) + phi2* (best_group_behavior - self.behavior)
        """Vlen = 0
        for i in range(len(self.velocity)):
            Vlen += math.pow(self.velocity[i],2)

        if Vlen > self.maxVlen:
            self.velocity = self.velocity * (self.maxVlen / Vlen)"""
        
    def change_behavior(self):
        self.behavior = self.behavior + self.velocity

    def Fitness(self,data_X,data_y):
        E = 0
        avgE = 0
        for i in range(len(data_y)):
            output_value = self.rbf.calOutput(data_X[i])
            expected_value = (data_y[i] + 40) / 80
            E += math.pow((expected_value - output_value),2)
            avgE += math.fabs(expected_value - output_value)
        E = E / 2
        avgE = avgE / len(data_y)
        self.fit = E
        

class PSO:
    def __init__(self,p,J,rbf,group_size,phi1,phi2):
        self.p = p
        self.J = J
        self.rbf = rbf
        self.group_size = group_size
        self.phi1 = phi1
        self.phi2 = phi2
        self.best_individual = Individual(self.p,self.J,self.rbf)
        self.group = []

    def init_group(self):
        for i in range(self.group_size):
            indivi = Individual(self.p,self.J,self.rbf)
            indivi.init_individual()
            self.group.append(indivi)

    def swarm_move(self,data_X,data_y):
        for i in range(self.group_size):
            #group_best
            self.group[i].setRBFN()
            self.group[i].Fitness(data_X,data_y)
            if self.best_individual.fit == -1 or self.best_individual.fit > self.group[i].fit:
                self.best_individual.fit = self.group[i].fit
                self.best_individual.behavior = self.group[i].behavior.copy()
            #self history best
            self.group[i].set_history_best()
        
        for i in range(self.group_size):
            self.group[i].change_velocity(self.best_individual.behavior,self.phi1,self.phi2)
            self.group[i].change_behavior()

    def last_check(self,data_X,data_y):
        for i in range(self.group_size):
            self.group[i].setRBFN()
            self.group[i].Fitness(data_X,data_y)
            if self.best_individual.fit == -1 or self.best_individual.fit > self.group[i].fit:
                self.best_individual.fit = self.group[i].fit
                self.best_individual.behavior = self.group[i].behavior.copy()

    def turn_back(self):
        #inital    
        self.best_individual.fit = -1
        

class CanvasDemo:    
    def __init__(self):
        window = Tk()
        window.title("PSO")
        window.minsize(width = 1000, height = 600)
        window.geometry("1000x600+120+100")

        self.data_X = []
        self.data_y = []
        
        self.canvas = Canvas(window, width = 600, height = 600, bg = "white")
        self.canvas.place(x = 400 , y = 0)

        self.canvas_info = Canvas(window,width = 380 , height = 300)
        self.canvas_info.place(x = 0 , y = 300)
            
        self.L_setting = Label(window,text = "Setting",font=("Helvetica", "20"))
        self.L_setting.place(x = 300 , y = 0)

        self.L_information_set = Label(window,text = "Information Set：",font=("Helvetica", "12"))
        self.L_information_set.place(x = 0 , y = 50)
        self.choose_Inf_set = IntVar()
        four_dimension = Radiobutton(window,text = "4-Dimension",variable = self.choose_Inf_set,value = 1,font=("Helvetica", "12"))
        four_dimension.place(x = 120 , y = 50)
        six_dimension = Radiobutton(window,text = "6-Dimension",variable = self.choose_Inf_set,value = 2,font=("Helvetica", "12"))
        six_dimension.place(x = 240 , y = 50)

        self.AgentN = Label(window,text = "AgentNum：",font=("Helvetica", "12"))
        self.AgentN.place(x = 0 , y = 90)
        self.AgentN_field = Entry(window,width = 18,font=("Helvetica", "12"))
        self.AgentN_field.place(x = 150 , y = 93)
        
        self.It_N = Label(window,text = "IterationNumber：",font=("Helvetica", "12"))
        self.It_N.place(x = 0 , y = 130)
        self.It_N_field = Entry(window,width = 18,font=("Helvetica", "12"))
        self.It_N_field.place(x = 150 , y = 133)

        self.WOC = Label(window,text = "WeightOfCognition：",font=("Helvetica", "12"))
        self.WOC.place(x = 0 , y = 170)
        self.WOC_field = Entry(window,width = 18,font=("Helvetica", "12"))
        self.WOC_field.place(x = 150 , y = 173)

        self.WOS = Label(window,text = "WeightOfSocial：",font=("Helvetica", "12"))
        self.WOS.place(x = 0 , y = 210)
        self.WOS_field = Entry(window,width = 18,font=("Helvetica", "12"))
        self.WOS_field.place(x = 150 , y = 213)

        self.set_btn = Button(window,text = "Set",font=("Helvetica", "12"),width = 9,command = self.Setting)
        self.set_btn .place(x = 80 , y = 250)
        self.run_btn = Button(window,text = "Run",font=("Helvetica", "12"),width = 9,state = DISABLED,command = self.Run)
        self.run_btn .place(x = 200 , y = 250)
        
        self.canvas_info.create_line(40,20,40,260,width = 1.3)    
        self.canvas_info.create_line(40,260,360,260,width = 1.3)
        self.canvas_info.create_text(200,280,text = "Iteration times",font=("Helvetica", "12"))
        self.canvas_info.create_text(40,10,text = "Best E(n)",font=("Helvetica", "10"))
        for i in range(21):
            self.canvas_info.create_text(20,260 - (240 / 10) * i,text = "{E}".format(E = '%.1f' % i))
        self.canvas_info.create_text(310,10,text = "Best E(n): 0.0000000",font=("Helvetica", "10"),tags = 'E_value')

        #line
        self.canvas.create_line(self.trans_w(-6), self.trans_h(0), self.trans_w(-6), self.trans_h(22), fill = "blue")
        self.canvas.create_line(self.trans_w(6), self.trans_h(0), self.trans_w(6), self.trans_h(10), fill = "blue")
        self.canvas.create_line(self.trans_w(-6), self.trans_h(22), self.trans_w(18), self.trans_h(22), fill = "blue")
        self.canvas.create_line(self.trans_w(6), self.trans_h(10), self.trans_w(30), self.trans_h(10), fill = "blue")
        self.canvas.create_line(self.trans_w(18), self.trans_h(22), self.trans_w(18), self.trans_h(37), fill = "blue")
        self.canvas.create_line(self.trans_w(30), self.trans_h(10), self.trans_w(30), self.trans_h(37), fill = "blue")
        self.canvas.create_line(self.trans_w(-11), self.trans_h(0), self.trans_w(11), self.trans_h(0), fill = "black")
        #self.canvas.create_line(self.trans_w(18), self.trans_h(50), self.trans_w(30), self.trans_h(50), fill = "black")

        line1 = Line(-6,0,-6,22)
        line2 = Line(6,0,6,10)
        line3 = Line(-6,22,18,22)
        line4 = Line(6,10,30,10)
        line5 = Line(18,22,18,37)
        line6 = Line(30,10,30,37)
        line7 = Line(-6,0,6,0)
        #line8 = Line(18,50,30,50)
        self.LineList = [line1,line2,line3,line4,line5,line6,line7]

        #car's init variable
        self.myCar = Car(0,0,0,90)
        self.myCar.distance(self.LineList)
        
        #car
        self.canvas.create_oval(self.trans_w(-3), self.trans_h(3), self.trans_w(3), self.trans_h(-3),tags='car')
        self.canvas.create_oval(self.trans_w(-0.5), self.trans_h(0.5), self.trans_w(0.5), self.trans_h(-0.5),fill='red',tags='carcenter')
        self.canvas.create_oval(self.trans_w(23.5), self.trans_h(36.5), self.trans_w(24.5), self.trans_h(37.5),tags='finish',fill='red')
        
        #information about car
        self.canvas.create_text(self.trans_w(0), self.trans_h(4),text ="({PosX},{PosY})".format(PosX = '%.2f'%self.myCar.x,PosY = '%.2f'%self.myCar.y),tags='text')
        self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.front*self.myCar.cos(self.myCar.phi)),
                                    self.trans_h(self.myCar.y+self.myCar.front*self.myCar.sin(self.myCar.phi)),fill = 'red',tags ='directionF',width=1.5)
        self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.right*self.myCar.cos(self.myCar.phi-45)),
                                    self.trans_h(self.myCar.y+self.myCar.right*self.myCar.sin(self.myCar.phi-45)),fill = 'green',tags ='directionR',width=1.5)
        self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.left*self.myCar.cos(self.myCar.phi+45)),
                                    self.trans_h(self.myCar.y+self.myCar.left*self.myCar.sin(self.myCar.phi+45)),fill = 'yellow',tags ='directionL',width=1.5)
        
        window.mainloop()

    def Setting(self):
        self.set_btn["text"] = "Wait..."
        self.canvas_info.delete("E_lines")
        self.init_car()

        numberOfneuron = 10
        self.times = (int)(self.It_N_field.get())
        group_size = (int)(self.AgentN_field.get())
        weightOfcognition = (float)(self.WOC_field.get())
        weightOfsocial = (float)(self.WOS_field.get())
        
        if self.choose_Inf_set.get() == 1:
            DATA_DIR = '資料集_不含位置'
        elif self.choose_Inf_set.get() == 2:
            DATA_DIR = '資料'
        else:
            messagebox.showerror ("Error","Didn't Choose Information Set")
        
        if self.choose_Inf_set.get() != 0:
           self.data_X = []
           self.data_y = []
           temp = []
           for filename in os.listdir(DATA_DIR):
               f = open(os.path.join(DATA_DIR,filename),'r')
               for line in f.readlines():
                   temp = line.split()
                   new = []
                   for i in range(len(temp)):
                       if i == len(temp) - 1:
                           self.data_y.append((float)(temp[i]))
                           self.data_X.append(new)
                       else:
                           new.append((float)(temp[i]))
                           
           self.dimension_X = len(self.data_X[0])
           
           self.rbf = RBFN(self.dimension_X,numberOfneuron)
           self.pso = PSO(self.dimension_X,numberOfneuron,self.rbf,group_size,weightOfcognition,weightOfsocial)
           self.pso.init_group()
           
           self.run_btn["state"] = "normal"
        self.set_btn["text"] = "Set"

    def Run(self):
        x1 = x2 = y1 = y2 =0
        for i in range(self.times):
            self.pso.swarm_move(self.data_X,self.data_y)
            self.canvas_info.delete("E_value")
            self.canvas_info.create_text(310,10,text = "Best E(n): {E}".format(E = '%.7f' %self.pso.best_individual.fit),font=("Helvetica", "10"),tags = 'E_value')
            if i == 0:
                x1 = i
                y1 = self.pso.best_individual.fit
            else:
                x2 = i
                y2 = self.pso.best_individual.fit
                self.canvas_info.create_line(50 + (300 / self.times) * x1,260 - (240 / 10) * y1,50 + (300 / self.times) * x2,260 - (240 / 10) * y2,fill = 'red',tag = 'E_lines')
                x1 = x2
                y1 = y2
            self.canvas.update()
            self.pso.turn_back()

        #last
        self.pso.last_check(self.data_X,self.data_y)
        self.canvas_info.delete("E_value")
        self.canvas_info.create_text(310,10,text = "Best E(n): {E}".format(E = '%.7f' %self.pso.best_individual.fit),font=("Helvetica", "10"),tags = 'E_value')
        x2 = self.times
        y2 = self.pso.best_individual.fit
        self.canvas_info.create_line(50 + (300 / self.times) * x1,260 - (240 / 10) * y1,50 + (300 / self.times) * x2,260 - (240 / 10) * y2,fill = 'red',tag = 'E_lines')
        #Set Final RBFN
        self.pso.best_individual.setRBFN()      
        
        self.run_btn["state"] = "disabled"

        while True:
            Prex = self.myCar.x
            Prey = self.myCar.y
            
            if self.myCar.y >= 37:
                break
            
            if self.dimension_X == 3:
                Input_X = [self.myCar.front,self.myCar.right,self.myCar.left]
            elif self.dimension_X ==5:
                Input_X = [self.myCar.x,self.myCar.y,self.myCar.front,self.myCar.right,self.myCar.left]
                
            theta = 80 * self.rbf.calOutput(Input_X) - 40
            
            self.myCar.turn(theta)
            self.myCar.nextPhi()

            dx = self.myCar.x - Prex
            dy = self.myCar.y - Prey

            self.canvas.after(100)
            self.canvas.move("carcenter", dx * 10, -dy * 10)
            self.canvas.move("car", dx * 10, -dy * 10)
            self.canvas.create_oval(self.trans_w(self.myCar.x-0.15), self.trans_h(self.myCar.y+0.15), self.trans_w(self.myCar.x+0.15), self.trans_h(self.myCar.y-0.15),fill='blue',tags="footprint")

            self.myCar.distance(self.LineList)

            self.canvas.delete('text')
            self.canvas.create_text(self.trans_w(self.myCar.x), self.trans_h(self.myCar.y+4),text ="({PosX},{PosY})".format(PosX = '%.2f'%self.myCar.x,PosY = '%.2f'%self.myCar.y),tags='text')
            
            #car direction
            self.canvas.delete('directionF')
            self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.front*self.myCar.cos(self.myCar.phi)),
                                    self.trans_h(self.myCar.y+self.myCar.front*self.myCar.sin(self.myCar.phi)),fill = 'red',tags ='directionF',width=1.5)
            self.canvas.delete('directionR')
            self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.right*self.myCar.cos(self.myCar.phi-45)),
                                    self.trans_h(self.myCar.y+self.myCar.right*self.myCar.sin(self.myCar.phi-45)),fill = 'green',tags ='directionR',width=1.5)
            self.canvas.delete('directionL')
            self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.left*self.myCar.cos(self.myCar.phi+45)),
                                    self.trans_h(self.myCar.y+self.myCar.left*self.myCar.sin(self.myCar.phi+45)),fill = 'yellow',tags ='directionL',width=1.5)
            self.canvas.update()

    def trans_w(self,point):
        i = (point + 20) * 10
        return i
    
    def trans_h(self,point):
        j = 600 - 100 - 10 * point
        return j

    def init_car(self):
        self.myCar.x = 0
        self.myCar.y = 0
        self.myCar.theta = 0
        self.myCar.phi = 90

        self.myCar.distance(self.LineList)

        self.canvas.delete('footprint')
        #car
        self.canvas.delete('car')
        self.canvas.create_oval(self.trans_w(-3), self.trans_h(3), self.trans_w(3), self.trans_h(-3),tags='car')
        self.canvas.delete('carcenter')
        self.canvas.create_oval(self.trans_w(-0.5), self.trans_h(0.5), self.trans_w(0.5), self.trans_h(-0.5),fill='red',tags='carcenter')
        
        #information about car
        self.canvas.delete('text')
        self.canvas.create_text(self.trans_w(0), self.trans_h(4),text ="({PosX},{PosY})".format(PosX = '%.2f'%self.myCar.x,PosY = '%.2f'%self.myCar.y),tags='text')

        self.canvas.delete('directionF')
        self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.front*self.myCar.cos(self.myCar.phi)),
                                    self.trans_h(self.myCar.y+self.myCar.front*self.myCar.sin(self.myCar.phi)),fill = 'red',tags ='directionF',width=1.5)
        self.canvas.delete('directionR')
        self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.right*self.myCar.cos(self.myCar.phi-45)),
                                    self.trans_h(self.myCar.y+self.myCar.right*self.myCar.sin(self.myCar.phi-45)),fill = 'green',tags ='directionR',width=1.5)
        self.canvas.delete('directionL')
        self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.left*self.myCar.cos(self.myCar.phi+45)),
                                    self.trans_h(self.myCar.y+self.myCar.left*self.myCar.sin(self.myCar.phi+45)),fill = 'yellow',tags ='directionL',width=1.5)
        
myCanvas = CanvasDemo()

