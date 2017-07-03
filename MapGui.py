# THIS is my class for perfect potential field debugging, enjoy :P

from tkinter import *

class Gurren_Tk():    
    def __del__(self):
        self.root.update()
        self.root.destroy()
    def __init__(self):
        font = 'mono'
        self.c = {'bd':'#0F0F0F',
                 'nor_text':'#FF8000',
                 'pl_usual':'#808080',
                 'pl_lead':'#'+hex(246)[2:]+hex(139)[2:]+hex(49)[2:],
                 'pl_me': '#0000A0',
                 'red':'#A00000',
                 'yel':'#A0A000',
                 'gre':'#00A000'}
        # подготавливаем окно
        self.root = Tk()
        self.root.geometry('800x580+0+0')
        self.root.configure(background=self.c['bd'])
        self.can = Canvas(self.root, width=560, height=560)
        self.can.configure(background=self.c['bd'])
        self.can.place(x=0, y=20)
        self.turn_num = Label(self.root, font=font)
        self.turn_num.configure(background=self.c['bd'])
        self.turn_num.configure(foreground=self.c['nor_text'])
        self.turn_num['text']='turns = 0'+'|'+'_'*100+'|'
        self.turn_num.place(x=0, y=0)
        ###
        righty = 580
        next_per = 140
        ots = 17
        # x - y
        letter = [righty, 0]
        name = [righty+30, 0]
        elo = [righty+30, ots]
        gold = [righty, ots*2]
        pos = [righty, ots*3]
        spa = [righty, ots*4]
        cra = [righty, ots*5]
        life = [righty, ots*6]
        
        ###
        self.first_time = True
        self.players = {}
        k = 0
        
        for i in ['Q', 'W', 'E', 'R']:
            
            self.players.update({i : {'letter':Label(self.root, font = 'Ubuntu 18', text= i),
                               'name':Label(self.root, text = 'name '+i, font =font),
                               'elo':Label(self.root, text = 'elo '+i, font = font),
                               'gold':Label(self.root, text = 'gold '+i, font = font),
                               'pos':Label(self.root, text = 'pos '+i, font = font),
                               'spa':Label(self.root, text = 'spa '+i, font =font),
                               'cra':Label(self.root, text = 'cra '+i, font =font),
                               'life':Label(self.root, text= 'life '+i, font =font)
                              }
                       })
            self.players[i]['letter'].place(x=letter[0], y=letter[1]+next_per*k)
            self.players[i]['name'].place(x=name[0], y=name[1]+next_per*k)
            self.players[i]['elo'].place(x=elo[0], y=elo[1]+next_per*k)
            self.players[i]['gold'].place(x=gold[0], y=gold[1]+next_per*k)
            self.players[i]['pos'].place(x=pos[0], y=pos[1]+next_per*k)
            self.players[i]['spa'].place(x=spa[0], y=spa[1]+next_per*k)
            self.players[i]['cra'].place(x=cra[0], y=cra[1]+next_per*k)
            self.players[i]['life'].place(x=life[0], y=life[1]+next_per*k)
            
            for z in self.players[i].keys():
                self.players[i][z].configure(background=self.c['bd'])
                self.players[i][z].configure(foreground=self.c['nor_text'])
            k+=1
            
        
        self.items = []
    def write(self, size, mmap, pf):
        rebro = 20
        text_go = 8
        #get max and min pot fields
        potpot = []
        for i in pf:
            potpot+=i
        mmin = min(potpot)
        mmax = max(potpot)
        #
        #if it is our first write
  
        flag = False if len(self.items)==0 else True
        for y in range (size):
            for x in range(size):
                a = pf[y][x]
                to_max = abs(a-mmax)
                to_min = abs(a-mmin)
                    
                if (to_min+to_max) !=0:
                    abshun = to_min/(to_min+to_max)
                else: hun = 1
                if abshun<0.5:
                    hun = abshun*2
                    heh = hex(int(hun*255))[2:] if len(hex(int(hun*255))[2:])!=1 else '0'+hex(int(hun*255))[2:]
                    col='FF'+heh+'FF'
                else:
                    hun = 1 - (abshun-0.5)*2
                    heh = hex(int(hun*255))[2:] if len(hex(int(hun*255))[2:])!=1 else '0'+hex(int(hun*255))[2:]
                    col=heh+'FF'+heh
                if not flag:
                    self.items.append(self.can.create_rectangle(x*rebro, y*rebro, (x+1)*rebro, (y+1)*rebro, outline='#'+col,fill="#"+col))
                    self.items.append(self.can.create_text(x*rebro+text_go, y*rebro+text_go, text = mmap[y][x]))
                else:
                    self.can.itemconfig(self.items[2*y*size+2*x], outline = '#'+col, fill = '#'+col)
                    self.can.itemconfig(self.items[2*y*size+2*x+1], text=mmap[y][x])
        self.root.update()
    def info_change(self, data):
        perc = data['game']['turn']/data['game']['maxTurns']
        rer = round(35*perc)
        self.turn_num['text'] = 'Size: '+str(data['game']['board']['size'])+'   |'+'#'*rer+' '*(35-rer)+'| Turn'+str(data['game']['turn'])
        k =0 
        for pla in data['game']['heroes']:
            i = ['Q','W','E','R'][k]

            if self.first_time:
                
                self.players[i]['name']['text']=pla['name']
                if 'elo' in pla:
                    self.players[i]['elo']['text']=str(pla['elo'])
                else:
                    self.players[i]['elo']['text']=''
                self.players[i]['spa']['text'] = 'SPW xy: '+str(pla['spawnPos']['y'])+':'+str(pla['spawnPos']['x'])
            self.players[i]['gold']['text'] = 'Gold: '+str(pla['gold'])
            self.players[i]['pos']['text'] = 'POS xy: '+str(pla['pos']['y'])+':'+str(pla['pos']['x'])
            if pla['crashed']:
                self.players[i]['cra']['text'] = 'Crashed'
                self.players[i]['cra']['text'] = '#'
                self.players[i]['cra'].configure(foreground=self.c['red'])
            else:
                self.players[i]['cra']['text'] = 'Alive'
                self.players[i]['cra'].configure(foreground=self.c['nor_text'])
            perc = pla['life']/100
            rer = round(10*perc)
            #hp
            self.players[i]['life']['text'] = 'Life: '+str(pla['life'])+'  |'+'#'*rer+' '*(10-rer)+'|'
            if pla['life'] >50: self.players[i]['life'].configure(foreground=self.c['gre'])
            elif pla['life'] >25: self.players[i]['life'].configure(foreground=self.c['yel'])
            else:  self.players[i]['life'].configure(foreground=self.c['red'])            
            k+=1
        max_gold = max(data['game']['heroes'][0]['gold'], data['game']['heroes'][1]['gold'], data['game']['heroes'][2]['gold'], data['game']['heroes'][3]['gold'])
        for k in range(4):
            if data['game']['heroes'][k]['gold'] == max_gold:
                self.players[['Q','W','E','R'][k]]['letter'].configure(foreground=self.c['yel'])
            else:
                self.players[['Q','W','E','R'][k]]['letter'].configure(foreground=self.c['pl_usual'])
        #print(data['hero']['id'])
        self.players[['Q','W','E','R'][data['hero']['id'] -1]]['letter'].configure(foreground=self.c['pl_me'])
        self.first_time = False
        #self.tline['text']=text
