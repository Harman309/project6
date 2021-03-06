""" ===========================================================================
File   : norm.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Normalizes given AST objects; removes all back edges except 1 by applying 
3 different algorithms for 3 different cases:

Handles Sequential (SEQ), Ambiguous (AMB), and Nested (LOOP) combinations
=========================================================================== """
from lib import *
from ast import *
from cfg import *
from conv import _get_next_seq
from conv import to_ast

""" ======================================================================= """
""" ==================     PRIVATE FUNCTIONS      ========================= """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return edges in set that are not LOOP_BACK or AMB_JOIN
--------------------------------------------------------------------------- '''
def _get_valid_edges(edges):
    return [e for e in edges if e.getType() not in [LOOP_BACK, AMB_JOIN]]

''' ---------------------------------------------------------------------------
Return the LOOP_ENTRY edge in set
--------------------------------------------------------------------------- '''
def _get_loop_entry_edge(node):
    for e in node.getOutgoingEdges():
        if e.getType() == LOOP_ENTRY:
            return e
    raise ValueError("Calling _get_loop_entry_edge when no LOOP_ENTRY edge exists in set!")

''' ---------------------------------------------------------------------------
Return the LOOP_OUT (not LOOP_ENTRY) edge in set; must exist
--------------------------------------------------------------------------- '''
def _get_loop_out_edge(node):
    for e in node.getOutgoingEdges():
        if e.getType() != LOOP_ENTRY:
            return e
    raise ValueError("Calling _get_loop_out_edge when no LOOP_OUT edge exists in set!")

''' ---------------------------------------------------------------------------
Return the LOOP_IN (not LOOP_BACK) edge in set; must exist
--------------------------------------------------------------------------- '''
def _get_loop_in_edge(node):
    for e in node.getIncomingEdges():
        if e.getType() != LOOP_BACK:
            return e
    raise ValueError("Calling _get_loop_in_edge when no LOOP_IN edge exists in set!")

''' ---------------------------------------------------------------------------
Return the LOOP_BACK edge in set; must exist
--------------------------------------------------------------------------- '''
def _get_loop_back_edge(node):
    for e in node.getIncomingEdges():
        if e.getType() == LOOP_BACK:
            return e
    raise ValueError("Calling _get_loop_back_edge when no LOOP_BACK edge exists in set!")

''' ---------------------------------------------------------------------------
Return the previous node (for non-LOOP node)
--------------------------------------------------------------------------- '''
def _get_prev(node):
    in_edges = node.getIncomingEdges()
    assert len(in_edges) == 1
    for e in in_edges:
        return e.getSource()

''' ---------------------------------------------------------------------------
Remove all 4 edges (LOOP_ENTRY, LOOP_OUT; and LOOP_BACK, LOOP_IN)
--------------------------------------------------------------------------- '''
def _nuke_while_node(cfg, node):
    loop_in_edges = node.getIncomingEdges()
    assert len(loop_in_edges) == 2
    for e in loop_in_edges:
        e.getSource().delOutgoingEdge(e)
        cfg.removeEdges(set([e]))

    loop_out_edges = node.getOutgoingEdges()
    assert len(loop_out_edges) == 2
    for e in loop_out_edges:
        e.getEndpoint().delIncomingEdge(e)
        cfg.removeEdges(set([e]))

''' ---------------------------------------------------------------------------
Remove all 4 edges (2x AMB_SPLIT, 2x AMB_JOIN)
--------------------------------------------------------------------------- '''
def _nuke_amb_node(cfg, node):
    amb_split_edges = node.getOutgoingEdges()
    assert len(amb_split_edges) == 2
    for e in amb_split_edges:
        assert e.getType() == AMB_SPLIT
        e.getEndpoint().delIncomingEdge(e)
        cfg.removeEdges(set([e]))

    for e in node.getIncomingEdges():
        e.getSource().delOutgoingEdge(e)
        cfg.removeEdges(set([e]))

    exit_node = node.getAMBExit()
    amb_join_edges = exit_node.getIncomingEdges()
    assert len(amb_join_edges) == 2
    for e in amb_join_edges:
        assert e.getType() == AMB_JOIN
        e.getSource().delOutgoingEdge(e)
        cfg.removeEdges(set([e]))

    for e in exit_node.getOutgoingEdges():
        e.getEndpoint().delIncomingEdge(e)
        cfg.removeEdges(set([e]))


''' ---------------------------------------------------------------------------
Return a CFG with two nodes and edge: flag (type, = or ==) val
--------------------------------------------------------------------------- '''
def _flag_cfg(cfg, flag, t, val):
    flag_cfg = CFG()
    entryNode = Node(t)
    exitNode = Node()
    edge = Edge(flag + (" = " if t==ASSIGN else " == ") + val, entryNode, exitNode)
    entryNode.addOutgoingEdge(edge)
    exitNode.addIncomingEdge(edge)
    flag_cfg.setEntryNode(entryNode)
    flag_cfg.setExitNode(exitNode)

    cfg.unionEdges(set([edge]))

    return flag_cfg, entryNode, exitNode

''' ---------------------------------------------------------------------------
Connect two nodes in cfg with epsilon edge _connect(src, dst, cfg)
--------------------------------------------------------------------------- '''
def _connect(cfg, src, dst):
    epsilonEdge = Edge(EPS, src, dst, SEQ_TRANS)
    src.addOutgoingEdge(epsilonEdge)
    dst.addIncomingEdge(epsilonEdge)
    cfg.unionEdges(set([epsilonEdge]))

''' ---------------------------------------------------------------------------
Chain two CFGs together with epsilon edge _chain(cfg, first_cfg, second_cfg)
--------------------------------------------------------------------------- '''
def _chain(cfg, first_cfg, second_cfg):
    chained_cfg = CFG()
    chained_cfg.setEntryNode(first_cfg.getEntryNode())
    chained_cfg.setExitNode(second_cfg.getExitNode())
    _connect(cfg, first_cfg.getExitNode(), second_cfg.getEntryNode())
    return chained_cfg


''' ---------------------------------------------------------------------------
Create AMB CFG and return with left_CFG and right_CFG
--------------------------------------------------------------------------- '''
def _create_amb(cfg, lcfg, rcfg):
    amb_cfg = CFG()
    exitNode = Node()
    entryNode = Node(AMB, exitNode)

    # Epsilon transitions out from entryNode (x2)
    entryLeftOutEdge  = Edge(EPS, entryNode, lcfg.getEntryNode(), AMB_SPLIT)
    entryRightOutEdge = Edge(EPS, entryNode, rcfg.getEntryNode(), AMB_SPLIT)
    entryNode.addOutgoingEdge(entryLeftOutEdge)
    entryNode.addOutgoingEdge(entryRightOutEdge)
    lcfg.getEntryNode().addIncomingEdge(entryLeftOutEdge)
    rcfg.getEntryNode().addIncomingEdge(entryRightOutEdge)

    # Epsilon transitions in to exitNode (x2)
    exitLeftInEdge  = Edge(EPS, lcfg.getExitNode(), exitNode, AMB_JOIN)
    exitRightInEdge = Edge(EPS, rcfg.getExitNode(), exitNode, AMB_JOIN)
    lcfg.getExitNode().addOutgoingEdge(exitLeftInEdge)
    rcfg.getExitNode().addOutgoingEdge(exitRightInEdge)
    exitNode.addIncomingEdge(exitLeftInEdge)
    exitNode.addIncomingEdge(exitRightInEdge)

    # Encapsulate entry/ exit nodes in CFG, and return
    amb_cfg.setEntryNode(entryNode)
    amb_cfg.setExitNode(exitNode)

    cfg.unionEdges(set([entryLeftOutEdge, entryRightOutEdge, exitLeftInEdge, exitRightInEdge]))

    return amb_cfg

''' ---------------------------------------------------------------------------
Create LOOP CFG and return with body_CFG
--------------------------------------------------------------------------- ''' 
def _create_loop(cfg, body_cfg):
    while_cfg = CFG()
    whileNode = Node(LOOP) # Both entry and exit

    # Epsilon transition to enter the main LOOP body (from whileNode)
    loopEntryEdge = Edge(EPS, whileNode, body_cfg.getEntryNode(), LOOP_ENTRY)
    whileNode.addOutgoingEdge(loopEntryEdge)
    body_cfg.getEntryNode().addIncomingEdge(loopEntryEdge)

    # Epsilon transition to exit the main LOOP body (back to whileNode)
    loopBackEdge = Edge(EPS, body_cfg.getExitNode(), whileNode, LOOP_BACK)
    body_cfg.getExitNode().addOutgoingEdge(loopBackEdge)
    whileNode.addIncomingEdge(loopBackEdge)

    # Encapsulate entry/ exit nodes in CFG (same), and return
    while_cfg.setEntryNode(whileNode)
    while_cfg.setExitNode(whileNode)

    cfg.unionEdges(set([loopEntryEdge, loopBackEdge]))

    return while_cfg


''' ---------------------------------------------------------------------------
Reduce all back edges on the top-level of the program (ignoring inside LOOP/ AMB)
into one back edge - this function SHOULD NOT be recursively called, passes once
--------------------------------------------------------------------------- '''
def _normalize_seq_cfg(cfg):
    node = cfg.getEntryNode()
    first_while_node = None
    second_while_node = None

    while node:
        if node.getType() == LOOP:
            if first_while_node:
                second_while_node = node
                flag = nextFlagName()
                ''' Pre-algorithm Construction Phase '''
                # Construct <pre1>
                pre1 = None
                if cfg.getEntryNode() != first_while_node:
                    pre1 = CFG()
                    pre1.setEntryNode(cfg.getEntryNode())
                    pre1.setExitNode(_get_loop_in_edge(first_while_node).getSource())

                # Construct <body1>
                body1 = CFG()
                body1.setEntryNode(_get_loop_entry_edge(first_while_node).getEndpoint())
                body1.setExitNode(_get_loop_back_edge(first_while_node).getSource())
                
                # Construct <post1> <pre1>
                inter = CFG()
                inter.setEntryNode(_get_loop_out_edge(first_while_node).getEndpoint())
                inter.setExitNode(_get_loop_in_edge(second_while_node).getSource())

                # Construct <body2>
                body2 = CFG()
                body2.setEntryNode(_get_loop_entry_edge(second_while_node).getEndpoint())
                body2.setExitNode(_get_loop_back_edge(second_while_node).getSource())

                # Construct <post2>
                post2 = None
                if cfg.getExitNode() != second_while_node:
                    post2 = CFG()
                    post2.setEntryNode(_get_loop_out_edge(second_while_node).getEndpoint())
                    post2.setExitNode(cfg.getExitNode())

                ''' Algorithm phase; repoint above CFGs '''
                # 'nuke' the two while nodes (remove all 4 edges and discard the node ptrs)
                _nuke_while_node(cfg, first_while_node)
                _nuke_while_node(cfg, second_while_node)

                # <pre1>
                # flag := true
                flag_cfg_1, flagEntry_1, flagExit_1 = _flag_cfg(cfg, flag, ASSIGN, TRUE)
                if pre1:
                    _connect(cfg, pre1.getExitNode(), flagEntry_1)

                # while * do
                #   if flag ∧ * then flag := false
                #                    <post1>
                #                    <pre2>
                #   if flag then <body1>
                #           else <body2>
                flag_cfg_2, flagEntry_2, flagExit_2 = _flag_cfg(cfg, flag, ASSUME, TRUE)
                flag_cfg_3, flagEntry_3, flagExit_3 = _flag_cfg(cfg, flag, ASSIGN, FALSE)
                flag_cfg_4, flagEntry_4, flagExit_4 = _flag_cfg(cfg, flag, ASSUME, FALSE)
                flag_cfg_5, flagEntry_5, flagExit_5 = _flag_cfg(cfg, flag, ASSUME, TRUE)
                flag_cfg_6, flagEntry_6, flagExit_6 = _flag_cfg(cfg, flag, ASSUME, FALSE)

                single_loop_cfg = _create_loop(cfg, _chain(cfg, _create_amb(cfg, \
                                                                            _chain(cfg, _chain(cfg, flag_cfg_2, flag_cfg_3), inter), \
                                                                           flag_cfg_4),
                                                                _create_amb(cfg, \
                                                                            _chain(cfg, flag_cfg_5, body1), \
                                                                            _chain(cfg, flag_cfg_6, body2))))

                _connect(cfg, flagExit_1, single_loop_cfg.getEntryNode())
                # [flag == False]
                # <post2>
                flag_cfg_7, flagEntry_7, flagExit_7 = _flag_cfg(cfg, flag, ASSUME, FALSE)
                _connect(cfg, single_loop_cfg.getExitNode(), flagEntry_7)
                if post2:
                    _connect(cfg, flagExit_7, post2.getEntryNode())

                node = single_loop_cfg.getExitNode()

            first_while_node = node
        # Get next node in sequence after node
        node = _get_next_seq(node, node.getType())

''' ---------------------------------------------------------------------------
Return first LOOP node on this branch of AMB, if exists
--------------------------------------------------------------------------- '''
def _get_while_on_branch(amb_branch_node):
    start_node = amb_branch_node
    while amb_branch_node and (AMB_JOIN not in [e.getType() for e in amb_branch_node.getOutgoingEdges()]):
        if amb_branch_node.getType() == LOOP:
            # Get exit node of this amb branch too
            final_node = amb_branch_node
            n = _get_next_seq(final_node, final_node.getType())
            while n:
                final_node = n
                n = _get_next_seq(final_node, final_node.getType())
            if amb_branch_node == final_node:
                print("WARNING: A LOOP node is terminating an AMB branch, pad LOOP after with ASSUME(TRUE)")
            if amb_branch_node == start_node:
                print("WARNING: A LOOP node is starting an AMB branch, pad LOOP before with ASSUME(TRUE)")
            return amb_branch_node, start_node, final_node
        amb_branch_node = _get_next_seq(amb_branch_node, amb_branch_node.getType())
    return None, None, None

''' ---------------------------------------------------------------------------
Scan for branching back edges in all sub-structures (e.g. in AMBs and LOOPs)
... and reduce to a single back edge per sub-structure
- CFG modified in place
- Transplant the AMB block
- Does not handle a while loop on a single branch
--------------------------------------------------------------------------- '''
def _normalize_amb_cfg(cfg):
    node = cfg.getEntryNode()

    while node:
        if node.getType() == AMB:
            # Temporarily snip the AMB_JOINS
            for e in node.getAMBExit().getIncomingEdges():
                e.getSource().delOutgoingEdge(e)
            while_nodes = []
            for e in node.getOutgoingEdges():
                while_node, start_node, final_node = _get_while_on_branch(e.getEndpoint())
                if while_node and start_node and final_node:
                    while_nodes.append([while_node, start_node, final_node])
            # Restore the AMB_JOINS
            for e in node.getAMBExit().getIncomingEdges():
                e.getSource().addOutgoingEdge(e)
            if len(while_nodes) == 2:
                l_while     = while_nodes[0][0]
                l_amb_entry = while_nodes[0][1]
                l_amb_exit  = while_nodes[0][2]

                r_while     = while_nodes[1][0]
                r_amb_entry = while_nodes[1][1]
                r_amb_exit  = while_nodes[1][2]

                flag = nextFlagName()
                ''' Pre-algorithm Construction Phase '''
                # pre1, body1, post1, pre2, body2, post2
                before = None
                if cfg.getEntryNode() != node:
                    before = CFG()
                    before.setEntryNode(cfg.getEntryNode())
                    before.setExitNode(_get_prev(node))

                pre1 = CFG()
                pre1.setEntryNode(l_amb_entry)
                pre1.setExitNode(_get_loop_in_edge(l_while).getSource())

                body1 = CFG()
                body1.setEntryNode(_get_loop_entry_edge(l_while).getEndpoint())
                body1.setExitNode(_get_loop_back_edge(l_while).getSource())

                post1 = CFG()
                post1.setEntryNode(_get_loop_out_edge(l_while).getEndpoint())
                post1.setExitNode(l_amb_exit)

                pre2 = CFG()
                pre2.setEntryNode(r_amb_entry)
                pre2.setExitNode(_get_loop_in_edge(r_while).getSource())

                body2 = CFG()
                body2.setEntryNode(_get_loop_entry_edge(r_while).getEndpoint())
                body2.setExitNode(_get_loop_back_edge(r_while).getSource())

                post2 = CFG()
                post2.setEntryNode(_get_loop_out_edge(r_while).getEndpoint())
                post2.setExitNode(r_amb_exit)

                after = None
                if cfg.getExitNode() != node.getAMBExit():
                    after = CFG()
                    after.setEntryNode(_get_next_seq(node, node.getType()))
                    after.setExitNode(cfg.getExitNode())

                ''' Algorithm phase; repoint above CFGs '''
                _nuke_while_node(cfg, l_while)
                _nuke_while_node(cfg, r_while)
                _nuke_amb_node(cfg, node)

                flag_cfg_1, flagEntry_1, flagExit_1 = _flag_cfg(cfg, flag, ASSIGN, TRUE)
                flag_cfg_2, flagEntry_2, flagExit_2 = _flag_cfg(cfg, flag, ASSIGN, FALSE)

                flag_cfg_3, flagEntry_3, flagExit_3 = _flag_cfg(cfg, flag, ASSUME, TRUE)
                flag_cfg_4, flagEntry_4, flagExit_4 = _flag_cfg(cfg, flag, ASSUME, FALSE)

                flag_cfg_5, flagEntry_5, flagExit_5 = _flag_cfg(cfg, flag, ASSUME, TRUE)
                flag_cfg_6, flagEntry_6, flagExit_6 = _flag_cfg(cfg, flag, ASSUME, FALSE)

                if_cfg_1 = _create_amb(cfg, 
                                       _chain(cfg, flag_cfg_1, pre1),
                                       _chain(cfg, flag_cfg_2, pre2))

                if before:
                    _connect(cfg, before.getExitNode(), if_cfg_1.getEntryNode())

                while_cfg = _create_loop(cfg,
                                         _create_amb(cfg, 
                                                     _chain(cfg, flag_cfg_3, body1),
                                                     _chain(cfg, flag_cfg_4, body2)))

                _connect(cfg, if_cfg_1.getExitNode(), while_cfg.getEntryNode())

                if_cfg_2 = _create_amb(cfg,
                                       _chain(cfg, flag_cfg_5, post1),
                                       _chain(cfg, flag_cfg_6, post2))

                _connect(cfg, while_cfg.getExitNode(), if_cfg_2.getEntryNode())

                if after:
                    _connect(cfg, if_cfg_2.getExitNode(), after.getEntryNode())
                return
                #node = while_cfg.getExitNode()

        # Get next node in sequence after node
        node = _get_next_seq(node, node.getType())

''' ---------------------------------------------------------------------------
Scan for nested back edges in all sub-structures (e.g. in AMBs and LOOPs)
... and reduce to a single back edge per sub-structure
- CFG modified in place
- Transplant the LOOP block
- Does not handle a nesting deeper than 2
--------------------------------------------------------------------------- '''
def _normalize_loop_cfg(cfg):
    node = cfg.getEntryNode()

    while node:
        if node.getType() == LOOP:
            # Temporarily snip off back edge
            outer_back_edge = None
            for e in node.getIncomingEdges():
                if e.getType() == LOOP_BACK:
                    outer_back_edge = e
                    e.getSource().delOutgoingEdge(e)
            assert outer_back_edge is not None

            # Walk through inner node and try to find an inner while
            inner_node = _get_loop_entry_edge(node).getEndpoint()
            inner_while_found = False
            while inner_node:
                if inner_node.getType() == LOOP:
                    inner_while_found = True
                    break
                inner_node = _get_next_seq(inner_node, inner_node.getType())
            # Restore back edge
            restored_back_edge = False
            for e in node.getIncomingEdges():
                if e.getType() == LOOP_BACK:
                    outer_back_edge = e
                    e.getSource().addOutgoingEdge(e)
                    restored_back_edge = True
            assert restored_back_edge
            if inner_while_found:
                # We have both node (outer while) and inner_node (inner while)

                flag = nextFlagName()
                ''' Pre-algorithm Construction Phase '''
                # Construct <pre1>
                before = None
                if cfg.getEntryNode() != node:
                    before = CFG()
                    before.setEntryNode(cfg.getEntryNode())
                    before.setExitNode(_get_loop_in_edge(node).getSource())

                # pre
                pre = CFG()
                pre.setEntryNode(_get_loop_entry_edge(node).getEndpoint())
                pre.setExitNode(_get_loop_in_edge(inner_node).getSource())

                # body
                body = CFG()
                body.setEntryNode(_get_loop_entry_edge(inner_node).getEndpoint())
                body.setExitNode(_get_loop_back_edge(inner_node).getSource())

                # post
                post = CFG()
                post.setEntryNode(_get_loop_out_edge(inner_node).getEndpoint())
                post.setExitNode(_get_loop_back_edge(node).getSource())
                
                after = None
                if cfg.getExitNode() != node:
                    after = CFG()
                    after.setEntryNode(_get_loop_out_edge(node).getEndpoint())
                    after.setExitNode(cfg.getExitNode())

                ''' Algorithm phase; repoint above CFGs '''
                # 'nuke' the two while nodes (remove all 4 edges and discard the node ptrs)
                _nuke_while_node(cfg, node)
                _nuke_while_node(cfg, inner_node)

                pre_copy = pre.getCopy()
                post_copy = post.getCopy()

                # Chain together nodes per algorithm
                flag_cfg_1, flagEntry_1, flagExit_1 = _flag_cfg(cfg, flag, ASSIGN, TRUE)
                flag_cfg_2, flagEntry_2, flagExit_2 = _flag_cfg(cfg, flag, ASSIGN, FALSE)

                flag_cfg_3, flagEntry_3, flagExit_3 = _flag_cfg(cfg, flag, ASSUME, TRUE)
                flag_cfg_4, flagEntry_4, flagExit_4 = _flag_cfg(cfg, flag, ASSUME, FALSE)

                flag_cfg_5, flagEntry_5, flagExit_5 = _flag_cfg(cfg, flag, ASSUME, TRUE)
                flag_cfg_6, flagEntry_6, flagExit_6 = _flag_cfg(cfg, flag, ASSUME, FALSE)

                if_cfg_1 = _create_amb(cfg,
                                        _chain(cfg, flag_cfg_1, pre),
                                        flag_cfg_2)
                if before:
                    _connect(cfg, before.getExitNode(), if_cfg_1.getEntryNode())

                new_while = _create_loop(cfg,
                                         _create_amb(cfg,
                                                     _chain(cfg, _chain(cfg, flag_cfg_3, post), pre_copy),
                                                     _chain(cfg, flag_cfg_4, body)))
                if_cfg_2 = _create_amb(cfg,
                                       _chain(cfg, flag_cfg_5, post_copy),
                                       flag_cfg_6)

                _connect(cfg, if_cfg_1.getExitNode(), new_while.getEntryNode())
                _connect(cfg, new_while.getExitNode(), if_cfg_2.getEntryNode())

                if after:
                    _connect(cfg, if_cfg_2.getExitNode(), after.getEntryNode())

                node = new_while.getEntryNode()
            
        node = _get_next_seq(node, node.getType())

''' ---------------------------------------------------------------------------
Return number of backedges in the CFG
--------------------------------------------------------------------------- '''
def _num_back_edges(cfg):
    return sum(e.getType() == LOOP_BACK for e in cfg.getEdgeSet())

''' ---------------------------------------------------------------------------
Return equivalent CFG to given cfg that has at most one back edge
--------------------------------------------------------------------------- '''
def _normalize_cfg(cfg):
    back_edge_count = _num_back_edges(cfg)
    while back_edge_count > 1:
        # Three passes focused on different normalizations
        _normalize_seq_cfg(cfg)
        _normalize_loop_cfg(cfg)
        _normalize_amb_cfg(cfg)        
        
        # Loop invariant to guarantee termination
        old_back_edge_count    = back_edge_count
        back_edge_count        =  _num_back_edges(cfg)
        assert back_edge_count < old_back_edge_count

""" ======================================================================= """
""" ================== PUBLIC INTERFACE =================================== """
""" ======================================================================= """

''' ---------------------------------------------------------------------------
Return normalized AST representation, AST*, of given AST; AST* is equivalent
to given AST except that it has at most one LOOP construct.

Optionally returns normalized CFG
--------------------------------------------------------------------------- '''
def normalize_ast(ast, ret_norm_cfg=False):
    resetFlags() # Ensure unique flag names
    cfg = get_CFG(ast)
    print("\n--------------------------------------------------------------------------------")
    print(str(_num_back_edges(cfg)) + " back-edge(s) detected.")
    _normalize_cfg(cfg)
    print(str(_num_back_edges(cfg)) + " back-edge(s) after normalization.")
    if ret_norm_cfg:
        return to_ast(cfg), cfg
    else:
        return to_ast(cfg)