import os
import json
import random
import shutil
from itertools import permutations, product

EPS = 1e-5

class QuestionEnginePulley:
    def __init__(self, simulation, templates):
        self.simulation = simulation
        self.templates = templates
        self.template_generators = {
            "mass": self.generate_mass,
            "tension": self.generate_tension,
            "color": self.generate_color,
            "shape": self.generate_shape,
            "existence": self.generate_existence,

            "rope_counterfactual": self.generate_cf,
            "rope_counterfactual2": self.generate_cf2,
            "rope_goaldriven": self.generate_gd,
        }
        self.colors = set(['black', 'orange', 'yellow', 'brown', 'black', 'purple', 'cyan', 'gray', 'red', 'white', 'pink', 'blue', 'green']) 
        # self.object_colors = self.rope_colors - set(['black'])
        self.shapes = set(["cube", "sphere", "pulley", "solid pulley", "hollow pulley", "rope", "fixed point"])
        self.exact_shapes = self.shapes - set(["pulley"])
        self.types = set(["cube", "sphere", "pulley", "rope", "fixed"])
        self.pshape = set(["hollow", "solid"])
        self.dyn = set(["dynamic", "static"])

        self.comp_dict = {
                "greater than": lambda x, y, k: x > y*k + EPS,
                "less than": lambda x, y, k: x < y*k - EPS,
                "equal to": lambda x, y, k: abs(x - y*k) < EPS,
                # "exactly": lambda x, y, k: abs(x - y*k) < eps,
                # "no less than": lambda x, y, k: x > y*k - eps,
                # "no greater than": lambda x, y, k: x < y*k + eps
        }
        self.factor_dict = {
            '': 1,
            'twice ': 2,
            'half ': 0.5,
        }

    def abbr_object_name(self, obj_name):
        def _parse_color(obj_name_list):
            for color in self.colors:
                if color in obj_name_list:
                    return color
            return None
        
        def _parse_type(obj_name_list):
            for type in self.types:
                if type in obj_name_list:
                    return 'fixed point' if type == 'fixed' else type
            return None
        
        def _parse_pshape(obj_name_list):
            for pshape in self.pshape:
                if pshape in obj_name_list:
                    return pshape
            return None
        
        def _parse_dyn(obj_name_list):
            for dyn in self.dyn:
                if dyn in obj_name_list:
                    return dyn
            return None
        
        target_name_list = obj_name.strip().split(' ')
        color = _parse_color(target_name_list)
        type = _parse_type(target_name_list)
        pshape = _parse_pshape(target_name_list)
        dyn = _parse_dyn(target_name_list)

        if color is None or type is None:
            breakpoint()

        is_only = 0
        for o in self.simulation.objects:
            nl = o.name.strip().split(' ')
            c = _parse_color(nl)
            t = _parse_type(nl)
            if c == color and t == type:
                is_only += 1

        if is_only == 0:
            breakpoint()
        elif is_only == 1:
            return color + ' ' + type
        else:
            is_only = 0
            for o in self.simulation.objects:
                nl = o.name.strip().split(' ')
                c = _parse_color(nl)
                t = _parse_type(nl)
                p = _parse_pshape(nl)
                if c == color and t == type and p == pshape:
                    is_only += 1
            if is_only == 1:
                return obj_name if is_only > 1 else color + ' ' + pshape + ' ' + type
            if is_only == 0:
                breakpoint()
            else:
                is_only = 0
                for o in self.simulation.objects:
                    nl = o.name.strip().split(' ')
                    c = _parse_color(nl)
                    t = _parse_type(nl)
                    d = _parse_dyn(nl)
                    if c == color and t == type and d == dyn:
                        is_only += 1
                return obj_name if is_only > 1 else color + ' ' + dyn + ' ' + type

    def localize_object(self, obj):
        # function for uniquely localizing an object based on its properties
        return f"the {obj.color} {obj.shape} object"

    def generate(self, template_key, debug=False, obj=None):
        eps = 1e-5
        if template_key not in self.templates:
            return "Invalid template key"

        if obj:
            obj_str = self.localize_object(obj)
            return self.templates[template_key].format(obj_str), None
        else:
            objs = self.simulation.objects

            assert template_key in self.templates.keys() and template_key in self.template_generators.keys(), 'Invalid template key: {}'.format(template_key)

            generator = self.template_generators[template_key]
            ans_generated, ques_generated, feat_generated = generator(objs, eps, debug)
        
        return ques_generated, ans_generated, feat_generated
    
    def generate_color(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a = []
        res_q = []
        res_f = []
        template = self.templates["color"]

        for color in self.colors:
            if type(template) == list:
                template = random.choice(template)

            question = template.format(color)
            res_q.append(question)
            res_a.append(str(len([obj for obj in self.simulation.objects if obj.color.lower() == color])))
            res_f.append([color])

        return res_a, res_q, res_f
    
    def generate_shape(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a = []
        res_q = []
        res_f = []
        template = self.templates["shape"]

        unique_shapes = self.shapes
        for shape in unique_shapes:
            if type(template) == list:
                template = random.choice(template)
                
            question = template.format(shape)
            res_q.append(question)
            res_a.append(str(len([obj for obj in self.simulation.objects if shape.lower() in obj.shape.lower()])))
            res_f.append([shape])

        return res_a, res_q, res_f
    
    def generate_existence(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a=[]
        res_q=[]
        res_f = []

        template = self.templates["existence"]
        colors = self.colors
        shapes = self.exact_shapes

        for color, shape in product(colors, shapes):
            if type(template) == list:
                template = random.choice(template)
                
            question = template.format(color, shape)
            res_q.append(question)
            if len([obj for obj in self.simulation.objects if color in obj.color.lower() and shape in obj.shape.lower()]) != 0:
                res_a.append("yes")
            else:
                res_a.append("no")

            res_f.append([color, shape])

        return res_a, res_q, res_f
    
    def _fetch_comp_factor(self, obj1, obj2):
        """
        Return:
          ('yes'/'no'/'can not answer', comp, factor)
        
        There are three situations for two objects:
          1. no relationship (not in the same rope group)
          2b. obj1 links with dynamic pulley => factor should be 'twice of'
          2a. obj2 links with dynamic pulley => factor should be 'half of'
          3. linking with static pulley => factor should be one of, which is ''

        For situation 2 and 3, we balance the right ans and wrong ans probilities.
        Also, we generate some obvious factor for 2.
        """
        
        can_ans = self.simulation.check_relation(obj1, obj2)
        # situation 1
        if not can_ans:
            comp = random.choice(list(self.comp_dict.keys()))
            fac = ''
            cannot_ans_return_prob = 0.3
            r_value = random.random()
            if r_value < cannot_ans_return_prob:
                return 'can not answer', comp, fac
            else:
                return None, comp, fac
                
            # fac = random.choice(list(self.factor_dict.keys()))
        
        dy_pulley_objects = self.simulation.link_dy_pulley

        # should not happen
        if obj1 in dy_pulley_objects and obj2 in dy_pulley_objects:
            # conside as situation 3
            # breakpoint()
            dy_pulley_objects = []
            
        m1, m2 = float(obj1.mass), float(obj2.mass)
        return_tuple = None

        # situation 3
        if obj1 not in dy_pulley_objects and obj2 not in dy_pulley_objects:
            if m1 > m2+EPS:
                """
                c1) obj1 > obj2
                d1) We will return:
                right (50%):
                    45%: 'greater than' ''
                    5%: 'greater than' 'half of'
                wrong (50%):
                    0%: * 'twice of'
                    45%: * ''  
                    5%: * 'half of'
                """
                # right_diverse_thr = 0.1
                # right_tuple = ('yes', 'greater than', '')
                # d_value = random.random()
                # if d_value < right_diverse_thr:
                #     right_tuple = ('yes', 'greater than', 'half of')

                # wrong_diverse_thr = 0.1
                # ele = random.choice(['equal to', 'less than'])
                # wrong_tuple = ('no', ele, '')
                # d_value = random.random()
                # if d_value < wrong_diverse_thr:
                #     wrong_tuple = ('no', ele, 'half of')

                """
                c1) obj1 > obj2
                d1) We will return:
                right (50%): 'greater than' ''
                wrong (50%):
                    25%: 'less than' ''  
                    25%: 'equal to' ''  
                """
                right_tuple = ('yes', 'greater than', '')

                w_ele = random.choice(['less than', 'equal to'])
                wrong_tuple = ('no', w_ele, '')

            elif m1 < m2-EPS:
                """
                c1) obj1 > obj2
                d1) We will return:
                right (50%):
                    45%: 'greater than' ''
                    5%: 'greater than' 'half of'
                wrong (50%):
                    0%: * 'twice of'
                    45%: * ''  
                    5%: * 'half of'
                """
                # right_diverse_thr = 0.1
                # right_tuple = ('yes', 'less than', '')
                # d_value = random.random()
                # if d_value < right_diverse_thr:
                #     right_tuple = ('yes', 'less than', 'twice of')

                # wrong_diverse_thr = 0.1
                # ele = random.choice(['equal to', 'greater than'])
                # wrong_tuple = ('no', ele, '')
                # d_value = random.random()
                # if d_value < wrong_diverse_thr:
                #     wrong_tuple = ('no', ele, 'twice of')

                """
                c1) obj1 < obj2
                d1) We will return:
                right (50%): 'less than' ''
                wrong (50%):
                    25%: 'greater than' ''  
                    25%: 'equal to' ''  
                """
                right_tuple = ('yes', 'less than', '')

                w_ele = random.choice(['greater than', 'equal to'])
                wrong_tuple = ('no', w_ele, '')

            else: # m1 == m2
                """
                c2) obj1 == obj2
                d2) We will return:
                  right (50%): 'equal to' ''
                  wrong (50%):
                    20%: 'equal to' *
                    20%: * ''  
                    10%: * * 
                """
                # right_tuple = ('yes', 'equal to', '')

                # wrong_diverse_thr1 = 0.4
                # wrong_diverse_thr2 = 0.8
                # ele1 = random.choice(['', 'twice of'])
                # wrong_tuple = ('no', 'equal to', ele1)
                # d_value = random.random()
                # if d_value < wrong_diverse_thr1:
                #     ele2 = random.choice(['less than', 'greater than'])
                #     wrong_tuple = ('no', ele2, '')
                # elif d_value > wrong_diverse_thr2:
                #     wrong_tuple1 = ('no', 'greater than', 'twice of')
                #     wrong_tuple2 = ('no', 'less than', 'half of')
                #     wrong_tuple = random.choice([wrong_tuple1, wrong_tuple2])

                """
                c2) obj1 == obj2
                d2) We will return:
                  right (50%): 'equal to' ''
                  wrong (50%):
                    25%: 'less to' ''
                    25%: 'greater than' ''  
                """
                right_tuple = ('yes', 'equal to', '')

                w_ele = random.choice(['less than', 'greater than'])
                wrong_tuple = ('no', w_ele, '')

        elif obj1 in dy_pulley_objects: # obj1 links with dynamic pulley
            if m1 > 2*m2+EPS:
                """
                c1) obj1 > 2*obj2
                d1) We will return:
                right (50%):
                    45%: 'greater than' 'twice of'
                    5%: 'greater than' *
                wrong (50%):
                    45%: * 'twice of'
                    5%: * *
                """
                right_diverse_thr = 0.1
                right_tuple = ('yes', 'greater than', 'twice ')
                d_value = random.random()
                if d_value < right_diverse_thr:
                    r_ele = random.choice(['half ', ''])
                    right_tuple = ('yes', 'greater than', r_ele)

                wrong_diverse_thr = 0.1
                w_ele = random.choice(['equal to', 'less than'])
                wrong_tuple = ('no', w_ele, 'twice ')
                d_value = random.random()
                if d_value < wrong_diverse_thr:
                    w_ele2 = random.choice(['half ', ''])
                    wrong_tuple = ('no', w_ele, w_ele2)
            
            elif m1 < 2*m2 - EPS:
                """
                c1) obj1 < 2*obj2
                d1) We will return:
                right (50%): 'less than' 'twice of'
                wrong (50%):
                    25%: 'greater than' 'twice of'
                    25%: 'equal to' 'twice of'
                """
                right_tuple = ('yes', 'less than', 'twice ')

                w_ele = random.choice(['greater than', 'equal to'])
                wrong_tuple = ('no', w_ele, 'twice ')

            else: # m1 == 2*m2
                """
                c2) obj1 == 2*obj2
                d2) We will return:
                  right (50%): 'equal to' 'twice of'
                  wrong (50%):
                    45%: * 'twice of'  
                    5%: 'equal to' *
                """
                right_tuple = ('yes', 'equal to', 'twice ')

                wrong_diverse_thr = 0.1
                w_ele = random.choice(['greater than', 'less than'])
                wrong_tuple = ('no', w_ele, 'twice ')
                d_value = random.random()
                if d_value < wrong_diverse_thr:
                    w_ele2 = random.choice(['half ', ''])
                    wrong_tuple = ('no', 'equal to', w_ele2)

        elif obj2 in dy_pulley_objects:
            if m1 > 0.5*m2+EPS:
                """
                c1) obj1 > 0.5*obj2
                d1) We will return:
                right (50%): 'greater than' 'half of'
                wrong (50%):
                    25%: 'less than' 'half of'
                    25%: 'equal to' 'half of'
                """
                right_tuple = ('yes', 'greater than', 'half ')

                w_ele = random.choice(['less than', 'equal to'])
                wrong_tuple = ('no', w_ele, 'half ')
            
            elif m1 < 0.5*m2 - EPS:
                """
                c1) obj1 < 0.5*obj2
                d1) We will return:
                right (50%):
                    45%: 'less than' 'half of'
                    5%: 'less than' *
                wrong (50%):
                    45%: * 'half of'
                    5%: * *
                """
                right_diverse_thr = 0.1
                right_tuple = ('yes', 'less than', 'half ')
                d_value = random.random()
                if d_value < right_diverse_thr:
                    r_ele = random.choice(['twice ', ''])
                    right_tuple = ('yes', 'less than', r_ele)

                wrong_diverse_thr = 0.1
                w_ele = random.choice(['equal to', 'greater than'])
                wrong_tuple = ('no', w_ele, 'half ')
                d_value = random.random()
                if d_value < wrong_diverse_thr:
                    w_ele2 = random.choice(['twice ', ''])
                    wrong_tuple = ('no', w_ele, w_ele2)

            else: # m1 == 0.5*m2
                """
                c2) obj1 == 2*obj2
                d2) We will return:
                  right (50%): 'equal to' 'half of'
                  wrong (50%):
                    45%: * 'half of'  
                    5%: 'equal to' *
                """
                right_tuple = ('yes', 'equal to', 'half ')

                wrong_diverse_thr = 0.1
                w_ele = random.choice(['greater than', 'less than'])
                wrong_tuple = ('no', w_ele, 'half ')
                d_value = random.random()
                if d_value < wrong_diverse_thr:
                    w_ele2 = random.choice(['twice ', ''])
                    wrong_tuple = ('no', 'equal to', w_ele2)
        
        else:
            breakpoint()
            # Should not happen
            pass

        right_wrong_prob = 0.5
        wr_value = random.random()
        if wr_value < right_wrong_prob:
            return_tuple = right_tuple
        else:
            return_tuple = wrong_tuple

        return return_tuple

    def generate_mass(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a = []
        res_q = []
        res_f = []
        template = self.templates["mass"]

        for o1, o2 in permutations(objs, 2):
            if o1.mass == "null" or o2.mass == "null":
                continue

            if type(template) == list:
                template = random.choice(template)
                
            m1, m2 = float(o1.mass), float(o2.mass)
            if o1.name == o2.name:
                continue

            ans, comp, factor = self._fetch_comp_factor(o1, o2)
            if ans == None:
                continue
            
            feature = [o1.color.lower(), o1.shape.lower(), comp, factor, o2.color.lower(), o2.shape.lower()]
            question = template.format(*feature)
            res_q.append(question)
            res_a.append(ans)
            res_f.append(feature)

        return res_a, res_q, res_f
    
    def generate_tension(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a = []
        res_q = []
        res_f = []
        template = self.templates["tension"]

        for o1, o2 in permutations(objs, 2):
            if o1.mass == "null" or o2.mass == "null":
                continue

            if type(template) == list:
                template = random.choice(template)
                
            m1, m2 = float(o1.mass), float(o2.mass)
            ans, comp, factor = self._fetch_comp_factor(o1, o2)
            if ans == None:
                continue

            obj1_n, obj2_n = o1.name, o2.name
            if obj1_n == obj2_n:
                continue
            try:
                rope1_n, rope2_n = self.simulation.object_rope_map[obj1_n], self.simulation.object_rope_map[obj2_n]
                if rope1_n == rope2_n:
                    continue
                rope1, rope2 = self.simulation.name_object_map[rope1_n], self.simulation.name_object_map[rope2_n]
            except:
                breakpoint()
                continue

            feature = [rope1.color.lower(), rope1.shape.lower(), comp, factor, rope2.color.lower(), rope2.shape.lower()]

            question = template.format(*feature)
            res_q.append(question)
            res_a.append(ans)
            res_f.append(feature)

        return res_a, res_q, res_f
    
    def generate_cf(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a = []
        res_q = []
        res_f = []

        templates = self.templates["rope_counterfactual"]
        templates_q = templates['question']
        templates_c = templates['choice']
        counterfactual = self.simulation.counterfactual

        for item in counterfactual.values():
            true_choices, false_choices = [], []
            question = None

            # pull
            # if "mode" in list(item.keys()) and item["mode"] == "COUNTERFACTUAL_pull_object_up_or_down":
            #     obj_name = item["TargetMovingAgent"]["name"].split('(')[0].strip()
            #     obj_name = self.abbr_object_name(obj_name.lower())
            #     direction = "moved " + item["TargetMovingAgent"]["direction"]

            #     # get the dictionaries
            #     result_rotation = item["ResultRotation"]
            #     result_motion = item["ResultMotion"]

            #     rotation_temp = templates_c['rotate']
            #     motion_temp = templates_c['move']

            #     template_q = random.choice(templates_q)
            #     question = template_q.format(obj_name, direction)

            #     # rotation
            #     for k, v in result_rotation.items():
            #         if 'Shaft' in k:
            #             continue

            #         c_name = self.abbr_object_name(k.split('(')[0].strip().lower())
            #         template_c = rotation_temp

            #         if 'fixed' in c_name:
            #             continue

            #         if v == -1:
            #             choice = template_c.format(c_name, "anti-clockwise")
            #             true_choices.append(choice)
            #         elif v == 1:
            #             choice = template_c.format(c_name, "clockwise")
            #             true_choices.append(choice)
            #         elif v == 0:
            #             choice = template_c.format(c_name, "clockwise")
            #             false_choices.append(choice)
            #             choice = template_c.format(c_name, "anti-clockwise")
            #             false_choices.append(choice)
            #         else:
            #             raise ValueError("Rotation value is not in [-1, 0, 1]")
                    
            #     # motion
            #     for k, v in result_motion.items():
            #         if 'Shaft' in k:
            #             continue
                    
            #         c_name = self.abbr_object_name(k.split('(')[0].strip().lower())
            #         template_c = motion_temp

            #         if 'fixed' in c_name:
            #             continue

            #         if v == -1:
            #             choice = template_c.format(c_name, "down")
            #             true_choices.append(choice)
            #         elif v == 1:
            #             choice = template_c.format(c_name, "up")
            #             true_choices.append(choice)
            #         elif v == 0:
            #             choice = template_c.format(c_name, "up")
            #             false_choices.append(choice)
            #             choice = template_c.format(c_name, "down")
            #             false_choices.append(choice)
            #         else:
            #             raise ValueError("Motion value is not in [-1, 0, 1]")
                    
            if "mode" in list(item.keys()) and item["mode"] == "COUNTERFACTUAL_change_one_object_mass":
                obj_name = item["TargetObj_Name"].split('(')[0].strip()
                obj_name = self.abbr_object_name(obj_name.lower())

                prior_mass = round(float(item["TargetObj_Mass_Before_After"]["Item1"]),2)
                next_mass = round(float(item["TargetObj_Mass_Before_After"]["Item2"]),2)

                change = "lighter" if prior_mass > next_mass else "heavier"

                # get the dictionaries
                result_rotation = item["ResultRotation"]
                result_motion = item["ResultMotion"]

                rotation_temp = templates_c['rotate']
                motion_temp = templates_c['move']

                template_q = random.choice(templates_q)
                question = template_q.format(obj_name, change)
                
                f_change = "increase" if change == "heavier" else "decrease"
                question_f = [obj_name, f_change, 'mass']

                # rotation
                for k, v in result_rotation.items():
                    if 'Shaft' in k:
                        continue

                    c_name = self.abbr_object_name(k.split('(')[0].strip().lower())
                    template_c = rotation_temp
                    template_c_r = "The {} would not rotate"

                    if 'fixed' in c_name:
                        continue

                    if v == -1:
                        choice = template_c.format(c_name, "anti-clockwise")
                        f_choice = f'{c_name}|rotation|anti-clockwise'
                        choice = choice + '||' + f_choice
                        true_choices.append(choice) 
                        choice = template_c.format(c_name, "clockwise")
                        f_choice = f'{c_name}|rotation|clockwise'
                        choice = choice + '||' + f_choice
                        false_choices.append(choice) 

                        if random.random() < 0.1:
                            choice = template_c_r.format(c_name)
                            f_choice = f'{c_name}|rotation|stationary'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)

                    elif v == 1:
                        choice = template_c.format(c_name, "clockwise")
                        f_choice = f'{c_name}|rotation|clockwise'
                        choice = choice + '||' + f_choice
                        true_choices.append(choice)
                        choice = template_c.format(c_name, "anti-clockwise")
                        f_choice = f'{c_name}|rotation|anti-clockwise'
                        choice = choice + '||' + f_choice
                        false_choices.append(choice) 

                        if random.random() < 0.1:
                            choice = template_c_r.format(c_name)
                            f_choice = f'{c_name}|rotation|stationary'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)

                    elif v == 0:
                        if random.random()<0.5:
                            choice = template_c.format(c_name, "clockwise")
                            f_choice = f'{c_name}|rotation|clockwise'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)
                        else:
                            choice = template_c.format(c_name, "anti-clockwise")
                            f_choice = f'{c_name}|rotation|anti-clockwise'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)

                        choice = template_c_r.format(c_name)
                        f_choice = f'{c_name}|rotation|stationary'
                        choice = choice + '||' + f_choice
                        true_choices.append(choice)
                        
                    else:
                        raise ValueError("Rotation value is not in [-1, 0, 1]")
                    
                # motion
                for k, v in result_motion.items():
                    if 'Shaft' in k:
                        continue
                    
                    c_name = self.abbr_object_name(k.split('(')[0].strip().lower())
                    template_c = motion_temp
                    template_c_r = "The {} would not move"

                    if 'fixed' in c_name:
                        continue

                    if v == -1:
                        choice = template_c.format(c_name, "down")
                        f_choice = f'{c_name}|motion|down'
                        choice = choice + '||' + f_choice
                        true_choices.append(choice)
                        choice = template_c.format(c_name, "up")
                        f_choice = f'{c_name}|motion|up'
                        choice = choice + '||' + f_choice
                        false_choices.append(choice)

                        if random.random() < 0.1:
                            choice = template_c_r.format(c_name)
                            f_choice = f'{c_name}|motion|stationary'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)
                    elif v == 1:
                        choice = template_c.format(c_name, "up")
                        f_choice = f'{c_name}|motion|up'
                        choice = choice + '||' + f_choice
                        true_choices.append(choice)
                        choice = template_c.format(c_name, "down")
                        f_choice = f'{c_name}|motion|down'
                        choice = choice + '||' + f_choice
                        false_choices.append(choice)

                        if random.random() < 0.1:
                            choice = template_c_r.format(c_name)
                            f_choice = f'{c_name}|motion|stationary'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)
                    elif v == 0:
                        if random.random()<0.5:
                            choice = template_c.format(c_name, "up")
                            f_choice = f'{c_name}|motion|up'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)
                        else:
                            choice = template_c.format(c_name, "down")
                            f_choice = f'{c_name}|motion|down'
                            choice = choice + '||' + f_choice
                            false_choices.append(choice)

                        if random.random()<0.2:
                            choice = template_c_r.format(c_name)
                            f_choice = f'{c_name}|motion|stationary'
                            choice = choice + '||' + f_choice
                            true_choices.append(choice)
                    else:
                        raise ValueError("Motion value is not in [-1, 0, 1]")

            else:
                continue

            if len(true_choices) == 0 or len(false_choices) == 0:
                continue
            elif len(true_choices) == 1:
                all_choices = []
                qquestion = question
                f_choices = dict()

                all_choices.append((true_choices[0], 1))
                _f_temp = random.sample(false_choices, 2)
                all_choices.append((_f_temp[0], 0))
                all_choices.append((_f_temp[1], 0))
                random.shuffle(all_choices)

                for i, (choice, b) in enumerate(all_choices):
                    choice, f_choice = choice.split('||')
                    if choice in qquestion:
                        breakpoint()
                    qquestion += '\n' + chr(ord('A') + i) + '. ' + choice
                    f_choice = f_choice.split('|')
                    assert len(f_choice) == 3
                    f_choices[chr(ord('A') + i)] = f_choice

                    if b == 1:
                        answer += str(chr(ord('A') + i))
                res_a.append(' '.join(answer))
                res_q.append(qquestion)
                f_a = {
                    'question': question_f,
                    'choices': f_choices
                }
                res_f.append(f_a)
                continue
            elif len(false_choices) == 1:
                all_choices = []
                qquestion = question
                f_choices = dict()

                all_choices.append((false_choices[0], 0))
                _t_temp = random.sample(true_choices, 2)
                all_choices.append((_t_temp[0], 0))
                all_choices.append((_t_temp[1], 0))
                random.shuffle(all_choices)

                for i, (choice, b) in enumerate(all_choices):
                    choice, f_choice = choice.split('||')
                    if choice in qquestion:
                        breakpoint()
                    qquestion += '\n' + chr(ord('A') + i) + '. ' + choice
                    f_choice = f_choice.split('|')
                    assert len(f_choice) == 3
                    f_choices[chr(ord('A') + i)] = f_choice

                    if b == 1:
                        answer += str(chr(ord('A') + i))
                res_a.append(' '.join(answer))
                res_q.append(qquestion)
                f_a = {
                    'question': question_f,
                    'choices': f_choices
                }
                res_f.append(f_a)
                continue

            random.shuffle(true_choices)
            random.shuffle(false_choices)
            if len(false_choices) > len(true_choices):
                false_choices = random.sample(false_choices, len(true_choices))
            else:
                true_choices = random.sample(true_choices, len(false_choices))

            try:
                while True:
                    all_choices = []
                    qquestion = question
                    f_choices = dict()
                    answer = ''

                    c = true_choices.pop()
                    all_choices.append((c,1))

                    ans_num = random.randint(2, 4) # 3--5
                    for i in range(ans_num):
                        p = len(false_choices) / (len(false_choices) + len(true_choices))
                        rand_num = random.random()
                        if rand_num < p:
                            c = false_choices.pop()
                            all_choices.append((c,0))
                        else:
                            c = true_choices.pop()
                            all_choices.append((c,1))

                    if len(set(all_choices)) < 2:
                        breakpoint()
                        continue

                    _debug_choices = [a[0] for a in all_choices]
                    if len(_debug_choices) != len(set(_debug_choices)):
                        breakpoint()

                    random.shuffle(all_choices)

                    for i, (choice, b) in enumerate(all_choices):
                        choice, f_choice = choice.split('||')
                        if choice in qquestion:
                            breakpoint()

                        qquestion += '\n' + chr(ord('A') + i) + '. ' + choice
                        f_choice = f_choice.split('|')
                        assert len(f_choice) == 3
                        f_choices[chr(ord('A') + i)] = f_choice
                        if b == 1:
                            answer += str(chr(ord('A') + i))

                    res_a.append(' '.join(answer))
                    res_q.append(qquestion)
                    f_a = {
                        'question': question_f,
                        'choices': f_choices
                    }
                    res_f.append(f_a)
            except:
                pass

        return res_a, res_q, res_f
    

    def generate_cf2(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a = []
        res_q = []
        res_f = []

        templates = self.templates["rope_counterfactual2"]
        counterfactual = self.simulation.counterfactual

        for item in counterfactual.values():
            if "mode" in list(item.keys()) and item["mode"] == "COUNTERFACTUAL_change_one_object_mass":
                obj_name = item["TargetObj_Name"].split('(')[0].strip()
                obj_name = self.abbr_object_name(obj_name.lower())

                prior_mass = round(float(item["TargetObj_Mass_Before_After"]["Item1"]),2)
                next_mass = round(float(item["TargetObj_Mass_Before_After"]["Item2"]),2)

                change = "lighter" if prior_mass > next_mass else "heavier"

                # get the dictionaries
                result_rotation = item["ResultRotation"]
                result_motion = item["ResultMotion"]

                # rotation
                templates_r = templates['rotate']
                template_q_idx = random.randint(0,1)
                reverse_format = template_q_idx == 1
                template_q = templates_r['question'][template_q_idx]
                f_change = "increase" if change == "heavier" else "decrease"
                question_f = [obj_name, f_change, 'mass']
                for k, v in result_rotation.items():
                    if 'Shaft' in k:
                        continue
                    c_name = self.abbr_object_name(k.split('(')[0].strip().lower())
                    if 'fixed' in c_name:
                        continue

                    if not reverse_format:
                        question = template_q.format(obj_name, change, c_name) + '\n' + templates_r['choice']
                    else:
                        question = template_q.format(c_name, obj_name, change) + '\n' + templates_r['choice']
                    f_all = {
                        'question': question_f,
                        'choices': {
                            'A': [c_name, 'rotation', 'clockwise'],
                            'B': [c_name, 'rotation', 'anti-clockwise'],
                            'C': [c_name, 'rotation', 'stationary']
                        }
                    }
                    if v == -1:
                        ans = 'B'
                    elif v == 1:
                        ans = 'A'
                    elif v == 0:
                        ans = 'C'
                    else:
                        raise ValueError("Rotation value is not in [-1, 0, 1]")
                    
                    res_q.append(question)
                    res_a.append(ans)
                    res_f.append(f_all)
                    
                # motion
                templates_r = templates['move']
                template_q_idx = random.randint(0,1)
                reverse_format = template_q_idx == 1
                template_q = templates_r['question'][template_q_idx]
                for k, v in result_motion.items():
                    if 'Shaft' in k:
                        continue
                    c_name = self.abbr_object_name(k.split('(')[0].strip().lower())
                    if 'fixed' in c_name:
                        continue

                    if not reverse_format:
                        question = template_q.format(obj_name, change, c_name) + '\n' + templates_r['choice']
                    else:
                        question = template_q.format(c_name, obj_name, change) + '\n' + templates_r['choice']
                    f_all = {
                        'question': question_f,
                        'choices': {
                            'A': [c_name, 'motion', 'down'],
                            'B': [c_name, 'motion', 'up'],
                            'C': [c_name, 'motion', 'stationary']
                        }
                    }

                    if v == -1:
                        ans = 'A'
                    elif v == 1:
                        ans = 'B'
                    elif v == 0:
                        ans = 'C'
                    else:
                        raise ValueError("Motion value is not in [-1, 0, 1]")

                    res_q.append(question)
                    res_a.append(ans)
                    res_f.append(f_all)
            else:
                continue


        return res_a, res_q, res_f
    
    def generate_gd(self, objs, eps, debug):
        if debug:
            breakpoint()
        res_a = []
        res_q = []
        res_f = []

        templates = self.templates["rope_goaldriven"]
        templates_q = templates['question']
        templates_c = templates['choice']
        counterfactual = self.simulation.counterfactual

        # create dictionaries to store keys for gd
        rotation_gd = {}
        motion_gd = {}

        for item in counterfactual.values():    
            # if "mode" in list(item.keys()) and item["mode"] == "COUNTERFACTUAL_pull_object_up_or_down":
            #     obj_name = item["TargetMovingAgent"]["name"].split('(')[0].strip()
            #     obj_name = self.abbr_object_name(obj_name.lower())
            #     direction = item["TargetMovingAgent"]["direction"]

            #     # get the dictionaries
            #     result_rotation = item["ResultRotation"]
            #     result_motion = item["ResultMotion"]

            #     for key, value in result_rotation.items():
            #         _name_t = key.lower().split('(')[0].strip()
            #         if 'shaft' in _name_t or 'fixed' in _name_t:
            #             continue
            #         if _name_t not in rotation_gd:
            #             rotation_gd[_name_t] = [[],[],[]] # 0, 1, -1
            #         rotation_gd[_name_t][int(value)].append(('pull', obj_name, direction))
                    
            #     for key, value in result_motion.items():
            #         _name_t = key.lower().split('(')[0].strip()
            #         if 'shaft' in _name_t or 'fixed' in _name_t:
            #             continue
            #         if _name_t not in motion_gd:
            #             motion_gd[_name_t] = [[],[],[]] # 0, 1, -1
            #         motion_gd[_name_t][int(value)].append(('pull', obj_name, direction))

            if "mode" in list(item.keys()) and item["mode"] == "COUNTERFACTUAL_change_one_object_mass":
                obj_name = item["TargetObj_Name"].split('(')[0].strip()
                obj_name = self.abbr_object_name(obj_name.lower())

                prior_mass = round(float(item["TargetObj_Mass_Before_After"]["Item1"]),2)
                next_mass = round(float(item["TargetObj_Mass_Before_After"]["Item2"]),2)
                change = "Decrease" if prior_mass > next_mass else "Increase"

                # get the dictionaries
                result_rotation = item["ResultRotation"]
                result_motion = item["ResultMotion"]

                for key, value in result_rotation.items():
                    _name_t = key.lower().split('(')[0].strip()
                    if 'shaft' in _name_t or 'fixed' in _name_t:
                        continue
                    if _name_t not in rotation_gd:
                        rotation_gd[_name_t] = [[],[],[]] # 0, 1, -1
                    rotation_gd[_name_t][int(value)].append(('mass', change, obj_name))
                    
                for key, value in result_motion.items():
                    _name_t = key.lower().split('(')[0].strip()
                    if 'shaft' in _name_t or 'fixed' in _name_t:
                        continue
                    if _name_t not in motion_gd:
                        motion_gd[_name_t] = [[],[],[]] # 0, 1, -1
                    motion_gd[_name_t][int(value)].append(('mass', change, obj_name))

            else:
                continue

        # rotation
        for key, value in rotation_gd.items():
            choice_idx = random.randint(0,1)*2-1
            if len(value[1]) + len(value[-1]) == 0:
                continue
            if len(value[choice_idx]) == 0:
                choice_idx = -choice_idx
            if choice_idx == 1:
                direction = "rotate clockwise"
            elif choice_idx == -1:
                direction = "rotate anti-clockwise"

            template_q = random.choice(templates_q)
            obj_name = self.abbr_object_name(key.lower())
            question = template_q.format(obj_name, direction)
            f_question = [obj_name, 'rotation', direction.split(' ')[-1]]
            true_choices, false_choices = [], []

            for choice_argv in value[choice_idx]:
                _k, _v1, _v2 = choice_argv
                c = templates_c[_k].format(_v1, _v2)
                f_c = f'{_v2}|{_v1.lower()}|{_k}'
                c = c + '||' + f_c
                true_choices.append(c)
            for choice_argv in (value[-choice_idx]+value[0]):
                _k, _v1, _v2 = choice_argv
                c = templates_c[_k].format(_v1, _v2)
                f_c = f'{_v2}|{_v1.lower()}|{_k}'
                c = c + '||' + f_c
                false_choices.append(c)

            if len(true_choices) == 0 or len(false_choices) == 0:
                continue

            random.shuffle(true_choices)
            random.shuffle(false_choices)

            all_choices = []
            f_choices = dict()
            answer = ''

            if len(true_choices) == 1:
                c = true_choices.pop()
                all_choices.append((c,1))
                try:
                    c = false_choices.pop()
                    all_choices.append((c,0))
                    c = false_choices.pop()
                    all_choices.append((c,0))
                except:
                    continue
            else:
                c = true_choices.pop()
                all_choices.append((c,1))
                ans_num = random.randint(2, 4) # 3--5
                
                if len(false_choices)+len(true_choices) <= ans_num:
                    all_choices.extend([(c,1) for c in true_choices])
                    all_choices.extend([(c,0) for c in false_choices])
                else:
                    for i in range(ans_num):
                        p = len(false_choices) / (len(false_choices) + len(true_choices))
                        rand_num = random.random()
                        if rand_num < p:
                            try:
                                c = false_choices.pop()
                                all_choices.append((c,0))
                            except:
                                c = true_choices.pop()
                                all_choices.append((c,1))
                        else:
                            try:
                                c = true_choices.pop()
                                all_choices.append((c,1))
                            except:
                                c = false_choices.pop()
                                all_choices.append((c,0))

            random.shuffle(all_choices)
            for i, (choice, b) in enumerate(all_choices):
                choice, f_choice = choice.split('||')
                if choice in question:
                    breakpoint()

                question += '\n' + chr(ord('A') + i) + '. ' + choice
                f_choice = f_choice.split('|')
                assert len(f_choice) == 3
                f_choices[chr(ord('A') + i)] = f_choice
                if b == 1:
                    answer += str(chr(ord('A') + i))

            res_a.append(' '.join(answer))
            res_q.append(question)
            f_a = {
                'question': f_question,
                'choices': f_choices
            }
            res_f.append(f_a)

        # rotation
        for key, value in motion_gd.items():
            choice_idx = random.randint(0,1)*2-1
            if len(value[1]) + len(value[-1]) == 0:
                continue
            if len(value[choice_idx]) == 0:
                choice_idx = -choice_idx
            if choice_idx == 1:
                direction = "move up"
            elif choice_idx == -1:
                direction = "move down"

            template_q = random.choice(templates_q)
            obj_name = self.abbr_object_name(key.lower())
            question = template_q.format(obj_name, direction)
            f_question = [obj_name, 'motion', direction.split(' ')[-1]]
            true_choices, false_choices = [], []

            for choice_argv in value[choice_idx]:
                _k, _v1, _v2 = choice_argv
                c = templates_c[_k].format(_v1, _v2)
                f_c = f'{_v2}|{_v1.lower()}|{_k}'
                c = c + '||' + f_c
                true_choices.append(c)
            for choice_argv in (value[-choice_idx]+value[0]):
                _k, _v1, _v2 = choice_argv
                c = templates_c[_k].format(_v1, _v2)
                f_c = f'{_v2}|{_v1.lower()}|{_k}'
                c = c + '||' + f_c
                false_choices.append(c)

            if len(true_choices) == 0 or len(false_choices) == 0:
                continue

            random.shuffle(true_choices)
            random.shuffle(false_choices)

            all_choices = []
            f_choices = dict()
            answer = ''

            if len(true_choices) == 1:
                c = true_choices.pop()
                all_choices.append((c,1))
                try:
                    c = false_choices.pop()
                    all_choices.append((c,0))
                    c = false_choices.pop()
                    all_choices.append((c,0))
                except:
                    continue
            else:
                c = true_choices.pop()
                all_choices.append((c,1))
                ans_num = random.randint(2, 4) # 3--5
                
                if len(false_choices)+len(true_choices) <= ans_num:
                    all_choices.extend([(c,1) for c in true_choices])
                    all_choices.extend([(c,0) for c in false_choices])
                else:
                    for i in range(ans_num):
                        p = len(false_choices) / (len(false_choices) + len(true_choices))
                        rand_num = random.random()
                        if rand_num < p:
                            try:
                                c = false_choices.pop()
                                all_choices.append((c,0))
                            except:
                                c = true_choices.pop()
                                all_choices.append((c,1))
                        else:
                            try:
                                c = true_choices.pop()
                                all_choices.append((c,1))
                            except:
                                c = false_choices.pop()
                                all_choices.append((c,0))

            random.shuffle(all_choices)
            for i, (choice, b) in enumerate(all_choices):
                choice, f_choice = choice.split('||')
                if choice in question:
                    breakpoint()

                question += '\n' + chr(ord('A') + i) + '. ' + choice
                f_choice = f_choice.split('|')
                assert len(f_choice) == 3
                f_choices[chr(ord('A') + i)] = f_choice
                if b == 1:
                    answer += str(chr(ord('A') + i))

            res_a.append(' '.join(answer))
            res_q.append(question)
            f_a = {
                'question': f_question,
                'choices': f_choices
            }
            res_f.append(f_a)

        return res_a, res_q, res_f
