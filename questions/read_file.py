import os
import json
import random
import shutil
from object import ObjectPulley
from itertools import combinations
from math import ceil


def read_annotation_pulley(path, sim):
    if os.path.isfile(path) and path.endswith(".json"):
        # Read the JSON data from the file and append it to the list
        with open(path, "r") as f:
            data = json.load(f)
            if data["validity"] == False:
                return False
            
            mass_info = data["outputMass"]
 
            # create the objects from the mass_info dictionary and add them to the sim
            for name, mass in mass_info.items():
                # extract the color and shape from the object name (assuming format "{color} {shape}")
                n_split = name.split(' ')
                shape = n_split[-1]
                color = ""
                for i in range(len(n_split)-2):
                    color = color + n_split[i] + " "
                color = color + n_split[len(n_split)-2]
                # create a new object with the extracted properties and the given mass
                # mass_real = round(float(mass),2)
                mass_real = ceil(float(mass*100))/100
                if len(str(mass_real)) > 3 and str(mass_real)[-1] != '0' and str(mass_real)[-1] != '5':
                    breakpoint()
                obj = ObjectPulley(color=color, mass=mass_real, shape=shape, dynamics='dynamic', class_type='object', motion='stationary', tension='null')
                # if the object already exists in sim.objects, update its mass
                for existing_obj in sim.objects:
                    if existing_obj.color == obj.color and existing_obj.shape == obj.shape:
                        existing_obj.mass = obj.mass
                        obj = existing_obj
                        break
                # add the object to the sim

                sim.add_object(obj, name.split('(')[0].lower().strip())
            
            relation_info = data["relatedGroups"]
            # add the relation information to the sim.relations
            for group in relation_info:
                group_set = set(group)
                for obj1_n, obj2_n in combinations(group_set, 2):
                    obj1_name, obj2_name = obj1_n.split('(')[0].strip().lower(), obj2_n.split('(')[0].strip().lower()
                    if obj1_name in sim.name_object_map:
                        obj1 = sim.name_object_map[obj1_name]
                    else:
                        continue

                    if obj2_name in sim.name_object_map:
                        obj2 = sim.name_object_map[obj2_name]
                    else:
                        continue

                    sim.add_relation(obj1, obj2)

                for i in range(len(group)):
                    if 'ynamic' in group[i]:
                        obj_name = None
                        if i-2 >= 0:
                            if 'ube' in group[i-2] or 'phere' in group[i-2]:
                                obj_name = group[i-2].split('(')[0].strip().lower()
                        if i+2 < len(group):
                            if 'ube' in group[i+2] or 'phere' in group[i+2]:
                                obj_name = group[i+2].split('(')[0].strip().lower()

                        if obj_name is not None:
                            obj = sim.name_object_map[obj_name]
                            sim.link_dy_pulley.append(obj)
                        else:
                            continue

                    if 'ube' in group[i] or 'phere' in group[i]:
                        if i == 0:
                            obj = group[i].lower().strip()
                            rope = group[i+1].lower().strip()
                            if 'rope' not in rope:
                                # breakpoint()
                                continue
                            sim.add_rope_map(obj, rope)

                        elif i == len(group)-1:
                            obj = group[i].lower().strip()
                            rope = group[i-1].lower().strip()
                            if 'rope' not in rope:
                                # breakpoint()
                                continue
                            sim.add_rope_map(obj, rope)

                        else:
                            obj = group[i].lower().strip()
                            if 'ynamic' in group[i+2]:
                                rope = group[i+1].lower().strip()
                            elif 'ynamic' in group[i-2]:
                                rope = group[i-1].lower().strip()
                            else:
                                if 'ope' in group[i-1]:
                                    rope = group[i-1].lower().strip()
                                elif 'ope' in group[i+1]:
                                    rope = group[i+1].lower().strip()
                                else:
                                    breakpoint()
                                    continue
                            sim.add_rope_map(obj, rope)
                        
            relation_rope_info = data["relatedGroupsInRope"]
            tension_rope_info = data["ResultTension"]
            # add the rope to the sim.objects
            for group in relation_rope_info:
                rope_objs = []
                g_list = list(group.keys())
                for i in range(len(g_list)):
                    rope_name = g_list[i].split('(')[0].strip()
                    n_split = rope_name.split(' ')
                    color = ""
                    for j in range(len(n_split)-2):
                        color = color + n_split[j] + " "
                    color = color + n_split[len(n_split)-2]
                    tension = list(tension_rope_info[color + " Rope"].values())[0]
                    obj = ObjectPulley(color=color, mass="null", shape="Rope", dynamics='dynamic', class_type='rope', motion='stationary', tension=abs(tension))
                    # add the object to the sim
                    sim.add_object(obj, rope_name.lower())
                    rope_objs.append(obj)
                # add relations between ropes in the same group
                for i in range(len(rope_objs)):
                    for j in range(i+1, len(rope_objs)):
                        sim.add_relation(rope_objs[i], rope_objs[j])
                        
            # add the pulley, fixed point to the sim.objects
            for group in relation_rope_info:
                for obj_linked in group.values():
                    for obj_name in obj_linked:
                        # ignore any content in parentheses when adding object information
                        obj_color_shape = obj_name.split('(')[0].strip()
                        n_split = obj_color_shape.split(' ')
                        # create a new object with the extracted properties
                        if "Fixed Point" in obj_name:
                            color = ""
                            for i in range(len(n_split)-3):
                                color = color + n_split[i] + " "
                            color = color + n_split[len(n_split)-3]
                            obj = ObjectPulley(color=color, mass="null", shape="Fixed Point", dynamics='static', class_type='fixed point', motion='stationary', tension='null')
                        elif "Dynamic Pulley" in obj_name:
                            color = ""
                            for i in range(len(n_split)-4):
                                color = color + n_split[i] + " "
                            color = color + n_split[len(n_split)-4]
                            obj = ObjectPulley(color=color, mass="null", shape=n_split[-3] + " Pulley", dynamics='dynamic', class_type='pulley', motion='stationary', tension='null')
                        elif "Static Pulley" in obj_name:
                            color = ""
                            for i in range(len(n_split)-4):
                                color = color + n_split[i] + " "
                            color = color + n_split[len(n_split)-4]
                            obj = ObjectPulley(color=color, mass="null", shape=n_split[-3] + " Pulley", dynamics='static', class_type='pulley', motion='stationary', tension='null')
                        # add the object to the sim
                        sim.add_object(obj, obj_name.split('(')[0].lower().strip())
                        
            # read CounterFactualAnnotations
            counterfactual_info = data["CounterFactualAnnotations"]

            for item in counterfactual_info:
                c_dict=counterfactual_info[item]
                try:
                    c_dict0=c_dict["0"]
                    c_dict1=c_dict["1"]
                    sim.counterfactual[item+"_0"]=c_dict0
                    sim.counterfactual[item+"_1"]=c_dict1
                except:
                    print("Counterfactual not exists")
                    continue
                
            group_info = data["relatedGroupsInRope"]
            sim.rope_group=group_info
            #print(sim.counterfactual)
            return True
