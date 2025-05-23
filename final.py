import turtle as t
from collections import namedtuple
from itertools import product
Node = namedtuple("Node", ["type", "value", "children"])
t.hideturtle()
t.speed(5)
t.pensize(3)

is_S = []
is_D = []

is_Ss = []
is_Dd = []

def draw_contact(pos=(0, 0)):
    t.color("black")
    t.penup()
    t.goto(pos)
    t.setheading(45)
    t.pendown()
    t.forward(5)
    t.backward(10)
    t.penup()

    t.goto(pos)
    t.setheading(135)
    t.pendown()
    t.forward(5)
    t.backward(10)

def draw_poly(name="A", pos=(0, 0), length=100):
    t.penup()
    t.setheading(90)
    t.goto(pos)
    t.pendown()

    t.color("black")
    t.write(name, font=("Arial", 12, "normal"))

    t.color("red")
    t.pendown()
    t.backward(length)

    t.penup()

def draw_out(pos=(0, 0)):
    t.setheading(0)
    t.penup()
    t.goto(pos)
    t.pendown()
    t.color("blue")
    t.forward(50)
    t.color("black")
    t.write("OUT", font=("Arial", 12, "normal"))

    t.penup()

def draw_vdd(pos=(0, 0)):
    t.penup()
    t.setheading(0)  
    t.goto(pos)
    t.pendown()

    t.color('blue')
    t.forward(100)
    t.backward(200)
    t.color("black")
    t.write("VDD", font=("Arial", 15, "normal"))

    t.penup()

def draw_gnd(pos=(0, 0)):
    t.penup()
    t.setheading(0)
    t.goto(pos)
    t.pendown()

    t.color('blue')
    t.forward(100)
    t.backward(200)
    t.color("black")
    t.write("GND", font=("Arial", 15, "normal"))

    t.penup()

def draw_pdiff(pos=(0, 0)):
    t.penup()
    t.goto(pos)
    t.setheading(0)
    t.pendown()

    t.color("yellow")
    t.forward(30)
    t.color("black")
    t.write("S", align="right", font=("Arial", 12, "normal"))
    is_S.append(t.pos())
    
    t.color("yellow")
    t.backward(60)
    t.color("black")
    t.write("D", font=("Arial", 12, "normal"))
    is_D.append(t.pos())

    t.penup()

def draw_ndiff(pos=(0, 0)):
    t.penup()
    t.goto(pos)
    t.setheading(0)
    t.pendown()

    t.color("green")
    t.backward(30)
    t.color("black")
    t.write("S", font=("Arial", 12, "normal"))
    is_S.append(t.pos())
    
    t.color("green")
    t.forward(60)
    t.color("black")
    t.write("D", align="right", font=("Arial", 12, "normal"))
    is_D.append(t.pos())

    t.penup()

def draw_op(name="A", pos=(0, 0), pdiff = True): #a
    draw_poly(name, pos, 50)
    if pdiff:
        draw_pdiff((pos[0], pos[1]-25))
    else:
        draw_ndiff((pos[0], pos[1]-25))

def concor_or(pos, pos2):
    t.pendown()
    for i in range(len(pos)):
        if i + 1 < len(pos2):
            sx, sy = pos[i]
            dx, dy = pos2[i+1]
            mid_y = (sy + dy) / 2
            t.penup()
            t.goto(sx, sy)
            t.pendown()
            draw_contact((sx, sy))
            t.pencolor("blue")
            t.goto(sx, sy)
            t.goto(sx, mid_y)  
            t.goto(dx, mid_y)  
            t.goto(dx, dy)
            draw_contact((dx, dy))
            t.penup()

def concor_and(pos, pos2):
    t.pendown()
    for i in range(len(pos)):
        if i + 1 < len(pos2):
            sx, sy = pos[i]
            dx, dy = pos2[i + 1]
            mid_y = sy + 20
            mid_x = dx
            t.penup()
            t.goto(sx, sy)
            t.pencolor("blue")
            t.pendown()
            draw_contact((sx, sy))
            t.color("blue")
            t.penup()
            t.goto(sx, sy)
            t.pendown()
            t.goto(sx, mid_y)
            t.goto(mid_x, mid_y)
            t.goto(dx, dy)
            draw_contact((dx, dy))
            t.penup()

def reset_queue():
    global is_S, is_D
    is_S = []
    is_D = []

def tokenize(expr): 
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isalpha():
            tokens.append(c)
        elif c in "+.()":
            tokens.append(c)
        i += 1
    return tokens

def parse_expr(tokens): 
    def parse_term():
        if tokens and tokens[0] == "(":
            tokens.pop(0)
            node = parse_or()
            tokens.pop(0)  # remove ")"
            return node
        else:
            return Node("VAR", tokens.pop(0), [])

    def parse_and():
        nodes = [parse_term()]
        while tokens and tokens[0] == ".":
            tokens.pop(0)
            nodes.append(parse_term())
        if len(nodes) == 1:
            return nodes[0]
        return Node("AND", None, nodes)

    def parse_or():
        nodes = [parse_and()]
        while tokens and tokens[0] == "+":
            tokens.pop(0)
            nodes.append(parse_and())
        if len(nodes) == 1:
            return nodes[0]
        return Node("OR", None, nodes)

    return parse_or()

def extract_sum_of_products(expr): 
    tokens = tokenize(expr)
    tree = parse_expr(tokens)

    def expand(node):
        if node.type == "VAR":
            return [[node.value]]
        elif node.type == "AND":
            expanded = [expand(child) for child in node.children]
                  
            combined = []
            for prod_terms in product(*expanded):
                flat = []
                for group in prod_terms:
                    flat.extend(group)
                combined.append(flat)
            return combined
        elif node.type == "OR":
            
            result = []
            for child in node.children:
                result.extend(expand(child))
            return result
        else:
            return []

    sop_terms = expand(tree)

    unique_terms = set([".".join(sorted(term)) for term in sop_terms])
    return sorted(unique_terms)

def draw_sop_expression(expr,  start_pos=(0, 0), pdiff=True):
    sop = extract_sum_of_products(expr)
    x, y = start_pos
    spacing_y = 80
    spacing_x = 80

    is_Ss = []
    is_Dd = []

    for op in sop:
        vars = op.split(".")
        if pdiff: #and
            if len(vars) == 1:
                draw_op(vars[0], (x, y), pdiff)
                is_Ss = is_Ss + is_S # lưu đầu
                is_Dd = is_Dd + is_D # lưu đuôi
                reset_queue()
            elif len(vars) == 2:
                draw_op(vars[0], (x, y), pdiff)
                is_Ss = is_Ss + is_S # lưu đầu
                draw_op(vars[1], (x + 80, y), pdiff)
                concor_and(is_S, is_D)
                is_D.pop(0)
                is_Dd = is_Dd + is_D # lưu đuôi
                reset_queue()
            elif len(vars) == 3:
                draw_op(vars[0], (x, y), pdiff) # vẽ đầu
                is_Ss = is_Ss + is_S # lưu đầu
                draw_op(vars[1], (x + 80, y), pdiff) # vẽ giữa
                draw_op(vars[2], (x + 160, y), pdiff) # vẽ cuối
                concor_and(is_S, is_D)
                is_D.pop(0)
                is_D.pop(0)
                is_Dd = is_Dd + is_D # lưu đuôi
                reset_queue()
            y -= spacing_y
            
        else: #or
            if len(vars) == 1:
                draw_op(vars[0], (x, y), pdiff)
                is_Ss = is_Ss + is_S # lưu đầu
                is_Dd = is_Dd + is_D # lưu đuôi
                reset_queue()
            elif len(vars) == 2:
                draw_op(vars[0], (x, y), pdiff)
                is_Ss = is_Ss + is_S # lưu đầu
                draw_op(vars[1], (x, y - 80), pdiff)
                concor_or(is_S, is_D)
                is_D.pop(0)
                is_Dd = is_Dd + is_D # lưu đuôi
                reset_queue()
            elif len(vars) == 3:
                draw_op(vars[0], (x, y), pdiff) # vẽ đầu
                is_Ss = is_Ss + is_S # lưu đầu
                draw_op(vars[1], (x, y - 80), pdiff) # vẽ giữa
                draw_op(vars[2], (x, y - 160), pdiff) # vẽ cuối
                concor_or(is_S, is_D)
                is_D.pop(0)
                is_D.pop(0)
                is_Dd = is_Dd + is_D # lưu đuôi
                reset_queue()
            x += spacing_x
    
   
    if len(is_Ss) > 0 and len(is_Dd) > 1:
        if pdiff:
            concor_or(is_Dd, is_Ss)
        else:
            concor_and(is_Dd, is_Dd)
            concor_and(is_Ss, is_Ss)

def draw_layout(expr, center_x=-250, start_y=300):
    t.penup()
    vdd_y = start_y
    t.pendown()
    draw_vdd((center_x, vdd_y))
    pdiff_y = t.ycor() - 50
    draw_sop_expression(expr, (center_x, pdiff_y), pdiff=True)
    out_y = t.ycor() - 50
    draw_out((center_x + 160, out_y))
    ndiff_y = t.ycor() - 50
    draw_sop_expression(expr, (center_x, ndiff_y), pdiff=False)
    gnd_y = t.ycor() - 200
    draw_gnd((center_x, gnd_y))
    t.penup()

expr = input("Enter a  expression ").strip()
sop = extract_sum_of_products(expr)

print(sop)
draw_layout(expr)

t.done()

