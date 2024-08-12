#!/bin/bash

julia --threads=1 --project=. julia_files/run_sim.jl "julia_nthreads_1_" 
julia --threads=2 --project=. julia_files/run_sim.jl "julia_nthreads_2_" 
julia --threads=5 --project=. julia_files/run_sim.jl "julia_nthreads_5_" 
julia --threads=8 --project=. julia_files/run_sim.jl "julia_nthreads_8_" 