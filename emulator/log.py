
class Logger(object):
    def __init__(self, filename):
        self.filename = filename
        self.file_handler = open(filename, 'w')
        self.cnt = 0
        self.miss_cnt = 0
        self.first_hit_cnt = 0
        self.search_cnt = 0
        self.search_length = 0
        self.log_text = ""

    def report_miss(self, op, addr):
        self.miss_cnt += 1
        # self.log_text += "[%d] %s@ %s\n" % (self.cnt, op, addr)
    
    def get_hit_rate(self):
        return 1.0 - self.miss_cnt / self.cnt
    
    def get_first_hit_rate(self):
        return self.first_hit_cnt / self.cnt

    def get_none_first_hit_rate(self):
        return (self.cnt - self.first_hit_cnt - self.miss_cnt) / self.cnt

    def get_avg_search_length(self):
        return self.search_length / self.search_cnt

    def end_emulate(self):
        if self.first_hit_cnt > 0:
            print("First hit rate: ", self.first_hit_cnt / self.cnt)
            print("Non-first hit rate: ", (self.cnt - self.first_hit_cnt - self.miss_cnt) / self.cnt)
        print("Hit rate: ", 1.0- self.miss_cnt / self.cnt)
        self.file_handler.write(self.log_text)
        self.file_handler.close()