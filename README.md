# ContPhy_Public

This repo contains the code related to the ICML 2024 paper [ContPhy: Continuum Physical Concept Learning and Reasoning from Videos](https://physical-reasoning-project.github.io/), including dataset construction of question generation, ContPRO and Baselines. 

**For more information about code in this repo, please directly email cakeyanxin@gmail.com.**

If you need codebase for ContPhy dataset generation, please see [Code-VideoGen](https://github.com/zzcnewly/ContPhy-Gen/tree/main). 

> ### ContPhy: Continuum Physical Concept Learning and Reasoning from Videos   
> Zhicheng Zheng\*, Xin Yan\*, Zhenfang Chen\*, Jingzhou Wang, Qin Zhi Eddie Lim, Joshua B. Tenenbaum, and Chuang Gan (\* denotes equal contributions)  
>
> *ICML 2024*  
> Links | [Project Page](https://physical-reasoning-project.github.io/) | [Paper (Arxiv)](https://arxiv.org/abs/2402.06119) | [Dataset Download](https://huggingface.co/datasets/zzcnewly/ContPhy_Dataset) | [Cite ContPhy ](#citation) | [Code (Video-Gen)](https://github.com/zzcnewly/ContPhy-Gen/tree/main)

## Question Generation

See folder 'questions'. We have released the question generation for 'rope'(aka 'pulley') scenario and included a raw metadata for debugging.

### To run pulley question generation

```bash
bash scripts/run_pulley_question.sh
```

### To sample

```bash
bash scripts/run_sampler_pulley.sh
```

### To visualize results

```bash
streamlit run visualization/visualize_pulley.py
```

## ContPRO, the Oracle Model

Comming soon......

**Some tips for reproduction**: ContPRO is an oracle model, building upon the oracle 3D information (which is beyond our public dataset release), and the ViperGPT framework. This is specifically designed for ContPhy. If you want to adapt to your work, you can directly refer to [ViperGPT](https://viper.cs.columbia.edu/), and find specific modules that will work on your data.

## Baselines

Comming soon......

Please refer to the official baseline repo. For specific baseline details, feel free to drop an email for more information.

## Note

Due to personal reasons, I will try to release the full details of our project, but the process may be slow. Some implementations may differ from our experiments' final version, and the code may not be so clean. **However, we are really open to help you reproduce all the results. If you have any questions, please see Contact info below.**

## Contact & Citation

For more information about code in this repo, please directly email cakeyanxin@gmail.com.

For questions related to the paper, please feel free to contact any authors in any ways.

Welcome to cite `ContPhy` if you find the paper, dataset, and implementations useful in your research.

```
@inproceedings{zheng2024contphy,
  author = {Zhicheng Zheng and Xin Yan and Zhenfang Chen and Jingzhou Wang and Qin Zhi Eddie Lim and Joshua B. Tenenbaum and Chuang Gan},
  title = {ContPhy: Continuum Physical Concept Learning and Reasoning from Videos},
  booktitle = {ICML 2024},
  year = {2024},
}
```

