
class Active_code():
    '''邀请码生成'''
    def __init__(self):
        self.loop = '0123456789abcdefghijklmnopqrstuvwxyz'

    def encode(self, num):
        str_list = []
        while num != 0:
            str_list.append(self.loop[num % 36])
            num = num // 36
        str_list.reverse()
        return ''.join(str_list)

    def decode(self, string):
        return int(string, 36)


ac = Active_code()
print(ac.decode('9'))
