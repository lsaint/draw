# -*- coding:utf-8 -*-
'''
    file: inventory.py
    date: 2011-10-10
    desc: 玩家道具以及背包类

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from draw_common import DrawObjConfig

class Bag(object):
    def __init__(self, inventory_capacity ):
        self._capacity = inventory_capacity
        self._inventory = {}
        
    def NewCategory( self, category_id, category_capacity, category_init_amount ):
        if len(self._inventory) < self._capacity and not self._inventory.has_key(category_id):
            if category_init_amount > category_capacity:
                category_init_amount = category_capacity
            new_object = BagObject(category_id, category_capacity, category_init_amount)
            self._inventory[category_id] = new_object
            
    def GetObjAmount(self, category_id):
        bag_object = self._inventory.get(category_id)
        if bag_object is not None:
            return bag_object.GetAmount()
        return 0

    def GetObjCapacity(self, category_id):
        bag_object = self._inventory.get(category_id)
        if bag_object is not None:
            return bag_object.GetCapacity()
        return 0
        
    def ChangeObjAmount(self, category_id, delta):
        bag_object = self._inventory.get(category_id)
        if bag_object is not None:
            return bag_object.ChangeAmount(delta)
        return False

class BagObject(object):
    def __init__(self, category_id, category_capacity, category_init_amount):
        self._id = category_id
        self._capacity = category_capacity
        self._amount = category_init_amount

    def GetCapacity(self):
        return self._capacity
        
    def GetAmount(self):
        return self._amount
        
    def SetAmount(self, new_amount):
        if new_amount < 0 or new_amount > self._capacity:
            return False
        
        self._amount = new_amount
        return True
        
    def ChangeAmount(self, delta):
        final_amount = self._amount + delta
        if final_amount < 0 or final_amount > self._capacity:
            return False

        self._amount = final_amount
        return True
        