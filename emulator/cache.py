from . import log

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
        self.cache_lines = ['x'] * 2**self.offset_width
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
        self.cache_lines = [['x'] * 2**self.assoc_sets] * 2**self.offset_width
        self.lru_list = [list(range(0, 2**self.assoc_sets))] * 2**self.offset_width
        self.logger = log.Logger(logger) 

    def maintain_lru_list(self, offset, access_line):
        lru_index = self.lru_list[offset].index(access_line)
        self.lru_list[offset].append(self.lru_list[offset].pop(lru_index))

    def memory_access(self, addr):
        tag, offset = self.address_decoder(addr, self.tag_width)
        self.logger.cnt += 1
        for line in range(0, 2**self.assoc_sets):
            if tag == self.cache_lines[offset][line]: 
                self.maintain_lru_list(offset, line)
                return 
        self.logger.report_miss('read', addr)
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
    pass