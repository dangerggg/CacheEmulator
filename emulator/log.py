
class Logger(object):
    def __init__(self, filename):
        self.filename = filename
        self.file_handler = open(filename, 'w')
        self.cnt = 0
        self.miss_cnt = 0
        self.first_hit_cnt = 0
        self.log_text = ""

    def report_miss(self, op, addr):
        self.miss_cnt += 1
        self.log_text += "[%d] %s@ %s\n" % (self.cnt, op, addr)

    def end_emulate(self):
        if self.first_hit_cnt > 0:
            print("First hit rate: ", self.first_hit_cnt / self.cnt)
            print("Non-first hit rate: ", (self.cnt - self.first_hit_cnt - self.miss_cnt) / self.cnt)
        print("Hit rate: ", 1 - self.miss_cnt / self.cnt)
        self.file_handler.write(self.log_text)
        self.file_handler.close()