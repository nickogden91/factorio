import os
from collections import defaultdict
from configparser import ConfigParser
from math import ceil

AM1_CRAFTING_SPEED = 0.5
AM2_CRAFTING_SPEED = 0.75
AM3_CRAFTING_SPEED = 1.25
AM3_CRAFTING_SPEED_SP3 = 1.25 * 3
CRAFTING_SPEED = AM3_CRAFTING_SPEED

TB_HALF_CAPACITY = 6.66666666
TB_FULL_CAPACITY = 13.3333333
FTB_HALF_CAPACITY = 13.333333
FTB_FULL_CAPACITY = 26.6666666
ETB_HALF_CAPACITY = 20
ETB_FULL_CAPACITY = 40
PIPE_FULL_CAPACITY = 1000

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
                                "mining_time": float(Config[item].get('mining_time', 0)), \
                                "transport": Config[item].get('transport', 'transport_belt'), \
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
            #print(1, name, item['crafting_time'] * count)
            cost['crafting_time'] += item['crafting_time'] * count
            cost['production_time'] += item['production_time'] * count
            cost['smelting_time'] += item['smelting_time'] * count
            if item['ingredients'] == None or max_recurse_depth == 0:
                cost['ingredients'][name] += count
            else:
                subdict = {key:value*count for (key,value) in item['ingredients'].items()}
                subcost = self.get_cost(subdict, max_recurse_depth-1)
                if max_recurse_depth > 1:
                    #print(2, name, subcost['crafting_time'])
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
        factory = {'item_name': item_name, 'rate': rate, 'ingredients': []}
        base_cost = self.get_cost({item_name: rate}, 1)
        production_time = base_cost['crafting_time']
        if not production_time:
            production_time = base_cost['production_time']
        factory['assembly_machines'] = production_time / CRAFTING_SPEED
        for (ingredient, count) in base_cost['ingredients'].items():
            factory['ingredients'].append((ingredient, count))
        return factory


    def print_factory(self, item_name, rate, recurse_level=0, raw_materials=defaultdict(int)):
        if recurse_level == 0:
            print("Factory:")
        factory = self.get_factory(item_name, rate)
        indent_str = '        '*recurse_level
        print('\n%s%s: %4.2f/s' % (indent_str, item_name, rate))
        print('%sassembly_machines: %d' % (indent_str, max(factory['assembly_machines'], 1)))
        print('%s%s' % (indent_str, self.get_transport(item_name, rate)))
        for item_n, count, in factory['ingredients']:
            if self.items[item_n]['smelting_time'] or self.items[item_n]['ingredients'] is None and not 'ore' in item_n:
                raw_materials[item_n] += count
            if self.items[item_n]['smelting_time'] is None or self.items[item_n]['ingredients'] is not None:
                self.print_factory(item_n, count, recurse_level=recurse_level+1, raw_materials=raw_materials)

        if recurse_level == 0:
            print('\nRaw Materials:\n')
            for item in raw_materials:
                if self.items[item]['ingredients'] and 'plate' in item:
                    ore = list(self.items[item]['ingredients'].keys())[0]
                    print('%s: %.2f, furnaces: %d, mining drills: %d' % \
                        (item, \
                         raw_materials[item], \
                         ceil(raw_materials[item]*(self.items[item]['smelting_time'])), \
                         ceil((raw_materials[item]*self.items[ore]['mining_time'])))\
                        )
                else:
                    print('%s: %.2f' % (item, raw_materials[item]))


    def get_production(self, item_name, rate):
        '''returns a production machine string (or equivalent) given the item rate'''
        pass


    def get_transport(self, item_name, rate):
        '''returns a belt type string (or equivalent) given the item rate'''
        item = self.items[item_name]
        if item['transport'] == 'transport_belt':
            # if rate <= 13.3333:
            #     return "transport belt         (%d%%)" % (100*rate/TB_FULL_CAPACITY)
            # if rate <= 26.6666:
            #     return "fast transport belt    (%d%%)" % (100*rate/FTB_FULL_CAPACITY)
            # else:
            #     return "express transport belt (%d%%)" % (100*rate/ETB_FULL_CAPACITY)
            return "express transport belt (%d%%)" % (100*rate/ETB_FULL_CAPACITY)
        if item['transport'] == 'pipe':
            return "pipe                   (%d%%)" % (100*rate/PIPE_FULL_CAPACITY)


if __name__ == '__main__':
    R = ResourceCalculator()
    #R.add({"science_pack_1": 1, "science_pack_2": 1, "science_pack_3": 1, "millitary_science_pack": 1, "production_science_pack": 1, "high_tech_science_pack": 1})
    #R.add({"rocket_silo": 1, "rocket_part": 100, "satellite": 1})
    R.print_factory("advanced_circuit", 10)
    #R.get_factory("express_transport_belt", 1)
