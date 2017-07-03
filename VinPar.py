import json as mjson
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from threading import Thread
import random
from tkinter import *
from MapGui import *

import urllib.request
import urllib.parse

import io
from subprocess import Popen, PIPE, STDOUT

# constants        
inp = input('Enter for local server. Press "pi" for orange pi server')
if len(inp)==0: # my local vindinium server
    userkey = "e5kisehn" 
    train_url = 'http://localhost:9000/api/training'
    arena_url = 'http://localhost:9000/api/arena'
    api_url = 'http://localhost:9000/api/' # %userkey/%token/play
elif inp=='pi': # my local vindi server for orange pi player
    userkey = "e5kisehn"
    train_url = 'http://10.42.0.1:9000/api/training'
    arena_url = 'http://10.42.0.1:9000/api/arena'
    api_url = 'http://10.42.0.1:9000/api/' # %userkey/%token/play
else:
    userkey = 'INPUT YOUR VARIANT' # global server for my user
    train_url = 'http://vindinium.org/api/training'
    arena_url = 'http://vindinium.org/api/arena'
    api_url = 'http://vindinium.org/api/' # %userkey/%token/play
    
    
###
### Checked functions
###

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
    #generating emply potfield
    size = len(mapp)
    temp = [0]*size
    ans = []
    for i in range(size):
        ans.append(temp[:])
    return ans

def send_best_field(pfs, y,x, size, mmap):
    # choose the best side of the world
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
    #print('RURU', ans)
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
    #print(ans)
    #print(max(ans))
    #print(['Stay','North', 'South','West', 'East'])
    if ans.count(max(ans))==1:
        return ['Stay','North', 'South','West', 'East'][ans.index(max(ans))]
    else:
        maxes = []
        for i in range(5):
            if ans[i]==max(ans):
                maxes.append(['Stay','North', 'South','West', 'East'][i])
        #print('maxed', maxes)
        return random.choice(maxes)


def rerere(url, json, debug = True):
    ### send my answer. I know, i can use more laconic way, but this variant works more stable with my bad internet connection
    try:
        f = request = Request(url, urlencode(json).encode())
        ff = urlopen(request).read()
    except Exception as e:
        if debug:
            print('[X] Catched an error')
            print(url, json)
        return e, ''
    return 200, mjson.loads(ff.decode()) #json.loads(str(f.read().decode()))
    
###
### end
###

###
### Battle function
###

def start(is_train = True, use_tk = False, show_turns = False, debug = False, thread_count = 4, use_apostol = False):
    # thread count - count of AT_FIELD
    '''
    Деление на те, от скорости выполнения которых зависит результат (+) и иные (-)
    0(-) Подготавливаем количество процессов, равное количеству подсчетов
    1(-) Инициализуем gui
    2(-) turn = 0
    3( ) Посылаем запрос на участие
    4(+) Включаем таймер
    5(+) Переводим ответ в удобный вид
    6(+) Достаем постоянные игровой сессии:
          - size - размер карты
          - dan_places - места локации баз врагов. TODO - отталкивающее поле в зависимости от % 20 здоровья ее обладателя
          - uid и enid - собственный id и массив id врагов
          - мой токен и id игры
          - вывести страничку, с которой можно посмотреть игру
          - местоположение шахт и пива

    7( ) Цикл пока статус_код == 200:
        8(+) Достаем переменные :
              - наше прошлое положение
              - Своё положение, здоровье, золото, количество шахт за мной
              - Положение каждого из врагов, здоровье, золото, количество шахт
        9(++) Запускаем распалаллеленную задачу по вычислению потенциала 5 координат
       10(+) Суммируем 5 координат, находящихся прямо рядом с нами
       11(+) Выбираем лучший вариант
       12(+) Отправляем этот вариант
       13(-) Останавливаем таймер
       14(-) Рисуем обновленную карту, отмечаем, куда мы пошли
       15(-) turn+=1
       16( ) Спрашиваем сервер
       17(+) Запускаем таймер
       18(+) Строим удобную карту
    '''
    #0
    thread_pool = []
    for i in range(thread_count):
        thread_pool.append(Popen(['python3', 'VinSubprocess.py'], stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True))
    #1
    if use_tk:
        gtk = Gurren_Tk()
    #2
    turn = 0
    #3
    if is_train:
        r = rerere(train_url, json={"key": userkey})
    else:
        r = rerere(arena_url, json={"key": userkey})
    #4
    t = time.time()
    #5
    data = r[1]
    #print(data)
    mmap = data['game']['board']['tiles']
    mapcl = GameMap(data['game']['board'])
    #6
    #####
    size = data['game']['board']['size'] #-
    # Do not forgive x => y and y=>x
    dan_places = [
        [data['game']['heroes'][0]['spawnPos']['x'], data['game']['heroes'][0]['spawnPos']['y']],
        [data['game']['heroes'][1]['spawnPos']['x'], data['game']['heroes'][1]['spawnPos']['y']],
        [data['game']['heroes'][2]['spawnPos']['x'], data['game']['heroes'][2]['spawnPos']['y']],
        [data['game']['heroes'][3]['spawnPos']['x'], data['game']['heroes'][3]['spawnPos']['y']],
                 ]
    del dan_places[dan_places.index([data['hero']['spawnPos']['x'], data['hero']['spawnPos']['y']])]
    uid = str(data['hero']['id'])
    en_id = ['1', '2', '3', '4']
    del en_id[en_id.index(uid)]
    token = data['token']
    game_id = data['game']['id']
    print(data['viewUrl'])
    mines = []
    beer = []
    for y in range(size):
        for x in range(size):
            if mapcl.map[y][x] in '01234':
                mines.append([y,x])
            elif mapcl.map[y][x]=='t':
                beer.append([y,x])
    if debug:
        print('Получили игру, установили константы')
    ####
    #7
    while r[0] == 200:
        #8 - get vars
        lx, ly = x, y # предыдущие x и y
        x = data['hero']['pos']['y']
        y = data['hero']['pos']['x']
        gold = data['hero']['gold']
        hp = data['hero']['life']
        mine_count = data['hero']['mineCount']
        enemy1 = data['game']['heroes'][int(en_id[0])-1]
        enemy2 = data['game']['heroes'][int(en_id[1])-1]
        enemy3 = data['game']['heroes'][int(en_id[2])-1]
        global_vars = {'size':size, 'dan_places':dan_places, 'uid':uid, 'en_id':en_id, 'mines':mines, 'beer':beer,
                      'x':x, 'y':y, 'gold':gold, 'hp':hp, 'mine_count':mine_count, 
                       'enemy1':enemy1, 'enemy2':enemy2, 'enemy3':enemy3}
        #9, 10,11
        """
                9(++) Запускаем распалаллеленную задачу по вычислению потенциала 5 координат
                10(+) Суммируем 5 координат, находящихся прямо рядом с нами
                11(+) Выбираем лучший вариант
        """
        # правило для нейтральных и вражеских майнилок
        ##rule = [mmap, element, function, global_vars = {}, do_enhance=True, maxrange=-1]
        #rule1 = [mmap, ['0']+en_id, 'miner_fun', global_vars, False]
        #for thr in thread_pool:
        #    thr.stdin.write('AT_FIELD({}, {}, {}, {}, {})')
        #print('###')
        #  mmap, element, function, global_vars = {}, do_enhance=True, maxrange=-1
        
        #rint(mapcl.map, ['0']+en_id, 'miner_fun', False, global_vars)
        # SISTA ICHI - farms
        misaka1 = str({'mmap':mapcl.map, 
                       'element': ['0']+en_id, 
                       'do_enhance':False, 
                        'global_vars':global_vars,
                        'function':'miner_fun'})
        # SISTA NI - taverns
        misaka2 = str({'mmap':mapcl.map, 
                       'element': ['t'], 
                       'do_enhance':False,      
                       'global_vars':global_vars,  
                       'function':'beer_fun'})
        # SISTA SAN - onee-sama
        misaka3 = str({'mmap':mapcl.map, 'element':[{'1':'Q','2':'W','3':'E','4':'R'}[uid]], 
                                         'do_enhance':False, 'global_vars':global_vars,
                                         'function':'mount_fun'})
        # SISTA YON - Uragiri-san
        misaka4 = str({'mmap':mapcl.map, 'element' : [{'1':'Q','2':'W','3':'E','4':'R'}[en_id[0]],{'1':'Q','2':'W','3':'E','4':'R'}[en_id[1]],{'1':'Q','2':'W','3':'E','4':'R'}[en_id[2]]],
                                          'do_enhance':'enemy','global_vars':global_vars,  
                                          'function':'enemy_fun'})
        sisters = [misaka1, misaka2, misaka3, misaka4]
        for thr in range(len(thread_pool)):
            thread_pool[thr].stdin.write(sisters[thr]+'\n')
            thread_pool[thr].stdin.flush()
        hh = ''
        for thr in thread_pool:
            sisters_noice = thr.stdout.readline()[:-1]
            #print("sista's noice:", sisters_noice)
            #print('end')
            #print()
            #print()
            hh+= sisters_noice+', '
        #print(hh)
        accelerator = {}
        railgun = exec('task_hub=['+hh+']', accelerator)
        #print('araragi-sempai! :',accelerator)
        task_hub = accelerator['task_hub']

        
        #print('###')
        ###  task1 = AT_FIELD(mapcl.map, ['0']+en_id, miner_fun, do_enhance=False, global_vars=global_vars)
        # правило для баров
        ###  task2 = AT_FIELD(mapcl.map, ['t'], beer_fun, do_enhance=False, global_vars=global_vars)
        # отталкивающее поле на самом себе - чтобы не стоять на месте
        #task3 = AT_FIELD(mapcl.map, [{'1':'Q','2':'W','3':'E','4':'R'}[uid]], mount_fun, do_enhance=False, global_vars=global_vars)
        #task4 = AT_FIELD(mapcl.map, [{'1':'Q','2':'W','3':'E','4':'R'}[en_id[0]],
        #                             {'1':'Q','2':'W','3':'E','4':'R'}[en_id[1]],
        #                             {'1':'Q','2':'W','3':'E','4':'R'}[en_id[2]]], enemy_fun, do_enhance=False, global_vars=global_vars)
        
        #print(type(task1), type(task2), type(task3))
        #task_hub = [task1, task2, task3, task4]
        #print(task1)
        desu = send_best_field(task_hub, y, x, size, mapcl.map)
        if debug:
            print('desu:',desu)
        #desu = random.choice(['West'])
        #12
        # система аПОСТол обеспечивает нам возможность слегка подумать, пока мы решаем задачи
        apostol_status = []
        def aPOSTol(func, args, res):
            try:
                res.append(func(args[0], json = args[1]))
                res.append('DONE')
                res.append(time.time())
            except Exception as e:
                res.append(-1)
                res.append('ERROR')
                res.append(e)
        timer = time.time()-t
        if show_turns:
            print('Время полного круга: ', timer)
        dr = time.time()
        if use_apostol :
            thr = Thread(target=aPOSTol, args=(rerere, (api_url+game_id+'/'+token+'/play', {"key": userkey, "dir": desu}), apostol_status))
        
            thr.start()
        else:
            r = rerere(api_url+game_id+'/'+token+'/play', json={"key": userkey, "dir": desu})
        #13
        
        #14
        # Тут мы суммируем потенциальные поля, ибо это наше вакантное время
        def task_summator(size, maps):
            ans = []

            for y in range(size):
                ans+=[[]]
                for x in range(size):
                    ans[y]+=[[]]
                    ans[y][x]=0
                    for mm in maps:
                        if mm==False:
                            continue
                        try:
                            ans[y][x]+=mm[y][x]
                        except Exception as e:
                            print(mm[y][x])
                            print(e)
                            raise Error('asd')
            return ans
        if use_tk:
            gtk.info_change(data)
            gtk.write(size, mapcl.map, task_summator(size, task_hub))
            
        #16-17
        if use_apostol:
            thr.join()
        if show_turns:
            print('Время отправки:',time.time()-dr)
        #print()
        if use_apostol and apostol_status[-2] != 'DONE':
            print('ERROR')
            print(apostol_status[-1])
            return -1
        if use_apostol:
            t = apostol_status[2]
        else:
            t = time.time()
        #18
        if use_apostol : 
            r = apostol_status[0]
        else: 
            pass
        if r[0] != 200:
            print('Request code :', r[0])
            print('error type:', r[1])
            break
        data = r[1]
        if data['game']['finished']:
            print('Game Finished')
            break
        mmap = data['game']['board']['tiles']
        mapcl = GameMap(data['game']['board'])
        turn+=1
        if show_turns:
            print(turn)
    for pro in thread_pool:
        pro.kill()
    if use_tk:
        del gtk
    print('THE END')
        
        
    
###
###
###
