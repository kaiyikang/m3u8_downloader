import argparse
import os

class AbstractParam:
    def __init__(self):
        # 新建一个基类
        self.parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
    def return_param(self, isprint= True):
        """打印函数，调用之后会打印所有的变量，并且将变量保存成特定文件。

        Returns:
            [dict]: 返回字典，为了主程序读取参数
        """
        self.opt = self.parser.parse_args()
        if isprint:
            print(">> the list of parameter: ")
            args = vars(self.opt)
            # print all values
            for k, v in sorted(args.items()):
                print("--%s: %s" % (str(k), str(v)))
        return args

class BasicParam(AbstractParam):
    """Record tha basic parameters like root path, epoch, batch_size and so on.
    """
    def __init__(self):
        super(BasicParam,self).__init__()    
        self.parser.add_argument("--url", type=str, required=True, help="请给出 jable 的 url 地址")
        self.parser.add_argument("--num_threads", type=str, default=4,  help="线程的数量")
        self.parser.add_argument("--is_proxy", type=bool, default=False, help="是否需要代理")


if __name__ == "__main__":
    demo = BasicParam()
    args = demo.print_param() 
    print(args.return_param)


