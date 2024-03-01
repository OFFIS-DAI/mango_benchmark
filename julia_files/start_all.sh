#!/bin/bash

julia --project julia_files/run_sim.jl "julia_"
julia --threads 2 --project julia_files/run_sim.jl "julia_2_threads_"
julia --threads 5 --project julia_files/run_sim.jl "julia_5_threads_"
julia --threads auto --project julia_files/run_sim.jl "julia_auto_threads_"