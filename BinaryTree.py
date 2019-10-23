class Node:
    def __init__(self,a):
        self.value = a
        self.LC = None
        self.RC = None
        self.Parent = None
class BT:
    def __init__(self,root):
        self.root = root
        self.size = 1
    def printTree(self):
        current_level = [self.root]
        while current_level:
            print(' '.join(str(node.value) for node in current_level))
            next_level = list()
            for n in current_level:
                if n.LC:
                    next_level.append(n.LC)
                if n.RC:
                    next_level.append(n.RC)
                current_level = next_level
    def removeLeaf(self,val):
        if self.root.value == val:
            if self.root.LC != None and self.root.RC == None:
                self.root.LC.Parent = None
                self.root = self.root.LC
                self.size -= 1
                return
            elif self.root.RC != None and self.root.LC == None:
                self.root.RC.Parent = None
                self.root = self.root.RC
                self.size -= 1
                return
            else:
                assert False
        current_level = [self.root]
        while current_level:
            next_level = list()
            for n in current_level:
                if n.LC:
                    next_level.append(n.LC)
                    if n.LC.value == val:
                        n.LC.Parent = None
                        n.LC = None
                        self.size -= 1
                        return
                if n.RC:
                    next_level.append(n.RC)
                    if n.RC.value == val:
                        n.RC.Parent = None
                        n.RC = None
                        self.size -= 1
                        return
                current_level = next_level
    def searchLeaves(self):
        leaves = []
        parent = []
        if self.root.LC == None or self.root.RC == None:
            leaves.append(self.root.value)
            if self.root.LC != None:
                parent.append(self.root.LC.value)
            elif self.root.RC != None:
                parent.append(self.root.RC.value)
            else:
                assert False
        l = self.findLastLevelElements()
        leaves = leaves + l
        return leaves
    
    def searchParents(self,val):
        # mainly for Prufer Code!
        if val == self.root.value:
            if self.root.LC != None:
                return self.root.LC.value
            elif self.root.RC != None:
                return self.root.RC.value
            else:
                assert False
        current_level = [self.root]
        while current_level:
            next_level = list()
            for n in current_level:   
                if n.LC:
                    if n.LC.value == val :
                        return n.value
                    next_level.append(n.LC)
                if n.RC:
                    if n.RC.value == val:
                        return n.value
                    next_level.append(n.RC)
                current_level = next_level
    
    def touchableElementsStructureLimit(self,ml,single_used):
        """
        This function assumes a full binary tree
        
        similar to the criteria used in findTouchableElementsLimit, this function
        finds the structure of those elements
        """
        # note this function only works if it is a full binary tree
        lastlevel = [[self.root.LC.value,self.root.RC.value]]
        current_level = [self.root.LC,self.root.RC]
        counter = 1
        while current_level:
            counter += 1
            next_level = list()
            for n in current_level:
                if n.LC and 'y' not in n.value and single_used[n.value] == True:
                    next_level.append(n.LC)
                    next_level.append(n.RC)
                    # call a function to write the structure
                    self.stringFindAndReplace(lastlevel,1,counter,n.value,n.LC.value,n.RC.value,ml)
                    if str(lastlevel).count('x') + str(lastlevel).count('t') + str(lastlevel).count('y') == ml:
                        return lastlevel[0]
                current_level = next_level
        return lastlevel[0]
    def stringFindAndReplace(self,level_elements,check_level,max_level,value_to_remove,value_add1,value_add2,ml):
        if check_level == max_level:
            if value_to_remove in level_elements:
                level_elements.remove(value_to_remove)
                level_elements.append([value_add1,value_add2])
            return
        # if the level is a string i.e. not a list, and it is not at the correct level, stop searching
        if type(level_elements) == str:
            return
        if check_level < max_level:
            for i in range(len(level_elements)):
                self.stringFindAndReplace(level_elements[i],check_level+1,max_level,value_to_remove,value_add1,value_add2,ml)
            return
    def findLastLevelElements(self):
        lastlevel = [self.root.value]
        current_level = [self.root]
        while current_level:
            next_level = list()
            for n in current_level:
                if n.LC:
                    if 'y' not in n.LC.value:
                        next_level.append(n.LC)
                    lastlevel.remove(n.value)
                    lastlevel.append(n.LC.value)
                if n.RC:
                    if not n.LC:
                        lastlevel.remove(n.value)
                    if 'y' not in n.RC.value:
                        next_level.append(n.RC)
                    lastlevel.append(n.RC.value)
                current_level = next_level
        return lastlevel
    def findTouchableElementsLimit(self,max_var,single_used):
        """
        This function assumes a full binary tree
        
        given a binary tree, find out all the elements that are involved in the tree
        with the criteria of
        - limit up to a number of nodes, n
        - do not proceed on when we encounter a 'y' 
        - do not proceed on when we encounter a 't' that is used more than once
        """
        lastlevel = [self.root.LC.value,self.root.RC.value]
        current_level = [self.root.LC,self.root.RC]
        while current_level:
            next_level = list()
            for n in current_level:
                if n.LC and 'y' not in n.value and single_used[n.value] == True:
                        next_level.append(n.LC)
                        next_level.append(n.RC)
                        lastlevel.remove(n.value)
                        lastlevel.append(n.LC.value)
                        lastlevel.append(n.RC.value)
                if len(lastlevel) == max_var:
                        return lastlevel
                current_level = next_level
        return lastlevel
    def findAllVars(self):
        variables = []
        current_level = [self.root]
        while current_level:
            next_level = list()
            for n in current_level:
                if n.LC:
                    next_level.append(n.LC)
                    variables.append(n.LC.value)
                if n.RC:
                    next_level.append(n.RC)
                    variables.append(n.RC.value)
                current_level = next_level
        return variables
