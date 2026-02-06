import pygame, math, time, collections, random
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# --- ГЕОМЕТРИЯ КУБА ---
V = ((1,-1,-1), (1,1,-1), (-1,1,-1), (-1,-1,-1), (1,-1,1), (1,1,1), (-1,1,1), (-1,-1,1))
FACES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 4, 7, 3))

def create_star_sphere(count):
    s_list = glGenLists(1)
    glNewList(s_list, GL_COMPILE)
    glBegin(GL_POINTS)
    for _ in range(count):
        theta, phi = random.uniform(0, 6.28), math.acos(random.uniform(-1, 1))
        r = 110
        x, y, z = r*math.sin(phi)*math.cos(theta), r*math.sin(phi)*math.sin(theta), r*math.cos(phi)
        glColor3f(random.uniform(0.5, 0.9), random.uniform(0.6, 1.0), 1.0)
        glVertex3f(x, y, z)
    glEnd(); glEndList()
    return s_list

def create_wireframe_mountains(res, size):
    """Сетка гор в стиле Matrix/Wireframe"""
    m_list = glGenLists(1)
    glNewList(m_list, GL_COMPILE)
    glLineWidth(1)
    step = (size * 2) / res
    
    # Рисуем линии вдоль оси X
    for i in range(res + 1):
        glBegin(GL_LINE_STRIP)
        for j in range(res + 1):
            x = -size + i * step
            z = -size + j * step
            
            # Математический шум ландшафта
            h = math.sin(x * 0.1) * math.cos(z * 0.1) * 4.5
            h += math.sin(x * 0.3) * math.sin(z * 0.4) * 1.5
            
            # Плавное затухание к краям
            dist = math.sqrt(x*x + z*z)
            falloff = max(0, 1.0 - (dist / size)**2)
            h *= falloff
            h -= 8

            # Цвет: неоново-зеленый градиент по высоте
            c = (h + 10) / 10
            glColor3f(0.0, 0.4 + c*0.6, 0.1) 
            glVertex3f(x, h, z)
        glEnd()

    # Рисуем линии вдоль оси Z (для создания сетки)
    for j in range(res + 1):
        glBegin(GL_LINE_STRIP)
        for i in range(res + 1):
            x = -size + i * step
            z = -size + j * step
            h = (math.sin(x * 0.1) * math.cos(z * 0.1) * 4.5 + 
                 math.sin(x * 0.3) * math.sin(z * 0.4) * 1.5)
            h *= max(0, 1.0 - (math.sqrt(x*x + z*z) / size)**2)
            h -= 8
            
            c = (h + 10) / 10
            glColor3f(0.0, 0.3 + c*0.5, 0.05)
            glVertex3f(x, h, z)
        glEnd()
        
    glEndList()
    return m_list

def draw_cube(r, g, b, t):
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)
    glEnable(GL_CULL_FACE); glCullFace(GL_BACK); glFrontFace(GL_CCW)
    glRotatef(t * 70, 1, 0.5, 0.2) 
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glBegin(GL_QUADS)
    glColor3f(r, g, b)
    for f in FACES:
        for v in f: glVertex3fv(V[v])
    glEnd()
    glLineWidth(3); glColor3f(0, 0, 0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glEnable(GL_POLYGON_OFFSET_LINE); glPolygonOffset(-1.0, -1.1)
    glBegin(GL_QUADS)
    for f in FACES:
        for v in f: glVertex3fv(V[v])
    glEnd()
    glDisable(GL_POLYGON_OFFSET_LINE); glPolygonMode(GL_FRONT_AND_BACK, GL_FILL); glDisable(GL_CULL_FACE); glPopMatrix()

def main():
    pygame.init()
    pygame.display.set_mode((1000, 700), DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)
    
    gpu_info = glGetString(GL_RENDERER).decode().split()[0]
    clock = pygame.time.Clock()
    fps_log = collections.deque(maxlen=1000)
    
    limits = [30, 60, 120, 144, 240, 0]; l_idx = 1 
    scene_idx = 3 
    cam_mode = 'E' 
    scenes = ["VOID", "SEA", "MATRIX", "WIRE-HILLS"]
    
    STARS = create_star_sphere(1200)
    MTN_LIST = create_wireframe_mountains(50, 60)
    
    px, py, vx, vy = 0.0, 0.0, 6.0, 4.5
    limit_x, limit_y = 5.8, 4.1
    last_stat_update = 0

    while True:
        curr_lock = limits[l_idx]
        dt = clock.tick_busy_loop(curr_lock) / 1000.0 if curr_lock > 0 else clock.tick() / 1000.0
        t = time.time()
        
        for event in pygame.event.get():
            if event.type == QUIT: return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: return
                if event.key in [K_1, K_2, K_3, K_4]: scene_idx = int(event.unicode)-1
                if event.key == K_q: cam_mode = 'Q'
                if event.key == K_w: cam_mode = 'W'
                if event.key == K_e: cam_mode = 'E'
                if event.key == K_r: cam_mode = 'R'
                if event.key == K_UP: l_idx = (l_idx + 1) % len(limits)
                if event.key == K_DOWN: l_idx = (l_idx - 1) % len(limits)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(45, 1.42, 0.1, 350.0)

        # КАМЕРА
        if cam_mode == 'Q': glTranslatef(0, 0, -20)
        elif cam_mode == 'W': gluLookAt(40, 30, 40, 0, -5, 0, 0, 1, 0)
        elif cam_mode == 'E': gluLookAt(math.sin(t*0.3)*50, 25, math.cos(t*0.3)*50, 0, -5, 0, 0, 1, 0)
        elif cam_mode == 'R': gluLookAt(0, 10, 40, 0, 0, 0, 0, 1, 0)

        glCallList(STARS)

        # СЦЕНЫ
        if scene_idx == 0: # VOID
            px += vx * dt; py += vy * dt
            if abs(px) > limit_x: vx *= -1; px = limit_x if px > 0 else -limit_x
            if abs(py) > limit_y: vy *= -1; py = limit_y if py > 0 else -limit_y
            glPushMatrix(); glTranslatef(px, py, 0); draw_cube((math.sin(t)+1)/2, (math.sin(t+2)+1)/2, (math.sin(t+4)+1)/2, t); glPopMatrix()
        
        elif scene_idx == 1: # SEA
            glLineWidth(1); glBegin(GL_LINES)
            s = 2.5
            for i in range(-15, 16):
                for j in range(-15, 16):
                    x, z = i*s, j*s
                    y = math.sin(t*2.5 + x*0.3 + z*0.3) * 0.8 - 6
                    glColor3f(0.0, 0.5, 0.9)
                    if i < 15:
                        yn = math.sin(t*2.5 + (x+s)*0.3 + z*0.3) * 0.8 - 6
                        glVertex3f(x, y, z); glVertex3f(x+s, yn, z)
                    if j < 15:
                        yn = math.sin(t*2.5 + x*0.3 + (z+s)*0.3) * 0.8 - 6
                        glVertex3f(x, y, z); glVertex3f(x, yn, z+s)
            glEnd()
            glPushMatrix(); glTranslatef(0, math.sin(t*2.5)*1.2 + 2, 0); draw_cube((math.sin(t)+1)/2, (math.sin(t+2)+1)/2, (math.sin(t+4)+1)/2, t); glPopMatrix()

        elif scene_idx == 2: # MATRIX (СИНЕ-ФИОЛЕТОВЫЙ)
            glLineWidth(2); m = (t * 10) % 10
            glBegin(GL_LINES)
            for i in range(-55, 56, 5):
                alpha = max(0, 1.0 - abs(i)/55); mix = (i + 55) / 110 
                glColor3f(mix * 0.6 * alpha, (1-mix) * 0.3 * alpha, 0.9 * alpha)
                glVertex3f(i, -6, -55 + m); glVertex3f(i, -6, 55 + m)
                glVertex3f(-55, -6, i + m); glVertex3f(55, -6, i + m)
            glEnd()
            glPushMatrix(); glTranslatef(0, 2, 0); draw_cube((math.sin(t)+1)/2, (math.sin(t+2)+1)/2, (math.sin(t+4)+1)/2, t); glPopMatrix()

        elif scene_idx == 3: # WIREFRAME HILLS
            glCallList(MTN_LIST)
            glPushMatrix(); glTranslatef(0, 2 + math.sin(t)*0.5, 0); draw_cube((math.sin(t)+1)/2, (math.sin(t+2)+1)/2, (math.sin(t+4)+1)/2, t); glPopMatrix()

        # ТЕЛЕМЕТРИЯ
        if t - last_stat_update > 0.5:
            cfps = clock.get_fps()
            if cfps > 1: fps_log.append(cfps)
            sorted_f = sorted(list(fps_log)) if len(fps_log) > 100 else [0]*100
            l1 = sorted_f[int(len(sorted_f)*0.01)]
            pygame.display.set_caption(f"{scenes[scene_idx]} | {gpu_info} | FPS: {int(cfps)} | 1% Low: {int(l1)} | Lock: {curr_lock if curr_lock > 0 else 'INF'}")
            last_stat_update = t
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
