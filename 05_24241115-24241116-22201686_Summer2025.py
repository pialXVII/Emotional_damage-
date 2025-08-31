from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, random, sys


# Window or World

WIN_W, WIN_H = 1000, 800
FOVY = 120.0

# Round arena size
ARENA_R   = 600.0                    # ground disk radius 
WALL_H    = 120.0                    # wall height visible
WALL_THK  = 18.0                     # wall thickness
WALL_IN   = ARENA_R - 2.0            # inner wall radius
WALL_OUT  = ARENA_R + WALL_THK       # outer wall radius
PLAY_R    = WALL_IN - 10.0           # playable inner radius for player/bullets
ENEMY_RIM = WALL_IN                  # enemies/ bullets clamp against inner wall

# Close button 

BTN_W, BTN_H = 44, 32
BTN_MARGIN   = 10
_close_btn_rect = (WIN_W - BTN_W - BTN_MARGIN, WIN_H - BTN_H - BTN_MARGIN, BTN_W, BTN_H)

def draw_close_button():
    global _close_btn_rect
    x0 = WIN_W - BTN_W - BTN_MARGIN
    y0 = WIN_H - BTN_H - BTN_MARGIN
    _close_btn_rect = (x0, y0, BTN_W, BTN_H)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glColor3f(0.8, 0.1, 0.1)
    glBegin(GL_QUADS)
    glVertex2f(x0, y0); glVertex2f(x0+BTN_W, y0); glVertex2f(x0+BTN_W, y0+BTN_H); glVertex2f(x0, y0+BTN_H)
    glEnd()
    glColor3f(1,1,1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x0, y0); glVertex2f(x0+BTN_W, y0); glVertex2f(x0+BTN_W, y0+BTN_H); glVertex2f(x0, y0+BTN_H)
    glEnd()
    glRasterPos2f(x0+BTN_W//2-5, y0+BTN_H//2-6)
    for ch in "X": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glEnable(GL_DEPTH_TEST)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def mouse_inside_close(x_win, y_win):
    y2d = WIN_H - y_win
    x0, y0, w, h = _close_btn_rect
    return (x_win >= x0 and x_win <= x0+w and y2d >= y0 and y2d <= y0+h)


# Camera (orbit + FP toggle)

cam_pos = [0.0, 600.0, 600.0]
cam_orbit_deg = 0.0
cam_height_step = 2.0
first_person = False

def setup_camera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(FOVY, float(WIN_W)/float(WIN_H), 0.1, 1500.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    if first_person:
        eye_x, eye_y = pl_pos[0], pl_pos[1]
        eye_z = pl_pos[2] + gun_tip_local[2] + 60
        ang = math.radians(-face_deg)
        center_x = eye_x - math.sin(ang)*100
        center_y = eye_y - math.cos(ang)*100
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, eye_z, 0,0,1)
    else:
        r = math.hypot(cam_pos[0], cam_pos[1])
        a = math.radians(cam_orbit_deg)
        x = r*math.sin(a); y = r*math.cos(a); z = cam_pos[2]
        gluLookAt(x, y, z, 0,0,0, 0,0,1)


# Player or Movement

pl_pos = [0.0, 0.0, 15.0]
face_deg = 0.0
PLAYER_STEP = 10.0
TURN_STEP   = 2.5

# Fullarm shoulder swing 
SLAP_RANGE        = 95.0
arm_rest_deg      = 0.0
arm_angle         = 0.0
arm_stage         = 0
arm_scale_boost   = 0.0
pl_slap_target    = None

# Gun tip for bulletss
gun_tip_local = (0.0, -82.0, 70.0)


# Bullets

SLOTS = ['R','Y','B','P','G']
slot_used = [False]*5
current_slot = None
BULLET_SIZE  = 10.0
BULLET_SPEED = 0.6
shots = []  


# Enemies always 5 ta thakbe

NUM_ENEMIES     = 5
ENEMY_SPEED     = 0.095
ENEMY_BASE_R    = 40.0
ENEMY_SCALE_MIN = 0.85
ENEMY_SCALE_MAX = 1.18
ENEMY_SCALE_RATE= 0.00028
speed_scale     = 1.0
pack = []  # each enemy also carries rot to face travel direction


# Game state

PLAYER_LIFE_INIT = 30
life   = PLAYER_LIFE_INIT
score  = 0
missed = 0
is_over = False
lying_down = False


# Cheats (toggle + counters)

cheat_on = False
cheat_infinite_timer = 0.0
cheat_slow_timer     = 0.0
cheat_has_infinite   = False
cheat_has_slow       = False
cheat_on_count       = 0
punish_lock          = False

# Mood durations (long)

MOOD_T = {'R':60.0, 'Y':60.0, 'B':60.0, 'P':60.0, 'G':70.0}

# Slap visual scale
SCALE_MAX = 0.60

# Helpers functions

def clamp(v, lo, hi): return max(lo, min(hi, v))
def len2_xy(a, b):    return (a[0]-b[0])**2 + (a[1]-b[1])**2
def norm2(vx, vy):
    m = math.hypot(vx, vy)
    return (0.0,0.0) if m==0 else (vx/m, vy/m)
def world_from_local_offset(ax_deg, off):
    rad = math.radians(ax_deg)
    cx, sx = math.cos(rad), math.sin(rad)
    x = off[0]*cx - off[1]*sx
    y = off[0]*sx + off[1]*cx
    return (x, y)

def confine_xy_to_circle(x, y, limit_r):
    d = math.hypot(x, y)
    if d > limit_r and d > 0.0:
        k = limit_r / d
        return x*k, y*k
    return x, y


# Round Arena (gradient + solid circular wall)

def draw_circular_arena():
    segs = 144

    # floor disk slightly inside the inner wall to avoid z-fighting
    glBegin(GL_TRIANGLE_FAN)
    glColor3f(0.45, 1.00, 0.45)        # center bright
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(segs+1):
        a = 2.0*math.pi * (i/float(segs))
        x = (WALL_IN-0.5)*math.cos(a)
        y = (WALL_IN-0.5)*math.sin(a)
        glColor3f(0.05, 0.35, 0.05)    # darker rim
        glVertex3f(x, y, 0.0)
    glEnd()

    # inner vertical wall faces inward
    glColor3f(0.60, 0.60, 0.60)
    glBegin(GL_QUAD_STRIP)
    for i in range(segs+1):
        a = 2.0*math.pi * (i/float(segs))
        x = WALL_IN*math.cos(a); y = WALL_IN*math.sin(a)
        glVertex3f(x, y, 0.0)
        glVertex3f(x, y, WALL_H)
    glEnd()

    # outer vertical wall (faces outward) for thickness
    glColor3f(0.06, 0.18, 0.08)
    glBegin(GL_QUAD_STRIP)
    for i in range(segs+1):
        a = 2.0*math.pi * (i/float(segs))
        x = WALL_OUT*math.cos(a); y = WALL_OUT*math.sin(a)
        glVertex3f(x, y, 0.0)
        glVertex3f(x, y, WALL_H)
    glEnd()

    # top ring cap between inner and outer wall
    glColor3f(0.10, 0.26, 0.12)
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(segs+1):
        a = 2.0*math.pi * (i/float(segs))
        xi = WALL_IN*math.cos(a); yi = WALL_IN*math.sin(a)
        xo = WALL_OUT*math.cos(a); yo = WALL_OUT*math.sin(a)
        glVertex3f(xi, yi, WALL_H)
        glVertex3f(xo, yo, WALL_H)
    glEnd()

# Geometry helpers (blocky)

def draw_block(sx, sy, sz):
    glPushMatrix(); glScalef(sx, sy, sz); glutSolidCube(1.0); glPopMatrix()

def draw_arm_block(arm_deg, boost_scale=0.0, color=(1,1,1), palm=True):
    arm_len = 48.0
    arm_w   = 10.0
    arm_t   = 10.0
    glRotatef(arm_deg, 0,0,1)
    glTranslatef(0.0, -arm_len*0.5, 0.0)
    glScalef(1.0+boost_scale, 1.0+boost_scale, 1.0+boost_scale)
    glColor3f(*color)
    draw_block(arm_w, arm_len, arm_t)
    if palm:
        glPushMatrix()
        glTranslatef(0.0, -arm_len*0.5-2.0, 0.0)
        glColor3f(color[0]*0.9, color[1]*0.9, color[2]*0.9)
        draw_block(12.0, 4.0, 12.0)
        glPopMatrix()

def draw_block_gun():
    glPushMatrix(); glColor3f(0.22,0.22,0.25); draw_block(18.0, 10.0, 9.0); glPopMatrix()
    glPushMatrix(); glTranslatef(0.0, -8.0, 0.0); glColor3f(0.35,0.35,0.37); draw_block(4.0, 16.0, 4.0); glPopMatrix()


# Draw: Player / Enemy / Bullets

def draw_player_and_arms():
    glPushMatrix(); glTranslatef(pl_pos[0], pl_pos[1], pl_pos[2]); glRotatef(face_deg,0,0,1)
    if lying_down: glRotatef(-90,1,0,0)

    C_BODY = (0.30, 0.80, 1.00)
    C_LIGHT= (0.70, 0.95, 1.00)
    C_DARK = (0.15, 0.55, 0.85)

    # legs
    glColor3f(*C_BODY)
    glPushMatrix(); glTranslatef( 9,  0, 22); draw_block(12, 12, 44); glPopMatrix()
    glPushMatrix(); glTranslatef(-9,  0, 22); draw_block(12, 12, 44); glPopMatrix()

    # torso
    glPushMatrix(); glTranslatef(0, 0, 60); glColor3f(*C_BODY); draw_block(34, 18, 38); glPopMatrix()
    glPushMatrix(); glTranslatef( 17.1, 0, 60); glColor3f(*C_DARK); draw_block(2.2, 18, 38); glPopMatrix()
    glPushMatrix(); glTranslatef(-17.1, 0, 60); glColor3f(*C_DARK); draw_block(2.2, 18, 38); glPopMatrix()
    glPushMatrix(); glTranslatef(0, -9.8, 60); glColor3f(*C_LIGHT); draw_block(18, 2.5, 22); glPopMatrix()

    # head
    glPushMatrix()
    glTranslatef(0, 0, 60+28); glColor3f(*C_BODY); draw_block(22, 22, 22)
    glTranslatef(0, -11.8, 0); glColor3f(*C_LIGHT)
    glPushMatrix(); glTranslatef(-5.0, 0, 3.5); draw_block(5, 1.6, 5); glPopMatrix()
    glPushMatrix(); glTranslatef( 5.0, 0, 3.5); draw_block(5, 1.6, 5); glPopMatrix()
    glPopMatrix()

    # LEFT ARM — snug
    glPushMatrix()
    glTranslatef(-19, -9.5, 60)
    draw_arm_block(arm_angle, boost_scale=arm_scale_boost, color=C_BODY, palm=True)
    glPopMatrix()

    # RIGHT ARM + gun — snug
    glPushMatrix()
    glTranslatef( 19, -9.5, 60)
    draw_arm_block(12.0, boost_scale=0.0, color=C_BODY, palm=True)
    glTranslatef(0.0, -22.0, -5.0)
    draw_block_gun()
    glPopMatrix()

    glPopMatrix()

def draw_enemy(e):
    glPushMatrix()
    glTranslatef(e['p'][0], e['p'][1], e['p'][2])
    glRotatef(e.get('rot', 0.0), 0,0,1)   # face travel direction
    glScalef(e['s'],e['s'],e['s'])

    base_dark = (0.10, 0.10, 0.12)
    mood = e['m']
    if   mood=='R': tint=(0.7,0.1,0.1)
    elif mood=='Y': tint=(0.6,0.6,0.1)
    elif mood=='B': tint=(0.15,0.35,0.7)
    elif mood=='P': tint=(0.5,0.2,0.6)
    elif mood=='G': tint=(0.2,0.7,0.2)
    else:           tint=(0.0,0.0,0.0)
    body_col = (base_dark[0]+tint[0], base_dark[1]+tint[1], base_dark[2]+tint[2])

    # legs
    glColor3f(*body_col)
    glPushMatrix(); glTranslatef( 6, 0, 26); draw_block(6, 8, 52); glPopMatrix()
    glPushMatrix(); glTranslatef(-6, 0, 26); draw_block(6, 8, 52); glPopMatrix()

    # torso + accents
    glPushMatrix(); glTranslatef(0, 0, 60); draw_block(16, 12, 34); glPopMatrix()
    accent = (0.18, 0.18, 0.22)
    glPushMatrix(); glTranslatef(0, -6.6, 60); glColor3f(*accent); draw_block(14, 1.6, 8); glPopMatrix()
    glPushMatrix(); glTranslatef(0,  6.6, 60); glColor3f(*accent); draw_block(14, 1.6, 8); glPopMatrix()

    # head (happy spins)
    glPushMatrix()
    glTranslatef(0, 0, 60+24)
    if e['m']=='Y': glRotatef(e['spin'], 0,0,1)
    glColor3f(*body_col); draw_block(20, 20, 20)
    glTranslatef(0, -10.8, 0)
    glColor3f(0.85, 0.25, 0.95)
    glPushMatrix(); glTranslatef(-4.5, 0, 3.5); draw_block(4.5, 1.3, 4.5); glPopMatrix()
    glPushMatrix(); glTranslatef( 4.5, 0, 3.5); draw_block(4.5, 1.3, 4.5); glPopMatrix()
    glPopMatrix()

    # LEFT ARM — snug anchor
    glPushMatrix()
    glTranslatef(-11, -9.0, 60)
    progress = abs(e['ea'] - e['er'])/90.0
    sb = SCALE_MAX * progress
    draw_arm_block(e['ea'], boost_scale=sb, color=body_col, palm=True)
    glPopMatrix()

    # crying tears
    if e['m'] == 'B' and e['drops']:
        for d in e['drops']:
            glPushMatrix()
            glColor3f(0.6,0.8,1.0)
            glTranslatef(d['lp'][0], d['lp'][1], d['lp'][2])
            draw_block(6,6,6)
            glPopMatrix()

    glPopMatrix()

def draw_bullet(b):
    glPushMatrix(); glTranslatef(b['p'][0], b['p'][1], b['p'][2])
    m = b['m']
    if   m=='R': glColor3f(1,0.2,0.2)
    elif m=='Y': glColor3f(1,1,0.2)
    elif m=='B': glColor3f(0.7,0.8,1)
    elif m=='P': glColor3f(0.9,0.5,1)
    elif m=='G': glColor3f(0.6,1,0.6)
    else: glColor3f(1,1,1)
    draw_block(BULLET_SIZE, BULLET_SIZE, BULLET_SIZE)
    glPopMatrix()


# Spawns / Reset

def spawn_one():
    # spawn uniformly in the circle (keep margin from wall)
    er = random.uniform(-20.0, 20.0)
    rr = (random.random()**0.5) * (PLAY_R - ENEMY_BASE_R*1.2)
    aa = random.uniform(0.0, 2.0*math.pi)
    x = rr*math.cos(aa); y = rr*math.sin(aa)
    return {
        'p':[x, y, 38.0],
        's':1.0,'dir':1,
        'm':'N','t':0.0,
        'ea':er,'er':er,'es':0,'ec':0.0,
        'v':[random.uniform(-1,1)*0.6, random.uniform(-1,1)*0.6],
        'spin':0.0,
        'drops':[], 'dropt':0.0,
        'atk': None,
        'rot': 0.0
    }

def respawn_enemy(idx):
    pack[idx] = spawn_one()

def ensure_enemy_count():
    while len(pack) < NUM_ENEMIES: pack.append(spawn_one())
    while len(pack) > NUM_ENEMIES: pack.pop()

def reset_game():
    global arm_rest_deg, arm_angle, arm_stage, arm_scale_boost, pl_slap_target
    global face_deg, life, score, missed, is_over, lying_down, current_slot, speed_scale
    global cheat_on, cheat_infinite_timer, cheat_slow_timer, cheat_has_infinite, cheat_has_slow
    global cheat_on_count, punish_lock, first_person, cam_orbit_deg

    pl_pos[:] = [0.0,0.0,15.0]
    face_deg = 0.0
    arm_rest_deg = random.uniform(-22.0, 18.0)
    arm_angle    = arm_rest_deg
    arm_stage    = 0
    arm_scale_boost = 0.0
    pl_slap_target = None
    life = PLAYER_LIFE_INIT; score = 0; missed = 0
    is_over = False; lying_down = False
    shots[:] = []
    slot_used[:] = [False]*5; current_slot = None
    pack[:] = [spawn_one() for _ in range(NUM_ENEMIES)]
    ensure_enemy_count()
    first_person = False
    cam_pos[:] = [0.0, 600.0, 600.0]
    cam_orbit_deg = 0.0
    speed_scale = 1.0
    cheat_on = False; cheat_infinite_timer = 0.0; cheat_slow_timer = 0.0
    cheat_has_infinite = False; cheat_has_slow = False
    cheat_on_count = 0; punish_lock = False

# Actions

def gun_tip_world():
    gx, gy = world_from_local_offset(face_deg, (gun_tip_local[0], gun_tip_local[1]))
    return [pl_pos[0]+gx, pl_pos[1]+gy, pl_pos[2]+gun_tip_local[2]]

def fire_trigger():
    global current_slot
    if is_over or current_slot is None: return
    if punish_lock: return
    if slot_used[current_slot] and not (cheat_on and cheat_infinite_timer>0.0): return
    mood = SLOTS[current_slot]
    dirx = math.cos(math.radians(face_deg - 90))
    diry = math.sin(math.radians(face_deg - 90))
    mpos = gun_tip_world()
    mpos[0] += dirx * (BULLET_SIZE*0.6); mpos[1] += diry * (BULLET_SIZE*0.6)
    shots.append({'p':[mpos[0],mpos[1],mpos[2]], 'd':[dirx,diry], 'm':mood})
    if cheat_on and cheat_infinite_timer>0.0:
        SLOTS[current_slot] = random.choice(['R','Y','B','P','G'])
        slot_used[current_slot] = False
    else:
        slot_used[current_slot] = True
        current_slot = None

def _front_facing(pl, enemy):
    fx = math.cos(math.radians(face_deg - 90))
    fy = math.sin(math.radians(face_deg - 90))
    vx = enemy['p'][0] - pl[0]
    vy = enemy['p'][1] - pl[1]
    m = math.hypot(vx, vy)
    if m == 0: return True
    vx /= m; vy /= m
    dot = fx*vx + fy*vy
    return dot >= 0.5  # ~60° cone

def slap_trigger():
    global arm_stage, pl_slap_target
    if punish_lock: return
    if arm_stage != 0 or is_over: return
    arm_stage = 1
    pl_slap_target = None
    best = None; bestd2 = 1e18
    for e in pack:
        if not _front_facing(pl_pos, e): continue
        d2 = len2_xy(pl_pos, e['p'])
        if d2 < SLAP_RANGE*SLAP_RANGE and d2 < bestd2:
            best, bestd2 = e, d2
    if best: pl_slap_target = best

def kill_enemy(e):
    global score, speed_scale
    if   e['m']=='R': score += 15
    elif e['m']=='Y': score -= 5
    elif e['m']=='P': score += 20
    elif e['m']=='G': score += 1
    else:             score += 5
    used_idxs = [i for i,u in enumerate(slot_used) if u]
    if used_idxs:
        pick = random.choice(used_idxs)
        slot_used[pick] = False
        SLOTS[pick] = random.choice(['R','Y','B','P','G'])
    idx = pack.index(e)
    respawn_enemy(idx)
    ensure_enemy_count()
    speed_scale += 0.03

# Cheats (small helpers)

def set_cheat_infinite(sec):
    global cheat_infinite_timer, cheat_has_infinite
    cheat_infinite_timer = sec
    cheat_has_infinite = True

def set_cheat_heal():
    global life
    life = PLAYER_LIFE_INIT

def set_cheat_slow(sec):
    global cheat_slow_timer, cheat_has_slow
    cheat_slow_timer = sec
    cheat_has_slow = True


# Logic Update
#
def logic_update():
    global life, score, missed, is_over, lying_down
    global arm_stage, arm_angle, arm_scale_boost, pl_slap_target

    dt = 0.016
    strike_speed = 1000.0 * dt
    return_speed =  520.0 * dt

    if cheat_infinite_timer>0.0: globals()['cheat_infinite_timer'] = max(0.0, cheat_infinite_timer-dt)
    if cheat_slow_timer>0.0:     globals()['cheat_slow_timer']     = max(0.0, cheat_slow_timer-dt)

    # Player arm swing
    if arm_stage == 1:
        target = arm_rest_deg + 90.0
        arm_angle += strike_speed
        if arm_angle >= target:
            arm_angle = target
            if pl_slap_target and pl_slap_target in pack:
                e = pl_slap_target
                if _front_facing(pl_pos, e) and len2_xy(pl_pos, e['p']) < SLAP_RANGE*SLAP_RANGE:
                    kill_enemy(e)
            pl_slap_target = None
            arm_stage = 2
        progress = abs(arm_angle - arm_rest_deg) / 90.0
        arm_scale_boost = SCALE_MAX * progress
    elif arm_stage == 2:
        arm_angle -= return_speed
        if arm_angle <= arm_rest_deg:
            arm_angle = arm_rest_deg
            arm_stage = 0
        progress = abs(arm_angle - arm_rest_deg) / 90.0
        arm_scale_boost = SCALE_MAX * progress
    else:
        arm_scale_boost = 0.0

    # bullets (hit wall -> miss)
    out = []
    for i,b in enumerate(shots):
        b['p'][0] += b['d'][0]*BULLET_SPEED
        b['p'][1] += b['d'][1]*BULLET_SPEED
        if math.hypot(b['p'][0], b['p'][1]) > ENEMY_RIM:
            out.append(i); missed += 1
    for i in reversed(out): del shots[i]

    # enemies
    sp_mul = speed_scale * (0.5 if cheat_slow_timer>0.0 else 1.0)
    for e in pack:
        if e['ec']>0.0: e['ec'] = max(0.0, e['ec'] - dt)
        m = e['m']
        if m == 'N':
            dx, dy = pl_pos[0]-e['p'][0], pl_pos[1]-e['p'][1]
            nx, ny = norm2(dx, dy)
            e['p'][0] += nx*ENEMY_SPEED*sp_mul
            e['p'][1] += ny*ENEMY_SPEED*sp_mul
            e['rot'] = (math.degrees(math.atan2(dy, dx)) + 90.0) % 360.0
            if len2_xy(pl_pos, e['p']) < (30.0 + ENEMY_BASE_R*e['s'])**2 and e['es']==0 and e['ec']==0.0:
                e['es'] = 1
        elif m == 'Y':
            e['spin'] = (e['spin'] + 360.0*dt) % 360.0
        elif m == 'B':
            e['dropt'] += dt
            if e['dropt'] >= 0.10:
                e['dropt'] = 0.0
                e['drops'].append({'lp':[random.uniform(-4,4), -10.8, 60.0+24.0], 'vz':-60.0})
            still = []
            for d in e['drops']:
                d['lp'][2] += d['vz']*dt
                if d['lp'][2] > 0.0:
                    still.append(d)
            e['drops'] = still
        elif m == 'P':
            dx, dy = e['p'][0]-pl_pos[0], e['p'][1]-pl_pos[1]
            nx, ny = norm2(dx, dy)
            e['p'][0] += nx*ENEMY_SPEED*1.3*sp_mul
            e['p'][1] += ny*ENEMY_SPEED*1.3*sp_mul
            e['rot'] = (math.degrees(math.atan2(ny, nx)) + 90.0) % 360.0
        elif m == 'G':
            if e['v'] == [0.0,0.0]:
                e['v'] = [random.uniform(-1,1)*0.6, random.uniform(-1,1)*0.6]
            e['p'][0] += e['v'][0]*ENEMY_SPEED*3.0*sp_mul
            e['p'][1] += e['v'][1]*ENEMY_SPEED*3.0*sp_mul
            e['rot'] = (math.degrees(math.atan2(e['v'][1], e['v'][0])) + 90.0) % 360.0
            score += dt
        elif m == 'R':
            tgt, dmin, tidx = None, 1e18, -1
            for j,t in enumerate(pack):
                if t is not e and t['m']=='Y':
                    d2 = len2_xy(e['p'], t['p'])
                    if d2 < dmin: tgt, dmin, tidx = t, d2, j
            if tgt is None:
                for j,t in enumerate(pack):
                    if t is not e:
                        d2 = len2_xy(e['p'], t['p'])
                        if d2 < dmin: tgt, dmin, tidx = t, d2, j
            if tgt is not None:
                dx, dy = tgt['p'][0]-e['p'][0], tgt['p'][1]-e['p'][1]
                nx, ny = norm2(dx, dy)
                e['p'][0] += nx*ENEMY_SPEED*2.0*sp_mul
                e['p'][1] += ny*ENEMY_SPEED*2.0*sp_mul
                e['rot'] = (math.degrees(math.atan2(dy, dx)) + 90.0) % 360.0
                if dmin < (ENEMY_BASE_R*2.0)**2 and e['es']==0 and e['ec']==0.0:
                    e['atk'] = tidx
                    e['es'] = 1

        # enemy arm swing (slower, with cooldown)
        if e['es'] == 1:
            target = e['er'] + 90.0
            e['ea'] += 700.0 * dt
            if e['ea'] >= target:
                e['ea'] = target
                if e['m'] == 'N':
                    life -= 1
                if e['m'] == 'R' and e.get('atk') is not None:
                    tidx = e['atk']
                    if 0 <= tidx < len(pack) and pack[tidx] is not e:
                        if len2_xy(e['p'], pack[tidx]['p']) < (ENEMY_BASE_R*2.0)**2:
                            kill_enemy(pack[tidx])
                    e['atk'] = None
                e['es'] = 2
        elif e['es'] == 2:
            e['ea'] -= 380.0 * dt
            if e['ea'] <= e['er']:
                e['ea'] = e['er']
                e['es'] = 0
                e['ec'] = 1.20

        # clamp to circular arena + pulse
        limit_r = ENEMY_RIM - ENEMY_BASE_R
        e['p'][0], e['p'][1] = confine_xy_to_circle(e['p'][0], e['p'][1], limit_r)
        e['p'][2] = 38.0
        e['s'] += e['dir']*ENEMY_SCALE_RATE
        if e['s'] > ENEMY_SCALE_MAX: e['s'], e['dir'] = ENEMY_SCALE_MAX, -1
        if e['s'] < ENEMY_SCALE_MIN: e['s'], e['dir'] = ENEMY_SCALE_MIN, 1

        # mood timers
        if e['m'] != 'N':
            e['t'] -= dt
            if e['t'] <= 0.0:
                if e['m'] == 'P':
                    kill_enemy(e)
                else:
                    e['m'] = 'N'; e['t'] = 0.0; e['drops'] = []; e['atk'] = None

    # bullet hits
    rm = set()
    for i,b in enumerate(shots):
        for e in pack:
            if len2_xy(b['p'], e['p']) < (ENEMY_BASE_R + BULLET_SIZE*0.6)**2:
                m = b['m']
                e['m'] = m
                e['t'] = MOOD_T[m]
                if m == 'B':
                    e['drops'] = []; e['dropt'] = 0.0
                e['atk'] = None
                rm.add(i); break
    for i in sorted(rm, reverse=True): del shots[i]

    ensure_enemy_count()

    if life <= 0:
        is_over = True; lying_down = True


# HUD / Input

def hud_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)                    # make sure overlay is visible
    glColor3f(1,1,1); glRasterPos2f(x, y)
    for ch in s: glutBitmapCharacter(font, ord(ch))
    glEnable(GL_DEPTH_TEST)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_health_bar(x, y, w, h):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)                    # fixes “not green” (no depth fighting)

    pct = clamp(life/float(PLAYER_LIFE_INIT), 0.0, 1.0)

    # black background
    glColor3f(0.1,0.1,0.1)
    glBegin(GL_QUADS)
    glVertex2f(x, y); glVertex2f(x+w, y); glVertex2f(x+w, y+h); glVertex2f(x, y+h)
    glEnd()

    # green fill
    glColor3f(0.2,1.0,0.2)
    fill = w * pct
    glBegin(GL_QUADS)
    glVertex2f(x, y); glVertex2f(x+fill, y); glVertex2f(x+fill, y+h); glVertex2f(x, y+h)
    glEnd()

    # border
    glColor3f(1,1,1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y); glVertex2f(x+w, y); glVertex2f(x+w, y+h); glVertex2f(x, y+h)
    glEnd()

    glEnable(GL_DEPTH_TEST)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def slots_draw_strip():
    hud_text_2d(10, WIN_H-112, 'Bullets: 1=R 2=Y 3=B 4=P 5=G  |  Left Click = Fire,  F = Slap,  R = Restart')
    base_x = 10; base_y = WIN_H-140; w = 34; gap = 8
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    for i, m in enumerate(SLOTS):
        x0 = base_x + i*(w+gap); y0 = base_y
        used = slot_used[i]
        if   m=='R': glColor3f(1,0,0)
        elif m=='Y': glColor3f(1,1,0)
        elif m=='B': glColor3f(0.3,0.7,1)
        elif m=='P': glColor3f(0.8,0.3,1)
        elif m=='G': glColor3f(0.3,1,0.3)
        if used: glColor3f(0.3,0.3,0.3)
        glBegin(GL_QUADS)
        glVertex2f(x0, y0); glVertex2f(x0+w, y0); glVertex2f(x0+w, y0+28); glVertex2f(x0, y0+28)
        glEnd()
        if current_slot == i:
            glColor3f(1,1,1)
            glBegin(GL_LINE_LOOP)
            glVertex2f(x0-2, y0-2); glVertex2f(x0+w+2, y0-2); glVertex2f(x0+w+2, y0+30); glVertex2f(x0-2, y0+30)
            glEnd()
    glEnable(GL_DEPTH_TEST)
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def draw_cheat_messages():
    y = WIN_H - 180
    if punish_lock:
        hud_text_2d(10, y, "Punishment: controls disabled. Time for punishment!")
        return
    if not cheat_on:
        return
    hud_text_2d(10, y, "Cheat Mode: ON")
    y -= 24
    if cheat_has_infinite:
        hud_text_2d(10, y, "∞ bullets enabled")
        y -= 24
    if cheat_has_slow:
        hud_text_2d(10, y, "Enemies slowed down")
        y -= 24
    hud_text_2d(10, y, "Press H for full health")

def keyboard(key, x, y):
    global face_deg, first_person, cheat_on, is_over, current_slot
    global cheat_infinite_timer, cheat_slow_timer, cheat_on_count, punish_lock
    global cheat_has_infinite, cheat_has_slow

    if key in (b'r', b'R'):
        reset_game(); return
    if punish_lock or is_over:
        return

    if key in (b'w', b'W', b's', b'S'):
        sign = 1 if key in (b'w', b'W') else -1
        nx = sign * (-PLAYER_STEP*math.sin(math.radians(-face_deg)))
        ny = sign * (-PLAYER_STEP*math.cos(math.radians(face_deg)))
        newx = pl_pos[0]+nx; newy = pl_pos[1]+ny
        pl_pos[0], pl_pos[1] = confine_xy_to_circle(newx, newy, PLAY_R)
    if key in (b'a', b'A'): face_deg = (face_deg + TURN_STEP*5) % 360.0
    if key in (b'd', b'D'): face_deg = (face_deg - TURN_STEP*5) % 360.0
    if key in (b'1',b'2',b'3',b'4',b'5'):
        idx = int(key.decode('utf-8'))-1
        if 0 <= idx < 5 and not slot_used[idx]: current_slot = idx
    if key in (b'f', b'F'): slap_trigger()

    if key in (b'c', b'C'):
        if not cheat_on:
            cheat_on = True; cheat_on_count += 1
            cheat_has_infinite = False; cheat_has_slow = False
            if cheat_on_count >= 3:
                cheat_on = False; punish_lock = True
                cheat_infinite_timer = 0.0; cheat_slow_timer = 0.0
                cheat_has_infinite = False; cheat_has_slow = False
                return
        else:
            cheat_on = False
            cheat_infinite_timer = 0.0; cheat_slow_timer = 0.0
            cheat_has_infinite = False; cheat_has_slow = False

    if cheat_on:
        if key in (b'i', b'I'): set_cheat_infinite(30.0)
        if key in (b'h', b'H'): set_cheat_heal()
        if key in (b'k', b'K'): set_cheat_slow(30.0)

def special(key, x, y):
    global cam_pos, cam_orbit_deg
    if not first_person:
        if key == GLUT_KEY_UP:    cam_pos[2] = max(10.0, cam_pos[2]-cam_height_step)
        if key == GLUT_KEY_DOWN:  cam_pos[2] += cam_height_step
        if key == GLUT_KEY_LEFT:  cam_orbit_deg = (cam_orbit_deg - 0.5) % 360.0
        if key == GLUT_KEY_RIGHT: cam_orbit_deg = (cam_orbit_deg + 0.5) % 360.0

def mouse(btn, state, x, y):
    global first_person
    if btn == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if mouse_inside_close(x, y):
            try:
                wid = glutGetWindow()
                if wid != 0: glutDestroyWindow(wid)
            except Exception: pass
            sys.exit(0)
        if not is_over and not punish_lock:
            fire_trigger()
    if btn == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not is_over and not punish_lock:
            first_person = not first_person


# Display / Idle

def display():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity(); setup_camera()
    draw_circular_arena()
    draw_player_and_arms()
    if not is_over:
        for e in pack: draw_enemy(e)
        for b in shots: draw_bullet(b)
        hud_text_2d(10, WIN_H-30, f"HP: {life}")
        hud_text_2d(10, WIN_H-56, f"Points: {int(score)}")
        draw_health_bar(10, WIN_H-84, 280, 16)   # GREEN bar (depth disabled)
        slots_draw_strip()
        draw_cheat_messages()
    else:
        hud_text_2d(10, WIN_H-30, f"Game Over. Points: {int(score)}")
        hud_text_2d(10, WIN_H-56, 'Press "R" to Restart')
    draw_close_button()
    glutSwapBuffers()

def idle():
    if not is_over: logic_update()
    glutPostRedisplay()


# Main

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Mood Bullet Arena  (round arena + walls + green HP)")
    reset_game()
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    glutMouseFunc(mouse)
    glutMainLoop()

if __name__ == "__main__":
    main()