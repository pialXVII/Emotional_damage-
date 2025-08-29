def slap_trigger():
    global arm_stage
    if arm_stage != 0: return
    arm_stage = 1
    best=None; bestd2=1e18
    for e in pack:
        d2 = len2_xy(pl_pos, e['p'])
        if d2 < SLAP_RANGE*SLAP_RANGE and d2 < bestd2:
            best, bestd2 = e, d2
    if best: kill_enemy(best)

def set_cheat_infinite(sec):
    global cheat_infinite_timer
    cheat_infinite_timer = sec
def set_cheat_heal():
    global life
    life = PLAYER_LIFE_INIT
def set_cheat_slow(sec):
    global cheat_slow_timer
    cheat_slow_timer = sec

def logic_update():
    global life, score, missed, is_over, lying_down
    global arm_stage, arm_angle, arm_scale_boost
    dt = 0.016
    strike_speed = 1000.0 * dt
    return_speed =  520.0 * dt
    if cheat_infinite_timer>0.0: globals()['cheat_infinite_timer'] = max(0.0, cheat_infinite_timer-dt)
    if cheat_slow_timer>0.0:     globals()['cheat_slow_timer']     = max(0.0, cheat_slow_timer-dt)
    if arm_stage == 1:
        target = arm_rest_deg + 90.0
        arm_angle += strike_speed
        if arm_angle >= target:
            arm_angle = target
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
    out = []
    for i,b in enumerate(shots):
        b['p'][0] += b['d'][0]*BULLET_SPEED
        b['p'][1] += b['d'][1]*BULLET_SPEED
        if abs(b['p'][0])>FLOOR_HALF or abs(b['p'][1])>FLOOR_HALF:
            out.append(i); missed += 1
    for i in reversed(out): del shots[i]
    sp_mul = speed_scale * (0.5 if cheat_slow_timer>0.0 else 1.0)
    for e in pack:
        if e['ec']>0.0: e['ec'] = max(0.0, e['ec'] - dt)
        m = e['m']
        if m == 'N':
            dx, dy = pl_pos[0]-e['p'][0], pl_pos[1]-e['p'][1]
            nx, ny = norm2(dx, dy)
            e['p'][0] += nx*ENEMY_SPEED*sp_mul
            e['p'][1] += ny*ENEMY_SPEED*sp_mul
            if len2_xy(pl_pos, e['p']) < (30.0 + ENEMY_BASE_R*e['s'])**2 and e['es']==0 and e['ec']==0.0:
                e['es'] = 1
        elif m == 'Y':
            e['spin'] = (e['spin'] + 360.0*dt) % 360.0
        elif m == 'B':
            e['dropt'] += dt
            if e['dropt'] >= 0.10:
                e['dropt'] = 0.0
                e['drops'].append({'lp':[random.uniform(-4,4), -10.8, 28.0], 'vz':-60.0})
            still=[]
            for d in e['drops']:
                d['lp'][2] += d['vz']*dt
                if d['lp'][2] > 0.0: still.append(d)
            e['drops'] = still
        elif m == 'P':
            dx, dy = e['p'][0]-pl_pos[0], e['p'][1]-pl_pos[1]
            nx, ny = norm2(dx, dy)
            e['p'][0] += nx*ENEMY_SPEED*1.3*sp_mul
            e['p'][1] += ny*ENEMY_SPEED*1.3*sp_mul
        elif m == 'G':
            if e['v'] == [0.0,0.0]:
                e['v'] = [random.uniform(-1,1)*0.6, random.uniform(-1,1)*0.6]
            e['p'][0] += e['v'][0]*ENEMY_SPEED*0.8*sp_mul
            e['p'][1] += e['v'][1]*ENEMY_SPEED*0.8*sp_mul
            score += dt
        elif m == 'R':
            tgt, dmin = None, 1e18
            for t in pack:
                if t is not e and t['m']=='Y':
                    d2 = len2_xy(e['p'], t['p'])
                    if d2 < dmin: tgt, dmin = t, d2
            if tgt is None:
                for t in pack:
                    if t is not e:
                        d2 = len2_xy(e['p'], t['p'])
                        if d2 < dmin: tgt, dmin = t, d2
            if tgt is not None:
                dx, dy = tgt['p'][0]-e['p'][0], tgt['p'][1]-e['p'][1]
                nx, ny = norm2(dx, dy)
                e['p'][0] += nx*ENEMY_SPEED*2.0*sp_mul
                e['p'][1] += ny*ENEMY_SPEED*2.0*sp_mul
                if dmin < (ENEMY_BASE_R*2.0)**2:
                    kill_enemy(tgt)
        if e['es'] == 1:
            target = e['er'] + 90.0
            e['ea'] += 1000.0 * dt
            if e['ea'] >= target:
                e['ea'] = target
                if e['m'] == 'N': life -= 1
                e['es'] = 2
        elif e['es'] == 2:
            e['ea'] -= 520.0 * dt
            if e['ea'] <= e['er']:
                e['ea'] = e['er']
                e['es'] = 0
                e['ec'] = 0.70
        e['p'][0] = clamp(e['p'][0], -FLOOR_HALF+ENEMY_BASE_R, FLOOR_HALF-ENEMY_BASE_R)
        e['p'][1] = clamp(e['p'][1], -FLOOR_HALF+ENEMY_BASE_R, FLOOR_HALF-ENEMY_BASE_R)
        e['p'][2] = 38.0
        e['s'] += e['dir']*ENEMY_SCALE_RATE
        if e['s'] > ENEMY_SCALE_MAX: e['s'], e['dir'] = ENEMY_SCALE_MAX, -1
        if e['s'] < ENEMY_SCALE_MIN: e['s'], e['dir'] = ENEMY_SCALE_MIN, 1
        if e['m'] != 'N':
            e['t'] -= dt
            if e['t'] <= 0.0:
                if e['m'] == 'P':
                    kill_enemy(e)
                else:
                    e['m'] = 'N'; e['t'] = 0.0; e['drops'] = []
    rm=set()
    for i,b in enumerate(shots):
        for e in pack:
            if len2_xy(b['p'], e['p']) < (ENEMY_BASE_R + BULLET_SIZE*0.6)**2:
                m=b['m']; e['m']=m; e['t']=MOOD_T[m]
                if m=='B': e['drops']=[]; e['dropt']=0.0
                rm.add(i); break
    for i in sorted(rm, reverse=True): del shots[i]
    ensure_enemy_count()
    if life <= 0:
        is_over = True; lying_down = True

def hud_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(1,1,1); glRasterPos2f(x, y)
    for ch in s: glutBitmapCharacter(font, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def slots_draw_strip():
    hud_text_2d(10, WIN_H-25, 'Bullets: 1=R 2=Y 3=B 4=P 5=G  |  Left Click=Fire  F=Slap  R=Restart')
    base_x=10; base_y=WIN_H-55; w=34; gap=8
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    for i, m in enumerate(SLOTS):
        x0=base_x+i*(w+gap); y0=base_y
        used=slot_used[i]
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
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global face_deg, first_person, cheat_on, is_over, current_slot
    if key in (b'r', b'R'): reset_game(); return
    if is_over: return
    if key in (b'w', b'W', b's', b'S'):
        sign = 1 if key in (b'w', b'W') else -1
        nx = sign * (-PLAYER_STEP*math.sin(math.radians(-face_deg)))
        ny = sign * (-PLAYER_STEP*math.cos(math.radians(face_deg)))
        pl_pos[0] = clamp(pl_pos[0]+nx, -FLOOR_HALF+10, FLOOR_HALF-10)
        pl_pos[1] = clamp(pl_pos[1]+ny, -FLOOR_HALF+10, FLOOR_HALF-10)
    if key in (b'a', b'A'): face_deg = (face_deg + TURN_STEP*5) % 360.0
    if key in (b'd', b'D'): face_deg = (face_deg - TURN_STEP*5) % 360.0
    if key in (b'1',b'2',b'3',b'4',b'5'):
        idx = int(key.decode('utf-8'))-1
        if 0 <= idx < 5 and not slot_used[idx]: current_slot = idx
    if key in (b'f', b'F'): slap_trigger()
    if key in (b'c', b'C'): cheat_on = not cheat_on
    if cheat_on:
        if key in (b'i', b'I'): set_cheat_infinite(10.0)
        if key in (b'h', b'H'): set_cheat_heal()
        if key in (b's', b'S'): set_cheat_slow(5.0)

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
            except Exception:
                pass
            sys.exit(0)
        if not is_over:
            fire_trigger()
    if btn == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not is_over:
            first_person = not first_person

def display():
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity(); setup_camera()
    draw_floor_and_walls()
    draw_player_and_arms()
    if not is_over:
        for e in pack: draw_enemy(e)
        for b in shots: draw_bullet(b)
        hud_text_2d(10, WIN_H-30, f"HP: {life}")
        hud_text_2d(10, WIN_H-55, f"Points: {int(score)}")
        slots_draw_strip()
    else:
        hud_text_2d(10, WIN_H-30, f"Game Over. Points: {int(score)}")
        hud_text_2d(10, WIN_H-55, 'Press "R" to Restart')
    draw_close_button()
    glutSwapBuffers()

def idle():
    if not is_over: logic_update()
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Mood Bullet Arena – 3 Members Split")
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
