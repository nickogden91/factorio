import os
from collections import defaultdict
from configparser import ConfigParser

class ResourceCalculator:

    def __init__(self):
        self.build_dict()
        #self.test()
        self.clear()

    def build_dict(self):
        self.items = {}
        Config = ConfigParser()
        Config.read('items.txt')
        for item in Config.sections():
            ingredients = {}
            data = Config[item]['ingredients'].split(', ')
            if data == ['None']:
                ingredients = None
            else:
                for i in data:
                    ingredients[i.split(': ')[0]] = float(i.split(': ')[1])
            time = float(Config[item]['time'])
            self.items[item] = {"ingredients": ingredients, "time": time}
        #print(self.items)

    def clear(self):
        self.cost = defaultdict(int)
        self.time = 0

    def add(self, item_dict, max_recurse_depth):
        for (name,count) in item_dict.items():
            item = self.items[name]
            if max_recurse_depth > 0:
                self.time += item['time'] * count
            if item['ingredients'] == None or max_recurse_depth == 0:
                self.cost[name] += count
            else:
                self.add({key:value*count for (key,value) in item['ingredients'].items()}, max_recurse_depth-1)

    def print_(self):
        print("cost:", dict(self.cost))
        print("time:", self.time)

    def test(self):
        for item in self.items:
            self.clear()
            self.add({item: 1})
            #print(item, dict(self.cost))



if __name__ == '__main__':
    R = ResourceCalculator()
    #R.add({"science_pack_1": 1, "science_pack_2": 1, "science_pack_3": 1, "millitary_science_pack": 1, "production_science_pack": 1, "high_tech_science_pack": 1})
    #R.add({"rocket_silo": 1, "rocket_part": 100, "satellite": 1})
    R.add({"advanced_circuit": 1}, 2)
    R.print_()
