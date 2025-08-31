cheat_on = False
cheat_infinite_timer = 0.0
cheat_slow_timer     = 0.0
cheat_has_infinite   = False
cheat_has_slow       = False
cheat_on_count       = 0
punish_lock          = False

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
    global cheat_on, cheat_on_count, punish_lock
    global cheat_infinite_timer, cheat_slow_timer
    global cheat_has_infinite, cheat_has_slow

    if key in (b'c', b'C'):
        if not cheat_on:
            cheat_on = True
            cheat_on_count += 1
            cheat_has_infinite = False
            cheat_has_slow = False
            if cheat_on_count >= 3:
                cheat_on = False
                punish_lock = True
                cheat_infinite_timer = 0.0
                cheat_slow_timer = 0.0
                cheat_has_infinite = False
                cheat_has_slow = False
                return
        else:
            cheat_on = False
            cheat_infinite_timer = 0.0
            cheat_slow_timer = 0.0
            cheat_has_infinite = False
            cheat_has_slow = False

    if cheat_on:
        if key in (b'i', b'I'):
            set_cheat_infinite(30.0)
        if key in (b'h', b'H'):
            set_cheat_heal()
        if key in (b'k', b'K'):
            set_cheat_slow(30.0)

def fire_trigger():
    global current_slot
    if is_over or current_slot is None: return
    if punish_lock: return
    if slot_used[current_slot] and not (cheat_on and cheat_infinite_timer > 0.0):
        return

    mood = SLOTS[current_slot]
    dirx = math.cos(math.radians(face_deg - 90))
    diry = math.sin(math.radians(face_deg - 90))
    mpos = gun_tip_world()
    mpos[0] += dirx * (BULLET_SIZE * 0.6)
    mpos[1] += diry * (BULLET_SIZE * 0.6)
    shots.append({'p':[mpos[0], mpos[1], mpos[2]], 'd':[dirx, diry], 'm':mood})

    if cheat_on and cheat_infinite_timer > 0.0:
        SLOTS[current_slot] = random.choice(['R','Y','B','P','G'])
        slot_used[current_slot] = False
    else:
        slot_used[current_slot] = True
        current_slot = None

def logic_update():
    global cheat_infinite_timer, cheat_slow_timer

    dt = 0.016
    if cheat_infinite_timer > 0.0:
        cheat_infinite_timer = max(0.0, cheat_infinite_timer - dt)
    if cheat_slow_timer > 0.0:
        cheat_slow_timer = max(0.0, cheat_slow_timer - dt)

    sp_mul = speed_scale * (0.5 if cheat_slow_timer > 0.0 else 1.0)