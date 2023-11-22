import random

class ImageQueue:
    def __init__(self,data=[]):
        self.queue = data

    def get_next(self):
        if len(self.queue) > 0:
            element = self.queue[0]
            self.queue = self.queue[1:]
            return element
        else:
            raise RuntimeError("Queue is empty!")
        
    def peak(self):
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            raise RuntimeError("Queue is empty!")
    
    def add_to_top(self,element):
        self.queue.insert(0,element)


    def __len__(self):
        return len(self.queue)
    
    def __str__(self):
        return str(self.queue)
    
    def shuffle(self):
        random.shuffle(self.queue)


if __name__ == '__main__':
    myHistory = ImageQueue([i for i in range(30)])

    for i in range(20):
        el = myHistory.get_next()
        print(el,myHistory)

    for i in range(100,110):
        myHistory.add_to_top(i)
        print(i,myHistory)
