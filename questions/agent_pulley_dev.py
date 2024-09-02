import argparse
import os
import json
import random
import glob
from tqdm import tqdm
import copy
from multiprocessing import Pool

from object import SimulationPulley
from read_file import read_annotation_pulley
from question_engine_pulley import QuestionEnginePulley

THREAD_NUM = 20

class Randomization:
    def __init__(self, questions, answers):
        self.questions = questions
        self.answers = answers
    
    def shuffle_choice(self, skip=False):
        """ Shuffle the options of the choice questions and update the answers accordingly """
        questions_shuffled, answers_shuffled, raw_options_shuffled = [], [], []

        for ques, ans in zip(self.questions, self.answers):
            ques_title, options = ques.split('\n')[0], ques.split('\n')[1:]
            ans_choices = ans.split()
            # shuffle the options
            positive = [options[ord(choice) - ord('A')] for choice in ans_choices]
            if not skip:
                options_unshuffled = copy.deepcopy(options)
                random.shuffle(options)

            # update the answer and options
            ans_shuffled = ' '.join(sorted([chr(ord('A') + options.index(choice)) for choice in positive]))
            raw_opt_shuffled = [option[3:] for option in options]
            # TODO: duplicate detect, remove when release
            assert len(raw_opt_shuffled) == len(set(raw_opt_shuffled))

            opt_shuffled = [chr(ord('A') + i) + '. ' + opt for i, opt in enumerate(raw_opt_shuffled)]
            ques_shuffled = ques_title + '\n' + '\n'.join(opt_shuffled)
            questions_shuffled.append(ques_shuffled)
            answers_shuffled.append(ans_shuffled)
            raw_options_shuffled.append(raw_opt_shuffled)

        return questions_shuffled, answers_shuffled, raw_options_shuffled
    

class RandomizationProgram:
    def __init__(self, questions, answers, programs):
        self.questions = questions
        self.answers = answers
        self.programs = programs
    
    def shuffle_choice(self, skip=False):
        """ Shuffle the options of the choice questions and update the answers accordingly """
        questions_shuffled, answers_shuffled, raw_options_shuffled = [], [], []
        programs_shuffled = []

        for ques, ans, pg in zip(self.questions, self.answers, self.programs):
            ques_title, options = ques.split('\n')[0], ques.split('\n')[1:]
            ans_choices = ans.split()
            # shuffle the options
            positive = [options[ord(choice) - ord('A')] for choice in ans_choices]
            if not skip:
                options_unshuffled = copy.deepcopy(options)
                random.shuffle(options)
                shuffle_mapping = {options_unshuffled[i][0]: options[i][0] for i in range(len(options))}
                # update the programs
                pg_copy = copy.deepcopy(pg)
                for k, v in shuffle_mapping.items():
                    pg[k] = pg_copy[v]

            # update the answer and options
            ans_shuffled = ' '.join(sorted([chr(ord('A') + options.index(choice)) for choice in positive]))
            raw_opt_shuffled = [option[3:] for option in options]
            # TODO: duplicate detect, remove when release
            assert len(raw_opt_shuffled) == len(set(raw_opt_shuffled))

            opt_shuffled = [chr(ord('A') + i) + '. ' + opt for i, opt in enumerate(raw_opt_shuffled)]
            ques_shuffled = ques_title + '\n' + '\n'.join(opt_shuffled)
            questions_shuffled.append(ques_shuffled)
            answers_shuffled.append(ans_shuffled)
            raw_options_shuffled.append(raw_opt_shuffled)
            programs_shuffled.append(pg)

        return questions_shuffled, answers_shuffled, raw_options_shuffled, programs_shuffled
    


class RandomizationFeature:
    def __init__(self, questions, answers, features):
        self.questions = questions
        self.answers = answers
        self.features = features
    
    def shuffle_choice(self, skip=False):
        """ Shuffle the options of the choice questions and update the answers accordingly """
        questions_shuffled, answers_shuffled, raw_options_shuffled = [], [], []
        features_shuffled = []

        for ques, ans, ft in zip(self.questions, self.answers, self.features):
            ques_title, options = ques.split('\n')[0], ques.split('\n')[1:]
            ans_choices = ans.split()
            # shuffle the options
            positive = [options[ord(choice) - ord('A')] for choice in ans_choices]
            if not skip:
                options_unshuffled = copy.deepcopy(options)
                random.shuffle(options)
                shuffle_mapping = {options_unshuffled[i][0]: options[i][0] for i in range(len(options))}
                # update the features
                ft_copy = copy.deepcopy(ft)
                for k, v in shuffle_mapping.items():
                   ft['choices'][k] = ft_copy['choices'][v]

            # update the answer and options
            ans_shuffled = ' '.join(sorted([chr(ord('A') + options.index(choice)) for choice in positive]))
            raw_opt_shuffled = [option[3:] for option in options]
            # TODO: duplicate detect, remove when release
            if len(raw_opt_shuffled) != len(set(raw_opt_shuffled)):
                breakpoint()

            opt_shuffled = [chr(ord('A') + i) + '. ' + opt for i, opt in enumerate(raw_opt_shuffled)]
            ques_shuffled = ques_title + '\n' + '\n'.join(opt_shuffled)
            questions_shuffled.append(ques_shuffled)
            answers_shuffled.append(ans_shuffled)
            raw_options_shuffled.append(raw_opt_shuffled)
            features_shuffled.append(ft)

        return questions_shuffled, answers_shuffled, raw_options_shuffled, features_shuffled
    

class AgentPulley:
    """ Random withouot programs"""
    def __init__(self, args=None):
        self.args = args
        self.input_path = args.input_video_ann_path
        self.simulation = SimulationPulley()
        self.templates = {
            "mass": "Is the mass of the {} {} {} {}that of the {} {}?",
            # "mass_pos": "Is it possible to determine the relationship of mass between the {} {} and the {} {}.",
            "tension": "Is the tension of the {} {} {} {}that of the {} {}?",
            # "tension_pos": "Is it possible to determine the relationship of tension between the {} {} and the {} {}.",
            "shape": "How many {}s are there in the video?",
            "color": "How many {} objects are there in the video?",
            "existence": "Is there any {} {} in the video?",
            
            "rope_counterfactual":{
                "question": [
                    "If the {} were much {}, what would happen?",
                    "If the {} were much {}, which of the following would happen?",
                    "What would happen if the {} were much {}?",
                    "Which of the following would happen if the {} were much {}?",
                ],
                "choice": {
                    "rotate": "The {} would rotate {}",
                    "move": "The {} would move {}",
                }
            },

            "rope_counterfactual2":{
                "move": {
                    "question": [
                        "If the {} were much {}, which direction would the {} move?",
                        "Which direction would the {} move if the {} were much {}?"
                    ],
                    "choice": "A. Down\nB. Up\nC. Stationary"
                },
                "rotate": {
                    "question": [
                        "If the {} were much {}, which direction would the {} rotate?",
                        "Which direction would the {} rotate if the {} were much {}?"
                    ],
                    "choice": "A. Clockwise\nB. Anti-clockwise\nC. Stationary"
                }
            },
                        
            "rope_goaldriven":{
                "question": [
                    "If we want the {} to {}, what can we do?",
                    "What can we do to let the {} to {}?",
                ],
                "choice": {
                    "mass": "{} the mass of the {}",
                }
            },
            
            }
        
        self.multi_choice_keys = ['rope_counterfactual', 'rope_goaldriven', 'rope_counterfactual2']
        self.single_choice_keys =  []
        self.shuffle_keys = ['rope_counterfactual2']
        self.open_ended_keys = ['color', 'shape', 'existence', 'mass', 'tension']
    
    def read_json(self, read_path):
        return read_annotation_pulley(read_path, self.simulation)
    
    def generate(self, te_key, debug=False):
        """ Generate several questions based on the specified question type of template

        Args:
            te_key: template key

        te_key:
        >>>>Factual:
            'surface_tension': Comparison of surface tension of two liquids
        """
        engine = QuestionEnginePulley(self.simulation, self.templates)
        ques_generated, ans_generated, feat_generated = engine.generate(te_key, debug=debug)

        if te_key in self.multi_choice_keys+self.single_choice_keys:
            if feat_generated is None:
                randomization = Randomization(ques_generated, ans_generated)
                skip = True
                if te_key in self.shuffle_keys:
                    skip = False
                ques_generated, ans_generated, raw_options = randomization.shuffle_choice(skip=skip)
                features_shuffled = None
            else:
                randomization = RandomizationFeature(ques_generated, ans_generated, feat_generated)
                skip = True
                if te_key in self.shuffle_keys:
                    skip = False
                ques_generated, ans_generated, raw_options, features_shuffled = randomization.shuffle_choice(skip=skip)

        else:
            raw_options = [None]*len(ques_generated)
            features_shuffled = feat_generated

        data_generated = []
        if features_shuffled is None:
            zip_iter = zip(ques_generated, ans_generated, raw_options, [None]*len(ques_generated))
        else:
            zip_iter = zip(ques_generated, ans_generated, raw_options, features_shuffled)

        for ques, ans, opts, fts in zip_iter:
            item = {}
            item['question'] = ques
            item['answer'] = ans
            item['question_family'] = te_key
            item['positive'] = []
            item['negative'] = []
            if fts is not None:
                item['program'] = fts

            if te_key in self.open_ended_keys:
                item['answer_type'] = 'open_ended'
                item['positive'].append(ans)
            else:
                if te_key in self.single_choice_keys: 
                    item['answer_type'] = 'single_choice'
                elif te_key in self.multi_choice_keys: 
                    item['answer_type'] = 'multiple_choice'
                else:
                    raise NotImplementedError

                for ans_char in ans.split(' '):
                    item['positive'].append(opts[ord(ans_char) - ord('A')])
                item['negative'] = list(set(opts) - set(item['positive']))
        
            data_generated.append(item)

        return data_generated            

    def generate_all_multithread(self):
        """ Generate questions for all types """
        args = self.args
        all_jsons = glob.glob(os.path.join(self.input_path, '*/outputs.json')) # include invalid json
        all_jsons = sorted(all_jsons)[int(len(all_jsons) * args.start): int(len(all_jsons) * args.end)]

        output_path = os.path.join(args.output_ques_ann_path, args.video_type)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        with Pool(THREAD_NUM) as p:
            args_list = [(json_path, output_path, args) for json_path in all_jsons]
            list(tqdm(p.imap(self.generate_multithread, args_list), total=len(args_list)))

    def generate_multithread(self, arg_list):
        json_path, output_path, args = arg_list
        video_id = json_path.split('/')[-2]
        intermidiate_path = os.path.join(output_path, f'{video_id}.json')
        if os.path.exists(intermidiate_path) and not args.restart:
            return 0
        skip_ids = ['1846']
        if video_id in skip_ids:
            return 0

        output_dict = {}
        self.simulation = SimulationPulley()
        if self.read_json(json_path):
            if args.key:
                te_keys = [args.key] # TODO: for debugging, remove when release
            else:
                te_keys=list(self.templates.keys())
            for key in te_keys:
                output_dict[key] = self.generate(key)

            with open(intermidiate_path, 'w') as f:
                json.dump({
                    "video_id": video_id, 
                    "question_dict":output_dict}
                    , f, indent=4)
                
    def generate_all(self):
        """ Generate questions for all types """
        args = self.args
        debug_video = False
        # if args.debug:
            # breakpoint()
        all_jsons = glob.glob(os.path.join(self.input_path, '*/outputs.json')) # include invalid json
        all_jsons = sorted(all_jsons)[int(len(all_jsons) * args.start): int(len(all_jsons) * args.end)]

        output_path = os.path.join(args.output_ques_ann_path, args.video_type)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # for json_path in tqdm(all_jsons):
        for json_path in all_jsons:
            video_id = json_path.split('/')[-2]
            intermidiate_path = os.path.join(output_path, f'{video_id}.json')
            if os.path.exists(intermidiate_path) and not args.restart:
                continue

            debug_ids = []
            if video_id in debug_ids:
                breakpoint()
                debug_video = True
            print(video_id)
            skip_ids = ['1846']
            if video_id in skip_ids:
                continue

            output_dict = {}
            self.simulation = SimulationPulley()
            if self.read_json(json_path):
                if args.key:
                    te_keys = [args.key] # TODO: for debugging, remove when release
                else:
                    te_keys=list(self.templates.keys())
                for key in te_keys:
                    output_dict[key] = self.generate(key, debug=debug_video)

                with open(intermidiate_path, 'w') as f:
                    json.dump({
                        "video_id": video_id, 
                        "question_dict":output_dict}
                        , f, indent=4)


def build_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument( "--video_type", type=str, default="pulley", help="")
    parser.add_argument("--input_video_ann_path", type=str, default="../data/pulley_group", help="")
    parser.add_argument("--output_ques_ann_path", type=str, default="output", help="")
    parser.add_argument("--max_iter", type=int, default=5, help="")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--restart', action='store_true')
    parser.add_argument("--start", type=float, default=0.0, help="")
    parser.add_argument("--end", type=float, default=1.0, help="")
    parser.add_argument('--key', type=str, default='', help='Only generate the specified key, for debugging, e.g. surface_tension')
    parser.add_argument('--multithread', type=bool, default=True, help='Whether to use multithread')
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = build_args_parser()
    print(args)
    agent = AgentPulley(args)
    if args.debug:
        args.multithread = False
        breakpoint()

    if args.multithread:
        agent.generate_all_multithread()
    else:
        agent.generate_all()
