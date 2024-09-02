vid_type=pulley
python3 tools/utils.py \
	--video_type $vid_type \
	--output_ques_ann_path output \
	--merge_ques_path output/merge_${vid_type}/merge.json \
    --count_ques_num 1 \
    --fact_ques_num 1 \
    --analysis pulley
