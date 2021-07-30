Highlights:
   - **Documentation**
      - Add .md documentation (#2494) (by **Taichi Gardener**)
      - Remove all .rst docs (#2492) (by **Taichi Gardener**)
   - **Examples**
      - Refactor example library (#2475) (by **Andrew Sun**)
   - **Performance improvements**
      - Use warp reduction to improve reduction performance (#2487) (by **Dunfan Lu**)
   - **Refactor**
      - Cleanup CUDA AtomicOpStmt codegen (#2490) (by **Dunfan Lu**)

Full changelog:
   - [refactor] remove global_program in kernel.cpp (#2508) (by **ljcc0930**)
   - [misc] Added palette in taichi GUI for circles (#2504) (by **Jiasheng Zhang**)
   - [lang] Support ti.fields with shape after materialized (#2503) (by **ljcc0930**)
   - [doc] Add a basic doc explaining how to run Taichi CPP tests (#2502) (by **Ye Kuang**)
   - [lang] Support ti.FieldsBuilder() (#2501) (by **ljcc0930**)
   - [misc] Add needs_grad property for SNode (#2500) (by **ljcc0930**)
   - [lang] Support fake FieldsBuilder() with same memory location (#2493) (by **ljcc0930**)
   - [ci] Fix appveyor (#2496) (by **Ye Kuang**)
   - [ir] Add some comments to implementation of CFG optimizations and analyses (#2474) (by **xumingkuan**)
   - [Doc] Add .md documentation (#2494) (by **Taichi Gardener**)
   - [Example] Refactor example library (#2475) (by **Andrew Sun**)
   - [Doc] Remove all .rst docs (#2492) (by **Taichi Gardener**)
   - [Refactor] [cuda] Cleanup CUDA AtomicOpStmt codegen (#2490) (by **Dunfan Lu**)
   - [Perf] [cuda] Use warp reduction to improve reduction performance (#2487) (by **Dunfan Lu**)
   - [vulkan] Add kernel metadata and utils (#2481) (by **Ye Kuang**)
   - [opengl] [refactor] Use macro to generate atomic float functions (#2486) (by **xndcn**)
