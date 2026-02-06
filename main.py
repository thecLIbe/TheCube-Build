import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math, time, collections

# --- ГЕОМЕТРИЯ КУБА ---
V = ((1,-1,-1), (1,1,-1), (-1,1,-1), (-1,-1,-1), (1,-1,1), (1,1,1), (-1,1,1), (-1,-1,1))
FACES = ((0,1,2,3), (4,5,6,7), (0,4,7,3), (1,5,6,2), (1,0,4,5), (2,3,7,6))
EDGES = ((0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7))

def draw_cube(r, g, b):
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    for f in FACES:
        for v in f: glVertex3fv(V[v])
    glEnd()
    glLineWidth(5)
    glColor3f(0, 0, 0)
    glBegin(GL_LINES)
    for e in EDGES:
        for v in e: glVertex3fv(V[v])
    glEnd()

def get_beautiful_mtn(res=25):
    grid = []
    for i in range(res):
        row = []
        for j in range(res):
            dist = math.sqrt((i-res/2)**2 + (j-res/2)**2)
            h = 0
            if dist > 6:
                h = (dist - 6) * 1.2 * (0.8 + 0.4 * math.sin(i*0.5) * math.cos(j*0.5))
            row.append(h - 5)
        grid.append(row)
    return grid

def main():
    pygame.init()
    pygame.display.set_mode((1000, 700), DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    gpu = glGetString(GL_RENDERER).decode().split()[0]
    clock = pygame.time.Clock()
    fps_log = collections.deque(maxlen=500)
    limits = [30, 60, 120, 144, 200, 240, 0]
    l_idx = 6 
    
    scene_idx = 1 
    scenes = ["VOID", "WAVY SEA", "NEON GRID", "FAR HILLS"]
    mtn = get_beautiful_mtn()
    px, py, vx, vy = 0.0, 0.0, 4.2, 3.2

    while True:
        t = time.time()
        lim = limits[l_idx]
        dt = clock.tick(lim) / 1000.0
        
        cfps = clock.get_fps()
        if cfps > 1: fps_log.append(cfps)
        
        sorted_f = sorted(list(fps_log))
        l1 = sorted_f[int(len(sorted_f)*0.01)] if len(sorted_f) > 100 else 0
        l01 = sorted_f[int(len(sorted_f)*0.001)] if len(sorted_f) > 100 else 0

        for event in pygame.event.get():
            if event.type == QUIT: return
            if event.type == KEYDOWN:
                if event.key == K_RIGHT: scene_idx = (scene_idx + 1) % 4
                if event.key == K_LEFT: scene_idx = (scene_idx - 1) % 4
                if event.key == K_UP: l_idx = (l_idx + 1) % len(limits)
                if event.key == K_DOWN: l_idx = (l_idx - 1) % len(limits)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, 1.42, 0.1, 150.0)
        
        # Камера
        if scene_idx == 0: 
            glTranslatef(0, 0, -15)
        else: 
            gluLookAt(math.sin(t*0.3)*25, 8, math.cos(t*0.3)*25, 0, 0, 0, 0, 1, 0)

        # --- ОТРИСОВКА ОКРУЖЕНИЙ ---
        if scene_idx == 1: # МОРЕ
            glLineWidth(1)
            glBegin(GL_LINES)
            glColor3f(0.0, 0.5, 0.8)
            for i in range(-20, 21):
                for j in range(-20, 20):
                    z1, z2 = j*2, (j+1)*2
                    x = i*2
                    y1 = math.sin(t*2 + x*0.2 + z1*0.3) * 0.4 - 5
                    y2 = math.sin(t*2 + x*0.2 + z2*0.3) * 0.4 - 5
                    glVertex3f(x, y1, z1); glVertex3f(x, y2, z2)
                    x1, x2 = i*2, (i+1)*2
                    z = j*2
                    y3 = math.sin(t*2 + x1*0.2 + z*0.3) * 0.4 - 5
                    y4 = math.sin(t*2 + x2*0.2 + z*0.3) * 0.4 - 5
                    glVertex3f(x1, y3, z); glVertex3f(x2, y4, z)
            glEnd()

        elif scene_idx == 2: # КИБЕР
            glLineWidth(2)
            glBegin(GL_LINES)
            m = (t * 8) % 10
            for i in range(-40, 41, 2):
                for j in range(-40, 40, 4):
                    grad = (j + 40) / 80.0
                    glColor3f(0.5 * grad, 0.2, 1.0 - 0.5 * grad)
                    glVertex3f(i, -4.5, j + m); glVertex3f(i, -4.5, j + 4 + m)
                    glVertex3f(j + m, -4.5, i); glVertex3f(j + 4 + m, -4.5, i)
            glEnd()

        elif scene_idx == 3: # ГОРЫ
            glLineWidth(1)
            glBegin(GL_LINES)
            for i in range(len(mtn) - 1):
                for j in range(len(mtn) - 1):
                    h = mtn[i][j]
                    if h > -4.9:
                        c = (h + 5) / 10.0
                        glColor3f(0.1, 0.3 + c, 0.1 + c*0.5)
                        glVertex3f(i*4-50, h, j*4-50); glVertex3f((i+1)*4-50, mtn[i+1][j], j*4-50)
                        glVertex3f(i*4-50, h, j*4-50); glVertex3f(i*4-50, mtn[i][j+1], (j+1)*4-50)
            glEnd()

        # --- КУБ (ОБЪЕДИНЕННАЯ ЛОГИКА) ---
        glPushMatrix()
        if scene_idx == 0:
            # Движение DVD
            px += vx * dt; py += vy * dt
            # Проверка границ с принудительным выталкиванием (px=6.5)
            if px > 6.5:  px = 6.5;  vx *= -1
            elif px < -6.5: px = -6.5; vx *= -1
            if py > 4.5:  py = 4.5;  vy *= -1
            elif py < -4.5: py = -4.5; vy *= -1
            glTranslatef(px, py, 0)
        else:
            # Парение в море/сетке
            glTranslatef(0, math.sin(t*2)*1.2 + 2, 0)
        
        # ВРАЩЕНИЕ — ВСЕГДА ПОСЛЕ ТРАНСЛЯЦИИ
        glRotatef(t * 80, 1, 1, 0)
        
        # РИСУЕМ
        r, g, b = (math.sin(t)+1)/2, (math.sin(t+2)+1)/2, (math.sin(t+4)+1)/2
        draw_cube(r, g, b)
        glPopMatrix()

        # --- ПАНЕЛЬ ---
        stats = f"FPS:{int(cfps)} | 1%:{int(l1)} | 0.1%:{int(l01)}"
        pygame.display.set_caption(f"{scenes[scene_idx]} | {gpu} | {stats} | LIM:{lim if lim > 0 else 'INF'}")
        pygame.display.flip()

if __name__ == "__main__":
    main()