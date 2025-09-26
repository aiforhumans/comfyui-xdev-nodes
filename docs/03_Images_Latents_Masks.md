# Images, Latents, and Masks

- **IMAGE** is channel‑last: `[B,H,W,C]` with `C=3`.
- **LATENT** uses a dict; samples are channel‑first: `[B,C,H,W]` with `C=4`.
- **MASK** is `[B,H,W]` (single channel).

Always validate shapes and data types in your node code and return tuples.
