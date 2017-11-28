""" ===========================================================================
File   : cfg.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Michael

Converts an AST to a CFG
=========================================================================== """

# import graphviz as gv
from lib import *

class CFG():
    # head is first Node in CFG
    # last is last Node in CFG
    def __init__(self):
        self._head = None
        self._last = None

    def getHead(self):
        return self._head

    def getLast(self):
        return self._last

    def setHead(self, head):
        self._head = head

    def setLast(self, last):
        self._last = last

class Node():
    # left and right are Edge values
    def __init__(self):
        self._left = None
        self._right = None

    def getLeft(self):
        return self._left 

    def getRight(self):
        return self._right 

    def setLeft(self, left):
        self._left = left

    def setRight(self, right):
        self._right = right

class Edge():
    def __init__(self, data, source, endpoint):
        self._data = data
        self._source = source
        self._endpoint = endpoint

    def getSource(self):
        return self._source

    def getEndpoint(self):
        return self._endpoint 

    def getData(self):
        return self._data

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

    edge = Edge(statement, firstNode, secondNode)

    firstNode.setLeft(edge)

    control.setHead(firstNode)
    control.setLast(secondNode)
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

    edge = Edge(statement, firstNode, secondNode)
    firstNode.setLeft(edge)

    control.setHead(firstNode)
    control.setLast(secondNode)
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

    graph.setHead(lcfg.getHead())
    graph.setLast(rcfg.getLast())

    epsilonEdge = Edge(EPS, lcfg.getLast(), rcfg.getHead())

    (lcfg.getLast()).setLeft(epsilonEdge)
    return graph

def cfg_amb(AST):
    graph = CFG()
    lcfg = create_cfg(AST.getLeft())
    rcfg = create_cfg(AST.getRight())
    beginningNode = Node()
    endNode = Node() 

    beginningLeft = Edge(EPS, beginningNode, lcfg.getHead())
    beginningRight = Edge(EPS, beginningNode, rcfg.getHead())

    beginningNode.setLeft(beginningLeft)
    beginningNode.setRight(beginningRight)

    endingLeft = Edge(EPS, lcfg.getLast(), endNode)
    endingRight = Edge(EPS, rcfg.getLast(), endNode)

    (lcfg.getLast()).setLeft(endingLeft)
    (rcfg.getLast()).setLeft(endingLeft)

    graph.setHead(beginningNode)
    graph.setLast(endNode)
    return graph

def cfg_loop(AST):
    graph = CFG()
    loopcfg = create_cfg(AST.getLeft())
    whileNode = Node()
    
    beginningEdge = Edge(EPS, whileNode, loopcfg.getHead())

    whileNode.setLeft(beginningEdge)

    loopEdge = Edge(EPS, loopcfg.getLast(), whileNode)

    (loopcfg.getLast()).setLeft(loopEdge)

    graph.setHead(whileNode)
    graph.setLast(whileNode)
    return graph 