import math
import BinaryTree
def genStruct(n): # from internet with minimal changes
    leafnode = 'z'
    dp = []
    newset = list()
    newset.append(leafnode)
    dp.append(newset)
    for i in range(1,n):
        newset = list()
        for j in range(i):
            for leftchild in dp[j]:
                for rightchild in dp[i-j-1]:
                    newset.append('[' + leftchild + "," + rightchild + ']')
        dp.append(newset)
    return dp[-1][0:math.ceil(len(dp[-1])/2)]

def permutation(lst): # from internet
  
    # If lst is empty then there are no permutations 
    if len(lst) == 0: 
        return [] 
  
    # If there is only one element in lst then, only 
    # one permuatation is possible 
    if len(lst) == 1: 
        return [lst] 
  
    # Find the permutations for lst if there are 
    # more than 1 characters 
  
    l = [] # empty list that will store current permutation 
  
    # Iterate the input(lst) and calculate the permutation 
    for i in range(len(lst)): 
       m = lst[i] 
  
       # Extract lst[i] or m from the list.  remLst is 
       # remaining list 
       remLst = lst[:i] + lst[i+1:] 
  
       # Generating all permutations where m is first 
       # element 
       for p in permutation(remLst): 
           l.append([m] + p) 
    return l 
def convertToTrees(tree,elements):
    lst = permutation(elements)
    all_tree = []
    for i in range(len(lst)):
        tree_str = str(tree)
        for e in lst[i]:
            tree_str = tree_str.replace('z','\"'+e+'\"',1)
        exec('tmp1 = '+tree_str,None,globals())
        all_tree.append(tmp1)
    return all_tree


def constructBinaryTree(l):
    counter = 0
    y = BinaryTree.Node(l)
    thislevel = [y]
    A = BinaryTree.BT(y)
    while len(thislevel) > 0:
        nextlevel = []
        for i in range(len(thislevel)):
            if type(thislevel[i].value) == list and len(thislevel[i].value) == 2:
                k = thislevel[i]
                k.LC = BinaryTree.Node(thislevel[i].value[0])
                k.RC = BinaryTree.Node(thislevel[i].value[1])
                A.size += 2
                k.value = "z"+str(counter)
                counter += 1
                k.LC.parent = k
                k.RC.parent = k
                nextlevel.append(k.LC)
                nextlevel.append(k.RC)
        thislevel = nextlevel
        
    return A
    
def lineToCode(l,length):
    counter = length-3
    lst = [['z'+str(length-2),str(l[0]),str(l[1])]]
    Q = l.copy()
    while len(Q) > 0:
        nextQ = []
        for i in range(len(Q)):
            if type(Q[i]) == list and len(Q[i]) == 2:
                for j in range(len(lst)):
                    if lst[j][1] == str(Q[i]):
                        lst[j][1] = 'z'+str(counter)
                    if lst[j][2] == str(Q[i]):
                        lst[j][2] = 'z'+str(counter)
                lst.insert(0,['z'+str(counter),str(Q[i][0]),str(Q[i][1])])
                counter -= 1
                nextQ.append(Q[i][0])
                nextQ.append(Q[i][1])
        Q = nextQ
    return lst
        
def PruferCode(l,var_dict,elements_tmp):
    A = constructBinaryTree(l)
    code = []
    while A.size > 2:
        leaves = A.searchLeaves()
        parents = []
        for i in range(len(leaves)):
            parents.append(A.searchParents(leaves[i]))
        
        smallest = 10000
        smallest_leaf = None
        smallest_parent = None
        for i in range(len(leaves)):
            if var_dict[leaves[i]] < smallest:
                smallest_parent = parents[i]
                smallest_leaf = leaves[i]
                smallest = var_dict[leaves[i]]
        code.append(smallest_parent)
        A.removeLeaf(smallest_leaf)
        leaves = A.searchLeaves()
    return code
    
def dummying(code):
    d = {}
    j = 0
    dummy_code = []
    for i in range(len(code)):
        if code[i] not in d.keys():
            d[code[i]] = j
            j += 1
        dummy_code.append(d[code[i]])
    return dummy_code
            
        

def convertDistinct(trees,elements):
    elements_tmp = elements.copy()
    l = len(elements_tmp) - 1
    d = {}
    for i in range(l):
        elements_tmp.append('z'+str(i))
    for i,e in enumerate(elements_tmp):
        d[e] = i
    i = 0
    codes = []
    dummy_codes = []
    while i < len(trees):
        code = PruferCode(trees[i],d,elements_tmp)
        # changing the variables to dummy variables
        dummy_code = dummying(code)
        if dummy_code in dummy_codes:
            del trees[i]
            i -= 1
        else:
            codes.append(code)
            dummy_codes.append(dummy_code)
        i += 1
#    for i in range(len(trees)):
#        print(trees[i],codes[i],dummy_codes[i])
    return trees
        

    


