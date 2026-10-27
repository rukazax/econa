# Software verification with the package's example kite, not ECONA sizing.
using KiteModels, LinearAlgebra, Printf
cd(@__DIR__)
KiteModels.copy_model_settings()
set = deepcopy(load_settings("system.yaml"))
set.abs_tol=0.00006
set.rel_tol=0.000001
set.solver="DFBDF"
set.v_wind=14.5
set.v_reel_out=1.0
set.upwind_dir=-170.0
kps=KPS4(KCU(set))
integrator=KiteModels.init!(kps;delta=0.001,stiffness_factor=0.1,prn=false)
open("verification.csv","w") do io
    println(io,"time_s,lift_N,drag_N,tether_force_N,height_m")
    for i in 1:80
        next_step!(kps,integrator;set_speed=1.0,upwind_dir=deg2rad(-170.0),dt=0.05)
        lift,drag=lift_drag(kps)
        force=winch_force(kps)
        height=pos_kite(kps)[3]
        @assert all(isfinite.([lift,drag,force,height]))
        @assert lift>0 && drag>0 && force>0 && height>0
        @printf(io,"%.6f,%.9f,%.9f,%.9f,%.9f\n",integrator.t,lift,drag,force,height)
    end
end
lift,drag=lift_drag(kps)
@assert isapprox(integrator.t,4.0;atol=1e-9)
open("verification.txt","w") do io
    println(io,"PASS: KPS4, 80 steps, 4 s, Julia ",VERSION)
    println(io,"Lift [N]: ",lift,"; drag [N]: ",drag,"; tether force [N]: ",winch_force(kps))
    println(io,"Package example, fixed ground base, wind 14.5 m/s. NOT vessel sizing or moving-base validation.")
end
println(read("verification.txt",String))
