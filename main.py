# from emulator import cache
from emulator import cache
import re
from prettytable import PrettyTable

table = PrettyTable(['测试用例', '组织方式', '总命中率', '一次命中率', '非一次命中率'])

def run(trace_file):
    f = open(trace_file)
    # DM
    dm_cache = cache.DirectMap(logger='log/log_dm.txt')
    # SA
    assoc_cache = []
    for i in range(1, 5):
        assoc_cache.append(cache.SetAssoc(i, logger='log/log_sa'+str(2**i)+'.txt'))
    # MRU 
    mru_cache = []
    for i in range(1, 5):
        mru_cache.append(cache.MRUAssoc(i, logger='log/log_mru'+str(2**i)+'.txt'))
    # MC 
    mc_cache = []
    for i in range(1, 5):
        mc_cache.append(cache.MCAssoc(i, logger='log/log_mc'+str(2**i)+'.txt'))
    # MCP 
    mcp_cache = []
    for i in range(1, 5):
        mcp_cache.append(cache.MCPAssoc(i, logger='log/log_mcp'+str(2**i)+'.txt'))
    
    for line in f.readlines():
        line_sp = re.split('[ ]+', line.strip())
        dm_cache.memory_access(line_sp[1])
        for assoc in assoc_cache:
            assoc.memory_access(line_sp[1])
        for mru in mru_cache:
            mru.memory_access(line_sp[1])
        for mc in mc_cache:
            mc.memory_access(line_sp[1])
        for mcp in mcp_cache:
            mcp.memory_access(line_sp[1])

    table.add_row([trace_file, 'DM', dm_cache.logger.get_hit_rate(), ' ', ' '])
    for i in range(1, 5):
        table.add_row([' ', 'SA-'+str(2**i), assoc_cache[i-1].logger.get_hit_rate(), ' ', ' '])
    for i in range(1, 5):
        table.add_row([' ', 'MRU-'+str(2**i), mru_cache[i-1].logger.get_hit_rate(), mru_cache[i-1].logger.get_first_hit_rate(), mru_cache[i-1].logger.get_none_first_hit_rate()])
    for i in range(1, 5):
        table.add_row([' ', 'MC-'+str(2**i), mc_cache[i-1].logger.get_hit_rate(), mc_cache[i-1].logger.get_first_hit_rate(), mc_cache[i-1].logger.get_none_first_hit_rate()])
        print('multi-column('+str(2**i)+') search length: ', mc_cache[i-1].logger.get_avg_search_length())
    for i in range(1, 5):
        table.add_row([' ', 'MCP-'+str(2**i), mcp_cache[i-1].logger.get_hit_rate(), mcp_cache[i-1].logger.get_first_hit_rate(), mcp_cache[i-1].logger.get_none_first_hit_rate()])

    f.close()

if __name__ == '__main__':
    run('testcase/astar.trace')
    run('testcase/bzip2.trace')
    run('testcase/mcf.trace')
    run('testcase/perlbench.trace')
    print(table)
    