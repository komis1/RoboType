import pickle
import json
from autocorrect import Speller 

class TrieNode:
    """A node in the trie structure"""

    def __init__(self, char):
        # the character stored in this node
        self.char = char

        # whether this can be the end of a word
        self.is_end = False

        # a counter indicating how many times a word is inserted
        # (if this node's is_end is True)
        self.counter = 0

        # a dictionary of child nodes
        # keys are characters, values are nodes
        self.children = {}
        
        # a counter indicating how many times this character is selected following the previous input
        self.pcounter = 1

class Trie(object):
    """The trie object"""

    def __init__(self):
        """
        The trie has at least the root node.
        The root node does not store any character
        """
        self.root = TrieNode("")
    
    def insert(self, word):
        """Insert a word into the trie"""
        node = self.root
        
        # Loop through each character in the word
        # Check if there is no child containing the character, create a new child for the current node
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                # If a character is not found,
                # create a new node in the trie
                new_node = TrieNode(char)
                node.children[char] = new_node
                node = new_node
        
        # Mark the end of a word
        node.is_end = True

        # Increment the counter to indicate that we see this word once more
        node.counter += 1
        
    def insert_from_csv(self, csvfile, limit):
        """Insert a word and its frequencies into the trie
        see https://www.kaggle.com/datasets/rtatman/english-word-frequency"""
        
        linecount = 0
        
        with open(csvfile,"r") as infile:
            
            for line in infile:
                data= line.split(",")
                word=data[0]
                count=int(data[1])
                node = self.root
                # Loop through each character in the word
                # Check if there is no child containing the character, create a new child for the current node
                for char in word:
                    if char in node.children:
                        node = node.children[char]
                        node.pcounter+=1
                    else:
                        # If a character is not found,
                        # create a new node in the trie
                        new_node = TrieNode(char)
                        node.children[char] = new_node
                        node = new_node

                # Mark the end of a word
                node.is_end = True

                # Increment the counter to indicate that we see this word once more
                node.counter = count
                if limit!=-1:
                    linecount+=1
                    if linecount>=limit:
                        break
            
        infile.close()
        
    def insert_from_json(self, jsonfile, limit):
        """Insert a word and its frequencies into the trie
        see EN lang tar.gz from https://github.com/filyp/autocorrect/tree/master"""
        linecount = 0
        
        with open(jsonfile,"r") as infile:
            data=json.load(infile)
            for word in data:
                count=data[word]
                node = self.root
                # Loop through each character in the word
                # Check if there is no child containing the character, create a new child for the current node
                for char in word:
                    if char in node.children:
                        node = node.children[char]
                        node.pcounter+=1
                    else:
                        # If a character is not found,
                        # create a new node in the trie
                        new_node = TrieNode(char)
                        node.children[char] = new_node
                        node = new_node

                # Mark the end of a word
                node.is_end = True

                # Increment the counter to indicate that we see this word once more
                node.counter = count
                if limit!=-1:
                        linecount+=1
                        if linecount>=limit:
                            break
            infile.close()
            
        
    def dfs(self, node, prefix):
        """Depth-first traversal of the trie
        
        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
        if node.is_end:
            self.output[prefix + node.char]=node.counter
        
        for child in node.children.values():
            self.dfs(child, prefix + node.char)
    
    def dfs_with_limit(self, node, prefix, limit):
        """Depth-first traversal of the trie
        
        Args:
            - node: the node to start with
            - prefix: the current prefix, for tracing a
                word while traversing the trie
        """
            
        if node.is_end:
            #self.output.append((prefix + node.char,node.counter))
            self.output[prefix + node.char]=node.counter
            
        if (len(prefix+node.char)<limit):
            for child in node.children.values():
                self.dfs_with_limit(child, prefix + node.char, limit)
        

        
    def query(self, x):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of 
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        self.output = {}
        node = self.root
        
        # Check if the prefix is in the trie
        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return {}
        
        # Traverse the trie to get all candidates
        self.dfs(node, x[:-1])

        # Sort the results in reverse order and return
        return sorted(self.output, key=lambda x: x[1], reverse=True)
    
    def query_next_letter(self, x):
        """Given an input (a prefix), retrieve all letters stored in
        the trie with that prefix, sort the letters by the number of 
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        #self.output = []
        self.output = {}
        node = self.root
        
        # Check if the prefix is in the trie
        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return {}
        
        for child in node.children:
            self.output[child]=node.children[child].pcounter
        # Sort the results in reverse order and return
        return dict(sorted(self.output.items(), key=lambda x: x[1], reverse=True))
    
    def query_with_limit(self, x, wordlenlimit, suglimit):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of 
        times they have been inserted. 
        =Limit length of returned words to limit (-1 for no limit). 
        =Return up to suglimit suggestions and not the actual prefix 
        itself (if it is a word). Use -1 for no suggestion limit.
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        #self.output = []
        self.output = {}
        node = self.root
        
        # Check if the prefix is in the trie
        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return {}
        
        # Traverse the trie to get all candidates
        if wordlenlimit==-1:
            self.dfs(node, x[:-1])
        else:
            self.dfs_with_limit(node, x[:-1], wordlenlimit)
        
        #spellcheck or word suggestion?
        
        #spellcheck
        if (suglimit==1 and limit==len(x)):
            return self.output
        
        #word suggestions
        else:
            # Sort the results in reverse order and return
            suggestions = dict(sorted(self.output.items(), key=lambda x: x[1], reverse=True))
            if x in suggestions:
                suggestions.pop(x)
            if suglimit==-1:
                return suggestions
            else:
                return dict(list(suggestions.items())[0: suglimit])
            
    # Serialize model and save to disk
    def write_to_file(self, file):
        with open(file, "wb") as outfile:
            pickle.dump(self, outfile)
            outfile.close()
        print("Written to disk")
    
    @classmethod
    def load_from_file(cls, file):
        with open(file, "rb") as infile:
            #self = pickle.load(infile)
            #infile.close
            print("Reconstructed object")
            return pickle.load(infile)

class LanguageModel (object):
    """The trie object"""
    
    def __init__(self, pickled_model, wordjson):
        self.trie = Trie()
        self.trie = Trie.load_from_file(file=pickled_model)
        with open("support_files/unigram_freq.json","r") as infile:
            wordjson=json.load(infile)
            infile.close()
        self.speller = Speller(nlp_data=wordjson)
        