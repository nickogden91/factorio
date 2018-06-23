import os
from collections import defaultdict
from configparser import ConfigParser

class ResourceCalculator:

    def __init__(self):
        self.build_dict()
        self.test()
        self.clear_cost()

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
            self.items[item] = {"ingredients": ingredients}

    def clear_cost(self):
        self.cost = defaultdict(int)

    def add_cost(self, item_dict):
        for (name,count) in item_dict.items():
            item = self.items[name]
            if item['ingredients'] == None:
                self.cost[name] += count
            else:
                self.add_cost({key:value*count for (key,value) in item['ingredients'].items()})

    def print_cost(self):
        print(dict(self.cost))

    def test(self):
        for item in self.items:
            self.clear_cost()
            self.add_cost({item: 1})
            print(item, dict(self.cost))



if __name__ == '__main__':
    R = ResourceCalculator()
    R.add_cost({"science_pack_1": 1, "science_pack_2": 1, "science_pack_3": 1, "millitary_science_pack": 1, "production_science_pack": 1, "high_tech_science_pack": 1})
    #R.add_cost({"rocket_silo": 1, "rocket_part": 100, "satellite": 1})