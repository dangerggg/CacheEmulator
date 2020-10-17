# from emulator import cache
from emulator import cache
import re

def run(trace_file):
    f = open(trace_file)
    dm_cache = cache.DirectMap()
    assoc_cache = cache.SetAssoc()
    mru_cache = cache.MRUAssoc()
    for line in f.readlines():
        line_sp = re.split('[ ]+', line.strip())
        dm_cache.memory_access(line_sp[1])
        assoc_cache.memory_access(line_sp[1])
        mru_cache.memory_access(line_sp[1])
    dm_cache.logger.end_emulate()
    assoc_cache.logger.end_emulate()
    mru_cache.logger.end_emulate()

if __name__ == '__main__':
    run("testcase/astar.trace")