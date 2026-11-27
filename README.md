RL-Based Adaptive Battery Management for UAVs

Reinforcement learning for adaptive speed and battery management of rotary-wing Unmanned Aerial Vehicles (UAVs), comparing DQN, PPO, SAC and TD3 against rule-based baselines.

Table of Contents
Overview
Key Features
Repository Structure
Installation
Usage
Experimental Protocol
Results
Demo
Reproducibility
Team
Contributing
References
1. Overview

UAV flight time is limited by battery energy, and battery behaviour depends on discharge rate, temperature, wind and payload. This project builds a simulated UAV environment with a physics-based rotary-wing power model and a detailed battery model, then trains RL agents to choose flight speed so that the mission is completed with efficient energy use and healthy battery operation.

We compare four RL algorithms (DQN, PPO, SAC, TD3) against three baselines, and study robustness through ablation and generalization experiments.

2. Key Features
UAV power model: rotary-wing power with wind and payload effects; U-shaped power curve with minimum-power and maximum-range speeds
Battery model: state of charge (SoC), Peukert effect, 1-RC Thevenin circuit, thermal model and degradation, each switchable with flags
Environment (env-v1): Gymnasium environment with discrete and continuous action modes and reproducible reset(seed)
Algorithms: DQN (discrete), PPO, SAC and TD3 (continuous), using Stable-Baselines3
Baselines: 3 rule-based policies (including FixedSpeed and MaxRange)
Common evaluator: one evaluate.py used by every method
Ablation study: no wind, no temperature model, no energy reward term, no Peukert effect
Streamlit demo: interactive comparison of RL agent vs best baseline
3. Repository Structure
uav-rl-battery-management/
├── env/            # UAV environment, battery model (battery.py), reward (reward.py)
├── eval/           # evaluate.py, baselines.py, plots.py
├── tests/          # test_env.py and other tests
├── app/            # Streamlit demo (app.py)
├── docs/           # mdp_table.md, battery_notes.md, literature_table.md
├── figures/        # Plots (300 dpi PNG)
├── tables/         # LaTeX tables
├── sections/       # LaTeX report sections
├── results/        # CSV results (dqn_results.csv, ppo_results.csv, ...)
├── models/         # Trained models (<algo>_seedX.zip)
├── logs/           # SB3 Monitor logs (logs/<algo>/seed_X/)
├── refs.bib        # Bibliography
├── requirements.txt
└── README.md
4. Installation

Requirements: Python 3.10 or higher, git.

bash
# 1. Clone the repository
git clone https://github.com/Laxmi2024ctrl/uav-rl-battery-management.git
cd uav-rl-battery-management

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

Google Colab:

python
!git clone https://github.com/Laxmi2024ctrl/uav-rl-battery-management.git
%cd uav-rl-battery-management
!pip install -r requirements.txt
5. Usage
Task	Command
Run environment tests	python tests/test_env.py
Evaluate baselines	python eval/baselines.py
Evaluate a trained model	python eval/evaluate.py
Train DQN	python train_dqn.py
Train PPO	python train_ppo.py
Train SAC	python train_sac.py
Train TD3	python train_td3.py
Generate plots	python eval/plots.py
Launch demo	streamlit run app/app.py
6. Experimental Protocol
Item	Setting
Training seeds	0, 1, 2
Evaluation	100 episodes, seeds 1000-1099
Evaluator	evaluate.py only (same for all methods)
Discount factor	gamma = 0.99
DQN	discrete env, 300K steps
PPO	500K steps
SAC / TD3	continuous env
Logging	SB3 Monitor wrapper, logs/<algo>/seed_X/
Model files	models/<algo>_seedX.zip
Environment version	env-v1 (frozen after Day 4)

Generalization tests: wind +/- 8 m/s, payload 1-1.5 kg.

7. Results

Final results (mean +/- std over 3 seeds for every method), ablation and generalization tables are stored in results/, the plots in figures/, and the LaTeX tables in tables/. The full discussion is in the project report.

File	Content
results/baseline_results.csv	Rule-based baselines
results/dqn_results.csv	DQN
results/ppo_results.csv	PPO
results/sac_results.csv, results/td3_results.csv	SAC, TD3
results/tuning.csv	Learning rate and gamma tuning
results/ablation.csv	Ablation study
8. Demo
bash
streamlit run app/app.py

The demo provides sidebar controls (agent, wind, payload, seed), the UAV trajectory, live SoC / temperature / speed plots, and RL vs best-baseline side by side.

Screenshots are in figures/.

9. Reproducibility
All training uses seeds 0, 1, 2; evaluation uses seeds 1000-1099
Dependency versions are pinned in requirements.txt
Environment version is tagged env-v1; the final code is tagged final
A bug in env-v1 leads to an announced env-v2, never a silent change
To reproduce the report numbers: fresh clone, install, then run the evaluation commands in Usage
10. Team
Member	Role
Laxmi	Repository & Documentation
Nikita	Report Lead & Plots
Deva	MDP, Baselines, SAC/TD3
Ujwal	Environment, DQN & Demo
Yash Raj	Battery Model, PPO & Results
11. Contributing
Create one branch per task: git checkout -b task/<task-name>
Commit with clear messages
Open a Pull Request with 1 reviewer
Do not push directly to main
Do not modify env-v1 after the freeze

Daily update format: Done: ... | Doing next: ... | Blocked by: ...

12. References

See refs.bib. Main algorithm references: DQN (Mnih et al., 2015), PPO (Schulman et al., 2017), SAC (Haarnoja et al., 2018), TD3 (Fujimoto et al., 2018), Stable-Baselines3 (Raffin et al., 2021).
