# Blender SDF Node Addon
This addon provides **SDF Node System** for **SDF Rendering** and physics simulation with **SDF Collision**. 

SDF refers to signed distance field. You may find lots of impressive content to do with SDF on this website https://www.iquilezles.org/www/articles/distfunctions/distfunctions.htm.

Since this addon is still work-in-progress and has no official releases, you can only go for it by manual installation. For now you have to install another blender addon [taichi-blend](https://github.com/taichi-dev/taichi_blend) firstly. Then just copy the `sdf_node_addon` folder to your blender's `scripts/addons` folder directly.


## Features
- SDF Rendering
  - Node system which allows real-time viewport update
  - Support combination of SDF primitives, including *Union*, *Subtraction*, *Intersection*, *Blend shape*
  - Support a lot of SDF operations, including *Transform*, *Twist*, *Round*, *Solidify*, *Elongate*, *Mirror*, etc.
  - FBM noise displacement
  - Basic PBR rendering
- CPU/GPU Physics Simulation
  - PBD Cloth simulation which allows real-time interaction and caching
  - Analytical SDF collider generated by node system
  - 3 gradient algorithms are implemented for SDF collider: automatic, numerical, analytical
  - Support backends on different platforms, including CPU, CUDA, OpenGL, Metal
  - Powered by [taichi-blend](https://github.com/taichi-dev/taichi_blend), a project aiming at integrating [Taichi](https://github.com/taichi-dev/taichi) into blender for physics simulation and animation

## To-Do List
* Preview and Rendering
  - [ ] More shaders, such as volume shader, Matcap shader
  - [ ] Image-based lighting and more complete light system
  - [ ] Material assignment for each part of a contructive SDF
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
