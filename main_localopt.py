'''
Main file for LocalOpt
Automatically reads all the files in local_test_source folder and run the localOpt operation 
and save the results in local_test_dest
'''

import os
import BinaryTree
import gendistinct

def get_line_header(lines):
    line_header = {}
    for i in range(len(lines)):
        line_header[lines[i][0]] = i
    return line_header

def find_depth(lines):
    # find the depth of each line
    line_header = get_line_header(lines)
    line_depth = [0]*(len(lines))
    for i in range(len(lines)):
        if "x" in lines[i][1]:
            depth1 = 0
        else:
            depth1 = line_depth[line_header[lines[i][1]]]
        if "x" in lines[i][2]:
            depth2 = 0
        else:
            depth2 = line_depth[line_header[lines[i][2]]]
        line_depth[i] = max(depth1,depth2) + 1
    return line_depth

def sort_by_depth(line_depth,l_list):
    # sort the l_list, by the depth in ascending order
    A = []
    for l in l_list:
        A.append([min(line_depth[l[0]],line_depth[l[1]]),l])
    def myfunc(s):
        return s[0]
    A.sort(key=myfunc)
    return A
def removeTrivial(lines,T):
    i = 0
    while i < len(T):
        line_header = get_line_header(lines)
        if len(list(T[i][1])) == 1:
            TBR = T[i][0]
            New = 'x'+str(list(T[i][1])[0])
            for l in lines:
                if l[1] == TBR:
                    l[1] = New
                elif l[2] == TBR:
                    l[2] = New
            del lines[line_header[TBR]]
            del T[i]
            i -= 1
        i+=1

def sortInOrder(l):
    # this function exists purely for reordering in a list:
    a1 = l[1]
    a2 = l[2]
    if 'x' in a1:
        if 'x' in a2:
            if int(a1[1:]) > int(a2[1:]):
                l[1],l[2] = l[2],l[1]
    if 't' in a1:
        if 't' in a2:
            if int(a1[1:]) > int(a2[1:]):
                l[1],l[2] = l[2],l[1]
        elif 'x' in a2:
            l[1],l[2] = l[2],l[1]
    if 'y' in a1:
        if 'y' not in a2:
            l[1],l[2] = l[2],l[1]
        else:
            if int(a1[1:]) > int(a2[1:]):
                l[1],l[2] = l[2],l[1]
    return

    
def removeSameTerms(lines):
    """
    This function checks if there are two lines that actually operates the same function
    If yes, the one with the least depth is chosen
    SPECIAL CASE: IF a 'y' and a 't' operate the same function, with 't' at a less depth,
    the substitution will take 'y' instead of 't'
    """
    flag_main = 0
    line_depth = find_depth(lines)

    i = 0
    while i < len(lines):
        subst_dict = {}
        j = i + 1
        while j < len(lines):
            if set(lines[i][1:3]) == set(lines[j][1:3]): # same function detected
                flag_main = 1
                if 'y' in lines[j][0]: # taking care of the special case
                    subst_dict[lines[i][0]] = lines[j][0]
                else: # 'y' in lines[i][0] is covered in this case too
                    subst_dict[lines[j][0]] = lines[i][0]
                
                # deletion
                if line_depth[i] < line_depth[j]:
                    del lines[j]
                else:
                    del lines[i]
                    
                # substitution
                for k in range(len(lines)):
                    if lines[k][0] in subst_dict.keys():
                        lines[k][0] = subst_dict[lines[k][0]]
                    elif lines[k][1] in subst_dict.keys():
                        lines[k][1] = subst_dict[lines[k][1]]
                    elif lines[k][2] in subst_dict.keys():
                        lines[k][2] = subst_dict[lines[k][2]]
                        
                # restart the whole loop after substitution
                i = -1
                break
            j += 1
        i += 1
        
    # reorganise the order
    reorgOrder(lines)
    # renaming in order
    renaming(lines)
    
    return flag_main
                    
                    
def reorgOrder(lines):
    # this function reorder the naming so that it is coherent
    i = 0
    while i < len(lines):
        line_header = get_line_header(lines)
        if "x" not in lines[i][1] and line_header[lines[i][1]] > i:
            swap1 = line_header[lines[i][1]]
            swap2 = i
            lines[swap1],lines[swap2] = lines[swap2],lines[swap1]
            continue
        
        if "x" not in lines[i][2] and line_header[lines[i][2]] > i:
            swap1 = line_header[lines[i][2]]
            swap2 = i
            lines[swap1],lines[swap2] = lines[swap2],lines[swap1]
            continue
        i += 1

def renaming(all_sorted):
    # reordering the namings
    t_counter = 0
    t_ref = [0]*100
    for l in all_sorted:
        if "t" in l[0]:
            t_ref[int(l[0][1:])] = t_counter
        t_counter += 1
    for i in range(len(all_sorted)):
        for j in range(len(all_sorted[0])):
            if "t" in all_sorted[i][j]:
                all_sorted[i][j] = "t"+str(t_ref[int(all_sorted[i][j][1:])])


def baseElementTables(lines):
    """
    This function calculates the base elements required for each line
    """
    # initialization
    line_header = get_line_header(lines)
    lines_elements = []
    for i in range(len(lines)):
        line_elements = set()
        temp = [] # temp contains all 'y' and 't' variables
        if 'x' in lines[i][1]:
            if int(lines[i][1][1:]) in list(line_elements): # if it is inside, cancellation takes place
                line_elements.remove(int(lines[i][1][1:]))
            else:
                line_elements.add(int(lines[i][1][1:]))
        else:
            temp.append(lines[i][1])
        if 'x' in lines[i][2]:
            if int(lines[i][2][1:]) in list(line_elements): # if it is inside, cancellation takes place
                line_elements.remove(int(lines[i][2][1:]))
            else:
                line_elements.add(int(lines[i][2][1:]))
        else:
            temp.append(lines[i][2])
        while len(temp) > 0:
            if 'x' in lines[line_header[temp[0]]][1]:
                if int(lines[line_header[temp[0]]][1][1:]) in list(line_elements): # if it is inside, cancellation takes place
                    line_elements.remove(int(lines[line_header[temp[0]]][1][1:]))
                else:
                    line_elements.add(int(lines[line_header[temp[0]]][1][1:]))
            else:
                temp.append(lines[line_header[temp[0]]][1])
            if 'x' in lines[line_header[temp[0]]][2]:
                if int(lines[line_header[temp[0]]][2][1:]) in list(line_elements): 
                    line_elements.remove(int(lines[line_header[temp[0]]][2][1:]))
                else:
                    line_elements.add(int(lines[line_header[temp[0]]][2][1:]))
            else:
                temp.append(lines[line_header[temp[0]]][2])
            del temp[0]
        lines_elements.append(line_elements)
    return lines_elements
                
            


def reduceDepthMain(lines):
    """
    This function uses the number of base elements of a gate and compares it to the depth
    If the depth is equal or more than the number of elements present, then it MAY be recomputed 
    in some other ways that can reduce the depth
    """

    # generate depth tables for lines, a T table and Y table with depth
    main_flag = 0
    while True:
        elements = baseElementTables(lines)
        depth_list = find_depth(lines)
        
        least_depth = 100000 # placeholder
        chosen_line = -1
        # search for all gates that the depth is equal or more than the number of base 
        # elements present. Among those valid ones, choose the one that has the least depth
        for i in range(len(lines)):
            if depth_list[i] >= len(elements[i]):
                if depth_list[i] < least_depth:
                    least_depth = depth_list[i]
                    chosen_line = i
        if chosen_line == -1: # if there is nothing to choose, break
            break
        if not reduceDepth(lines,lines[chosen_line]):
            break
        main_flag = 1
        # reorganise the order
        reorgOrder(lines)
        # renaming in order
        renaming(lines)
    return main_flag

def reduceDepth(lines,T):
    # loop through all descendants of T 
    # checking for any 't' descendants that only used in this tree
    # return true if found
    line_header = get_line_header(lines)
    LC = T[1]
    RC = T[2]
    store = []
    node_tracker = [LC,RC]
    node_ingredient = []
    recursiveReduceDepth(line_header,lines,T[0],LC,RC,store,node_ingredient,node_tracker)
    # this is to do a modulo 2 on the items
    for i in range(len(store)):
        j = 0
        while j < len(store[i][1]):
            k = j+1
            while k < len(store[i][1]):
                if store[i][1][j] == store[i][1][k]:
                    del store[i][1][j]
                    del store[i][1][k]
                    k = j
                k += 1
            j += 1
    for i in range(len(node_ingredient)):
        j = 0
        while j < len(node_ingredient[i]):
            k = j+1
            while k < len(node_ingredient[i]):
                if node_ingredient[i][j] == node_ingredient[i][k]:
                    del node_ingredient[i][k]
                    del node_ingredient[i][j]
                    k = j
                k += 1
            j += 1
    for i in range(len(store)):
        if set(node_ingredient[i]).issubset(set(store[i][1])) and len(node_ingredient[i]) == 2:
            # great!
            l = lines[line_header[store[i][0]]]
            
            if l[1] == node_ingredient[i][0]:
                temp = l[2]
                l[2] = node_ingredient[i][1]
            elif l[1] == node_ingredient[i][1]:
                temp = l[2]
                l[2] = node_ingredient[i][0]
            elif l[2] == node_ingredient[i][0]:
                temp = l[1]
                l[1] = node_ingredient[i][1]
            elif l[2] == node_ingredient[i][1]:
                temp = l[1]
                l[1] = node_ingredient[i][0] 
            l2 = lines[line_header[store[i][2]]]
            if l2[1] == store[i][0]:
                l2[2] = temp
            elif l2[2] in store[i][0]:
                l2[1] = temp
            else:
                assert False
            del lines[line_header[T[0]]]
            for l3 in lines:
                if l3[1] == T[0]:
                    l3[1] = store[i][0]
                elif l3[2] == T[0]:
                    l3[2] = store[i][0]
            return True
    return False
            
def recursiveReduceDepth(line_header,lines,parent,LC,RC,store,node_ingredient,node_tracker):
    node_tracker1 = node_tracker.copy()
    node_tracker2 = node_tracker.copy()
    if 't' in LC:
        for i in range(len(node_tracker1)):
            if node_tracker1[i] == LC:
                node_tracker1[i] = lines[line_header[LC]][1]
        node_tracker1.append(lines[line_header[LC]][2])
        count = 0
        for l in lines:
            if LC in l[1] or LC in l[2]:
                count += 1
        if count == 1:
            node_ingredient.append(node_tracker1)
            child_ingredients = [RC] + lines[line_header[LC]][1:3]
            store.append([LC,child_ingredients,parent])
        recursiveReduceDepth(line_header,lines,LC,lines[line_header[LC]][1],lines[line_header[LC]][2],store,node_ingredient,node_tracker1)
            
    if 't' in RC:
        for i in range(len(node_tracker2)):
            if node_tracker2[i] == RC:
                node_tracker2[i] = lines[line_header[RC]][1]
        node_tracker2.append(lines[line_header[RC]][2])
        count = 0
        for l in lines:
            if RC in l[1] or RC in l[2]:
                count += 1
        if count == 1:
            node_ingredient.append(node_tracker2)
            child_ingredients = [LC] + lines[line_header[RC]][1:3] 
            store.append([RC,child_ingredients,parent])
        recursiveReduceDepth(line_header,lines,RC,lines[line_header[RC]][1],lines[line_header[RC]][2],store,node_ingredient,node_tracker2)

def findSubTree(lines,line_header,BT,root):
    LC = lines[line_header[root.value]][1]
    RC = lines[line_header[root.value]][2]
    l = BinaryTree.Node(LC)
    r = BinaryTree.Node(RC)
    root.LC = l
    root.RC = r
    BT.size += 2
    l.Parent = root
    r.Parent = root
    if 'x' not in LC:
        findSubTree(lines,line_header,BT,l)
    if 'x' not in RC:
        findSubTree(lines,line_header,BT,r)
        
def substitution(tree,lines):
    # take care of the substitution
    # if the tree is in the circuit, replace by those variables
    for i in range(len(tree)):
        for j in range(len(lines)):
            if 'z' in tree[i][1] or 'z' in tree[i][2]:
                continue
            if set(tree[i][1:]) == set(lines[j][1:]):
                temp = tree[i][0]
                tree[i][0] = lines[j][0]
                for m in range(len(tree)):
                    if tree[m][1] == temp:
                        tree[m][1] = tree[i][0]
                    elif tree[m][2] == temp:
                        tree[m][2] = tree[i][0]
                    
            
def XOR_count(tree,lines):
    # count the number of XORs required in the tree
    XOR = len(tree)-1
    for i in range(len(tree)-1):
        # len(lines)-1 ignores the final computation
        for j in range(len(lines)):
            if 'z' in tree[i][1] or 'z' in tree[i][2]:
                continue
            if set(tree[i][1:]) == set(lines[j][1:]):
                XOR -= 1
                temp = tree[i][0]
                tree[i][0] = lines[j][0]
                for m in range(len(tree)):
                    if tree[m][1] == temp:
                        tree[m][1] = tree[i][0]
                    elif tree[m][2] == temp:
                        tree[m][2] = tree[i][0]
    return XOR
def single_used_variables(lines):
    """
    This function returns a dictionary stating if the key is used more than once
    """
    l = {}
    for i in range(len(lines)):
        l[lines[i][0]] = 0
        if lines[i][1] not in l.keys():
            l[lines[i][1]] = 0
        else:
            l[lines[i][1]] = 1
        if lines[i][2] not in l.keys():
            l[lines[i][2]] = 0
        else:
            l[lines[i][2]] = 1
        for j in range(len(lines)):
            if lines[j][1] == lines[i][0] or lines[j][2] == lines[i][0]:
                l[lines[i][0]] = 1
                break
    return l
            
def saving(tree,var,lines):
    var1 = var.copy()
    for i in range(len(tree)):
        for j in range(len(lines)):
            if 'z' in tree[i][1] or 'z' in tree[i][2]:
                continue
            if set(tree[i][1:]) == set(lines[j][1:]):
                temp = tree[i][0]
                tree[i][0] = lines[j][0]
                for m in range(len(tree)):
                    if tree[m][1] == temp:
                        tree[m][1] = tree[i][0]
                    elif tree[m][2] == temp:
                        tree[m][2] = tree[i][0]
    
    save = 0
    # check how many var1 variables are not in the trees1
    for i in range(len(var1)):
        c = 0
        for t in tree:
            if var1[i] == t[0] or var1[i] == t[1] or var1[i] == t[2]:
                c = 1
                break
        if c == 0:
            save += 1
    return save
def removeRedundants(lines):
    i = len(lines)-1
    while i >= 0:
        j = i + 1
        flag = 1
        while j < len(lines):
            flag = 0
            if lines[i][0] == lines[j][1] or lines[i][0] == lines[j][2] or 'y' in lines[i][0]:
                flag = 1
                break
            j += 1
        if flag == 0:
            del lines[i]
        i -= 1
            

def replaceLines(old_line,new_line,lines, one_time_variables):
    old = len(lines)
    for i in range(len(lines)):
        if lines[i] == old_line[-1]:
            del lines[i]
            break
    i = 0
    while i < len(new_line):
        if 'z' not in new_line[i][0]:
            del new_line[i]
            continue
        i += 1
    new_line[-1][0] = old_line[-1][0]
    var_dict = {}
    for k in range(i):
        line_header = get_line_header(lines)
        if 'z' in new_line[k][0] and 'y' in old_line[len(old_line)-len(new_line)+k][0]:
            var_dict[new_line[k][0]] = old_line[len(old_line)-len(new_line)+k][0]
            new_line[k][0] = old_line[len(old_line)-len(new_line)+k][0]
            del lines[line_header[old_line[len(old_line)-len(new_line)+k][0]]]
        elif 'z' in new_line[k][0]:
            var_dict[new_line[k][0]] = 't'+str(len(lines))
            new_line[k][0] = 't'+str(len(lines))
        if 'z' in new_line[k][1]:
            new_line[k][1] = var_dict[new_line[k][1]]
        if 'z' in new_line[k][2]:
            new_line[k][2] = var_dict[new_line[k][2]]
        lines.append(new_line[k])
    # reorganise the order
    reorgOrder(lines)
    # renaming in order
    renaming(lines)
    # remove redundants
    removeRedundants(lines)
    # reorganise the order
    reorgOrder(lines)
    # renaming in order
    renaming(lines)
    if (len(lines)>= old):
        assert False
        
def findSubtreeAndOpt(lines):
    # still under construction
    # exhaust a small tree reconstruction
    i = 0
    while i < len(lines):
        line_header = get_line_header(lines)
        # constructing the Binary Tree
        N = BinaryTree.Node(lines[i][0])
        BT1 = BinaryTree.BT(N)
        findSubTree(lines,line_header,BT1,N)
        # generate dictionary of singly-used-variables
        singly_used_variables = single_used_variables(lines)
        # finding all the elements, with a limit 
        elements = BT1.findTouchableElementsLimit(5,singly_used_variables)
        # original lines involved with the elements
        struct = BT1.touchableElementsStructureLimit(5,singly_used_variables)
        original_line = gendistinct.lineToCode(struct,len(elements))
        # substitute to be compatible with the lines
        substitution(original_line,lines)
        # find out all the variables that only used a single time if no such variables, skip
        one_time_variables = []
        for e in elements:
            if singly_used_variables[e] == 0:
                one_time_variables.append(e)
        if len(one_time_variables) == 0:
            i += 1
            continue
        
        # generate all possible structures of the binary tree
        alltrees = gendistinct.genStruct(len(elements))
        trees = []
        # looping through all the possible structures, try to optimise it
        for tree in alltrees:
            T = gendistinct.convertToTrees(tree,elements)
            for t in T:
                trees.append(t)
        # eliminate isomorphic trees
        gendistinct.convertDistinct(trees,elements)
        # find the best tree
        # criteria for best tree:
        best_tree = None
        best_XOR = 100
        for j in range(len(trees)):
            trees[j] = gendistinct.lineToCode(trees[j],len(elements))
            substitution(trees[j],lines)
            # if the tree is the original tree, skip it
            flag = 0
            for k in range(len(trees[j])):
                if set(trees[j][k][1:]) == set(original_line[k][1:]):
                    continue
                else:
                    flag = 1
                    break
            if flag == 0:
                continue
            
            XOR = XOR_count(trees[j],lines)
            saves = saving(trees[j],one_time_variables,lines)
            XOR = XOR - saves
            if best_XOR > XOR:
                best_XOR = XOR
                best_tree = trees[j]
        if best_XOR < 0:
            saves = saving(trees[j],one_time_variables,lines)
            replaceLines(original_line,best_tree,lines,one_time_variables)
            i -= 1
        i += 1

def find_one_dependency(lines):
    # construct a list of list of the line numbers that are used once only
    things_to_change = []
    dependencies = {}
    line_number = {}
    for i in range(len(lines)):
        dependencies[lines[i][0]] = []
    for i in range(len(lines)):
        if "x" not in lines[i][1]:
            dependencies[lines[i][1]].append(lines[i][0])
        if "x" not in lines[i][2]:
            dependencies[lines[i][2]].append(lines[i][0])
        line_number[lines[i][0]] = i
        
    for key,value in dependencies.items():
        if len(value) == 1:
            things_to_change.append([line_number[key],line_number[value[0]]])
    return things_to_change

def swap_order(lines):
    flag = 1
    l_list = find_one_dependency(lines)
    while len(l_list) > 0 and flag == 1:  
        l_list = find_one_dependency(lines)
        line_depth = find_depth(lines)
        flag = 0
        # sort the l_list by depth, ranking them
        l_list = sort_by_depth(line_depth,l_list)
        i = 0
        while flag == 0 and i < len(l_list):
            l = l_list[i][1]
            # main function to reduce depth
            # swap the order of evaluating in favour of nearer circuits. 
            flag = 1
            line1 = lines[l[0]]
            line2 = lines[l[1]]
            line_header = get_line_header(lines)
            # we cannot swap the "y"s if line1 is y!
            if "y" in line1[0]:
                flag = 0
                i += 1
                continue
            if line1[0] != line2[1]:
                tri = [line2[1],line1[1],line1[2]]
            else:
                tri = [line2[2],line1[1],line1[2]]
            if 'x' in tri[0]:
                depth0 = 0
            else:
                depth0 = line_depth[line_header[tri[0]]]
            if 'x' in tri[1]:
                depth1 = 0
            else:
                depth1 = line_depth[line_header[tri[1]]]
            if 'x' in tri[2]:
                depth2 = 0
            else:
                depth2 = line_depth[line_header[tri[2]]]
            if depth0 >= depth1 and depth0 >= depth2:
                line1 = [line1[0],tri[1],tri[2]]
                line2 = [line2[0],line1[0],tri[0]]
                flag = 0
            elif depth1 > depth0 and depth1 > depth2:
                line1 = [line1[0],tri[0],tri[2]]
                line2 = [line2[0],line1[0],tri[1]]
            else:
                line1 = [line1[0],tri[0],tri[1]]
                line2 = [line2[0],line1[0],tri[2]]
            lines[l[0]] = line1
            lines[l[1]] = line2
            i += 1
        reorgOrder(lines)
        renaming(lines)
    return flag

dir_source = "./local_test_source"
dir_dest = "./local_test_dest"
if not os.path.exists(dir_dest):
    os.makedirs(dir_dest)
for filename in os.listdir(dir_source):
     # reading the data
    file_source = os.path.join(dir_source, filename)
    f1 = open(file_source,'r')
    lines = f1.readlines().copy()
    print(file_source)
    # arranging the data properly
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip('\n\r') 
    for i in range(len(lines)):
        line = lines[i].split(" ")
        lines[i] = [line[0],line[2],line[4]]
    
    flag = 1
    while flag == 1:
        # swap orders to reduce depth
        flag1 = swap_order(lines)
        # removing variables representing the same thing
        flag2 = removeSameTerms(lines)
        # check for depth that are actually nearer than calculated
        flag3 = reduceDepthMain(lines)
        flag = max(flag1,flag2,flag3)
    # reorganise the order and renaming in order
    reorgOrder(lines)
    renaming(lines)
    findSubtreeAndOpt(lines)
    reorgOrder(lines)
    renaming(lines)
    dep = find_depth(lines)
    file_dest = os.path.join(dir_dest, filename)
    f2 = open(file_dest,'w')
    for i in range(len(lines)):
        f2.write(str(lines[i][0])+' = '+str(lines[i][1])+' + '+str(lines[i][2])+'\n')
    f2.flush()
    f2.close()




