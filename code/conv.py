""" ===========================================================================
File   : conv.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Performs conversion from CFG to AST object
=========================================================================== """
from lib import *
from ast import *
from cfg import *

""" ======================================================================= """
""" ==================     PRIVATE FUNCTIONS      ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return next node following this one in SEQ; if exists
--------------------------------------------------------------------------- '''
def _get_next_seq(node, node_type):
    def _next_seq(ep):
        next_edge = ep.getOutgoingEdges()
        # Either has next SEQ, or this is the terminal node
        assert len(next_edge) in [0, 1]
        # No next SEQ
        if len(next_edge) == 0:
            return None
        # Next SEQ
        elif len(next_edge) == 1:
            return next(iter(next_edge)).getEndpoint()

    if node_type in [ASSIGN, ASSUME]:
        return _next_seq(next(iter(node.getOutgoingEdges())).getEndpoint())
        
    elif node_type == AMB:
        return _next_seq(node.getAMBExit())

    elif node_type == LOOP:
        # node is it's own end point
        next_edge = node.getOutgoingEdges()
        # Either has only LOOP_ENTRY (loop is sub-program's terminal node), 
        # ... or has a next SEQ
        assert len(next_edge) in [1, 2]
        # No next SEQ; only outgoing is LOOP_ENTRY
        if len(next_edge) == 1:
            return None
        # Next SEQ
        elif len(next_edge) == 2:
            for e in next_edge:
                if not e.getType() == LOOP_ENTRY:
                    return e.getEndpoint()
            raise ValueError("Encountered LOOP node with two outgoing edges, but no next SEQ edge!")

''' ---------------------------------------------------------------------------
Return AST representation of assign flow {  (node) --- VAR=EXPR --> ( )  }
at given node
--------------------------------------------------------------------------- '''
def _assign_flow_to_ast(node):
    assert node.getType() == ASSIGN
    assert len(node.getOutgoingEdges()) == 1

    return get_assignment_ast(next(iter(node.getOutgoingEdges())).getData())

''' ---------------------------------------------------------------------------
Return AST representation of assign flow {  (node) --- VAR=EXPR --> ( )  }
at given node
--------------------------------------------------------------------------- '''
def _assume_flow_to_ast(node):
    assert node.getType() == ASSUME
    assert len(node.getOutgoingEdges()) == 1

    return get_assumption_ast(next(iter(node.getOutgoingEdges())).getData())

''' ---------------------------------------------------------------------------
Build a sequence AST, with left_ast as left and AST defined by CFG at node's
next_node as right; if node does not have a next_node, then just return left_ast
--------------------------------------------------------------------------- '''
def _build_seq_ast(left_ast, node, node_type):
    # Check for next SEQ
    next_node = _get_next_seq(node, node_type)
    if next_node:
        # Build the SEQ AST and return
        ast = AST(SEQ)
        ast.setLeft(left_ast)
        ast.setRight(_cfg_node_to_ast(next_node))
        return ast

    # No next SEQ, just return the ASSIGN | ASSUME AST
    else:
        return left_ast

''' ---------------------------------------------------------------------------
Return AST representation of CFG with given root node:
- Root node is expected to be one of type: ASSIGN, ASSUME, AMB, LOOP
--------------------------------------------------------------------------- '''
def _cfg_node_to_ast(node):
    node_type = node.getType()
    assert node_type in ATOMS # [ASSIGN, ASSUME, AMB, LOOP]

    if node_type in [ASSIGN, ASSUME]:
        # Get the ASSIGN | ASSUME AST
        if node_type == ASSIGN:
            ast = _assign_flow_to_ast(node)
        elif node_type == ASSUME:
            ast = _assume_flow_to_ast(node)

    elif node_type == AMB:        
        # Snip AMB_JOIN edges (that close AMB) to form a sub-CFG for each branch
        amb_join_edges = node.getAMBExit().getIncomingEdges()
        assert len(amb_join_edges) == 2
        for e in amb_join_edges:
            assert e.getType() == AMB_JOIN
            e.getSource().delOutgoingEdge(e)

        # Get each of AMB path's head nodes
        amb_split_edges = node.getOutgoingEdges()
        assert len(amb_split_edges) == 2
        branch_nodes = []
        for e in amb_split_edges:
            assert e.getType() == AMB_SPLIT
            branch_nodes.append(e.getEndpoint())
        assert len(branch_nodes) == 2

        # Recursively build the AMB child paths
        ast = AST(AMB)
        ast.setLeft(_cfg_node_to_ast(branch_nodes[0]))
        ast.setRight(_cfg_node_to_ast(branch_nodes[1]))

    elif node_type == LOOP:
        # Snip LOOP_BACK edge (incoming to node) to form a sub-CFG for loop body
        loop_in_edges = node.getIncomingEdges()
        assert len(loop_in_edges) == 2
        snipped = False
        for e in loop_in_edges:
            if e.getType() == LOOP_BACK:
                e.getSource().delOutgoingEdge(e)
                snipped = True
        assert snipped

        # Get the LOOP_ENTRY edge and loop body entry Node
        loop_out_edges = node.getOutgoingEdges()
        assert len(loop_out_edges) in [1, 2]
        loop_entry_node = None
        for e in loop_out_edges:
            if e.getType() == LOOP_ENTRY:
                loop_entry_node = e.getEndpoint()
        assert loop_entry_node

        # Recursively build the LOOP body AST
        ast = AST(LOOP)
        ast.setLeft(_cfg_node_to_ast(loop_entry_node))

    else:
        raise ValueError("Unsupported node type encountered during CFG to AST conversion: " + node_type)
    
    # Build SEQ, if necessary, and return result
    return _build_seq_ast(ast, node, node_type)



""" ======================================================================= """
""" ================== PUBLIC INTERFACE =================================== """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return AST representation of given CFG; warning: CFG will be modified - either
save it first or pass in a deep copy
--------------------------------------------------------------------------- '''
def to_ast(cfg):
    return _cfg_node_to_ast(cfg.getEntryNode())