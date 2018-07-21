import os
from collections import defaultdict
from configparser import ConfigParser
from math import ceil

AM1_CRAFTING_SPEED = 0.5
AM2_CRAFTING_SPEED = 0.75
AM3_CRAFTING_SPEED = 1.25
AM3_CRAFTING_SPEED_SP3 = 1.25 * 3
CRAFTING_SPEED = AM3_CRAFTING_SPEED

DEFAULT_ASSEMBLY_MACHINE = 'assembly_machine_3'
DEFAULT_TRANSPORT_BELT = 'express_transport_belt'
DEFAULT_FURNACE = 'electric_furnace'
DEFAULT_MINING_DRILL = 'electric_mining_drill'

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
                                "crafting_speed": float(Config[item].get('crafting_speed', 1)), \
                                "produced_in": Config[item].get('produced_in', DEFAULT_ASSEMBLY_MACHINE), \
                                "transport": Config[item].get('transport', DEFAULT_TRANSPORT_BELT), \
                                "transport_speed": float(Config[item].get('transport_speed', 0))
                                }
        #print(self.items)

    def get_cost(self, item_dict, max_recurse_depth):
        cost = {}
        cost['ingredients'] = defaultdict(int)
        cost['crafting_time'] = 0
        for (name,count) in item_dict.items():
            item = self.items[name]
            #print(1, name, item['crafting_time'] * count)
            cost['crafting_time'] += item['crafting_time'] * count
            if item['ingredients'] == None or max_recurse_depth == 0:
                cost['ingredients'][name] += count
            else:
                subdict = {key:value*count for (key,value) in item['ingredients'].items()}
                subcost = self.get_cost(subdict, max_recurse_depth-1)
                if max_recurse_depth > 1:
                    #print(2, name, subcost['crafting_time'])
                    cost['crafting_time'] += subcost['crafting_time']
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
        factory['production_units'] = base_cost['crafting_time'] / self.items[self.items[item_name]['produced_in']]['crafting_speed']
        for (ingredient, count) in base_cost['ingredients'].items():
            factory['ingredients'].append((ingredient, count))
        return factory


    def print_factory(self, item_name, rate, recurse_level=0, aggregate_materials=defaultdict(int)):
        if recurse_level == 0:
            print("Factory:")
        factory = self.get_factory(item_name, rate)
        indent_str = '        '*recurse_level
        print('\n%s' % self.get_item_str(item_name, rate, multiline=True, indent_str=indent_str))
        for item_n, count, in factory['ingredients']:
            aggregate_materials[item_n] += count
            if self.items[item_n]['ingredients'] is not None:
                self.print_factory(item_n, count, recurse_level=recurse_level+1, aggregate_materials=aggregate_materials)

        if recurse_level == 0:
            print('\nAggregate Materials:\n')
            for item in aggregate_materials:
                print(self.get_item_str(item, aggregate_materials[item]))


    def get_item_str(self, item_name, rate, multiline=False, indent_str=''):
        '''returns a production machine string (or equivalent) given the item rate'''
        transport_name = self.items[item_name]['transport']
        transport_capacity = 100*rate/(self.items[self.items[item_name]['transport']]['transport_speed'])
        production_unit_name = self.items[item_name]['produced_in']
        production_unit_count = ceil(rate*(self.items[item_name]['crafting_time'])/self.items[self.items[item_name]['produced_in']]['crafting_speed'])
        if multiline:
            return '%s%-22s %6s\n%s%-22s %6s\n%s%-22s %6s' % (indent_str, item_name, '%.1f/s' % rate, indent_str, transport_name, '%.0f%%' % transport_capacity, indent_str, production_unit_name, production_unit_count)
        else:
            return '%s%-28s %6s  %28s  %6s  %28s  %4s' % (indent_str, item_name, '%3.1f/s' % rate, transport_name, '%.0f%%' % transport_capacity, production_unit_name, production_unit_count) 


if __name__ == '__main__':
    R = ResourceCalculator()
    #R.add({"science_pack_1": 1, "science_pack_2": 1, "science_pack_3": 1, "millitary_science_pack": 1, "production_science_pack": 1, "high_tech_science_pack": 1})
    #R.add({"rocket_silo": 1, "rocket_part": 100, "satellite": 1})
    R.print_factory("processing_unit", 1)
    #R.get_factory("express_transport_belt", 1)
