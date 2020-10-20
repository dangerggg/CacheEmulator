class Node(object):
    def __init__(self, data):
        self.next = None
        self.ahead = None
        self.data = data


class LinkedList(object):
    def __init__(self, size=0):
        self.head = Node(None)
        self.tail = Node(None)
        self.head.next = self.tail
        self.tail.ahead = self.head
        if size > 0:
            self.lru_init(size)
    
    def search_node(self, data):
        node = self.head.next
        while node != self.tail:
            if node.data == data:
                return node
            node = node.next
        return None

    def append_node(self, node):
        self.tail.ahead.next = node
        node.next = self.tail
        node.ahead = self.tail.ahead 
        self.tail.ahead = node

    def remove_first(self):
        first_node = self.head.next
        self.head.next = first_node.next
        first_node.next.ahead = self.head
        return first_node
    
    def remove_node(self, data):
        node = self.head.next
        while node != self.tail:
            if node.data == data:
                node_ahead = node.ahead
                node_next = node.next
                node_ahead.next = node_next
                node_next.ahead = node_ahead
                return node
            node = node.next
        return None

    def lru_init(self, size):
        cur_node = self.head
        for i in range(0, size):
            cur_node.next = Node(i)
            cur_node.next.ahead = cur_node
            cur_node = cur_node.next
        cur_node.next = self.tail
        self.tail.ahead = cur_node