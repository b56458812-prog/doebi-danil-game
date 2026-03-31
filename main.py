import pygame
import random
import time
import os

# Инициализация
pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = (info.current_w, info.current_h)
if WIDTH < HEIGHT: WIDTH, HEIGHT = HEIGHT, WIDTH

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Цвета
WHITE, RED, YELLOW, BLACK = (255, 255, 255), (220, 20, 60), (255, 215, 0), (0, 0, 0)
GREEN, BLUE, GOLD, DARK_PURPLE = (50, 205, 50), (30, 144, 255), (255, 223, 0), (25, 5, 45)

# Шрифты
font_status = pygame.font.SysFont("Verdana", 85, bold=True)
font_ui = pygame.font.SysFont("Verdana", 45, bold=True)
font_btn = pygame.font.SysFont("Verdana", 35, bold=True)

def draw_text(text, font, color, pos, center=False):
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()
    if center: rect.center = pos
    else: rect.topleft = pos
    screen.blit(surf, rect)

def load_res(name, size, fallback=(100, 100, 100)):
    try:
        img = pygame.image.load(name).convert()
        return pygame.transform.scale(img, size)
    except:
        s = pygame.Surface(size); s.fill(fallback); return s

# Загрузка ресурсов
img_menu_bg = load_res("1000061731.jpg", (WIDTH, HEIGHT))
img_back = load_res("danil_back.jpg", (WIDTH, HEIGHT))
img_think = load_res("danil_think.jpg", (WIDTH, HEIGHT))
img_angry = load_res("danil_angry.jpg", (WIDTH, HEIGHT))
img_smile = load_res("danil_smile.jpg", (WIDTH, HEIGHT))
img_clouds = load_res("clouds.png", (WIDTH, HEIGHT), (200, 200, 200))

SKIN_SIZE = (180, 180)
cat_grey_img = load_res("1000061764.jpg", SKIN_SIZE) 
cat_big_img = load_res("cat_big.png", SKIN_SIZE)
cat_lox_img = load_res("1000061765.jpg", SKIN_SIZE) 
leg_skin_img = load_res("knopka.png", SKIN_SIZE)

# Ректы (Кнопки)
play_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 130, 300, 80)
shop_rect_menu = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 30, 300, 80)
casino_rect_menu = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 70, 300, 80)
exit_rect = pygame.Rect(40, HEIGHT - 110, 200, 80)
shop_exit_rect = pygame.Rect(WIDTH - 240, HEIGHT - 110, 200, 80)
casino_spin_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 120, 300, 80)

btn_center = (WIDTH - 180, HEIGHT // 2)
btn_radius = 110

# Сохранение данных
def save_data(c, o, curr):
    with open("save.txt", "w") as f: f.write(f"{c}\n{','.join(map(str, o))}\n{curr}")

def load_data():
    if os.path.exists("save.txt"):
        try:
            with open("save.txt", "r") as f:
                ls = f.readlines()
                return int(ls[0].strip()), [int(x) for x in ls[1].strip().split(',')], int(ls[2].strip())
        except: pass
    return 0, [0], 0

coins, owned_cats, current_skin = load_data()
trans_y, trans_state, target_scr = HEIGHT, "none", "menu"

def draw_button(is_calling, game_over):
    pygame.draw.circle(screen, WHITE, btn_center, btn_radius + 10)
    img = {1:cat_grey_img, 2:cat_big_img, 3:cat_lox_img, 4:leg_skin_img}.get(current_skin)
    if not img:
        c = RED if not is_calling else (160, 0, 0)
        pygame.draw.circle(screen, c, btn_center, btn_radius)
        draw_text("ДОЕБАТЬ" if not game_over else "RETRY", font_btn, WHITE, btn_center, center=True)
    else:
        temp = pygame.Surface(SKIN_SIZE, pygame.SRCALPHA)
        pygame.draw.circle(temp, (255, 255, 255), (90, 90), 90)
        temp.blit(img, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(temp, (btn_center[0]-90, btn_center[1]-90))
        if current_skin == 4: pygame.draw.circle(screen, GOLD, btn_center, btn_radius, 10)

def main():
    global coins, owned_cats, current_skin, trans_y, trans_state, target_scr
    score, is_calling, game_over, waiting = 0, False, False, False
    game_running, shop_open, casino_open = False, False, False
    current_img = img_back
    status, status_color = "ДОЕБИ ДАНИЛА!", WHITE
    next_event, reaction_limit, smile_timer = 0, 0, 0
    current_bonus, is_spinning, spin_end, casino_res = 0, False, 0, ""
    
    clock = pygame.time.Clock()

    while True:
        now = time.time()
        screen.blit(current_img if game_running else img_menu_bg, (0, 0))

        if not game_running and not shop_open and not casino_open:
            draw_text("ДОЕБИ ДАНИЛА v0.2", font_status, WHITE, (WIDTH//2, 100), center=True)
            for r, t, c in [(play_rect, "ДОЕБАТЬ", RED), (shop_rect_menu, "МАГАЗИН", BLUE), (casino_rect_menu, "КАЗИНО", GREEN)]:
                pygame.draw.rect(screen, c, r, border_radius=20); draw_text(t, font_btn, WHITE, r.center, center=True)
            draw_text(f"Монеты: {coins}", font_ui, GOLD, (60, 60))

        elif game_running:
            draw_text(f"Очки: {score}", font_ui, YELLOW, (60, 60))
            if is_calling and not game_over and not waiting:
                draw_text(f"+{int(current_bonus)}", font_btn, GREEN, (btn_center[0], btn_center[1]-150), center=True)
            
            # ФИКС СТАТУСА ПРИ СМЕРТИ
            if game_over:
                draw_text("ОТХУЯРИЛ!", font_status, RED, (WIDTH//2, 100), center=True)
            else:
                draw_text(status, font_status, status_color, (WIDTH//2, 100), center=True)
                
            pygame.draw.rect(screen, BLACK, exit_rect, border_radius=20); draw_text("В МЕНЮ", font_btn, WHITE, exit_rect.center, center=True)
            draw_button(is_calling, game_over)

        elif shop_open:
            screen.fill(BLACK)
            pygame.draw.rect(screen, RED, shop_exit_rect, border_radius=20); draw_text("ВЫЙТИ", font_btn, WHITE, shop_exit_rect.center, center=True)
            for i, (img, name) in enumerate([(cat_grey_img, "Серый (15)"), (cat_big_img, "Большой (20)"), (cat_lox_img, "Хуйня (15)"), (leg_skin_img, "ЛЕГЕНДА")]):
                if i == 3 and 4 not in owned_cats: continue 
                y = 30 + i * (HEIGHT // 4.5)
                if current_skin == (i+1): pygame.draw.rect(screen, (0, 100, 255), (WIDTH//2-310, y-5, 620, 185), border_radius=15)
                screen.blit(img, (WIDTH//2 - 250, y)); draw_text(name, font_ui, WHITE, (WIDTH//2, y + 60))

        elif casino_open:
            screen.fill(DARK_PURPLE); draw_text("КАЗИНО", font_status, GOLD, (WIDTH//2, 100), center=True)
            pygame.draw.rect(screen, GREEN, casino_spin_rect, border_radius=20); draw_text("КРУТИТЬ (10)", font_btn, WHITE, casino_spin_rect.center, center=True)
            pygame.draw.rect(screen, RED, exit_rect, border_radius=20); draw_text("В МЕНЮ", font_btn, WHITE, exit_rect.center, center=True)
            if is_spinning:
                draw_text(random.choice(["X100", "777", "WIN"]), font_status, YELLOW, (WIDTH//2, HEIGHT//2), center=True)
                if now > spin_end:
                    is_spinning, r = False, random.random()
                    if r < 0.10: casino_res = "ЛЕГЕНДАРКА!"; owned_cats.append(4) if 4 not in owned_cats else None
                    elif r < 0.30: casino_res = "+20 МОНЕТ"; coins += 20
                    elif r < 0.90: casino_res = "+8 МОНЕТ"; coins += 8
                    else: casino_res = "+1 МОНЕТА"; coins += 1
                    save_data(coins, owned_cats, current_skin)
            elif casino_res: draw_text(casino_res, font_ui, GOLD, (WIDTH//2, HEIGHT//2), center=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN and trans_state == "none":
                if not game_running and not shop_open and not casino_open:
                    if play_rect.collidepoint(event.pos): trans_state, target_scr = "covering", "game"
                    elif shop_rect_menu.collidepoint(event.pos): shop_open = True
                    elif casino_rect_menu.collidepoint(event.pos): casino_open = True
                elif shop_open:
                    if shop_exit_rect.collidepoint(event.pos): shop_open = False
                    else:
                        for i in range(4):
                            if pygame.Rect(WIDTH//2-310, 30+i*(HEIGHT//4.5), 620, 185).collidepoint(event.pos):
                                idx = i+1; pr = {1:15, 2:20, 3:15, 4:0}[idx]
                                if idx in owned_cats: current_skin = idx
                                elif coins >= pr: coins -= pr; owned_cats.append(idx); current_skin = idx
                                save_data(coins, owned_cats, current_skin)
                elif casino_open:
                    if exit_rect.collidepoint(event.pos): casino_open = False
                    elif casino_spin_rect.collidepoint(event.pos) and not is_spinning and coins >= 10:
                        coins -= 10; is_spinning, spin_end, casino_res = True, now + 1.2, ""
                elif game_running:
                    if exit_rect.collidepoint(event.pos): trans_state, target_scr = "covering", "menu"
                    dist = ((event.pos[0]-btn_center[0])**2 + (event.pos[1]-btn_center[1])**2)**0.5
                    if dist <= btn_radius:
                        if game_over: 
                            score, game_over, current_img, status, status_color = 0, False, img_back, "ДОЕБИ ДАНИЛА!", WHITE
                            next_event = 0
                        elif not waiting: 
                            is_calling, current_bonus = True, 0
                            status, status_color = "ДОЕБЫВАЕШЬ...", WHITE
            
            if event.type == pygame.MOUSEBUTTONUP and game_running:
                if is_calling:
                    if waiting:
                        score += int(current_bonus); coins += int(current_bonus // 10)
                        save_data(coins, owned_cats, current_skin)
                        current_img, status, status_color, smile_timer = img_smile, "УСПЕЛ!", GREEN, now + 0.5
                        waiting, next_event = False, 0
                    elif not game_over:
                        score += int(current_bonus); coins += int(current_bonus // 10)
                        status, status_color = "ДОЕБИ ДАНИЛА!", WHITE
                    is_calling = False

        if game_running and not game_over:
            if is_calling and not waiting:
                current_bonus += 0.4
                if next_event == 0: next_event = now + random.uniform(0.7, 1.8)
                if now > next_event:
                    waiting, current_img = True, img_think
                    status, status_color, reaction_limit = "РЫПНУЛСЯ!", YELLOW, now + 0.25 # ЧЕСТНЫЙ ТАЙМИНГ

            if waiting and is_calling:
                if now > reaction_limit:
                    game_over, current_img = True, img_angry
                    waiting = False
            elif waiting and not is_calling:
                waiting, next_event = False, 0

            if not is_calling and not waiting and current_img == img_smile and now > smile_timer:
                current_img, status, status_color = img_back, "ДОЕБИ ДАНИЛА!", WHITE

        # Анимация облаков
        if trans_state == "covering":
            trans_y -= 115
            screen.blit(img_clouds, (0, trans_y))
            if trans_y <= 0:
                trans_y, trans_state = 0, "revealing"
                game_running = (target_scr == "game"); score = 0; game_over = False; current_img = img_back
                shop_open = casino_open = False
        elif trans_state == "revealing":
            trans_y -= 115
            screen.blit(img_clouds, (0, trans_y))
            if trans_y <= -HEIGHT: trans_y, trans_state = HEIGHT, "none"

        pygame.display.flip(); clock.tick(60)

if __name__ == "__main__":
    main()

