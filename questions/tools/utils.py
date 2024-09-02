import json
import os
import argparse
import random
import re
from prettytable import PrettyTable


def build_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument( "--video_type", type=str, default="pulley", help="")
    parser.add_argument("--fact_ques_num", type=int, default=2, help="")
    parser.add_argument("--count_ques_num", type=int, default=2, help="")
    parser.add_argument("--output_ques_ann_path", type=str, default="output", help="")
    parser.add_argument("--merge_ques_path", type=str, default="output/merge/merge.json", help="")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--out_id", type=str, default="v1", help="")
    parser.add_argument("--analysis", type=str, default="", help="analysis of different scenes, pulley/fire/cloth/fluid")
    args = parser.parse_args()
    return args

def run_question_sampler_v1(args):
    out_dir = os.path.join(args.output_ques_ann_path, args.video_type)
    fn_list = [fn for fn in os.listdir(out_dir) if fn.endswith("json")]

    sample_out_list = []
    for idx, fn in enumerate(fn_list):
        full_path = os.path.join(out_dir, fn)
        ann_dict = json.load(open(full_path))
       
        if args.debug and idx > 10:
            break
        
        count_keys = [key for key in ann_dict["question_dict"].keys() if "counterfact" in key or "goal" in key or "multiple" in key]    
        fact_keys = [key for key in ann_dict["question_dict"].keys() if key not in count_keys]
        count_list, fact_list = [], []
        count_type_list, fact_type_list = [], []
        for qtype, qa_list in ann_dict["question_dict"].items(): 
            for idx, ele in enumerate(qa_list):
                ele["qtype"] = qtype
                ele["video_id"] = ann_dict["video_id"]
                qa_list[idx] = ele
            if len(qa_list)==0:
                continue
            if qtype in count_keys:
                count_list +=qa_list
                count_type_list += random.sample(qa_list, 1)
            else:
                fact_list +=qa_list
                fact_type_list += random.sample(qa_list, 1)
        if len(count_type_list) >=args.count_ques_num:
            count_smp_list = random.sample(count_type_list, args.count_ques_num)
        else:
            smp_num = min(len(count_list), args.count_ques_num - len(count_type_list))
            count_smp_list = count_type_list + random.sample(count_list, smp_num)
        if len(fact_type_list) >=args.fact_ques_num:
            fact_smp_list = random.sample(fact_type_list, args.fact_ques_num)
        else:
            smp_num = min(len(fact_list), args.fact_ques_num - len(fact_type_list))
            fact_smp_list = fact_type_list + random.sample(fact_list, smp_num)
        sample_out_list +=fact_smp_list
        sample_out_list +=count_smp_list
    
    # add question_id
    for idx, ele in enumerate(sample_out_list):
        ele["question_id"] = '{:0>5d}'.format(idx)
        if ele["answer"] == "No answer.":
            ele["positive"] = []

    base_dir = os.path.dirname(args.merge_ques_path)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)
    with open(args.merge_ques_path, 'w') as f:
        json.dump(sample_out_list, f)

def split_dataset(args):
    full_ann_list = json.load(open(args.merge_ques_path))
    base_dir = os.path.dirname(args.merge_ques_path)
    split_list = ["train", "val", "test"]
    split_ratio = {"train": 0.5, "val": 0.2, "test": 0.3}
    
    vid_list = list(set([ele["video_id"] for ele in full_ann_list]))
    vid_2_ques_list = {vid: [] for vid in vid_list}
    for ele in full_ann_list:
        vid_2_ques_list[ele["video_id"]].append(ele)
    # sort vid_list
    vid_list = [int(id) for id in vid_list]
    vid_list.sort()
    vid_list = [str(id) for id in vid_list]

    st_ratio, ed_ratio = 0.0, 0.0
    for split, ratio in split_ratio.items():
        ques_list = []
        ed_ratio = st_ratio + ratio
        st_id, ed_id = int(len(vid_list)*st_ratio), int(len(vid_list)*ed_ratio) 
        print("start: %d, end: %d, split: %s"%(st_id, ed_id, split))
        for vid in vid_list[st_id:ed_id]:
            tmp_list = vid_2_ques_list[vid]
            for idx, ele in enumerate(tmp_list):
                ele["split"] = split
            ques_list +=tmp_list
        output_file_path = os.path.join(base_dir, args.video_type + "_"+split+"_"+args.out_id+".json")
        with open(output_file_path, 'w') as f:
            json.dump(ques_list, f)
        st_ratio = ed_ratio 
        if args.analysis:
            simple_analysis(ques_list, split)

def sample_list_based_onanswer(qa_list):
    ans_list = list(set([ele["answer"] for ele in qa_list ]))
    ans2qlist = {ele: [] for ele in ans_list }
    for ele in qa_list:
        ans2qlist[ele["answer"]].append(ele)
    smp_list = []
    for ans, sub_list in ans2qlist.items():
        smp_list +=random.sample(sub_list, 1)
    return smp_list

def sample_list_based_on_answertext(qa_list):
    opt_list = []
    for ele in qa_list:
        opt_list += ele["positive"]
    opt_list = list(set(opt_list))
    ans2qlist = {ele: [] for ele in opt_list }
    for ele in qa_list:
        for pos_text in ele["positive"]:
            ans2qlist[pos_text].append(ele)
    smp_list = []
    for ans, sub_list in ans2qlist.items():
        smp_list +=random.sample(sub_list, 1)
    return smp_list

def run_question_sampler_v2(args):
    out_dir = os.path.join(args.output_ques_ann_path, args.video_type)
    fn_list = [fn for fn in os.listdir(out_dir) if fn.endswith("json")]

    sample_out_list = []
    for idx, fn in enumerate(fn_list):
        full_path = os.path.join(out_dir, fn)
        ann_dict = json.load(open(full_path))
       
        if args.debug and idx > 10:
            break
        
        count_keys = [key for key in ann_dict["question_dict"].keys() if "counterfact" in key or "goal" in key or "pred" in key]    
        fact_keys = [key for key in ann_dict["question_dict"].keys() if key not in count_keys]
        count_list, fact_list = [], []
        count_type_list, fact_type_list = [], []
        for qtype, qa_list in ann_dict["question_dict"].items(): 
            for idx, ele in enumerate(qa_list):
                ele["qtype"] = qtype
                ele["video_id"] = ann_dict["video_id"]
                qa_list[idx] = ele
            if len(qa_list)==0:
                continue
            
            if qtype in count_keys:
                count_list +=qa_list
                #Use answer to sample
                #sub_qa_list = sample_list_based_onanswer(qa_list)
                sub_qa_list = sample_list_based_on_answertext(qa_list)
                count_type_list += random.sample(sub_qa_list, 1)
            else:
                fact_list +=qa_list
                #Use answer to sample
                #sub_qa_list = sample_list_based_onanswer(qa_list)
                sub_qa_list = sample_list_based_on_answertext(qa_list)
                fact_type_list += random.sample(sub_qa_list, 1)
        if len(count_type_list) >= args.count_ques_num:
            count_smp_list = random.sample(count_type_list, args.count_ques_num)
        else:
            smp_num = min(len(count_list), args.count_ques_num - len(count_type_list))
            count_smp_list = count_type_list + random.sample(count_list, smp_num)

        if len(fact_type_list) >= args.fact_ques_num:
            fact_smp_list = random.sample(fact_type_list, args.fact_ques_num)
        else:
            smp_num = min(len(fact_list), args.fact_ques_num - len(fact_type_list))
            fact_smp_list = fact_type_list + random.sample(fact_list, smp_num)
        sample_out_list +=fact_smp_list
        sample_out_list +=count_smp_list

    # add question_id
    for idx, ele in enumerate(sample_out_list):
        ele["question_id"] = '{:0>5d}'.format(idx)
        if ele["answer"] == "No answer.":
            ele["positive"] = []

    base_dir = os.path.dirname(args.merge_ques_path)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)
    with open(args.merge_ques_path, 'w') as f:
        json.dump(sample_out_list, f)


def pulley_analysis(choices, answers):
    colors: set(["red", "cyan", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white", "gray", "turquoise", "magenta", "lime", "teal", "lavender"])
    shapes = set(["cube", "rope", "sphere", "fixed point", "solid pulley", "triple-rod pulley"]) 
    template = {
        'mass0': r"The mass of the (.+?) is ((?!not).+?) the mass of the (.+?)\.",
        'mass1': r"The mass of the (.+?) is not (.+?)the mass of the (.+?)\.",
        'mass2': r"It is impossible to determine the relationship between the masses of the (.+?) and the (.+?) based on the information given\.",
        'mass3': r"It is possible to determine the relationship between the masses of the (.+?) and the (.+?) based on the information given\.",
        "tension0": r"The average tension of the (.+?) is ((?!not).+?) the average tension of the (.+?)\.",
        "tension1": r"The average tension of the (.+?) is not (.+?)the average tension of the (.+?)\.",
        "tension2": r"It is impossible to determine the relationship between the average tension of the (.+?) and the (.+?) based on the information given\.",
        "tension3": r"It is possible to determine the relationship between the average tension of the (.+?) and the (.+?) based on the information given\.",
        "shape_number": r"The number of (.+?)s in the video is (.+?)\.",
        "color_number": r"The number of (.+?) objects in the video is (.+?)\.",
        "color_shape0": r"There exists a (.+?) in the video\.",
        "color_shape1": r"There does not exist a (.+?) in the video\.",
        "counterfactual_pull": r"If we pull the (.+?), (.+?)", 
        "counterfactual_mass": r"If we (.+?) the mass of the (.+?), (.+?)", 
        "goal_pull": r"Pull the (.+?)\.",
        "goal_mass": r"(Increase|Decrease) the mass of (.+?)\.",
    }
    df_dict0 = {}

    all_matches = []
    for choice in choices:
        match_key_list = []
        for k, v in template.items():
            if re.match(v, choice):
                if k == 'shape_number' and 'object' in re.match(v, choice)[1]:
                    continue # it not belongs to shape number
                match_key_list.append(k)
    
        if len(match_key_list) == 0 or len(match_key_list) > 1:
            print(choice)
            print(match_key_list)
            breakpoint()

        match_key = match_key_list[0]
        all_matches.append(match_key)

    for match_key, ans in zip(all_matches, answers):
        if match_key not in df_dict0:
            df_dict0[match_key] = [0, 0, 0] #  answer_right, answer_wrong, all
        if ans:
            df_dict0[match_key][0] += 1
        else:
            df_dict0[match_key][1] += 1
        df_dict0[match_key][2] += 1

    table = PrettyTable()
    table.field_names = ["template", "Ans True", "Ans False", "All"]
    factual_rows = []
    count_rows = []
    goal_rows = []
    
    for k, v in df_dict0.items():
        if 'goal' in k:
            goal_rows.append([k, v[0], v[1], v[2]])
        elif 'counter' in k:
            count_rows.append([k, v[0], v[1], v[2]])
        else:
            factual_rows.append([k, v[0], v[1], v[2]])

    factual_rows.sort(key=lambda x: x[0])
    count_rows.sort(key=lambda x: x[0])
    goal_rows.sort(key=lambda x: x[0])

    factual_row = ["factual", sum([x[1] for x in factual_rows]), sum([x[2] for x in factual_rows]), sum([x[3] for x in factual_rows])]
    count_row = ["counterfactual", sum([x[1] for x in count_rows]), sum([x[2] for x in count_rows]), sum([x[3] for x in count_rows])]
    goal_row = ["goal_driven", sum([x[1] for x in goal_rows]), sum([x[2] for x in goal_rows]), sum([x[3] for x in goal_rows])]

    for i, row in enumerate(factual_rows):
        table.add_row(row, divider=(i == len(factual_rows) - 1))
    table.add_row(factual_row)
    
    for i, row in enumerate(count_rows):
        table.add_row(row, divider=(i == len(count_rows) - 1))
    table.add_row(count_row)
    
    for i, row in enumerate(goal_rows):
        table.add_row(row, divider=(i == len(goal_rows) - 1))
    table.add_row(goal_row)

    print(table)

    return    

def simple_analysis(data, dataset_name):
    ana_dict = {}
    for ele in data:
        if ele['question_family'] not in ana_dict:
            ana_dict[ele['question_family']] = 1
        else:
            ana_dict[ele['question_family']] += 1

    table = PrettyTable()
    table.field_names = ["template", dataset_name]
    for k, v in ana_dict.items():
        table.add_row([k, v])

    print(table)

def run_question_sampler_v3(args):
    out_dir = os.path.join(args.output_ques_ann_path, args.video_type)
    fn_list = [fn for fn in os.listdir(out_dir) if fn.endswith("json")]

    sample_out_list = []
    for idx, fn in enumerate(fn_list):
        full_path = os.path.join(out_dir, fn)
        ann_dict = json.load(open(full_path))
       
        if args.debug and idx > 10:
            break
        
        count_keys = [key for key in ann_dict["question_dict"].keys() if "counterfact" in key or "goal" in key or "predict" in key] # counterfactual, goal_drivem
        fact_keys = [key for key in ann_dict["question_dict"].keys() if key not in count_keys] # factual, predictive
        count_list, fact_list = [], []
        count_type_list, fact_type_list = [], []

        for qtype, qa_list in ann_dict["question_dict"].items(): 
            for idx, ele in enumerate(qa_list):
                ele["qtype"] = qtype
                ele["video_id"] = ann_dict["video_id"]
                qa_list[idx] = ele
            if len(qa_list)==0:
                continue
            
            if qtype in count_keys:
                count_list +=qa_list
                #Use answer to sample
                #sub_qa_list = sample_list_based_onanswer(qa_list)
                # sub_qa_list = sample_list_based_on_answertext(qa_list)
                count_type_list.append(random.choice(qa_list))
            else:
                fact_list +=qa_list
                #Use answer to sample
                #sub_qa_list = sample_list_based_onanswer(qa_list)
                # sub_qa_list = sample_list_based_on_answertext(qa_list)
                fact_type_list.append(random.choice(qa_list))
        if len(count_type_list) >= args.count_ques_num: # TODO: change into each key choice 1 as we only has four keys
            count_smp_list = random.sample(count_type_list, args.count_ques_num)
        else:
            smp_num = min(len(count_list), args.count_ques_num - len(count_type_list))
            count_smp_list = count_type_list + random.sample(count_list, smp_num)

        if len(fact_type_list) >= args.fact_ques_num:
            fact_smp_list = random.sample(fact_type_list, args.fact_ques_num)
        else:
            smp_num = min(len(fact_list), args.fact_ques_num - len(fact_type_list))
            fact_smp_list = fact_type_list + random.sample(fact_list, smp_num)

        sample_out_list +=fact_smp_list
        sample_out_list +=count_smp_list

    # add question_id
    for idx, ele in enumerate(sample_out_list):
        ele["question_id"] = '{:0>5d}'.format(idx)
        if ele["answer"] == "No answer.":
            ele["positive"] = []

    base_dir = os.path.dirname(args.merge_ques_path)
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)
    with open(args.merge_ques_path, 'w') as f:
        json.dump(sample_out_list, f)

    # TODO: implement cloth/fluid/fire
    if args.analysis:
        simple_analysis(sample_out_list, 'All Num')

if __name__=="__main__":
    args = build_args_parser()
    print(args)
    # run_question_sampler_v2(args)
    run_question_sampler_v3(args)
    split_dataset(args)