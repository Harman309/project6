""" ===========================================================================
File   : cfg.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Michael

Converts an AST to a CFG
=========================================================================== """

# import graphviz as gv

class CFG():
    # head is first Node in CFG
    # last is last Node in CFG
    def __init__(self):
        self.head = None
        self.last = None

class Node():
    def __init__(self):
        self.left = None
        self.right = None

class Edge():

    def __init__(self, data, source, endpoint):
        self.data = data
        self.source = source
        self.endpoint = endpoint

def create_cfg(AST):
    graph = None

    if AST.getValue() == SEQ:
        graph = cfg_seq(AST)
        return graph

    elif AST.getValue() == ASSIGN:
        graph = cfg_assign(AST)
        return graph

    elif AST.getValue() == ASSUME:
        graph = cfg_assume(AST)
        return graph

    elif AST.getValue() == AMB:
        graph = cfg_amb(AST)
        return graph

    elif AST.getValue() == LOOP:
        graph = cfg_loop(AST)
        return graph
'''
Return a control flow graph representing an assign statement 
'''
def cfg_assign(AST):

    statement = get_assignment(AST)
    control = CFG()
    firstNode = Node()
    secondNode = Node()


    firstNode.left = Edge(statement, firstNode, secondNode)

    control.head = firstNode
    control.last = secondNode
    
    return control

'''
Return a control flow graph representing an assum statement
'''
def cfg_assume(AST):
    expr = AST.getLeft()
    statement = get_assumption(expr)
    control = CFG()
    firstNode = Node()
    secondNode = Node()

    firstNode.left = Edge(statement, firstNode, secondNode)

    control.head = firstNode
    control.last = secondNode
    
    return control

def get_assignment(AST):
    statement = ""
    left = AST.getLeft()
    right = AST.getRight()
    statement = left.getValue() + "=" + right.getValue()
    return statement

def get_assumption(AST):
    value = AST.getValue()
    statement = ""
    if (AST.isExpr()) and (value != TRUE and value != FALSE and value != NOT):
        left = AST.getLeft()
        right = AST.getRight()
        statement = "[" + left.getValue() + value + right.getValue() + "]"
    else: 
        statement = value

    return statement

def cfg_seq(AST):
    graph = CFG()
    lcfg = create_cfg(AST.getLeft())
    rcfg = create_cfg(AST.getRight())

    graph.head = lcfg.head

    graph.last = rcfg.last


    epsilonEdge = Edge(EPS, lcfg.last, rcfg.head)

    lcfg.last.left = epsilonEdge

    return graph

def cfg_amb(AST):
    graph = CFG()

    lcfg = create_cfg(AST.getLeft())
    rcfg = create_cfg(AST.getRight())


    beginningNode = Node()
    endNode = Node() 


    beginningLeft = Edge(EPS, beginningNode, lcfg.head)
    beginningRight = Edge(EPS, beginningNode, rcfg.head)

    beginningNode.left = beginningLeft
    beginningNode.right = beginningRight

    endingLeft = Edge(EPS, lcfg.last, endNode)
    endingRight = Edge(EPS, rcfg.last, endNode)

    lcfg.last.left = endingLeft
    rcfg.last.left = endingRight

    graph.head = beginningNode
    graph.last = endNode
    return graph

def cfg_loop(AST):

    graph = CFG()

    loopcfg = create_cfg(AST.getLeft())

    whileNode = Node()
    
    beginningEdge = Edge(EPS, whileNode, loopcfg.head)

    whileNode.left = beginningEdge

    loopEdge = Edge(EPS, loopcfg.last, whileNode)

    loopcfg.last.left = loopEdge

    graph.head = whileNode
    graph.last = whileNode
    return graph 