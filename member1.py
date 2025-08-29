from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, random, sys

WIN_W, WIN_H = 1000, 800
FOVY = 120.0
FLOOR_HALF = 600
TILE = 100

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

pl_pos = [0.0, 0.0, 15.0]
face_deg = 0.0
PLAYER_STEP = 10.0
TURN_STEP   = 2.5

SLAP_RANGE        = 95.0
arm_rest_deg      = 0.0
arm_angle         = 0.0
arm_stage         = 0
arm_scale_boost   = 0.0

gun_tip_local = (0.0, -82.0, 70.0)

SLOTS = ['R','Y','B','P','G']
slot_used = [False]*5
current_slot = None
BULLET_SIZE  = 10.0
BULLET_SPEED = 0.6
shots = []

cheat_on = False
cheat_infinite_timer = 0.0
cheat_slow_timer     = 0.0

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

def draw_floor_and_walls():
    glBegin(GL_QUADS)
    for gx in range(-FLOOR_HALF, FLOOR_HALF, TILE):
        for gy in range(-FLOOR_HALF, FLOOR_HALF, TILE):
            c = ((gx//TILE + gy//TILE) & 1)
            if c == 0: glColor3f(1.0, 1.0, 1.0)
            else:      glColor3f(0.7, 0.5, 0.95)
            glVertex3f(gx,          gy,          0)
            glVertex3f(gx+TILE,     gy,          0)
            glVertex3f(gx+TILE,     gy+TILE,     0)
            glVertex3f(gx,          gy+TILE,     0)
    h = 100.0
    glColor3f(0.72, 0.72, 0.72)
    glVertex3f(-FLOOR_HALF, -FLOOR_HALF, 0); glVertex3f(-FLOOR_HALF,  FLOOR_HALF, 0)
    glVertex3f(-FLOOR_HALF,  FLOOR_HALF, h); glVertex3f(-FLOOR_HALF, -FLOOR_HALF, h)
    glVertex3f( FLOOR_HALF, -FLOOR_HALF, 0); glVertex3f( FLOOR_HALF,  FLOOR_HALF, 0)
    glVertex3f( FLOOR_HALF,  FLOOR_HALF, h); glVertex3f( FLOOR_HALF, -FLOOR_HALF, h)
    glVertex3f(-FLOOR_HALF, -FLOOR_HALF, 0); glVertex3f( FLOOR_HALF, -FLOOR_HALF, 0)
    glVertex3f( FLOOR_HALF, -FLOOR_HALF, h); glVertex3f(-FLOOR_HALF, -FLOOR_HALF, h)
    glVertex3f(-FLOOR_HALF,  FLOOR_HALF, 0); glVertex3f( FLOOR_HALF,  FLOOR_HALF, 0)
    glVertex3f( FLOOR_HALF,  FLOOR_HALF, h); glVertex3f(-FLOOR_HALF,  FLOOR_HALF, h)
    glEnd()

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

def draw_player_and_arms():
    glPushMatrix(); glTranslatef(pl_pos[0], pl_pos[1], pl_pos[2]); glRotatef(face_deg,0,0,1)
    C_BODY=(0.30,0.80,1.00); C_LIGHT=(0.70,0.95,1.00); C_DARK=(0.15,0.55,0.85)
    glColor3f(*C_BODY); glPushMatrix(); glTranslatef( 9,0,22); draw_block(12,12,44); glPopMatrix()
    glColor3f(*C_BODY); glPushMatrix(); glTranslatef(-9,0,22); draw_block(12,12,44); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,60); glColor3f(*C_BODY); draw_block(34,18,38); glPopMatrix()
    glPushMatrix(); glTranslatef( 17.1,0,60); glColor3f(*C_DARK); draw_block(2.2,18,38); glPopMatrix()
    glPushMatrix(); glTranslatef(-17.1,0,60); glColor3f(*C_DARK); draw_block(2.2,18,38); glPopMatrix()
    glPushMatrix(); glTranslatef(0,-9.8,60); glColor3f(*C_LIGHT); draw_block(18,2.5,22); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,60+28); glColor3f(*C_BODY); draw_block(22,22,22)
    glTranslatef(0,-11.8,0); glColor3f(*C_LIGHT)
    glPushMatrix(); glTranslatef(-5.0,0,3.5); draw_block(5,1.6,5); glPopMatrix()
    glPushMatrix(); glTranslatef( 5.0,0,3.5); draw_block(5,1.6,5); glPopMatrix()
    glPopMatrix()
    glPushMatrix(); glTranslatef(-19,-36,60); draw_arm_block(arm_angle, boost_scale=arm_scale_boost, color=C_BODY, palm=True); glPopMatrix()
    glPushMatrix(); glTranslatef( 19,-36,60); draw_arm_block(12.0, boost_scale=0.0, color=C_BODY, palm=True); glTranslatef(0.0,-22.0,-5.0); draw_block_gun(); glPopMatrix()
    glPopMatrix()

def draw_bullet(b):
    glPushMatrix(); glTranslatef(b['p'][0], b['p'][1], b['p'][2])
    m=b['m']
    if m=='R': glColor3f(1,0.2,0.2)
    elif m=='Y': glColor3f(1,1,0.2)
    elif m=='B': glColor3f(0.7,0.8,1)
    elif m=='P': glColor3f(0.9,0.5,1)
    elif m=='G': glColor3f(0.6,1,0.6)
    else: glColor3f(1,1,1)
    draw_block(BULLET_SIZE, BULLET_SIZE, BULLET_SIZE)
    glPopMatrix()

def gun_tip_world():
    gx, gy = world_from_local_offset(face_deg, (gun_tip_local[0], gun_tip_local[1]))
    return [pl_pos[0]+gx, pl_pos[1]+gy, pl_pos[2]+gun_tip_local[2]]

def fire_trigger():
    global current_slot
    if current_slot is None: return
    if slot_used[current_slot] and not (cheat_on and cheat_infinite_timer>0.0): return
    mood = SLOTS[current_slot]
    dirx = math.cos(math.radians(face_deg - 90))
    diry = math.sin(math.radians(face_deg - 90))
    mpos = gun_tip_world()
    mpos[0] += dirx*(BULLET_SIZE*0.6); mpos[1] += diry*(BULLET_SIZE*0.6)
    shots.append({'p':[mpos[0],mpos[1],mpos[2]], 'd':[dirx,diry], 'm':mood})
    if not (cheat_on and cheat_infinite_timer>0.0):
        slot_used[current_slot] = True
        current_slot = None