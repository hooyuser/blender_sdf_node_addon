# Blender SDF Node Addon

![Code size](https://img.shields.io/github/languages/code-size/hooyuser/blender_sdf_node_addon)
![Repo size](https://img.shields.io/github/repo-size/hooyuser/blender_sdf_node_addon)
![Lines of code](https://tokei.rs/b1/github/hooyuser/blender_sdf_node_addon)

This addon provides **SDF Node System** for **SDF Rendering** and physics simulation with **SDF Collision**. 

SDF refers to signed distance field. You may find lots of impressive content to do with SDF on this website https://www.iquilezles.org/www/articles/distfunctions/distfunctions.htm.


This addon is still work-in-progress. Though the SDF rendering node system is relatively stable, physics simulation may crash your Blender. Since the release version of this addon is targeted on Blender 4.1, I'm not sure whether it can function correctly on Blender 3.x.

## Download
- Addons for Blender 4.1
  - Download the [master branch](https://github.com/hooyuser/blender_sdf_node_addon/archive/refs/heads/master.zip) and then copy the `sdf_node_addon` folder to your Blender's `/scripts/addons/` folder directly.
  - Download the [pre-release](https://github.com/hooyuser/blender_sdf_node_addon/releases/download/0.0.3/sdf_node_beta_0_0_3.zip) and install it like any other addons for Blender.
- Addons for Blender 2.92
  - Download the [blender2.92 branch](https://github.com/hooyuser/blender_sdf_node_addon/archive/refs/heads/blender2.92.zip). This branch will not get updated anymore.

## Features
- SDF Rendering
  - Node system which allows real-time viewport update
  - Support combination of SDF primitives, including *Union*, *Subtraction*, *Intersection*, *Blend shape*
  - Support a lot of SDF operations, including *Transform*, *Twist*, *Round*, *Solidify*, *Elongate*, *Mirror*, etc.
  - FBM noise displacement
  - Basic PBR rendering
- CPU/GPU Physics Simulation (redesign needed)
  - PBD Cloth simulation which allows real-time interaction and caching
  - Analytical SDF collider generated by node system
  - 3 gradient algorithms are implemented for SDF collider: automatic, numerical, analytical
  - Support backends on different platforms, including CPU, CUDA, OpenGL, Metal
  - Powered by [taichi-blend](https://github.com/taichi-dev/taichi_blend), a project aiming at integrating [Taichi](https://github.com/taichi-dev/taichi) into blender for physics simulation and animation

## To-Do List
* Preview and Rendering
  - [ ] More shaders, such as volume shader, Matcap shader
  - [ ] Image-based lighting and more complete light system
  - [x] Material assignment for each part of a contructive SDF
  - [x] Image Output
* Physics Simulation
  - [ ] SDF collision with simple primitives and analytical gradient
  - [ ] VDB SDF collision
  - [ ] Improve the stability and performance of the Cloth PBD solver
  - [ ] More PBD solvers
* Node System
  - [x] Animation system
  - [x] Support more input types, such as *Object Info Input*
  - [x] Support math operations
  - [ ] Support creating node groups
* Other Functions
  - [ ] Convert mesh to VDB SDF
  - [ ] Generate mesh from analytical SDF
  - [ ] Generate mesh from VDB SDF
