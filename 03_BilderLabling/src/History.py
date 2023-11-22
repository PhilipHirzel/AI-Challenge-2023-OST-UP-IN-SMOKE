

class History:

    def __init__(self,max_back_steps = 20):
        self.history = []
        self.max_back_steps =  max_back_steps

    def __str__(self):
        return str(self.history)

    def add(self,element):
        self.history.append(element)

        if len(self.history) > self.max_back_steps:
            self.history = self.history[abs(len(self.history) - self.max_back_steps):]

    def back_step(self):
        if len(self.history) >= 1:
            element = self.history[-1]
            self.history = self.history[:-1]
            return element
        else:
            raise RuntimeWarning("History is empty!")
    



if __name__ == '__main__':
    myHistory = History(20)
    for i in range(30):
        myHistory.add(i)
        print(myHistory)

    for i in range(30):
        myHistory.back_step()
        print(myHistory)