import actors, pygame, math, random, datetime
from pygame.locals import *

class StateMachine:

    def __init__(self):
        self.end = False
        self.next = None
        self.quit = False
        self.previous = None

class Textos:

    white = (255,255,255)
    black = (0,0,0) 
    
    def __init__(self):
        pygame.init()          
        self.basic_font = pygame.font.Font('freesansbold.ttf',32)     
        self.small_font = pygame.font.Font('freesansbold.ttf',20)  

    def gameover(self,displaysurf):
        gameOverSurf = self.basic_font.render('Game Over',True,self.white)
        resetSurf = self.basic_font.render('Pressione ENTER para reiniciar',True,self.white)
        gameOverRect = gameOverSurf.get_rect()
        resetRect = resetSurf.get_rect()
        gameOverRect.center = (405,250)
        resetRect.center = (405,300)    
        displaysurf.blit(gameOverSurf,gameOverRect)             
        displaysurf.blit(resetSurf,resetRect)

    def pontuacao(self,pontuacao_txt,displaysurf): 
        pontuacaoSurf = self.small_font.render('PONTOS: ' + pontuacao_txt,True,self.white)
        pontuacaoRect = pontuacaoSurf.get_rect()
        pontuacaoRect.center = (70,20)
        displaysurf.blit(pontuacaoSurf,pontuacaoRect)

    def vidas(self,vidas_txt,displaysurf):
        vidasSurf = self.small_font.render('VIDAS: ' + vidas_txt,True,self.white)
        vidasRect = vidasSurf.get_rect()
        vidasRect.center = (740,20)
        displaysurf.blit(vidasSurf,vidasRect)

    def menu_txt(self,displaysurf):
        logoSurf = self.basic_font.render('BREAKOUT',True,self.white)
        enterSurf = self.basic_font.render('Press ENTER',True,self.white)
        scoreSurf = self.basic_font.render('Press SPACE for MAX SCORES',True,self.white)
        logoRect = logoSurf.get_rect()
        enterRect = enterSurf.get_rect()
        scoreRect = scoreSurf.get_rect()
        logoRect.center = (400,250)
        enterRect.center = (400,300)   
        scoreRect.center = (400,400)      
        displaysurf.blit(logoSurf,logoRect)
        displaysurf.blit(enterSurf,enterRect)
        displaysurf.blit(scoreSurf,scoreRect)

    def input_box(self,displaysurf,nome_jogador):
        text_box = pygame.Rect(205,380,50,30)
        textSurf = self.small_font.render(nome_jogador,True,self.black)  
        scoreSurf = self.small_font.render('Digite o nome para a pontuação máxima:',True,self.white)
        scoreRect = scoreSurf.get_rect()
        scoreRect.center = (405,350)
        width = max(200,textSurf.get_width()+10)
        text_box.w = width
        displaysurf.blit(scoreSurf,scoreRect)
        pygame.draw.rect(displaysurf,self.white,text_box,0)
        displaysurf.blit(textSurf,(text_box.x+5,text_box.y+5))

    def maxscore_title(self,displaysurf):
        scoreSurf = self.basic_font.render('Pontuações máximas [Press ENTER]',True,self.white)
        scoreRect = scoreSurf.get_rect()
        scoreRect.center = (400,50)
        displaysurf.blit(scoreSurf,scoreRect)

    def maxscore_menu(self,displaysurf,indice,x,y):
        texto = str(indice)
        scoreSurf = self.basic_font.render(texto,True,self.white)
        scoreRect = scoreSurf.get_rect()
        scoreRect.center = (x,y)
        displaysurf.blit(scoreSurf,scoreRect)

class ScoreMenu(StateMachine):
    
    black = (0,0,0) 
    file = None
    lista = []

    def __init__(self):
        StateMachine.__init__(self)
        self.next = 'menu'

    def startup(self):
        pass

    def cleanup(self):
        pass

    def handle_events(self,event):
        if event.type == KEYDOWN:
            if event.key == K_RETURN or event.key == K_KP_ENTER:
                self.end = True

    def update(self,displaysurf):
        t = Textos()
        displaysurf.fill(self.black)

        self.file = open ('max_scores','r')
        count = len(open('max_scores').readlines())
        for i in range(count):
            self.lista.append(self.file.readline())
        self.file.close()
      
        t.maxscore_title(displaysurf)
        y = 120
        for i in range(len(self.lista)):
            t.maxscore_menu(displaysurf,self.lista[i],400,y)
            y = y + 50
            if i == 9:
                break
    
class MainMenu(StateMachine):  

    black = (0,0,0) 

    def __init__(self):
        StateMachine.__init__(self)
    
    def startup(self):
        pass

    def cleanup(self):
        pass

    def handle_events(self,event):
        if event.type == KEYDOWN:
            if event.key == K_RETURN or event.key == K_KP_ENTER:
                self.next = 'fase1'
                self.end = True
            elif event.key == K_SPACE:
                self.next = 'score'
                self.end = True

    def update(self,displaysurf):
        t = Textos()

        displaysurf.fill(self.black)
        t.menu_txt(displaysurf)        

class MainGame(StateMachine):
   
    background = None
    game_over = False  
    black = (0,0,0) 

    jogador = None
    bolinha = None
    bloco = []

    total_blocos = 0 
    blocos_destruidos = 0 
    pontuacao_max = 0
    nome_jogador = ''
    file = None
    lista = []
    
    def __init__(self,**game_images):
        StateMachine.__init__(self)
        Textos.__init__(self)
        self.__dict__.update(game_images)
        self.som_colisao_jogador = pygame.mixer.Sound("assets/pin.wav")
        self.som_colisao_parede = pygame.mixer.Sound("assets/pon.wav")
        self.som_colisao_blocos = pygame.mixer.Sound("assets/pong.wav")
        self.som_perdeu = pygame.mixer.Sound("assets/dead.wav")                      

    def startup(self):      
        pass

    def cleanup(self):
        self.bloco.clear()
        self.jogador.pontuacao = 0
        self.jogador.vidas = 5
        self.bolinha.x = 400
        self.bolinha.y = 350
        self.nome_jogador = ''
        self.pontuacao_max = 0

        for i in range(self.total_blocos):
            self.bloco.append(actors.Blocks(1 + 90*(i%9),35 + 35*math.floor(i/9),self.cores_blocos[math.floor(i/9)]))

        self.game_over = False
        self.lista.clear()

    def handle_events(self,event):
        jogador = self.jogador

        if event.type == KEYDOWN:
            if self.game_over:
                if event.key == K_RETURN or event.key == K_KP_ENTER:
                    self.salvar_pontuacaomax() 
                    self.next = 'menu'                   
                    self.end = True
                if event.key == pygame.K_BACKSPACE:
                    self.nome_jogador = self.nome_jogador[:-1] 
                else:
                    self.nome_jogador += event.unicode             
            else:      
                if event.key == K_LEFT:
                    jogador.mover = -10
                elif event.key == K_RIGHT:
                    jogador.mover = 10
        elif event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_RIGHT:
                jogador.mover = 0
    
    def actors_update(self):
        jogador = self.jogador
        bolinha = self.bolinha
        bloco = self.bloco

        if bolinha.lost == True:
            jogador.vidas -= 1          
            self.som_perdeu.play()
            bolinha.lost = False

        if bolinha.wall == True:
            self.som_colisao_parede.play()
            bolinha.wall = False

        if jogador.teste_colisao(bolinha):
            bolinha.mover_y *= -1
            self.som_colisao_jogador.play()

        for i in range(self.total_blocos):
            if bloco[i].rect!=0 and bolinha.teste_colisao(bloco[i]):
                bloco[i].kill()
                jogador.pontuacao += 10
                bolinha.mover_y *= -1
                self.blocos_destruidos += 1
                self.som_colisao_blocos.play()

        jogador.movimento()

        if not self.game_over:
            bolinha.movimento()

    def actors_draw(self,displaysurf):
        jogador = self.jogador
        bolinha = self.bolinha
        bloco = self.bloco

        jogador.desenhar(displaysurf)
        bolinha.desenhar(displaysurf)

        for i in range(self.total_blocos):
            if(bloco[i].image!=0):
                bloco[i].desenhar(displaysurf)         

    def update(self,displaysurf):  
        pass 
        
    def salvar_pontuacaomax(self):

        self.file = open ('max_scores','r')
        count = len(open('max_scores').readlines())
        for i in range(count):
            self.lista.append(self.file.readline())
        self.file.close()

        self.lista.pop(9)
        self.lista.insert(0,self.nome_jogador + " " + str(self.pontuacao_max) + "\n")

        self.file = open ('max_scores','w')
        for i in range(len(self.lista)):
            self.file.write(self.lista[i])
        self.file.close()       

class FaseI(MainGame):

    def __init__(self,**game_images):
        super().__init__(**game_images)
        self.total_blocos = 45

    def startup(self):
        random.seed(datetime.time())
        self.jogador = actors.Paddle(340,600,self.player_image)
        self.bolinha = actors.Ball(random.randint(300,600),random.randint(250,400),self.ball_image)

        for i in range(self.total_blocos):
            self.bloco.append(actors.Blocks(1 + 90*(i%9),35 + 35*math.floor(i/9),self.cores_blocos[math.floor(i/9)]))

    def update(self,displaysurf):
        t = Textos()

        pontuacao_txt = str(self.jogador.pontuacao) 
        vidas_txt = str(self.jogador.vidas)
   
        displaysurf.fill(self.black) 
        t.pontuacao(pontuacao_txt,displaysurf)
        t.vidas(vidas_txt,displaysurf)

        if self.jogador.vidas <= 0:
            self.pontuacao_max = self.jogador.pontuacao  
            self.game_over = True          
            t.gameover(displaysurf)
            t.input_box(displaysurf,self.nome_jogador)  

        if self.blocos_destruidos == self.total_blocos:     
            self.next = 'fase2'
            self.end = True             

        self.actors_update()
        self.actors_draw(displaysurf)  

class FaseII(MainGame):

    def __init__(self,**game_images):
        super().__init__(**game_images)
        self.total_blocos = 54 

    def startup(self):
        random.seed(datetime.time())
        self.jogador = actors.Paddle(340,600,self.player_image)
        self.bolinha = actors.Ball(random.randint(300,600),random.randint(250,400),self.ball_image)

        for i in range(self.total_blocos):
            self.bloco.append(actors.Blocks(1 + 90*(i%9),35 + 35*math.floor(i/9),self.cores_blocos[math.floor(i/9)%6]))

    def update(self,displaysurf):
        t = Textos()

        pontuacao_txt = str(self.jogador.pontuacao) 
        vidas_txt = str(self.jogador.vidas)
   
        displaysurf.fill(self.black) 
        t.pontuacao(pontuacao_txt,displaysurf)
        t.vidas(vidas_txt,displaysurf)

        if self.jogador.vidas <= 0:
            self.pontuacao_max = self.jogador.pontuacao  
            self.game_over = True          
            t.gameover(displaysurf)
            t.input_box(displaysurf,self.nome_jogador)  

        if self.blocos_destruidos == self.total_blocos:        
            self.next = 'fase3'
            self.end = True             

        self.actors_update()
        self.actors_draw(displaysurf)  

class FaseIII(MainGame):

    def __init__(self,**game_images):
        super().__init__(**game_images)
        self.total_blocos = 63 

    def startup(self):
        random.seed(datetime.time())
        self.jogador = actors.Paddle(340,600,self.player_image)
        self.bolinha = actors.Ball(random.randint(300,600),random.randint(250,400),self.ball_image)

        for i in range(self.total_blocos):
            self.bloco.append(actors.Blocks(1 + 90*(i%9),35 + 35*math.floor(i/9),self.cores_blocos[math.floor(i/9)%7]))

    def update(self,displaysurf):
        t = Textos()

        pontuacao_txt = str(self.jogador.pontuacao) 
        vidas_txt = str(self.jogador.vidas)
   
        displaysurf.fill(self.black) 
        t.pontuacao(pontuacao_txt,displaysurf)
        t.vidas(vidas_txt,displaysurf)

        if self.jogador.vidas <= 0:
            self.pontuacao_max = self.jogador.pontuacao  
            self.game_over = True          
            t.gameover(displaysurf)
            t.input_box(displaysurf,self.nome_jogador)  

        if self.blocos_destruidos == self.total_blocos:        
            self.next = 'fase4'
            self.end = True             

        self.actors_update()
        self.actors_draw(displaysurf)  

class FaseIV(MainGame):
    
    def __init__(self,**game_images):
        super().__init__(**game_images)
        self.total_blocos = 72 

    def startup(self):
        random.seed(datetime.time())
        self.jogador = actors.Paddle(340,600,self.player_image)
        self.bolinha = actors.Ball(random.randint(300,600),random.randint(250,400),self.ball_image)

        for i in range(self.total_blocos):
            self.bloco.append(actors.Blocks(1 + 90*(i%9),35 + 35*math.floor(i/9),self.cores_blocos[math.floor(i/9)%8]))

    def update(self,displaysurf):
        t = Textos()

        pontuacao_txt = str(self.jogador.pontuacao) 
        vidas_txt = str(self.jogador.vidas)
   
        displaysurf.fill(self.black) 
        t.pontuacao(pontuacao_txt,displaysurf)
        t.vidas(vidas_txt,displaysurf)

        if (self.jogador.vidas <= 0) or (self.blocos_destruidos == self.total_blocos):
            self.pontuacao_max = self.jogador.pontuacao  
            self.game_over = True          
            t.gameover(displaysurf)
            t.input_box(displaysurf,self.nome_jogador)           

        self.actors_update()
        self.actors_draw(displaysurf)  

class BreakoutGame:

    state_dictionary = None
    state_name = None
    state = None

    def __init__(self,**settings):      
        self.__dict__.update(settings)
        self.end = False  
        pygame.display.set_caption("Breakout")   
        self.displaysurf = pygame.display.set_mode(self.size)
        self.fpsclock = pygame.time.Clock()            

    def setup_states(self,state_dictionary,start_state):
        self.state_dictionary = state_dictionary
        self.state_name = start_state
        self.state = self.state_dictionary[self.state_name]
        self.state.startup()

    def flip_state(self):
        self.state.end = False
        previous,self.state_name = self.state_name,self.state.next
        self.state.cleanup()
        self.state = self.state_dictionary[self.state_name]
        self.state.startup()
        self.state.previous = previous

    def update(self):
        if self.state.quit:
            self.end = True
        elif self.state.end:
            self.flip_state()

        self.state.update(self.displaysurf)

    def event_loop(self):

        for event in pygame.event.get():
            if event.type == QUIT:
                self.end = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.end = True
            self.state.handle_events(event)

    def loop(self):

        while not self.end:
            self.event_loop()
            self.update()

            pygame.display.flip()
            pygame.display.update()
            self.fpsclock.tick(self.fps)
            
def main():   
    settings = {
        'size' : (800,650),
        'fps' : 30           
    }

    game_images = {
        'ball_image' : "assets/ball.png",
        'player_image' : "assets/paddle.png",        
        'cores_blocos' : ["assets/barrinha1.png","assets/barrinha2.png","assets/barrinha3.png",
        "assets/barrinha4.png","assets/barrinha5.png","assets/barrinha6.png","assets/barrinha7.png",
        "assets/barrinha8.png"]    
    }

    dicionario_estados = {
        #'game' : MainGame(**game_images),
        'menu' : MainMenu(),     
        'score' : ScoreMenu(),
        'fase1' : FaseI(**game_images),
        'fase2' : FaseII(**game_images),
        'fase3' : FaseIII(**game_images),
        'fase4' : FaseIV(**game_images)
    }

    main_game = BreakoutGame(**settings)
    main_game.setup_states(dicionario_estados,'menu')
    main_game.loop()

## MAIN ##
if __name__ == '__main__':
    main()
