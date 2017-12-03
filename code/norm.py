""" ===========================================================================
File   : norm.py
CSC410 : Project 6: Program Normalizer and Control Flow Graph Visualizer
Author : Harman Sran

Normalizes given AST objects; removes all back edges except 1 by applying 
3 different algorithms for 3 different cases:

Handles Sequential (SEQ), Ambiguous (AMB), and Nested (LOOP) combinations
=========================================================================== """

#TODO