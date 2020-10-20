from os import access
from emulator.linkedlist import LinkedList
from . import log
from . import linkedlist

class Cache(object):
    """ (1) Initialize the cache emulator parameters
        including: cache_width, block_width, replace_algorithm etc.
        All represented in 2^k, eg. 256 = 2^8, so we use 8 to represent 256
        (2) Orginize the cache lines
        (3) Cope with the access requirements
    """
    def __init__(self, cache_width=18, block_width=4, addr_width=64, replace_algo='LRU', write_policy='allocate'):
        self.cache_width = cache_width
        self.block_width = block_width
        self.addr_width = addr_width
        self.replace_algo = replace_algo
        self.write_policy = write_policy
        self.assoc_sets = 0
    
    def address_decoder(self, addr, tag_width):
        """ Parameter:
        addr: hex in str format, like '0101100..." 
        Return:
        tag: binary in str format
        offset: integer as list index
        """
        binary_format = bin(int(addr, base=16))[2:].zfill(self.addr_width)
        return binary_format[0:tag_width], int(binary_format[tag_width:-self.block_width], base=2)
        
    def memory_access(self, addr):
        pass


class DirectMap(Cache):
    """Inherit from Cache, rewrite access() to emulate directly mapping cache organization
    """
    def __init__(self, cache_width=18, block_width=4, addr_width=64, replace_algo='LRU', write_policy='allocate', logger='log_dm.txt'):
        super(DirectMap, self).__init__(cache_width, block_width, addr_width, replace_algo, write_policy)
        self.tag_width = self.addr_width - self.cache_width + self.assoc_sets
        self.offset_width = self.addr_width - self.tag_width - self.block_width
        self.cache_lines = ['x' for i in range(0, 2**self.offset_width)]
        self.logger = log.Logger(logger)
    
    def memory_access(self, addr):
        tag, offset = self.address_decoder(addr, self.tag_width)
        self.logger.cnt += 1
        if tag != self.cache_lines[offset]:
            self.cache_lines[offset] = tag 
            self.logger.report_miss('read', addr)


class SetAssoc(Cache):
    """Inherit from Cache, rewrite access() to emulate set associative cache organization
    """
    def __init__(self, assoc_sets=2, cache_width=18, block_width=4, addr_width=64, replace_algo='LRU', write_policy='allocate', logger='log_sa.txt'):
        super(SetAssoc, self).__init__(cache_width, block_width, addr_width, replace_algo, write_policy)
        self.assoc_sets = assoc_sets
        self.tag_width = self.addr_width - self.cache_width + self.assoc_sets
        self.offset_width = self.addr_width - self.tag_width - self.block_width
        self.cache_lines = [['none' for i in range(0, 2**self.assoc_sets)] for j in range(0, 2**self.offset_width)]
        # self.lru_list = [LinkedList(2**self.assoc_sets) for i in range(0, 2**self.offset_width)]
        self.lru_list = [list(range(0, 2**self.assoc_sets)) for i in range(0, 2**self.offset_width)]
        self.logger = log.Logger(logger) 

    def maintain_lru_list(self, offset, access_line):
        # line = self.lru_list[offset].remove_node(access_line)
        # self.lru_list[offset].append_node(line)
        self.lru_list[offset].remove(access_line)
        self.lru_list[offset].append(access_line)

    def memory_access(self, addr):
        tag, offset = self.address_decoder(addr, self.tag_width)
        self.logger.cnt += 1
        for line in range(0, 2**self.assoc_sets):
            if tag == self.cache_lines[offset][line]: 
                self.maintain_lru_list(offset, line)
                return 
        self.logger.report_miss('read', addr)
        # victim = self.lru_list[offset].remove_first()
        # self.lru_list[offset].append_node(victim)
        # self.cache_lines[offset][victim.data] = tag
        victim = self.lru_list[offset].pop(0)
        self.lru_list[offset].append(victim)
        self.cache_lines[offset][victim] = tag


class MRUAssoc(SetAssoc):
    def __init__(self, assoc_sets=2, cache_width=18, block_width=4, addr_width=64, replace_algo='LRU', write_policy='allocate', logger='log_mru.txt'):
        super(MRUAssoc, self).__init__(assoc_sets, cache_width, block_width, addr_width, replace_algo, write_policy, logger)
    
    def memory_access(self, addr):
        tag, offset = self.address_decoder(addr, self.tag_width)
        self.logger.cnt += 1
        if self.cache_lines[offset][self.lru_list[offset][-1]] == tag:
            self.logger.first_hit_cnt += 1 
            return
        for line in range(0, 2**self.assoc_sets):
            if tag == self.cache_lines[offset][line]: 
                self.maintain_lru_list(offset, line)
                return 
        self.logger.report_miss('read', addr)
        victim = self.lru_list[offset].pop(0)
        self.lru_list[offset].append(victim)
        self.cache_lines[offset][victim] = tag


class MCAssoc(SetAssoc):
    def __init__(self, assoc_sets=2, cache_width=18, block_width=4, addr_width=64, replace_algo='LRU', write_policy='allocate', logger='log_mc.txt'):
        super(MCAssoc, self).__init__(assoc_sets, cache_width, block_width, addr_width, replace_algo, write_policy, logger)
        self.bitvec = [[[0 for i in range(0, 2**self.assoc_sets)] for j in range(0, 2**self.assoc_sets)] for k in range(0, 2**self.offset_width)]
    
    def swap_lines(self, offset, src, dst):
        # Maintain bit vector
        self.cache_lines[offset][src], self.cache_lines[offset][dst] = self.cache_lines[offset][dst], self.cache_lines[offset][src]
        self.bitvec[offset][dst][src] = 1
        # Maintain LRU list
        dst_index = self.lru_list[offset].index(dst)
        self.lru_list[offset][dst_index] = src
        self.lru_list[offset].remove(src)
        self.lru_list[offset].append(dst)

    def memory_access(self, addr):
        tag, offset = self.address_decoder(addr, self.tag_width)
        loc = int(tag[-self.assoc_sets:], base=2)
        self.logger.cnt += 1
        if self.cache_lines[offset][loc] == tag:
            self.logger.first_hit_cnt += 1
            self.maintain_lru_list(offset, loc)
            return
        if self.cache_lines[offset][loc][-self.assoc_sets:] != tag[-self.assoc_sets:]:
            self.logger.search_cnt += 1
            for line in range(0, 2**self.assoc_sets):
                if self.bitvec[offset][loc][line] == 1:
                    self.logger.search_length += 1
                    if self.cache_lines[offset][line] == tag:
                        self.swap_lines(offset, line, loc)
                        return
        else:
            for line in range(0, 2**self.assoc_sets):
                if self.bitvec[offset][loc][line] == 1:
                    if self.cache_lines[offset][line] == tag:
                        self.swap_lines(offset, line, loc)
                        return
        self.logger.report_miss('read', addr)
        victim = self.lru_list[offset].pop(0)
        self.lru_list[offset].append(victim)
        self.cache_lines[offset][victim] = tag
        self.swap_lines(offset, victim, loc)


class MCPAssoc(SetAssoc):
    def __init__(self, assoc_sets=2, cache_width=18, block_width=4, addr_width=64, replace_algo='LRU', write_policy='allocate', logger='log_mcp.txt'):
        super(MCPAssoc, self).__init__(assoc_sets, cache_width, block_width, addr_width, replace_algo, write_policy, logger)
        self.bitvec = [[-1 for i in range(0, 2**self.assoc_sets)] for j in range(0, 2**self.offset_width)]
    
    def swap_lines(self, offset, src, dst):
        # Maintain bit vector
        self.cache_lines[offset][src], self.cache_lines[offset][dst] = self.cache_lines[offset][dst], self.cache_lines[offset][src]
        self.bitvec[offset][dst] = src
        # Maintain LRU list
        dst_index = self.lru_list[offset].index(dst)
        self.lru_list[offset][dst_index] = src
        self.lru_list[offset].remove(src)
        self.lru_list[offset].append(dst)

    def memory_access(self, addr):
        tag, offset = self.address_decoder(addr, self.tag_width)
        loc = int(tag[-self.assoc_sets:], base=2)
        self.logger.cnt += 1
        if self.cache_lines[offset][loc] == tag:
            self.logger.first_hit_cnt += 1
            self.maintain_lru_list(offset, loc)
            return
        candidate = self.bitvec[offset][loc]
        if candidate != -1:
            if self.cache_lines[offset][candidate] == tag:
                self.swap_lines(offset, candidate, loc)
                return
        self.logger.report_miss('read', addr)
        victim = self.lru_list[offset].pop(0)
        self.lru_list[offset].append(victim)
        self.cache_lines[offset][victim] = tag
        self.swap_lines(offset, victim, loc)



