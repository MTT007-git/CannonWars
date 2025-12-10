from tkinter import *
from tkinter.messagebox import showinfo
import matplotlib.pyplot as plt
import math
import time

FLOOR_HEIGHT = 540
WHEEL_DIAMETER = 20
WHEEL_SPACE = 50
WHEEL_NAILS = 5
NAIL_DIAMETER = 2
NAIL_SPACE = 12
PLATFORM_HEIGHT = 13
SPEED = 100
ROT_SPEED = 20
RECHARGE = 0.5
RECOIL = 150
RECOIL_LOSS = 5
BALL_SPEED = 300
BALL_DIAMETER = 10
FLOOR_FRICTION = 7
AIR_FRICTION = 0.2
GRAVITY = 300
MAX_HEALTH = 100
HIT_DAMAGE = 5


def rotate_point(x: float, y: float, r: float) -> tuple[float, float]:
    """
    Rotate a point
    :param x: relative x
    :param y: relative y
    :param r: rotation
    :return: point coordinates (x, y)
    """
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)


def get_rect_rot(x: float, y: float, width: float, height: float, r: float) -> list[tuple[float, float]]:
    """
    Get the points of a rotated rectangle
    :param x:
    :param y:
    :param width:
    :param height:
    :param r:
    :return:
    """
    rad = math.radians(-r)
    p1 = rotate_point(-width / 2, -height / 2, rad)
    p2 = rotate_point(width / 2, -height / 2, rad)
    p3 = rotate_point(width / 2, height / 2, rad)
    p4 = rotate_point(-width / 2, height / 2, rad)
    return [(x + p1[0], y + p1[1]),
            (x + p2[0], y + p2[1]),
            (x + p3[0], y + p3[1]),
            (x + p4[0], y + p4[1])]


def onpress(e):
    global p1_dx, p1_dr, p2_dx, p2_dr, p1_last_shot, p2_last_shot, p1_drecoil, p2_drecoil
    key = e.keysym.lower()
    if key == "a":
        p1_dx = -SPEED
    if key == "d":
        p1_dx = SPEED
    if key == "s":
        p1_dr = -ROT_SPEED
    if key == "w":
        p1_dr = ROT_SPEED
    if key in ("q", "e", "r", "f", "space") and time.time() - p1_last_shot > RECHARGE:
        p1_drecoil = RECOIL
        pnt = rotate_point(WHEEL_SPACE + WHEEL_DIAMETER, 0, math.radians(-p1_r))
        speed = rotate_point(BALL_SPEED, 0, math.radians(-p1_r))
        balls.append([p1_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 + pnt[0],
                      FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT / 2 + pnt[1],
                      speed[0], speed[1], "red"])
        p1_last_shot = time.time()
    if key == "left":
        p2_dx = -SPEED
    if key == "right":
        p2_dx = SPEED
    if key == "down":
        p2_dr = -ROT_SPEED
    if key == "up":
        p2_dr = ROT_SPEED
    if key in ("shift_r", "next", "return", "control_r") and time.time() - p2_last_shot > RECHARGE:
        p2_drecoil = RECOIL
        pnt = rotate_point(-WHEEL_SPACE - WHEEL_DIAMETER, 0, math.radians(p2_r))
        speed = rotate_point(-BALL_SPEED, 0, math.radians(p2_r))
        balls.append([p2_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + pnt[0],
                      FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT / 2 + pnt[1],
                      speed[0], speed[1], "green"])
        p2_last_shot = time.time()


def onrelease(e):
    global p1_dx, p1_dr, p2_dx, p2_dr
    key = e.keysym.lower()
    if key in ("a", "d"):
        p1_dx = 0
    if key in ("s", "w"):
        p1_dr = 0
    if key in ("left", "right"):
        p2_dx = 0
    if key in ("down", "up"):
        p2_dr = 0


def update():
    global last_time, p1_x, p1_r, p1_recoil, p1_drecoil, p1_health, p2_x, p2_r, p2_recoil, p2_drecoil, p2_health
    if p1_health <= 0 or p2_health <= 0:
        if p1_health <= 0 and p2_health <= 0:
            showinfo("The game ended", "The game ended.\nIt's a tie")
        elif p1_health <= 0:
            showinfo("The game ended", "The game ended.\nGreen won")
        else:
            showinfo("The game ended", "The game ended.\nRed won")
        root.destroy()
        plt.plot(p1_health_history, color="red")
        plt.plot(p2_health_history, color="green")
        plt.show()
        return
    tm = time.time() - last_time
    p1_x = min(640 - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 - 5,
               max(0 + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + 5, p1_x + p1_dx * tm))
    p1_r = min(89, max(1, p1_r + p1_dr * tm))
    p1_drecoil -= p1_drecoil * RECOIL_LOSS * tm
    p1_recoil += p1_drecoil * tm
    p1_recoil -= p1_recoil * RECOIL_LOSS * tm
    p2_x = min(640 - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 - 5,
               max(0 + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + 5, p2_x + p2_dx * tm))
    p2_r = min(89, max(1, p2_r + p2_dr * tm))
    p2_drecoil -= p2_drecoil * RECOIL_LOSS * tm
    p2_recoil += p2_drecoil * tm
    p2_recoil -= p2_recoil * RECOIL_LOSS * tm
    for i in balls:
        i[3] += GRAVITY * tm
        i[2] -= i[2] * AIR_FRICTION * tm
        i[3] -= i[3] * AIR_FRICTION * tm
        i[0] += i[2] * tm
        i[1] += i[3] * tm
        if i[1] > FLOOR_HEIGHT - BALL_DIAMETER / 2:
            i[1] = FLOOR_HEIGHT - BALL_DIAMETER / 2
            i[2] -= i[2] * FLOOR_FRICTION * tm
            i[3] = 0
        else:
            if (p1_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 - 5 - BALL_DIAMETER / 2 <= i[0] <=
                    p1_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + 5 + BALL_DIAMETER / 2 and
                    FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT <= i[1] <= FLOOR_HEIGHT):
                p1_health -= HIT_DAMAGE
                balls.remove(i)
            if (p2_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 - 5 - BALL_DIAMETER / 2 <= i[0] <=
                    p2_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + 5 + BALL_DIAMETER / 2 and
                    FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT <= i[1] <= FLOOR_HEIGHT):
                p2_health -= HIT_DAMAGE
                balls.remove(i)
    last_time = time.time()
    c.delete("all")
    c.create_rectangle(0, FLOOR_HEIGHT, 645, 645, fill="gray")
    for i in balls:
        c.create_oval(i[0] - BALL_DIAMETER / 2, i[1] - BALL_DIAMETER / 2,
                      i[0] + BALL_DIAMETER / 2, i[1] + BALL_DIAMETER / 2, fill=i[4])
    c.create_oval(p1_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2, FLOOR_HEIGHT - WHEEL_DIAMETER,
                  p1_x - WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2, FLOOR_HEIGHT, fill="red")
    c.create_oval(p1_x + WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2, FLOOR_HEIGHT - WHEEL_DIAMETER,
                  p1_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2, FLOOR_HEIGHT, fill="red")
    for i in range(WHEEL_NAILS):
        x, y = rotate_point(NAIL_SPACE / 2, 0,
                            math.radians(p1_x / (WHEEL_DIAMETER * math.pi) * 360 + 360 / WHEEL_NAILS * i))
        c.create_oval(p1_x - WHEEL_SPACE / 2 + x - NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y - NAIL_DIAMETER / 2,
                      p1_x - WHEEL_SPACE / 2 + x + NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y + NAIL_DIAMETER / 2, fill="red")
    for i in range(WHEEL_NAILS):
        x, y = rotate_point(NAIL_SPACE / 2, 0,
                            math.radians(p1_x / (WHEEL_DIAMETER * math.pi) * 360 + 360 / WHEEL_NAILS * i))
        c.create_oval(p1_x + WHEEL_SPACE / 2 + x - NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y - NAIL_DIAMETER / 2,
                      p1_x + WHEEL_SPACE / 2 + x + NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y + NAIL_DIAMETER / 2, fill="red")
    pnt = rotate_point((WHEEL_SPACE + WHEEL_DIAMETER + 10) / 2 - p1_recoil, 0, math.radians(-p1_r))
    c.create_polygon(get_rect_rot(p1_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 + pnt[0],
                                  FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT / 2 + pnt[1],
                                  WHEEL_SPACE + WHEEL_DIAMETER + 5,
                                  PLATFORM_HEIGHT, p1_r), fill="red", outline="black")
    c.create_rectangle(p1_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 - 5, FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT,
                       p1_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + 5, FLOOR_HEIGHT - WHEEL_DIAMETER, fill="red")
    c.create_oval(p2_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2, FLOOR_HEIGHT - WHEEL_DIAMETER,
                  p2_x - WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2, FLOOR_HEIGHT, fill="green")
    c.create_oval(p2_x + WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2, FLOOR_HEIGHT - WHEEL_DIAMETER,
                  p2_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2, FLOOR_HEIGHT, fill="green")
    for i in range(WHEEL_NAILS):
        x, y = rotate_point(NAIL_SPACE / 2, 0,
                            math.radians(p2_x / (WHEEL_DIAMETER * math.pi) * 360 + 360 / WHEEL_NAILS * i))
        c.create_oval(p2_x - WHEEL_SPACE / 2 + x - NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y - NAIL_DIAMETER / 2,
                      p2_x - WHEEL_SPACE / 2 + x + NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y + NAIL_DIAMETER / 2, fill="green")
    for i in range(WHEEL_NAILS):
        x, y = rotate_point(NAIL_SPACE / 2, 0,
                            math.radians(p2_x / (WHEEL_DIAMETER * math.pi) * 360 + 360 / WHEEL_NAILS * i))
        c.create_oval(p2_x + WHEEL_SPACE / 2 + x - NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y - NAIL_DIAMETER / 2,
                      p2_x + WHEEL_SPACE / 2 + x + NAIL_DIAMETER / 2,
                      FLOOR_HEIGHT - WHEEL_DIAMETER / 2 + y + NAIL_DIAMETER / 2, fill="green")
    pnt = rotate_point(-(WHEEL_SPACE + WHEEL_DIAMETER + 10) / 2 + p2_recoil, 0, math.radians(p2_r))
    c.create_polygon(get_rect_rot(p2_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + pnt[0],
                                  FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT / 2 + pnt[1],
                                  WHEEL_SPACE + WHEEL_DIAMETER + 5,
                                  PLATFORM_HEIGHT, 180 - p2_r), fill="green", outline="black")
    c.create_rectangle(p2_x - WHEEL_SPACE / 2 - WHEEL_DIAMETER / 2 - 5, FLOOR_HEIGHT - WHEEL_DIAMETER - PLATFORM_HEIGHT,
                       p2_x + WHEEL_SPACE / 2 + WHEEL_DIAMETER / 2 + 5, FLOOR_HEIGHT - WHEEL_DIAMETER, fill="green")
    c.create_rectangle(10, 10, MAX_HEALTH + 10, 20)
    c.create_rectangle(10, 10, p1_health + 10, 20, fill="red")
    c.create_rectangle(630 - MAX_HEALTH, 10, 630, 20)
    c.create_rectangle(530, 10, 530 + p2_health, 20, fill="green")
    p1_health_history.append(p1_health)
    p2_health_history.append(p2_health)
    root.after(1, update)


root = Tk()
root.title("Battle")
c = Canvas(width=640, height=640, bg="white")
c.pack()

p1_x = 150
p1_dx = 0
p1_r = 25
p1_dr = 0
p1_recoil = 0
p1_drecoil = 0
p1_last_shot = time.time()
p1_health = MAX_HEALTH
p1_health_history = []
p2_x = 490
p2_dx = 0
p2_r = 25
p2_dr = 0
p2_recoil = 0
p2_drecoil = 0
p2_last_shot = time.time()
p2_health = MAX_HEALTH
p2_health_history = []
balls = []

last_time = time.time()
update()

root.bind("<KeyPress>", onpress)
root.bind("<KeyRelease>", onrelease)

root.mainloop()
