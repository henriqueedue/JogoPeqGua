# 🎮 Little Guardian - Version 1

Little Guardian é um jogo 2D feito em Python com Pygame onde o jogador deve derrotar um monstro usando tiros, granadas e habilidades especiais. O jogo foi projetado com um nível um pouco mais difícil para aumentar o desafio e o interesse em derrotar o inimigo.

---

# 🕹️ Objetivo do Jogo
Derrotar o monstro principal que possui **5 vidas**.  
Cada ataque reduz a vida gradualmente até o inimigo ser eliminado.

O jogo termina quando:
- ✅ O jogador derrota o monstro (YOU WIN)
- ❌ O jogador perde todas as vidas (YOU LOSE)

---

# 🎮 Controles

| Tecla | Ação |
|------|------|
| ⬅️ ➡️ | Mover |
| ⬆️ | Pular (duplo pulo) |
| ⬇️ | Abaixar |
| SPACE | Atirar |
| Pular + SPACE | Jogar granada |
| Segurar 0 (1s) | Mega Laser |
| Tecla 9 | Super Ray |
| P | Pause |

---

# ⚔️ Sistema de Combate

### Tiros Normais
- Causam pouco dano
- 25 tiros = 1 vida do inimigo
- 125 tiros para derrotar o monstro

### Mega Laser (Tecla 0)
- Segure por 1 segundo
- Remove **1 vida inteira**
- Mais forte do jogo

### Granada
- Pode ser usada no ar
- Cada granada = 2 tiros normais

### Super Ray (Tecla 9)
- Ativa com 60 de carga
- Aumenta muito a velocidade de tiro
- Dura 5 segundos

---

# ❤️ Sistema de Vida

- Jogador possui 5 vidas
- Inimigo possui 5 vidas
- HUD mostra as vidas no topo da tela

---

# 🧠 Mecânicas do Jogo

- Duplo pulo
- Plataforma móvel
- Inimigo com dois comportamentos:
  - Ataque normal (tiros)
  - Investida (charge)
- Sistema de habilidades especiais
- Granadas com física
- Mega laser carregável
- Sistema de pausa
- Menu principal
- Tela de vitória e derrota

---

# 🎯 Dificuldade

O jogo foi propositalmente deixado **um pouco mais difícil** para aumentar o desafio e tornar a vitória mais interessante e recompensadora.

---

# ▶️ Como Executar

Instale o pygame:

```bash
pip install pygame
