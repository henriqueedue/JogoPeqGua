import pygame
import sys
import time
import os
import math 

pygame.init()

# Tela
largura, altura = 800, 400
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Pequeno Guardião - Versão 1")

# ================= CLASSE GRANADA =================
class Granada:
    def __init__(self, x, y, direcao): 
        self.rect = pygame.Rect(x, y, 25, 25)
        self.vel_x = 7 * direcao 
        self.vel_y = -10
        self.gravidade = 0.5
        self.explodindo = False
        self.tempo_explosao = 0

    def atualizar(self):
        if not self.explodindo:
            self.vel_y += self.gravidade
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

# ================= FONTES PIXEL (RETRÔ) =================
fonte_titulo = pygame.font.SysFont("consolas", 32, bold=True)
fonte_menu   = pygame.font.SysFont("consolas", 22, bold=True)
fonte_peq    = pygame.font.SysFont("consolas", 16)

# ================= IMAGENS =================
def caminho_recurso(rel_path):
    try:
        base_path = sys._MEIPASS 
    except Exception:
        base_path = os.path.abspath("..")
    return os.path.join(base_path, rel_path)

def carregar_img(nome, tamanho):
    try:
        caminho = caminho_recurso(os.path.join("assets", nome))
        img = pygame.image.load(caminho)
        return pygame.transform.scale(img, tamanho)
    except:
        surf = pygame.Surface(tamanho)
        surf.fill((200, 0, 0))
        return surf
        
capa_img = carregar_img("capa1.png", (800, 400))
fundo = carregar_img("fundo.png", (800, 400))
player_img = carregar_img("player.png", (60, 60))
player_pulo_img = carregar_img("player_pu.png", (60, 60))
player_ag_img = carregar_img("player_ag.png", (60, 60))
player_granada_img = carregar_img("player_pu_granada.png", (60, 60))
inimigo_img = carregar_img("inimigo.png", (90, 90))
mag_inimigo = carregar_img("mag_1.png", (25, 25))
mag_player = carregar_img("mag_p_1.png", (30, 30))
grana_img = carregar_img("grana_1.png", (25, 25))
dano_grana_img = carregar_img("dano_granada.png", (50, 50))
laser_img = carregar_img("lay_1.png", (800, 320))
vida_img = carregar_img("v_1.png", (25, 25))
vida_perdida_img = carregar_img("v_-1.png", (25, 25))
raio_img = carregar_img("raio-.png", (40, 40))
pedra_img = carregar_img("pedra.png", (80, 60))

# ================= CHÃO =================
chao_mapa = []
for x in range(800):
    if x < 130: y = 380
    elif x < 160: y = 411 + (x - 179) * 0.8
    elif x < 240: y = 390
    elif x < 289: y = 423 - (x - 188) * 0.63
    elif x < 390: y = 355
    elif x < 423: y = 275 + (x - 181) * 0.4
    elif x < 669: y = 376
    elif x < 779: y = 388
    else: y = 405 - (x - 770) * 1.2
    chao_mapa.append(int(y))

# ================= ESTADOS DO JOGO =================
ESTADO_CAPA = -1
ESTADO_MENU = 0
ESTADO_TUTORIAL = 1
ESTADO_JOGANDO = 2
ESTADO_PAUSA = 3
ESTADO_FIM = 4 

estado = ESTADO_CAPA
tempo_inicio_capa = time.time()
resultado_texto = "" 

# ================= MENU =================
opcao_selecionada = 0
menu_principal = ["JOGAR", "TUTORIAL", "SAIR"]
menu_pausa = ["RETORNAR", "SAIR"]
menu_fim = ["JOGAR DE NOVO", "VOLTAR PRO MENU"] 

# ================= PLAYER =================
player = pygame.Rect(100, 100, 60, 60)
velocidade = 5
vel_y = 0
gravidade = 0.6
no_chao = False
vidas = 5
hits = 0
tempo_dano = 0
OFFSET_PE = 2
pulos = 0
MAX_PULOS = 2
granadas_estoque = 5
lista_granadas = []
jogando_granada = False
tempo_sprite_granada = 0
virado_direita = True
plataforma_atual = None
usos_raio = 0
MAX_USOS_RAIO = 3
dano_acumulado_raio = 0
raio_ativo = False
tempo_inicio_raio = 0 

# ================= NOVA PLATAFORMA MÓVEL =================
class PlataformaMovel:
    def __init__(self, x, y, largura, altura, limite_esq, limite_dir):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.vel_x = 2
        self.limite_esq = limite_esq
        self.limite_dir = limite_dir

    def atualizar(self):
        self.rect.x += self.vel_x
        if self.rect.right >= self.limite_dir or self.rect.left <= self.limite_esq:
            self.vel_x *= -1

# Cria a instância da plataforma móvel (pedra) no meio do mapa
pedra_plataforma = PlataformaMovel(largura//2 - 75, 200, 150, 40, 150, 650)

# ================= LASER =================
carregando_laser = False
tempo_inicio_laser = 0
laser_pronto = False
laser_ativo = False
tempo_laser = 0
arma_offset_x = 52
arma_offset_y = 32
laser_ja_deu_dano = False 

# ================= INIMIGO (LÓGICA NOVA) =================
inimigo = pygame.Rect(600, 215, 90, 90)
vidas_inimigo = 5
hits_inimigo = 0
vel_inimigo_x = 1.5
direcao_inimigo = 1
estado_inimigo = "NORMAL" 
tempo_troca_estado = time.time()
ja_deu_dano_investida = False

# ================= TIROS =================
tiros_player = [] 
tiros_inimigo = [] 
ultimo_tiro_player = 0
ultimo_tiro_inimigo = time.time()

clock = pygame.time.Clock()

def desenhar_texto_central(texto, fonte, cor, y):
    surf = fonte.render(texto, True, cor)
    tela.blit(surf, (largura//2 - surf.get_width()//2, y))

def mostrar_menu(opcoes, selecionado, fundo_img=None, titulo=None):
    if fundo_img:
        tela.blit(fundo_img, (0, 0))
        overlay = pygame.Surface((largura, altura))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        tela.blit(overlay, (0, 0))
    else:
        tela.fill((0,0,0))
    
    if titulo:
        desenhar_texto_central(titulo, fonte_titulo, (255, 255, 255), 100)

    for i, op in enumerate(opcoes):
        cor = (255, 255, 0) if i == selecionado else (255, 255, 255)
        seta = "> " if i == selecionado else "  "
        texto = fonte_menu.render(seta + op, True, cor)
        tela.blit(texto, (largura//2 - texto.get_width()//2, 200 + i*50))

def mostrar_tutorial():
    tela.fill((0,0,0))
    desenhar_texto_central("TUTORIAL - CONTROLES", fonte_titulo, (200, 255, 200), 40)
    instrucoes = [
        "SETA ↑ ................. Pular",
        "SETA ↓ ................. Abaixar",
        "SETA → / ← ......... Andar direita/esquerda",
        "ESPAÇO ................ Atirar",
        "SEGURAR 0 (1 seg) ... MEGA LASER (Tira 1 vida)",
        "PULAR + ESPAÇO ..... Jogar GRANADA (se tiver)",
        "TECLA 9 ............. SUPER RAIO (5s Tiro 10x rápido)",
        "PLATAFORMA .......... Pule na pedra para fugir",
        "",
        "Pressione ENTER ou ESC para voltar"
    ]
    for i, linha in enumerate(instrucoes):
        cor = (220, 220, 255) if i < 8 else (180, 180, 180)
        texto = fonte_peq.render(linha, True, cor)
        tela.blit(texto, (largura//2 - texto.get_width()//2, 110 + i*30))

def resetar_jogo():
    global vidas, vidas_inimigo, hits, hits_inimigo, granadas_estoque, lista_granadas
    global tiros_player, tiros_inimigo, player, inimigo, laser_ativo, laser_ja_deu_dano
    global dano_acumulado_raio, raio_ativo, tempo_inicio_raio, estado_inimigo, tempo_troca_estado
    global plataforma_atual, pedra_plataforma, usos_raio
    vidas, vidas_inimigo = 5, 5
    hits = hits_inimigo = 0
    granadas_estoque = 5
    lista_granadas.clear()
    tiros_player.clear()
    tiros_inimigo.clear()
    player.x, player.y = 100, 100
    inimigo.x = 600
    laser_ativo = False
    laser_ja_deu_dano = False
    dano_acumulado_raio = 0
    raio_ativo = False
    tempo_inicio_raio = 0
    usos_raio = 0 
    estado_inimigo = "NORMAL"
    tempo_troca_estado = time.time()
    plataforma_atual = None
    pedra_plataforma.rect.x = largura//2 - 75 

# ================= LOOP PRINCIPAL =================
while True:
    tempo_atual = time.time()
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if estado == ESTADO_CAPA:
                estado = ESTADO_MENU
            elif estado == ESTADO_TUTORIAL:
                if evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    estado = ESTADO_MENU
            elif estado in (ESTADO_MENU, ESTADO_PAUSA, ESTADO_FIM):
                menu_atual = menu_principal if estado == ESTADO_MENU else (menu_pausa if estado == ESTADO_PAUSA else menu_fim)
                if evento.key == pygame.K_UP:
                    opcao_selecionada = (opcao_selecionada - 1) % len(menu_atual)
                if evento.key == pygame.K_DOWN:
                    opcao_selecionada = (opcao_selecionada + 1) % len(menu_atual)
                if evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    escolha = menu_atual[opcao_selecionada]
                    if escolha in ("JOGAR", "RETORNAR", "JOGAR DE NOVO"):
                        resetar_jogo()
                        estado = ESTADO_JOGANDO
                        opcao_selecionada = 0
                    elif escolha == "TUTORIAL":
                        estado = ESTADO_TUTORIAL
                    elif escolha == "VOLTAR PRO MENU":
                        estado = ESTADO_MENU
                        opcao_selecionada = 0
                    elif escolha == "SAIR":
                        pygame.quit()
                        sys.exit()

            elif estado == ESTADO_JOGANDO:
                if evento.key == pygame.K_p:
                    estado = ESTADO_PAUSA
                    opcao_selecionada = 0
                if evento.key == pygame.K_UP and pulos < MAX_PULOS:
                    vel_y = -12
                    pulos += 1
                    plataforma_atual = None 
                if evento.key == pygame.K_0:
                    carregando_laser = True
                    tempo_inicio_laser = time.time()
                
                if (evento.key == pygame.K_9 
                    and dano_acumulado_raio >= 60 
                    and not raio_ativo 
                    and usos_raio < MAX_USOS_RAIO):
                    raio_ativo = True
                    tempo_inicio_raio = tempo_atual
                    dano_acumulado_raio = 0
                    usos_raio += 1
        if evento.type == pygame.KEYUP:
            if estado == ESTADO_JOGANDO and evento.key == pygame.K_0:
                carregando_laser = False
                if laser_pronto:
                    laser_ativo = True
                    laser_ja_deu_dano = False 
                    tempo_laser = time.time()
                    laser_pronto = False
    if estado == ESTADO_CAPA:
        tela.blit(capa_img, (0, 0))
        if tempo_atual - tempo_inicio_capa > 4:
            estado = ESTADO_MENU
    elif estado == ESTADO_MENU:
        mostrar_menu(menu_principal, opcao_selecionada, fundo_img=capa_img)

    elif estado == ESTADO_TUTORIAL:
        mostrar_tutorial()

    elif estado == ESTADO_PAUSA:
        mostrar_menu(menu_pausa, opcao_selecionada, fundo_img=fundo)

    elif estado == ESTADO_FIM:
        mostrar_menu(menu_fim, opcao_selecionada, fundo_img=fundo, titulo=resultado_texto)

    elif estado == ESTADO_JOGANDO:
        tela.blit(fundo, (0, 0))
        
        if vidas_inimigo <= 0 or vidas <= 0:
            resultado_texto = "VOCE VENCEU!" if vidas_inimigo <= 0 else "VOCE PERDEU!"
            estado = ESTADO_FIM
            opcao_selecionada = 0
            continue

        if raio_ativo:
            if tempo_atual - tempo_inicio_raio > 5:
                raio_ativo = False
            delay_tiro = 0.05
            tamanho_tiro = 50
            vel_tiro = 15
        else:
            delay_tiro = 0.4
            tamanho_tiro = 30
            vel_tiro = 10

        pedra_plataforma.atualizar()
        tela.blit(pedra_img, pedra_plataforma.rect)

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            player.x -= velocidade
            virado_direita = False
        if teclas[pygame.K_RIGHT]:
            player.x += velocidade
            virado_direita = True
        vel_y += gravidade
        player.y += vel_y
        no_chao = False
        pos_x = int(player.centerx)
        altura_chao_player = chao_mapa[max(0, min(799, pos_x))]
        if player.bottom >= altura_chao_player:
            player.bottom = altura_chao_player + OFFSET_PE
            vel_y, no_chao, pulos = 0, True, 0
            plataforma_atual = None
        if vel_y >= 0 and plataforma_atual is None: 
            if player.colliderect(pedra_plataforma.rect):
                
                if player.bottom <= pedra_plataforma.rect.top + 15:
                    plataforma_atual = pedra_plataforma
                    vel_y, no_chao, pulos = 0, True, 0
                    player.bottom = pedra_plataforma.rect.top + OFFSET_PE
        if plataforma_atual:
            player.x += plataforma_atual.vel_x
            player.bottom = plataforma_atual.rect.top + OFFSET_PE
            # Se andar para fora da plataforma, cair
            if not player.colliderect(pedra_plataforma.rect):
                plataforma_atual = None
        player.x = max(0, min(largura - player.width, player.x))

        # LÓGICA DO INIMIGO 
        if estado_inimigo == "NORMAL":
            inimigo.x += vel_inimigo_x * direcao_inimigo
            if inimigo.right >= largura or inimigo.left <= 0:
                direcao_inimigo *= -1
            if tempo_atual - ultimo_tiro_inimigo > 0.8:
                dx = player.centerx - inimigo.centerx
                dy = player.centery - inimigo.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    vx = (dx / dist) * 7
                    vy = (dy / dist) * 7
                    tiros_inimigo.append({'rect': pygame.Rect(inimigo.x, inimigo.y + 40, 25, 25), 'vx': vx, 'vy': vy})
                ultimo_tiro_inimigo = tempo_atual
            if tempo_atual - tempo_troca_estado > 7:
                estado_inimigo = "INVESTIDA"
                tempo_troca_estado = tempo_atual
                ja_deu_dano_investida = False

        elif estado_inimigo == "INVESTIDA":
            if inimigo.centerx < player.centerx:
                inimigo.x += 8
            elif inimigo.centerx > player.centerx:
                inimigo.x -= 8
            
            if inimigo.colliderect(player) and not ja_deu_dano_investida:
                if not plataforma_atual:
                    vidas -= 1
                    tempo_dano = tempo_atual
                    ja_deu_dano_investida = True
            
            if tempo_atual - tempo_troca_estado > 3:
                estado_inimigo = "NORMAL"
                tempo_troca_estado = tempo_atual

        inimigo.bottom = chao_mapa[max(0, min(799, int(inimigo.centerx)))]

        # --- TIROS E HABILIDADES DO PLAYER ---
        if teclas[pygame.K_SPACE] and tempo_atual - ultimo_tiro_player > delay_tiro:
            direcao_tiro = 1 if virado_direita else -1
            if not no_chao and granadas_estoque > 0:
                spawn_x = player.x + arma_offset_x if virado_direita else player.x
                lista_granadas.append(Granada(spawn_x, player.y, direcao_tiro))
                granadas_estoque -= 1
                jogando_granada = True
                tempo_sprite_granada = tempo_atual
            else:
                spawn_x = player.x + arma_offset_x if virado_direita else player.x
                tiros_player.append({'rect': pygame.Rect(spawn_x, player.y + arma_offset_y - 15, tamanho_tiro, tamanho_tiro), 'dir': direcao_tiro})
            ultimo_tiro_player = tempo_atual

        for g in lista_granadas[:]:
            g.atualizar()
            if not g.explodindo:
                if g.rect.colliderect(inimigo):
                    g.explodindo, g.tempo_explosao = True, tempo_atual
                    hits_inimigo += 2
                    dano_acumulado_raio += 2
                    if hits_inimigo >= 25: vidas_inimigo -= 1; hits_inimigo = 0
                elif g.rect.y > 400 or g.rect.x > 800 or g.rect.x < 0: lista_granadas.remove(g)
            elif tempo_atual - g.tempo_explosao > 0.3: lista_granadas.remove(g)

        if carregando_laser and tempo_atual - tempo_inicio_laser >= 1: laser_pronto = True
        if laser_ativo and tempo_atual - tempo_laser > 0.8: laser_ativo = False

        # Renderizar Player
        if jogando_granada and tempo_atual - tempo_sprite_granada < 0.3: img = player_granada_img
        elif teclas[pygame.K_DOWN]: img = player_ag_img
        elif not no_chao: img = player_pulo_img
        else: img = player_img

        if jogando_granada and tempo_atual - tempo_sprite_granada >= 0.3: jogando_granada = False
        if tempo_atual - tempo_dano < 0.5: img = pygame.transform.grayscale(img)

        img = pygame.transform.flip(img, not virado_direita, False)
        tela.blit(img, player)
        
        # Renderizar Inimigo
        tela.blit(inimigo_img, inimigo)

        # MEGA LASER
        if laser_ativo:
            lx = player.x + arma_offset_x if virado_direita else player.x - 800
            ly = player.y + arma_offset_y - 160
            img_laser_final = pygame.transform.flip(laser_img, not virado_direita, False)
            tela.blit(img_laser_final, (lx, ly))
            rect_laser = pygame.Rect(lx, ly, 800, 320)
            if rect_laser.colliderect(inimigo) and not laser_ja_deu_dano:
                vidas_inimigo -= 1
                hits_inimigo = 0
                dano_acumulado_raio += 25
                laser_ja_deu_dano = True

        # TIROS PLAYER
        for tiro in tiros_player[:]:
            tiro['rect'].x += vel_tiro * tiro['dir']
            tiro_img_scaled = pygame.transform.scale(mag_player, (tamanho_tiro, tamanho_tiro))
            tela.blit(tiro_img_scaled, tiro['rect'])
            
            if tiro['rect'].colliderect(inimigo):
                hits_inimigo += 1
                dano_acumulado_raio += 1
                if tiro in tiros_player: tiros_player.remove(tiro)
                if hits_inimigo >= 25: vidas_inimigo -= 1; hits_inimigo = 0
            elif tiro['rect'].x > largura or tiro['rect'].x < 0:
                if tiro in tiros_player: tiros_player.remove(tiro)

        for g in lista_granadas:
            tela.blit(dano_grana_img if g.explodindo else grana_img, g.rect)

        for tiro_data in tiros_inimigo[:]:
            tiro_rect = tiro_data['rect']
            tiro_rect.x += tiro_data['vx']
            tiro_rect.y += tiro_data['vy']
            tela.blit(mag_inimigo, tiro_rect)
            
            if tiro_rect.colliderect(player):
                hits += 1
                tiros_inimigo.remove(tiro_data)
                if hits >= 15: vidas -= 1; hits = 0; tempo_dano = tempo_atual
            elif tiro_rect.x < -50 or tiro_rect.x > largura + 50 or tiro_rect.y < -50 or tiro_rect.y > altura + 50:
                if tiro_data in tiros_inimigo: tiros_inimigo.remove(tiro_data)

        # INTERFACE
        for i in range(5):
            tela.blit(vida_img if i < vidas else vida_perdida_img, (10 + i*30, 10))
            tela.blit(vida_img if i < vidas_inimigo else vida_perdida_img, (650 + i*30, 10))
            if i < granadas_estoque: tela.blit(grana_img, (10 + i*30, 40))
        
        if dano_acumulado_raio >= 60 or raio_ativo:
            tela.blit(raio_img, (160, 10))
            if raio_ativo:
                tempo_restante = max(0, int(5 - (tempo_atual - tempo_inicio_raio)))
                txt_raio = fonte_peq.render(f"{tempo_restante}s (Usos:{usos_raio}/{MAX_USOS_RAIO})", True, (255,255,0))
                tela.blit(txt_raio, (205, 20))

    pygame.display.update()
    clock.tick(60)