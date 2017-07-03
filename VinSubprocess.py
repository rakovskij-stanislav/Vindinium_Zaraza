import sys
import time
import random



class GameMap():
    # creates pretty nice map
    def __init__(self, raw_map):
        self.raw_map = raw_map;
        self.map = self._map_to_eye(self.raw_map)
    def _map_to_eye(self, board):
        tiles = board['tiles'][:]
        size = board['size']
        ans = []
        for i in range(size):
            ans.append(tiles[i*size*2:(i+1)*size*2].replace('##', '#').replace('  ', ' ').replace('$-', '0').replace(
                          '$1', '1').replace('$2', '2').replace('$3', '3').replace(
                          '$4', '4').replace('[]', 't').replace('@1', 'Q').replace(
                          '@2', 'W').replace('@3', 'E').replace('@4', 'R'))
        return ans
    
def potenfield(mapp):
    #генерирует нулевое потенциальное поле
    size = len(mapp)
    temp = [0]*size
    ans = []
    for i in range(size):
        ans.append(temp[:])
    return ans

def send_best_field(pfs, y,x, size, mmap):
    #print()
    # Выбирает наилучшее поле среди всех в зависимости от потенциального поля и стен
    ans = [0,0,0,0,0]#{'Stay':0.01, 'North':0.01, 'South':0.01,'West':0.01, 'East': 0.01}
    '''
    a = {'North': 0, 'West': 0, 'Stay': -1000, 'East': 580.0, 'South': 580.0}
   (max(a))
    WHY 'West'???!!! I USED TO LOVE YOU, PYTHON! Why do you love integers better than floats? 
    '''
    if x==0 or mmap[y][x-1]=='#':
        ans[3]=False
    if x==size-1 or mmap[y][x+1]=='#':
        ans[4]=False
    if y==0 or mmap[y-1][x]=='#':
        ans[1]=False
    if y==size-1 or mmap[y+1][x]=='#':
        ans[2]=False
    print('RURU', ans)
    for one in pfs:
        if one==False:
            #print('PYSTISHKA')
            continue
        ans[0]+=one[y][x]
        #WEST
        if type(ans[3])!=type(False):
            #print('w', one[y][x-1])
            ans[3]+= one[y][x-1]
        #EAST
        if type(ans[4])!=type(False):
            #print('e',  one[y][x+1])
            ans[4]+= one[y][x+1]
        #NORTH
        if type(ans[1])!=type(False):
            #print('n',  one[y-1][x])
            ans[1]+= one[y-1][x]
        #SOUTH
        if type(ans[2])!=type(False):
            #print('s',  one[y+1][x])
            ans[2]+= one[y+1][x]

        #print('ib', ans) 
    for i in range(5):
        if ans[i]!=False:
            ans[i]=round(ans[i])
    ret = 'Stay'
    print(ans)
    #print(max(ans))
    #print(['Stay','North', 'South','West', 'East'])
    if ans.count(max(ans))==1:
        return ['Stay','North', 'South','West', 'East'][ans.index(max(ans))]
    else:
        maxes = []
        for i in range(5):
            if ans[i]==max(ans):
                maxes.append(['Stay','North', 'South','West', 'East'][i])
        print('maxed', maxes)
        return random.choice(maxes)



###
### Функции принятия поля
###

def miner_fun(hm, glob, symbol = '0'):
    if glob['hp']-hm<22:
        return -100 if hm==0 else 0
    if hm==0:
        return 99
    return 65 + 30/hm

def beer_fun(hm, glob, symbol = 't'):
        if (glob['hp']>80) and hm==0:
            return -100
        if glob['hp']>70:
            return 0
        if glob['gold']<2 and hm==0:
            return 0
        if hm==0:
            return 200
        if glob['hp']<21:
           return 190 - 15*hm
        ans = 60 + 30/hm
        return ans

def mount_fun(hm, glob, symbol = '#'):
    if hm==0:
        return -30
    return 0

def enemy_fun(hm, glob, symbol):
    nn = {'Q':'1','W':'2','E':'3','R':'4'}[symbol]
    if glob['enemy1']['id'] == int(nn):
        profile = glob['enemy1']
    elif glob['enemy2']['id'] == int(nn):
        profile = glob['enemy2']
    elif glob['enemy3']['id'] == int(nn):
        profile = glob['enemy3']
    else:
        print('ERROR ENEMY FUN'*40)
    
    if (glob['hp']-profile['life']>-19) and profile['mineCount']>0 and hm==1:
        return 80
    if (glob['hp']-profile['life']>-19) and profile['mineCount']>0 and hm==0:
        return 100
    if (glob['hp']-profile['life']<22) and hm==2:
        return -100
    if (glob['hp']-profile['life']<22) and hm<5: 
        return -10+hm
    return 0
    

###
###
###


def AT_FIELD(mmap, element, function, global_vars = {}, do_enhance=True, maxrange=-1):
    # самый базовый способ работы с полями
    # дает потенциальные поля для определенного элемента судя по функции
    # element - массив объектов, на которых распростаняется это дело
    # function - задает зависимость определенной формулы от расстояния до объекта
    # global_vars - словарь, в котором содержится информация об игроках и состоянии игры, передается функции
    # do_sum - усилять ли поля
    #   False - не усилять - будет использоваться наибольшее значение полей
    #   'enemy' - берется наименьшее значение полей
    #   True - усилять. Формула усиления : максимальное_значение_поля*1.1**количество_полей_не_менее_50%_положительной_силы
    #   Такого усиления достаточно, чтобы игрока тянуло не к наиближайшему, а к наибольшему скоплению
    # maxrange - максимальное распространение поля. Актуально для полей, имеющих строго определенный радиус. Оптимизирует счет
    '''
    план
    1) ищем все элементы
    2) Для каждого отдельного элемента просчитываем распространение влияния в качестве массива
    3) Пилим do_enhance
    '''
    #print('gh')
    size = len(mmap)
    #1 +
    elembox = [] # y,x, own_field
    elemmap = [] # хранит значения всех потенциалов, которых добавлялись. "Ведь зачем нам делать отдельную карту для каждого, когда можно всё скинуть, так будет быстрее" - подумал Стас в процессе оптимизации
    for y in range(size):
        elemmap+=[[]]
        for x in range(size):
            elemmap[y]+=[[]]
            if mmap[y][x] in element:
                elembox.append([y,x])
    if len(elembox)==0:
        return False
    #2
    #print('arara2')
    def can_go(size, y,x, mmap):
        # оценивает клетку по возможности распространения сигнала
        if -1<y<size and -1<x<size:
            if mmap[y][x]not in '#01234QWERt':
                return True
        return False
    for unit in elembox:
        checked = [] # checked positions
        layer = [[unit[0], unit[1]], ] # позиции на этом слое
        templayer = []
        layer_num = 0
        #print('zaraza', layer)
        while len(layer)!=0:
            for one_sl in layer:
                y = one_sl[0]
                x = one_sl[1]
                # просчитываем влияние, заносим
                #print('LAYER', layer_num)
                elemmap[y][x].append(function(layer_num, global_vars, mmap[unit[0]][unit[1]]))
                #if y==x==1:
                #    print('ya', function(layer_num, global_vars), layer_num)
                #print(function(layer_num, global_vars))
                # добавляем новые точки
                if (can_go(size, y+1, x, mmap)) and ([y+1, x] not in templayer) and ([y+1, x] not in checked):
                    templayer.append([y+1, x])
                if (can_go(size, y-1, x, mmap)) and ([y-1, x] not in templayer) and ([y-1, x] not in checked):
                    templayer.append([y-1, x])
                if (can_go(size, y, x+1, mmap)) and ([y, x+1] not in templayer) and ([y, x+1] not in checked):
                    templayer.append([y, x+1])
                if (can_go(size, y, x-1, mmap)) and ([y, x-1] not in templayer) and ([y, x-1] not in checked):
                    templayer.append([y, x-1])
            # обеспечиваем новый цикл
            #print('layer num',layer_num,'\n layer', layer,'\n templayer',templayer)
            layer_num+=1
            if layer_num==maxrange:
                break
            checked+=layer
            layer = []
            layer+=templayer
            templayer = []
            #print('update  layer num',layer_num,'\n   layer', layer)
    # 3
    #print('arar3')
    #for unit in elembox:
    total_field = potenfield(mmap)
    #display(HTML(gurren_mappan(mmap, total_field)))
    #display(total_field)
    if do_enhance==True:
        for y in range(size):
            for x in range(size):
                if len(elemmap[y][x])==0:
                    total_field[y][x] = 0
                    continue
                mmax = max(elemmap[y][x])
                if mmax<0:
                    total_field[y][x]=mmax
                coo = 0
                for u in elemmap[y][x]:
                    if u>mmax//2 : #and u>0 - условие выполнится по дефолту
                        coo+=1
                total_field[y][x]=mmax*(1.1**(coo-1))
    elif do_enhance=='enemy':
        for y in range(size):
            for x in range(size):
                if len(elemmap[y][x])==0:
                    total_field[y][x] = 0
                    continue
                total_field[y][x]=min(elemmap[y][x])            
    else:
        for y in range(size):
            for x in range(size):
                if len(elemmap[y][x])==0:
                    total_field[y][x] = 0
                    continue
                total_field[y][x]=max(elemmap[y][x])
    #print('arar4', total_field)
    return total_field

###
###
###


while True:
    #sys.stdout.write('nya, masta!\n')
    #sys.stdout.flush()
    #sys.stdout.write('you said:'+sys.stdin.readline()+'\n')
    #sys.stdout.flush()
    take = sys.stdin.readline()
    exec('info = '+take)
    #sys.stdout.write('nya, masta!\n')

    exec("info['function'] ="+info['function'] )
    #sys.stdout.write('you sent (+f reb):'+str(info)+'\n')
    
    mmap = info['mmap']
    element = info['element']
    function = info['function']
    global_vars = {}
    do_enhance=True
    maxrange=-1
    if 'global_vars' in info:
        global_vars = info['global_vars']
    if 'do_enhance' in info:
        do_enhance = info['do_enhance']
    if 'maxrange' in info:
        maxrange = info['do_enhance']
    #print('doing...')
    #print('map', mmap)
    #print('element', element)
    
    
    ans = AT_FIELD(mmap, element, function, global_vars, do_enhance, maxrange)
    print(str(ans))
    #exec('ans = AT_FIELD(*info)')
    #sys.stdout.flush()
    #sys.stdout.write('you said:'+sys.stdin.readline()+'\n')
    sys.stdout.flush()
    

'''
while True:
    mission = input()
    print(exec(mission))'''
