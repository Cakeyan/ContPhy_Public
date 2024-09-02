import argparse
import pdb
import json
import os
import operator
import random

def get_frequence_answer(train_list):
    ques_type_list = list(set([ele["qtype"] for ele in train_list]))
    out_dict = {ele : {} for ele in ques_type_list}
    for ele in train_list:
        ans, qtype = ele["answer"], ele["qtype"]
        tmp_dict = out_dict[qtype]
        if ans not in tmp_dict:
            tmp_dict[ans] = 1.0
        else:
            tmp_dict[ans] +=1
        out_dict[qtype] = tmp_dict
    out_dict_most_freq = {}
    frequent_answer_dict, random_answer_dict = {}, {}
    for qtype, tmp_dict in out_dict.items():
        sorted_list = sorted(tmp_dict.items(), key=operator.itemgetter(1))
        frequent_answer_dict[qtype] = sorted_list[-1][0]
        random_answer_dict[qtype] = list(tmp_dict.keys())
    return frequent_answer_dict, random_answer_dict
    
def eval_split(val_list, frequent_answer_dict, random_answer_dict):
    ques_type_list = list(set([ele["qtype"] for ele in val_list]))
    output_fre_acc_dict = {ele: 0.0 for ele in ques_type_list}
    output_rdn_acc_dict = {ele: 0.0 for ele in ques_type_list}
    output_total_dict = {ele: 0.0 for ele in ques_type_list}
    for idx, ele in enumerate(val_list):
        q_type, ans = ele["qtype"], ele["answer"]
        output_total_dict[q_type] +=1
        rdn_answer = random.choice(random_answer_dict[q_type])
        fre_answer = frequent_answer_dict[q_type]
        if rdn_answer == ans:
            output_rdn_acc_dict[q_type] +=1  
        if fre_answer == ans:
            output_fre_acc_dict[q_type] +=1  
    print("Evaluating split %s\n"%(ele["split"]))
    key_list = ["factual", "counterfactual", "goal_driven"]
    output_total_dict2 = {ele: 0.0 for ele in key_list}
    output_rdn_acc_dict2 = {ele: 0.0 for ele in key_list}
    output_fre_acc_dict2 = {ele: 0.0 for ele in key_list}
    print("************************")
    for key, rnd_acc in output_rdn_acc_dict.items():
        fre_acc = output_fre_acc_dict[key]
        total_num = output_total_dict[key]
        print("%s: %f\n"%(key, rnd_acc/total_num))
        print("%s: %f\n"%(key, fre_acc/total_num))
        if "counterfactual" in key:
            output_total_dict2["counterfactual"] +=total_num
            output_rdn_acc_dict2["counterfactual"] += rnd_acc 
            output_fre_acc_dict2["counterfactual"] += fre_acc 
        elif "goal" in key:
            output_total_dict2["goal_driven"] +=total_num
            output_rdn_acc_dict2["goal_driven"] += rnd_acc 
            output_fre_acc_dict2["goal_driven"] += fre_acc 
        else:
            output_total_dict2["factual"] +=total_num
            output_rdn_acc_dict2["factual"] += rnd_acc 
            output_fre_acc_dict2["factual"] += fre_acc 
    print("************************")
    for key, rnd_acc in output_rdn_acc_dict2.items():
        fre_acc = output_fre_acc_dict2[key]
        total_num = output_total_dict2[key]
        print("random, num: %d, %s: %f\n"%(total_num, key, rnd_acc/total_num))
        print("frequent, num: %d, %s: %f\n"%(total_num, key, fre_acc/total_num))

def eval_split_v2(val_list, frequent_answer_dict, random_answer_dict, args=None):
    ques_type_list = list(set([ele["qtype"] for ele in val_list]))
    output_fre_acc_dict = {ele: 0.0 for ele in ques_type_list}
    output_rdn_acc_dict = {ele: 0.0 for ele in ques_type_list}
    output_total_dict = {ele: 0.0 for ele in ques_type_list}
    
    output_fre_acc_dict_opt = {ele: 0.0 for ele in ques_type_list}
    output_rdn_acc_dict_opt = {ele: 0.0 for ele in ques_type_list}
    output_total_dict_opt = {ele: 0.0 for ele in ques_type_list}
    
    for idx, ele in enumerate(val_list):
        q_type, ans = ele["qtype"], ele["answer"]
        output_total_dict[q_type] +=1
        rdn_answer = random.choice(random_answer_dict[q_type])
        fre_answer = frequent_answer_dict[q_type]
        if rdn_answer == ans:
            output_rdn_acc_dict[q_type] +=1  
        if fre_answer == ans:
            output_fre_acc_dict[q_type] +=1  
    print("Evaluating split %s\n"%(ele["split"]))
    key_list = ["factual", "counterfactual", "goal_driven"]
    output_total_dict2 = {ele: 0.0 for ele in key_list}
    output_rdn_acc_dict2 = {ele: 0.0 for ele in key_list}
    output_fre_acc_dict2 = {ele: 0.0 for ele in key_list}
    print("************************")
    for key, rnd_acc in output_rdn_acc_dict.items():
        fre_acc = output_fre_acc_dict[key]
        total_num = output_total_dict[key]
        if args is not None and args.print_type1: 
            print("%s: %f\n"%(key, rnd_acc/total_num))
            print("%s: %f\n"%(key, fre_acc/total_num))
        
        if "counterfactual" in key:
            output_total_dict2["counterfactual"] +=total_num
            output_rdn_acc_dict2["counterfactual"] += rnd_acc 
            output_fre_acc_dict2["counterfactual"] += fre_acc 
        elif "goal" in key:
            output_total_dict2["goal_driven"] +=total_num
            output_rdn_acc_dict2["goal_driven"] += rnd_acc 
            output_fre_acc_dict2["goal_driven"] += fre_acc 
        else:
            output_total_dict2["factual"] +=total_num
            output_rdn_acc_dict2["factual"] += rnd_acc 
            output_fre_acc_dict2["factual"] += fre_acc 
    print("************************")
    for key, rnd_acc in output_rdn_acc_dict2.items():
        fre_acc = output_fre_acc_dict2[key]
        total_num = output_total_dict2[key]
        if args is not None and args.print_type2: 
            print("random, num: %d, %s: %f\n"%(total_num, key, rnd_acc/total_num))
            print("frequent, num: %d, %s: %f\n"%(total_num, key, fre_acc/total_num))
    
    key_list = ["factual", "counterfactual", "goal_driven"]
    ans_type_list = list(set([ele["answer_type"][0] for ele in val_list]))
    output_total_dict3 = {ele: {ans_type: 0.0 for ans_type in ans_type_list} for ele in key_list}
    output_rdn_acc_dict3 = {ele: {ans_type: 0.0 for ans_type in ans_type_list} for ele in key_list}
    output_fre_acc_dict3 = {ele: {ans_type: 0.0 for ans_type in ans_type_list} for ele in key_list}
    for idx, ele in enumerate(val_list):
        q_type, ans, ans_type = ele["qtype"], ele["answer"], ele["answer_type"][0]
        output_total_dict[q_type] +=1
        rdn_answer = random.choice(random_answer_dict[q_type])
        fre_answer = frequent_answer_dict[q_type]
        if rdn_answer == ans:
            if "counterfactual" in q_type:
                output_rdn_acc_dict3["counterfactual"][ans_type] +=1 
            elif "goal" in q_type:
                output_rdn_acc_dict3["goal_driven"][ans_type] +=1 
            else:
                output_rdn_acc_dict3["factual"][ans_type] +=1 
                 
        if fre_answer == ans:
            if "counterfactual" in q_type:
                output_fre_acc_dict3["counterfactual"][ans_type] +=1 
            elif "goal" in q_type:
                output_fre_acc_dict3["goal_driven"][ans_type] +=1 
            else:
                output_fre_acc_dict3["factual"][ans_type] +=1 
        
        if "counterfactual" in q_type:
            output_total_dict3["counterfactual"][ans_type] +=1 
        elif "goal" in q_type:
            output_total_dict3["goal_driven"][ans_type] +=1 
        else:
            output_total_dict3["factual"][ans_type] +=1 
   
    print("************************")
    for key, rnd_acc_dict in output_rdn_acc_dict3.items():
        fre_acc_dict = output_fre_acc_dict3[key]
        total_num_dict = output_total_dict3[key]
        for key2, rnd_acc in rnd_acc_dict.items():
            freq_acc = fre_acc_dict[key2]
            total_num = total_num_dict[key2]
            if args is not None and args.print_type3 and total_num>0: 
                print("random, num: %d, %s, %s: %f\n"%(total_num, key, key2, rnd_acc/total_num))
                print("frequent, num: %d, %s %s: %f\n"%(total_num, key, key2,  fre_acc/total_num))
    import pdb; pdb.set_trace()

def frequent_performer(args):
    base_dir = args.base_dir
    train_split_path = os.path.join(base_dir, args.video_type + "_train_"+args.out_id+".json")
    val_split_path = os.path.join(base_dir, args.video_type + "_val_"+args.out_id+".json")
    test_split_path = os.path.join(base_dir, args.video_type + "_test_"+args.out_id+".json")
    train_list = json.load(open(train_split_path))
    val_list = json.load(open(val_split_path))
    test_list = json.load(open(test_split_path))
    frequent_answer_dict, random_answer_dict = get_frequence_answer(train_list)
   

    eval_split_v2(val_list, frequent_answer_dict, random_answer_dict, args)
    eval_split_v2(test_list, frequent_answer_dict, random_answer_dict, args)

def build_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument( "--video_type", type=str, default="pulley", help="")
    parser.add_argument("--fact_ques_num", type=int, default=3, help="")
    parser.add_argument("--output_ques_ann_path", type=str, default="output", help="")
    parser.add_argument("--count_ques_num", type=int, default=2, help="")
    parser.add_argument("--base_dir", type=str, default="output/merge", help="")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument("--out_id", type=str, default="v1", help="")
    parser.add_argument("--type", type=str, default="random", help="")
    parser.add_argument('--print_type1', action='store_true')
    parser.add_argument('--print_type2', action='store_true')
    parser.add_argument('--print_type3', action='store_true')
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = build_args_parser()
    print(args)
    frequent_performer(args)