#!/bin/bash

julia --threads=1 --project=. julia_files/run_sim.jl "julia_nthreads_1" 
julia --threads=2 --project=. julia_files/run_sim.jl "julia_nthreads_2" 
julia --threads=5 --project=. julia_files/run_sim.jl "julia_nthreads_5" 
julia --threads=8 --project=. julia_files/run_sim.jl "julia_nthreads_8" 