import os
from collections import defaultdict
from configparser import ConfigParser

AM1_CRAFTING_SPEED = 0.5
AM2_CRAFTING_SPEED = 0.75
AM3_CRAFTING_SPEED = 1.25
CRAFTING_SPEED = AM2_CRAFTING_SPEED

TB_HALF_CAPACITY = 6.66666666
TB_FULL_CAPACITY = 13.3333333
FTB_HALF_CAPACITY = 13.333333
FTB_FULL_CAPACITY = 26.6666666
ETB_HALF_CAPACITY = 20
ETB_FULL_CAPACITY = 40

class ResourceCalculator:

    def __init__(self):
        self.build_dict()
        #self.test()

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
        cost = {}
        cost['ingredients'] = defaultdict(int)
        cost['crafting_time'] = 0
        cost['production_time'] = 0
        cost['smelting_time'] = 0
        for (name,count) in item_dict.items():
            item = self.items[name]
            cost['crafting_time'] += item['crafting_time'] * count
            cost['production_time'] += item['production_time'] * count
            cost['smelting_time'] += item['smelting_time'] * count
            if item['ingredients'] == None or max_recurse_depth == 0:
                cost['ingredients'][name] += count
            else:
                subdict = {key:value*count for (key,value) in item['ingredients'].items()}
                subcost = self.get_cost(subdict, max_recurse_depth-1)
                if max_recurse_depth > 1:
                    cost['crafting_time'] += subcost['crafting_time']
                    cost['production_time'] += subcost['production_time']
                    cost['smelting_time'] += subcost['smelting_time']
                for (name,count) in subcost['ingredients'].items():
                    cost['ingredients'][name] += count
        return dict(cost)

    def test(self):
        for item in self.items:
            print(self.get_cost({item: 1}, 1000))


    def get_factory(self, item_name, rate):
        '''item_name: item to craft, rate: desired products/s'''
        base_cost = self.get_cost({item_name: rate}, 1)
        num_assembly_machines = base_cost['crafting_time'] / CRAFTING_SPEED
        print('assembly machines:', num_assembly_machines)
        for (ingredient, count) in base_cost['ingredients'].items():
            print("%s: %s/s %s" % (ingredient, count, self.get_belt(count)))


    def get_belt(self, rate):
        '''returns a belt type string given the item rate'''
        if rate <= 13.3333:
            return "Transport Belt (%d%%)" % (100*rate/TB_FULL_CAPACITY)
        if rate <= 26.6666:
            return "Fast Transport Belt (%d%%)" % (100*rate/FTB_FULL_CAPACITY)
        if rate <= 40:
            return "Express Transport Belt (%d%%)" % (100*rate/ETB_FULL_CAPACITY)


if __name__ == '__main__':
    R = ResourceCalculator()
    #R.add({"science_pack_1": 1, "science_pack_2": 1, "science_pack_3": 1, "millitary_science_pack": 1, "production_science_pack": 1, "high_tech_science_pack": 1})
    #R.add({"rocket_silo": 1, "rocket_part": 100, "satellite": 1})
    #print(R.get_cost({"advanced_circuit": 1}, 1))
    R.get_factory("advanced_circuit", 10)
