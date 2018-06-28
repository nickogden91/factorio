import os
from collections import defaultdict
from configparser import ConfigParser

class ResourceCalculator:

    def __init__(self):
        self.build_dict()
        self.test()

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
            self.items[item] = {"ingredients": ingredients, \
                                "crafting_time": float(Config[item].get('crafting_time', 0)), \
                                "production_time": float(Config[item].get('production_time', 0)), \
                                "smelting_time": float(Config[item].get('smelting_time', 0)), \
                                }
        #print(self.items)

    def get_cost(self, item_dict, max_recurse_depth):
        cost = defaultdict(int)
        cost['crafting_time'] = 0
        for (name,count) in item_dict.items():
            item = self.items[name]
            print(name, count, item['crafting_time'])
            cost['crafting_time'] += item['crafting_time'] * count
            cost['production_time'] += item['production_time'] * count
            cost['smelting_time'] += item['smelting_time'] * count
            if item['ingredients'] == None or max_recurse_depth == 0:
                cost[name] += count
            else:
                subcost = self.get_cost({key:value*count for (key,value) in item['ingredients'].items()}, max_recurse_depth-1)
                for (name,count) in subcost.items():
                    cost[name] += count
        return dict(cost)

    def test(self):
        for item in self.items:
            print(self.get_cost({item: 1}, 1000))



if __name__ == '__main__':
    R = ResourceCalculator()
    #R.add({"science_pack_1": 1, "science_pack_2": 1, "science_pack_3": 1, "millitary_science_pack": 1, "production_science_pack": 1, "high_tech_science_pack": 1})
    #R.add({"rocket_silo": 1, "rocket_part": 100, "satellite": 1})
    print(R.get_cost({"advanced_circuit": 1}, 3))
