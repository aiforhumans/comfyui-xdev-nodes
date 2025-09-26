# Datatypes (Cheat‑Sheet)

Common built‑ins you’ll encounter:
- `IMAGE`: torch.Tensor `[B,H,W,C]`, `C=3`
- `MASK`:  torch.Tensor `[B,H,W]`
- `LATENT`: dict with key `samples` shaped `[B,C,H,W]`
- `STRING`, other basic widgets
- `*` (aka ANY): matches anything
- **Custom datatypes**: use your own all‑caps name for intra‑pack types

Tips:
- Be strict about shapes (see examples).
- Use `ANY` only when it makes sense for UX.
