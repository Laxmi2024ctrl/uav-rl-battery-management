# Literature Table (review draft)

Gap legend: **Stated** = source/authors ne khud likha hai. **FPVR** = Full paper verification required.

| # | Paper | Problem | Method | Key Result (evidence type) | Research Gap | Connection to Our Project |
|---|---|---|---|---|---|---|
| 1 | Gao et al., Energy 2023 | Fuel-cell hybrid UAV ka energy management, component durability aur safe exploration | Safe RL, CMDP, improved TD3 + safety optimizer; wind aur random payload | **Simulation:** flight cost 14.6% aur fuel-cell degradation 15.3% kam (online benchmark ke muqable). Training aur real-time control scenarios mein zero constraint violations | FPVR | Wind/payload environment, degradation-aware reward, TD3 |
| 2 | Liu et al., IEEE TMC 2020 | Multi-UAV mobile base stations se long-term coverage, kam energy | Decentralized DRL (actor-critic) | **Simulation:** DRL-EC3 aur 3 baselines se behtar; abstract mein number nahi | FPVR | Energy-aware RL aur state/action/reward design |
| 3 | Li, Zhan, Wang, J. Field Robotics 2024 | Rotary-wing delivery drone ka energy model | Integrated force/power model (climb, descent, hover, horizontal) | **Computational experiments:** ek flight segment mein horizontal phase ne average 87.63% battery capacity li; zyada mass par endurance kam; tested range mein zyada airspeed par endurance zyada | FPVR | uav_power() ka payload/speed background |
| 4 | Tavakol-Moghaddam et al., Results in Eng. 2024 | Li-ion pack mein cell imbalance | Deep RL passive balancing, 2-RC ECM; TRPO, PPO, DQN, ARS, A3C | **Simulation:** TRPO se capacity up to 16.8% zyada, SoC variance 69.4% kam, switching 40.4% kam | FPVR | Battery RL, multi-algorithm comparison, ECM |
| 5 | Agostini et al., ESARS-ITEC 2024 | VTOL UAV LiPo cells ka thermal behaviour aur discontinuous load | Simplified identification aur thermal modelling | **Experiment** (HPPC aur discharge-test section titles se; abstract mein explicit nahi). Numeric result abstract mein nahi | Stated: "preliminary study". Specific limitations: FPVR | Thermal model, high C-rate |
| 6 | Zhang et al., Drones 2026 | UAV cruise trajectory tracking | ED-SAC; PPO, TD3, SAC se compare (PyBullet) | **Simulation:** tracking error 0.27 m (SAC se 40% behtar); success 98.7% bina disturbance, 96.2% random disturbance mein | Stated: sirf simulation, sim-to-real baaki; terrain, sensor uncertainty, actuator delay, livestock movement model nahi | PPO/TD3/SAC comparison, evaluation protocol |
| 7 | Yan, Chen, Yang, IEEE WCL 2021 | Rotary-wing UAV ka simple aur accurate energy model | Closed-form model: initial velocity, acceleration, duration | **Numerical analysis:** model valid aur reliable bataya gaya; abstract mein number nahi | FPVR | uav_power() ke liye candidate model |
| 8 | Suti et al., Energies 2022 | Fixed-wing UAV Li-Po pack model, temperature aur transient load | Thevenin + Bouc-Wen hysteretic model | **Experiment:** voltage max relative error <1% (SoC >10%). **Simulation:** mission mein efficiency 0.93 (take-off) se 0.75 (cold cruise) | Stated future work: high-fidelity UAV simulator mein integration | Thevenin/RC aur temperature model |
| 9 | Di Nisio et al., Sensors 2023 | UAV LiPo discharged capacity/SoC estimation | Empirical discharge model, 3 tunable parameters | **Experiment:** variable-power discharge prediction, normalized capacity error <0.7% | Stated: temperature aur aging include nahi | Discharge/SoC validation. Peukert source ke roop mein cite nahi karna |
| 10 | Ma et al., Drones 2024 | Wind disturbance mein UAV tracking aur stability | Fractal wind model, dual-loop PID + DDPG compensator | **Simulation (composite wind):** trained vs *untrained* PID-DRL: mean RMSE 0.8 se 0.28 m (65%). Trained vs PID: RMSE peak approx. 30% kam, max error approx. 36% kam. **Real flight:** wind mein hover/tracking; abstract ke mutabiq level 5 tak behtar stability | Full paper verification required | Sirf wind modelling aur wind-robust RL. Energy/battery management ka evidence nahi |

## Verification status

| # | Status |
|---|---|
| 1 | Verified: publisher page + Crossref record (Xingyu Zhang) |
| 2 | Verified via bibliographic records (dblp, peeref) |
| 3 | Publisher page aur dblp verified |
| 4 | Title/article publisher page; authors aur DOI citing records se |
| 5 | University repository verified |
| 6 | Publisher page verified |
| 7 | Repository verified; IEEE page par title, authors, vol. 10, issue 9 confirmed; pages aur DOI IEEE par check pending |
| 8 | Publisher page verified |
| 9 | PMC (publisher version) verified |
| 10 | Publisher page verified |
