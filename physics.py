"""
Not used in main.py, but could be useful
"""
from tkinter import Canvas
from typing import Literal
import math
import time


class Physics:
    """
    A parent for all Objects
    """

    def __init__(self, canv: Canvas, gravity: float = 100, friction: float = 0.1) -> None:
        """
        Initiates the Physics class
        :param canv: a tkinter.Canvas to draw on
        :param gravity: the default gravity for all objects to use
        :param friction: the default friction for all objects to use
        """
        self.canv = canv
        self.gravity = gravity
        self.friction = friction
        self.width = int(self.canv.cget("width"))
        self.height = int(self.canv.cget("height"))
        self.objs: list[Object] = []

    def add(self, obj) -> None:
        """
        Adds a new Object. Used internally by the Object __init__ function
        :param obj:
        :return:
        """
        self.objs.append(obj)

    def draw(self, delete_all: bool = True) -> None:
        """
        Draw all Objects
        :param delete_all: if True, deletes everything beforehand
        :return: None
        """
        if delete_all:
            self.canv.delete("all")
        for obj in self.objs:
            obj.draw()

    def sim(self) -> None:
        """
        Simulates the physics for all Objects
        :return: None
        """
        for obj in self.objs:
            obj.sim()

    def tick(self, delete_all: bool = True) -> None:
        """
        Simulates the physics for all Objects, then draws them
        :param delete_all: if True, deletes everything before drawing the Objects
        :return: None
        """
        self.sim()
        self.draw(delete_all)


class Object:
    """
    A physics Object
    """

    def __init__(self, phys: Physics, typ: Literal["rect", "circle"], x: float, y: float,
                 width: float, height: float = 0, r: float = 0, gravity_amp: float = 1, hitbox: bool = True,
                 nocollide: list | tuple = (), movable: bool = True, bounce: float = 1, friction: float = -1,
                 draw: bool = True, mass: float = -1, fill: str = "red", outline: str = "black") -> None:
        """
        Initiate the Object
        :param phys: the parent Physics object
        :param typ: Object type: "rect" or "circle"
        :param x: Object x
        :param y: Object y
        :param width: Object width (diameter for a circle)
        :param height: Object height (if Object.typ == "rect")
        :param r: Object rotation
        :param gravity_amp: Gravity amplifier (0 for no gravity, 1 for Physics.gravity)
        :param hitbox: True if the Object should have a hitbox (other objects with hitboxes will collide)
        :param nocollide: Objects this Object should not collide with
        :param movable: True if the Object should be movable
        :param bounce: bounciness on collision
        :param friction: friction, if -1, inherits from Physics
        :param draw: True if the Object should be drawn
        :param mass: the Object's mass (used for collision)
        :param fill: Object fill
        :param outline: Object outline
        """
        self.phys: Physics = phys
        self.canv: Canvas = self.phys.canv
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.r: float = r
        self.gravity_amp: float = gravity_amp
        self.hitbox: bool = hitbox
        self.nocollide: list[Object] = list(nocollide)
        self.movable: bool = movable
        self.bounce: float = bounce
        self.friction: float = friction
        if self.friction == -1:
            self.friction = self.phys.friction
        self.do_draw: bool = draw
        self.mass: float = mass
        self.dx: float = 0
        self.dy: float = 0
        self.dr: float = 0
        if typ not in ("rect", "circle"):
            raise ValueError(f"\"{typ}\" is not a valid object type (\"rect\" or \"circle\")")
        self.typ: Literal["rect", "circle"] = typ
        if self.typ == "circle":
            self.height = self.width
        if self.mass == -1:
            if self.typ == "rect":
                self.mass = self.width * self.height
            elif self.typ == "circle":
                self.mass = math.pi * (self.width / 2) * (self.width / 2)
        self.fill: str = fill
        self.outline: str = outline
        self.last_time: float = time.time()
        self.phys.add(self)

    def draw(self) -> None:
        """
        Draw the Object (no physics)
        :return: None
        """
        if not self.do_draw:
            return
        if self.typ == "rect":
            self.canv.create_polygon(self.get_points(), fill=self.fill, outline=self.outline)
        elif self.typ == "circle":
            self.canv.create_oval(self.x - self.width / 2, self.y - self.width / 2,
                                  self.x + self.width / 2, self.y + self.width / 2,
                                  fill=self.fill, outline=self.outline)
        else:
            raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")

    def sim(self) -> None:
        """
        Simulate the Object's physics
        :return: None
        """
        if self.hitbox and self.movable:
            for idx, obj in enumerate(self.phys.objs):
                if (obj.hitbox and obj is not self and obj not in self.nocollide and self not in obj.nocollide
                        and self.collides(obj) and (not obj.movable or idx < self.phys.objs.index(self))):
                    if self.typ == "rect":
                        if obj.typ == "rect":
                            pass
                        elif obj.typ == "circle":
                            point = rotate_point(obj.x - self.x, obj.y - self.y, math.radians(-self.r))
                            if abs(point[0]) > self.width / 2 - obj.width / 4:
                                ax = math.radians(self.r)
                            else:
                                ax = math.radians(self.r) + math.pi / 2
                            ax += ax - math.atan2(obj.dy, obj.dx) + math.pi
                            self.dx = math.cos(ax) * math.hypot(self.dx, self.dy) * self.bounce * obj.bounce
                            self.dy = math.sin(ax) * math.hypot(self.dx, self.dy)
                            if obj.movable:
                                obj.dx += -self.dx / 2
                                obj.dy += -self.dy / 2
                                self.dx /= 2
                                self.dy /= 2
                        else:
                            raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")
                    elif self.typ == "circle":
                        if obj.typ == "rect":
                            point = rotate_point(self.x - obj.x, self.y - obj.y, math.radians(-obj.r))
                            if abs(point[0]) > obj.width / 2 - self.width / 4:
                                ax = math.radians(obj.r)
                            else:
                                ax = math.radians(obj.r) + math.pi / 2
                            ax += ax - math.atan2(self.dy, self.dx) + math.pi
                            self.dx = math.cos(ax) * math.hypot(self.dx, self.dy) * self.bounce * obj.bounce
                            self.dy = math.sin(ax) * math.hypot(self.dx, self.dy)
                            if obj.movable:
                                obj.dx += -self.dx / 2
                                obj.dy += -self.dy / 2
                                self.dx /= 2
                                self.dy /= 2
                        elif obj.typ == "circle":
                            ax = math.atan2(obj.y - self.y, obj.x - self.x) + math.pi
                            ax += ax - math.atan2(self.dy, self.dx) + math.pi
                            self.dx = math.cos(ax) * math.hypot(self.dx, self.dy)
                            self.dy = math.sin(ax) * math.hypot(self.dx, self.dy)
                            if obj.movable:
                                obj.dx += -self.dx / 2
                                obj.dy += -self.dy / 2
                                self.dx /= 2
                                self.dy /= 2
                        else:
                            raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")
                    else:
                        raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")
        tm = time.time() - self.last_time
        self.dy += self.phys.gravity * self.gravity_amp * tm
        self.x += self.dx * tm
        self.y += self.dy * tm
        self.r = (self.r + self.dr * tm) % 360
        self.dx -= self.dx * self.friction * tm
        self.dy -= self.dy * self.friction * tm
        self.dr -= self.dr * self.friction * tm
        self.last_time = time.time()

    def tick(self) -> None:
        """
        Simulate the physics, then draw (use Physics.tick() if you want to tick all Objects)
        :return: None
        """
        self.sim()
        self.draw()

    def get_points(self) -> list[tuple[float, float]]:
        if self.typ == "rect":
            rad = math.radians(self.r)
            p1 = rotate_point(-self.width / 2, -self.height / 2, rad)
            p2 = rotate_point(self.width / 2, -self.height / 2, rad)
            p3 = rotate_point(self.width / 2, self.height / 2, rad)
            p4 = rotate_point(-self.width / 2, self.height / 2, rad)
            return [(self.x + p1[0], self.y + p1[1]),
                    (self.x + p2[0], self.y + p2[1]),
                    (self.x + p3[0], self.y + p3[1]),
                    (self.x + p4[0], self.y + p4[1])]
        elif self.typ == "circle":
            return [(self.x, self.y)]
        else:
            raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")

    def isin(self, x: float, y: float) -> bool:
        """
        Whether a point is inside the Object
        :param x: point x
        :param y: point y
        :return: True if the point is inside the object, False otherwise
        """
        if self.typ == "rect":
            point = rotate_point(x - self.x, y - self.y, math.radians(-self.r))
            return -self.width / 2 <= point[0] <= self.width / 2 and -self.height / 2 <= point[1] <= self.height / 2
        elif self.typ == "circle":
            return math.hypot(x - self.x, y - self.y) <= self.width / 2
        else:
            raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")

    def collides(self, obj) -> bool:
        """
        Check if this Object collides with another Object
        :param obj: Object to check collision with
        :return: True if this Object collides with obj, False otherwise
        """
        if self.typ == "rect":
            if obj.typ == "rect":  # Algorithm using the Separating Axis Theorem inspired by ChatGPT
                axis = [(math.cos(math.radians(self.r)), math.sin(math.radians(self.r))),
                        (math.cos(math.radians(self.r + 90)), math.sin(math.radians(self.r + 90))),
                        (math.cos(math.radians(obj.r)), math.sin(math.radians(obj.r))),
                        (math.cos(math.radians(obj.r + 90)), math.sin(math.radians(obj.r + 90)))]
                points = self.get_points()
                points_obj = obj.get_points()
                for ax in axis:
                    proj = project_polygon(points, ax)
                    proj_obj = project_polygon(points_obj, ax)
                    if not (proj[0] <= proj_obj[0] <= proj[1] or proj[0] <= proj_obj[1] <= proj[1] or
                            proj_obj[0] <= proj[0] <= proj_obj[1] or proj_obj[0] <= proj[1] <= proj_obj[1]):
                        return False
                return True
            elif obj.typ == "circle":  # Not very precise
                self.width += obj.width
                self.height += obj.width
                ans = self.isin(obj.x, obj.y)
                self.width -= obj.width
                self.height -= obj.width
                return ans
            else:
                raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")
        elif self.typ == "circle":
            if obj.typ == "rect":
                return obj.collides(self)
            elif obj.typ == "circle":
                return math.hypot(obj.x - self.x, obj.y - self.y) <= self.width / 2 + obj.width / 2
            else:
                raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")
        else:
            raise ValueError(f"\"{self.typ}\" is not a valid object type (\"rect\" or \"circle\")")


def minmax(val: float, mn: float, mx: float) -> float:
    """
    Bind a value to a range
    :param val: value
    :param mn: minimum value
    :param mx: maximum value
    :return: bound value
    """
    return min(mx, max(mn, val))


def rotate_point(x: float, y: float, r: float) -> tuple[float, float]:
    """
    Rotate a point
    :param x: relative x
    :param y: relative y
    :param r: rotation
    :return: point coordinates (x, y)
    """
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)


def project_polygon(points: list[tuple[float, float]], axis: tuple[float, float]) -> tuple[float, float]:
    """
    Made by ChatGPT
    Algorithm using the Separating Axis Theorem
    Get the projection of a polygon on an axis
    :param points: polygon points
    :param axis: axis to project on
    :return: (projection start, projection end)
    """
    min_p = float("inf")
    max_p = float("-inf")

    for x, y in points:
        projection = x * axis[0] + y * axis[1]  # dot product
        min_p = min(min_p, projection)
        max_p = max(max_p, projection)

    return min_p, max_p


if __name__ == "__main__":
    from tkinter import Tk

    root = Tk()
    root.title("Physics")

    c = Canvas(root, width=640, height=640, bg="white")
    c.pack()
    p = Physics(c, friction=0)
    rect = Object(p, "rect", 320, 320, 100, 20, gravity_amp=0, movable=False)
    circle = Object(p, "circle", 370, 320, 20, gravity_amp=0, movable=False)
    r1 = Object(p, "rect", 320, 420, 50, 25, gravity_amp=0)
    r2 = Object(p, "rect", 420, 420, 50, 25, r=45, gravity_amp=0)
    rect.nocollide.append(circle)
    r1.nocollide.append(r2)
    ramp = Object(p, "rect", 200, 320, 100, 20, -45, gravity_amp=0, fill="green", movable=False)
    ball = Object(p, "circle", 200, 220, 20, gravity_amp=1)
    r2.dx = 20
    rect.dr = -20


    def onclick(e):
        ball.x = e.x
        ball.y = e.y
        ball.dx = ball.dy = 0


    def update():
        pnt = rotate_point(rect.width / 2 - 10, 0, math.radians(rect.r))
        rect.x, rect.y = 320 + pnt[0], 320 + pnt[1]
        if minmax(rect.r, 271, 359) != rect.r:
            rect.dr = -rect.dr
        if rect.collides(circle):
            rect.fill = "green"
            circle.fill = "green"
        else:
            rect.fill = "red"
            circle.fill = "red"
        if r2.collides(r1):
            r2.fill = "green"
            r1.fill = "green"
        else:
            r2.fill = "red"
            r1.fill = "red"
        if r2.x < 350 or r2.x > 420:
            r2.dx = -r2.dx
        if ball.y > 400:
            ball.y = 220
            ball.dy = 0
            ball.x = 200
            ball.dx = 0
        p.draw()
        p.sim()
        root.after(1, update)


    root.bind("<Button-1>", onclick)

    update()

    root.mainloop()
