import os
import json
import random
import shutil


class ObjectPulley:
    def __init__(self, color, mass, shape, dynamics, class_type, motion, tension=0):
        self.color = color
        self.mass = mass
        self.shape = shape
        self.dynamics = dynamics
        self.class_type = class_type
        self.motion = motion
        self.tension = tension

class SimulationPulley:
    def __init__(self):
        self.objects = []
        self.relations = {}
        self.counterfactual = {}
        self.rope_group=[]

        self.name_object_map = {}
        self.object_rope_map = {}
        self.link_dy_pulley = []

    def add_object(self, obj, name):
        for existing_obj in self.objects:
            if all([
                existing_obj.color == obj.color,
                existing_obj.mass == obj.mass,
                existing_obj.shape == obj.shape,
                existing_obj.dynamics == obj.dynamics,
                existing_obj.class_type == obj.class_type,
                existing_obj.motion == obj.motion,
                existing_obj.tension == obj.tension,
            ]):
                return False
        obj.name = name
        self.objects.append(obj)
        self.name_object_map[name] = obj
        return True

    def remove_object(self, obj):
        breakpoint() # should not happen
        self.objects.remove(obj)
        if obj in self.relations:
            del self.relations[obj]
        for other_obj in self.relations:
            if obj in self.relations[other_obj]:
                self.relations[other_obj].remove(obj)

    def add_relation(self, obj1, obj2):
        if obj1 not in self.objects or obj2 not in self.objects:
            return False
        if obj1 not in self.relations:
            self.relations[obj1] = []
        if obj2 not in self.relations[obj1]:
            self.relations[obj1].append(obj2)

        if obj2 not in self.relations:
            self.relations[obj2] = []
        if obj1 not in self.relations[obj2]:
            self.relations[obj2].append(obj1)
        return True
    
    def add_rope_map(self, object, rope):
        object = object.lower().strip()
        rope = rope.lower().strip()
        
        self.object_rope_map[object] = rope

    def remove_relation(self, obj1, obj2):
        if obj1 in self.relations and obj2 in self.relations[obj1]:
            self.relations[obj1].remove(obj2)
            self.relations[obj2].remove(obj1)
            return True
        return False
    
    def print_objs(self):
        print("Objects:")
        for obj in self.objects:
            print(f"Color: {obj.color}, Mass: {obj.mass}, Shape: {obj.shape}, Dynamics: {obj.dynamics}, Class: {obj.class_type}, Motion: {obj.motion}, Tension: {obj.tension}")

    def print_relations(self):
        print("Relations:")
        for obj in self.relations:
            for other_obj in self.relations[obj]:
                print(f"({obj.color}, {obj.shape}) is related to ({other_obj.color}, {other_obj.shape})")
    
    def check_relation(self, obj1, obj2):
        if obj1 in self.relations and obj2 in self.relations[obj1]:
            return True
        return False
    
    def find_object_by_color(self, obj_color):
        for obj in self.objects:
            if obj.color == obj_color and obj.class_type == "object":
                return obj
        return None

