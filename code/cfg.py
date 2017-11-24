import sys
import graphviz as gv



 class Node(object):
    def __init__(self, data ):
        self.edge = data

        self.left = None
        self.right = None



def create_cfg(AST):

    head = None

    if AST.data == "ASSIGN":


        head = Node(AST.data)


        head.child = create_cfg(data[statement.end():])
        return head 

    elif statement.group() == "ASSUME":

        assign = re.search("\((.*?)\)", data[statement.end():])
        assign = assign.group()
        assign = assign[1:-1]
        print(assign)
        head = Node(assign)
        head.child = create_cfg(data[statement.end():])
        return head 

    elif statement.group() == "AMB":
        target = data[statement.end():]

        inner = scope_find(target)

        if_statement = target[:inner]
    
        head = Node("if statement")

        path1 = scope_find(if_statement[1:])


        branch1 = if_statement[:path1]
        
        head.child = create_cfg(branch1)

        branch2 = if_statement[(path1+2):]
        
        head.child2 = create_cfg(branch2)
    
        return head

    else:
        return head




# def scope_find(data):
#     pos = 0
#     counter = 0
#     stop = 0

#     while (pos <= len(data)) and (stop == 0):
#         if data[pos] == "(":
#             counter = counter + 1
#         elif data[pos] == ")":
#             counter = counter - 1
#             if counter == 0:
#                 stop = 1
#         pos = pos + 1
#     return pos




def parse_data(data):
    ast = data.replace("\n", "")
    ast = ast.replace("\t", "")
    ast = ast.replace(" ", "")
    return ast


if __name__ == '__main__':
    if len(sys.argv) == 2:

        g = graph()

        f = open(sys.argv[1], "r")
        data = f.read()    
        ast = parse_data(data)
        print(ast)
        f.close()

    else:
        print("Expected usage: $ python whileparser.py input-file")