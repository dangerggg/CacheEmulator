# from emulator import cache
from emulator import cache
import re

def run(trace_file):
    print(trace_file)
    f = open(trace_file)
    dm_cache = cache.DirectMap()
    assoc_cache = cache.SetAssoc()
    mru_cache = cache.MRUAssoc()
    mc_cache = cache.MCAssoc()
    mcp_cache = cache.MCPAssoc()
    for line in f.readlines():
        line_sp = re.split('[ ]+', line.strip())
        dm_cache.memory_access(line_sp[1])
        assoc_cache.memory_access(line_sp[1])
        mru_cache.memory_access(line_sp[1])
        mc_cache.memory_access(line_sp[1])
        mcp_cache.memory_access(line_sp[1])
    print("-----------------")
    print("Directly Map:")
    dm_cache.logger.end_emulate()
    print("-----------------")
    print("Associated Sets:")
    assoc_cache.logger.end_emulate()
    print("-----------------")
    print("MRU:")
    mru_cache.logger.end_emulate()
    print("-----------------")
    print("Multi-Column:")
    mc_cache.logger.end_emulate()
    print("-----------------")
    print("Multu-Column Partial:")
    mcp_cache.logger.end_emulate()
    print("-----------------")
    f.close()

if __name__ == '__main__':
    run("testcase/astar.trace")
    run("testcase/bzip2.trace")
    run("testcase/mcf.trace")
    run("testcase/perlbench.trace")