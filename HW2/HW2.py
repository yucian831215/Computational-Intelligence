from tkinter import *
import math
import random
import os
import copy

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
    def __init__(self,x,y):
        
        window = Tk()
        window.title("Canvas Demo")
        window.minsize(width = 460, height = 600)
        
        self.canvas = Canvas(window, width = 560, height = 600, bg = "white")
        self.canvas.pack()

        window.title("GA Optimization")

        self.x = x
        self.y = y

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
        
        self.LineList = [line1,line2,line3,line4,line5,line6,line7,line8]

        #car
        self.canvas.create_oval(self.trans_w(-3), self.trans_h(3), self.trans_w(3), self.trans_h(-3),tags='car')
        self.canvas.create_oval(self.trans_w(-0.5), self.trans_h(0.5), self.trans_w(0.5), self.trans_h(-0.5),fill='red',tags='carcenter')
        self.canvas.create_oval(self.trans_w(23.5), self.trans_h(37.5), self.trans_w(24.5), self.trans_h(38.5),tags='finish',fill='red')
        self.canvas.create_rectangle(self.trans_w(-15),self.trans_h(53.5),self.trans_w(6),self.trans_h(42))
        self.canvas.create_line(self.trans_w(0),self.trans_h(0),self.trans_w(0),self.trans_h(5),fill = 'red',tags ='direction',width=1.5)
        self.canvas.create_text(self.trans_w(1), self.trans_h(52),text ="information",fill='blue',font=("Helvetica", "15"))

        #car's init variable
        self.myCar = Car(0,0,0,90)
        #information about car
        self.canvas.create_text(self.trans_w(0), self.trans_h(4),text ="({PosX},{PosY})".format(PosX = '%.2f'%self.myCar.x,PosY = '%.2f'%self.myCar.y),tags='text')
        self.canvas.create_line(self.trans_w(0),self.trans_h(0),
                                self.trans_w(10*self.myCar.cos(self.myCar.phi-45)),self.trans_h(10*self.myCar.sin(self.myCar.phi-45)),fill = 'green',tags ='directionR',width=1.5)
        self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                self.trans_w(10*self.myCar.cos(self.myCar.phi+45)),self.trans_h(10*self.myCar.sin(self.myCar.phi+45)),fill = 'yellow',tags ='directionL',width=1.5)
        self.canvas.create_text(self.trans_w(-6), self.trans_h(48),text ="{info}".format(info = self.all_info(self.myCar)),tags='all_info')
        self.myCar.distance(self.LineList)

        #graphics of RBFN process
        self.canvas.create_text(self.trans_w(-7), self.trans_h(38),text ="RBFN Processing",fill='blue',font=("Helvetica", "15"))
        self.canvas.create_text(self.trans_w(-5), self.trans_h(35),text ="00.00%",font=("Helvetica", "12"),tags = 'ready_probability')
        self.canvas.create_text(self.trans_w(-2), self.trans_h(32),text ="Best E(n): 0.0000000   Best avgE(n): 0.0000000",font=("Helvetica", "10"),tags = 'fit')                                
        self.canvas.create_rectangle(self.trans_w(-15),self.trans_h(36),self.trans_w(5),self.trans_h(34))
        self.canvas.create_rectangle(self.trans_w(-15),self.trans_h(36),self.trans_w(-15),self.trans_h(36),fill = 'red',tags = 'ready')

        self.run = Button(self.canvas)
        self.run["text"] = "Run"
        self.run.place(x = self.trans_w(10) , y = self.trans_h(30))
        self.run["command"] = self.runMethod

        self.C_P = Label(self.canvas)
        self.C_P["text"] = "交配機率: "
        self.C_P.place(x = self.trans_w(-15.5) , y = self.trans_h(30))
        self.C_Pfield = Entry(self.canvas)
        self.C_Pfield["width"] = 8
        self.C_Pfield.place(x = self.trans_w(-9.5) , y = self.trans_h(30))

        self.M_P = Label(self.canvas)
        self.M_P["text"] = "突變機率: "
        self.M_P.place(x = self.trans_w(-3) , y = self.trans_h(30))
        self.M_Pfield = Entry(self.canvas)
        self.M_Pfield["width"] = 8
        self.M_Pfield.place(x = self.trans_w(3) , y = self.trans_h(30))

        self.It = Label(self.canvas)
        self.It["text"] = "迭代次數: "
        self.It.place(x = self.trans_w(-15.5) , y = self.trans_h(28))
        self.Itfield = Entry(self.canvas)
        self.Itfield["width"] = 8
        self.Itfield.place(x = self.trans_w(-9.5) , y = self.trans_h(28))

        self.G_N = Label(self.canvas)
        self.G_N["text"] = "族群大小: "
        self.G_N.place(x = self.trans_w(-3) , y = self.trans_h(28))
        self.G_Nfield = Entry(self.canvas)
        self.G_Nfield["width"] = 8
        self.G_Nfield.place(x = self.trans_w(3) , y = self.trans_h(28))

        self.canvas.update()
        window.mainloop()

    def runMethod(self):
        #基因演算法
        self.numberOfneuron = 4
        self.times = (int)(self.Itfield.get())
        self.rbf = RBFN(len(self.x[0]),self.numberOfneuron)
        self.ga = GA((int)(self.G_Nfield.get()),len(self.x[0]),self.numberOfneuron,self.rbf,(float)(self.C_Pfield.get()),(float)(self.M_Pfield.get()))
        
        self.ga.init_Pool()
        
        for i in range (self.times):
            self.ga.reproduction(self.x,self.y)
            self.ga.crossover()
            self.ga.mutation()
            self.ga.movePool()
            self.canvas.delete('ready')
            self.canvas.create_rectangle(self.trans_w(-15),self.trans_h(36),self.trans_w(-15 + ((i+1)/self.times * 20)),self.trans_h(34),fill = 'red',tags = 'ready')
            self.canvas.delete('ready_probability')
            self.canvas.create_text(self.trans_w(-5), self.trans_h(35),text ="{R_P}%".format(R_P = '%.2f' %((i+1)/self.times*100)),font=("Helvetica", "12"),tags = 'ready_probability')
            self.canvas.delete('fit')
            self.canvas.create_text(self.trans_w(-2), self.trans_h(32),text ="Best E(n): {fit}   Best avgE(n): {avgfit}".format(
                                    fit = '%.7f' %self.ga.best_Fit,avgfit = '%.7f' %self.ga.best_avgfit),font=("Helvetica", "10"),tags = 'fit')  
            self.canvas.update()
    
        #let best gene be RBFN's parameters
        self.ga.best_gene.setRBFN()

        while True:

            Prex = self.myCar.x
            Prey = self.myCar.y
            
            self.myCar.distance(self.LineList)

            Input_X = [self.myCar.front,self.myCar.right,self.myCar.left]
            theta = 80 * self.rbf.calOutput(Input_X) - 40

            if self.myCar.y >= 37:
                self.Summary(self.myCar)
                break
            
            self.myCar.turn(theta)

            #update car information
            self.Summary(self.myCar)
            self.myCar.nextPhi()

            dx = self.myCar.x - Prex
            dy = self.myCar.y - Prey

            self.canvas.after(100)
            self.canvas.move("carcenter", dx * 10, -dy * 10)
            self.canvas.move("car", dx * 10, -dy * 10)
            self.canvas.create_oval(self.trans_w(self.myCar.x-0.15), self.trans_h(self.myCar.y+0.15), self.trans_w(self.myCar.x+0.15), self.trans_h(self.myCar.y-0.15),fill='blue')

            self.myCar.distance(self.LineList)
            #car direction
            self.canvas.delete('direction')
            self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.front*self.myCar.cos(self.myCar.phi)),
                                    self.trans_h(self.myCar.y+self.myCar.front*self.myCar.sin(self.myCar.phi)),fill = 'red',tags ='direction',width=1.5)
            self.canvas.delete('directionR')
            self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.right*self.myCar.cos(self.myCar.phi-45)),
                                    self.trans_h(self.myCar.y+self.myCar.right*self.myCar.sin(self.myCar.phi-45)),fill = 'green',tags ='directionR',width=1.5)
            self.canvas.delete('directionL')
            self.canvas.create_line(self.trans_w(self.myCar.x),self.trans_h(self.myCar.y),
                                    self.trans_w(self.myCar.x+self.myCar.left*self.myCar.cos(self.myCar.phi+45)),
                                    self.trans_h(self.myCar.y+self.myCar.left*self.myCar.sin(self.myCar.phi+45)),fill = 'yellow',tags ='direction',width=1.5)
            self.canvas.update()
        
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
              
    def Summary(self,myCar):
        self.canvas.delete('all_info')
        self.canvas.create_text(self.trans_w(-6), self.trans_h(48),text ="{info}".format(info = self.all_info(myCar)),tags='all_info')

        self.canvas.delete('text')
        self.canvas.create_text(self.trans_w(myCar.x), self.trans_h(myCar.y+4),text ="({PosX},{PosY})".format(PosX = '%.2f'%myCar.x,PosY = '%.2f'%myCar.y),tags='text')

#RBFN (p is Input's dimension and J is the number of neuron)
class RBFN:
    def __init__(self,p,J):
        self.p = p
        self.J = J
        self.theta = 0
        self.W = []
        self.M = []
        self.sigma = []

    def setlistsize(self):
        for i in range(self.J):
            self.W.append(i)

        for i in range(self.J):
            new = []
            for j in range(self.p):
                new.append(j)
            self.M.append(new)
            
        for i in range(self.J):
            self.sigma.append(i)
            

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

class GA:
    def __init__(self,poolsize,p,J,rbf,C_P,M_P):
        self.Pool = []
        self.NewPool = []
        self.poolsize = poolsize
        self.p = p
        self.J = J
        self.rbf = rbf
        self.crossover_probability = C_P
        self.crossover_ratio = 0.5
        self.mutation_probability = M_P
        self.mutation_ratio = 0.5
        self.best_avgfit = 100
        self.best_Fit = 100
        self.best_gene = Gene(self.p,self.J,self.rbf)
        
        
    def init_Pool(self):
        for i in range (self.poolsize):
            g = Gene(self.p,self.J,self.rbf)
            g.init_DNA()
            self.Pool.append(g)
            self.NewPool.append(g)

    def reproduction(self,data_X,data_y):
        for i in range (self.poolsize):
            self.Pool[i].setRBFN()
            self.Pool[i].Fitness(data_X,data_y)
            
            if self.Pool[i].fit < self.best_Fit:
                self.best_Fit = self.Pool[i].fit
                self.best_gene.fit = self.best_Fit
                self.best_gene.DNA = copy.deepcopy(self.Pool[i].DNA)
                
            if self.Pool[i].avgfit < self.best_avgfit:
                self.best_avgfit = self.Pool[i].avgfit
                

        #輪盤式選擇
        sum_Fit = 0
        for i in range (self.poolsize):
            sum_Fit += 1 / self.Pool[i].fit

        alloc_pointer = 0
        for i in range (self.poolsize):
            self.Pool[i].interval_start = alloc_pointer
            alloc_pointer += ( 1 / self.Pool[i].fit ) / sum_Fit
            self.Pool[i].interval_end = alloc_pointer

        for i in range (self.poolsize):
            pointer = random.uniform(0,1)
            for j in range (self.poolsize):
                if pointer >= self.Pool[j].interval_start and pointer <= self.Pool[j].interval_end:
                    self.NewPool[i] = self.Pool[j]

    def crossover(self):
        crossover_num = (int)(len(self.NewPool) * self.crossover_probability)
        for i in range (crossover_num):
            index1 = random.randint(0,len(self.NewPool)-1)
            index2 = random.randint(0,len(self.NewPool)-1)

            DNA1 = copy.deepcopy(self.NewPool[index1].DNA)
            DNA2 = copy.deepcopy(self.NewPool[index2].DNA)
            
            ratio = (random.randint(0,1) - 0.5) * 2 * self.crossover_ratio
            
            for j in range (len(DNA1)):
                self.NewPool[index1].DNA[j] = DNA1[j] + ratio * (DNA1[j] - DNA2[j])
                self.NewPool[index2].DNA[j] = DNA2[j] - ratio * (DNA1[j] - DNA2[j])

    def mutation(self):
        mutation_num = (int)(len(self.NewPool) * self.mutation_probability)
        for i in range (mutation_num):
            index1 = random.randint(0,len(self.NewPool)-1)

            DNA1 = copy.deepcopy(self.NewPool[index1].DNA)

            ratio = (random.randint(0,1) - 0.5) * 2 * self.mutation_ratio
            
            for j in range(len(DNA1)):
                self.NewPool[index1].DNA[j] = DNA1[j] + ratio * random.randint(0,1) * DNA1[j]

    def movePool(self):
        self.Pool = copy.deepcopy(self.NewPool)

class Gene:
    def __init__(self,p,J,rbf):
        self.p = p
        self.J = J
        self.DNA = []
        self.fit = 0
        self.avgfit = 0
        self.rbf = rbf
        self.interval_start = 0
        self.interval_end = 0

    def init_DNA(self):
        #theta
        self.DNA.append(random.uniform(0,1))
        #W
        for i in range (1,1 + self.J):
            self.DNA.append(random.uniform(0,1))
        #M
        for i in range (1 + self.J,1 + self.J + self.J * self.p):
            self.DNA.append(random.uniform(0,30))
        for i in range (1 + self.J + self.J * self.p,1 + self.J + self.J * self.p + self.J):
            self.DNA.append(random.uniform(0,10))

    def setinterval(self,start,end):
        self.interval_start = start
        self.interval_end = end

    def setRBFN(self):
        if len(self.rbf.W) != self.J:
            self.rbf.setlistsize()
        #set theta
        self.rbf.theta = min(max(self.DNA[0],0),1)
        self.DNA[0] = self.rbf.theta
        #set W
        for i in range (1,1 + self.J):
            self.rbf.W[i-1] = min(max(self.DNA[i],0),1)
            self.DNA[i] = self.rbf.W[i-1]
        #set M
        for i in range (1 + self.J,1 + self.J + self.J * self.p):
            self.rbf.M[(i - 1 - self.J) // self.p][(i - 1 - self.J) % self.p] = min(max(self.DNA[i],0),30)
            self.DNA[i] = self.rbf.M[(i - 1 - self.J) // self.p][(i - 1 - self.J) % self.p]
        for i in range (1 + self.J + self.J * self.p,1 + self.J + self.J * self.p + self.J):
            self.rbf.sigma[(i - 1 - self.J - self.J * self.p)] = min(max(self.DNA[i],1e-7),10)
            self.DNA[i] = self.rbf.sigma[(i - 1 - self.J - self.J * self.p)]
            
    #data_X是二維向量 data_y為一維向量        
    def Fitness(self,data_X,data_y):
        E = 0
        avgE = 0
        for i in range (len(data_y)):
            output_value = self.rbf.calOutput(data_X[i])
            #yn轉換
            expected_value = (data_y[i] + 40) / 80
            E += math.pow((expected_value - output_value),2)
            avgE += math.fabs(expected_value - output_value)
            
        self.fit = E / 2
        self.avgfit = avgE / len(data_y)

 #data_Input and expeccted_Output read in
DATA_DIR = '資料集_不含位置'
s = []
x = []
y = []
temp = []
for filename in os.listdir(DATA_DIR):
    #print ("Loading: %s" %filename)
    f = open(os.path.join(DATA_DIR,filename),'r')
    s.append(f.read())
for i in range (len(s)):
    new = []
    temp = s[i].split()
    for j in range (len(temp)):
        if j % 4 == 0:
            new = []
        elif j % 4 == 3:
            y.append((float)(temp[j]))
            x.append(new)
            
        if j % 4 != 3:
            new.append((float)(temp[j]))
                    
myCanvas = CanvasDemo(x,y)
