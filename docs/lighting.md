# Lighting

RayceKar provides a basic builtin lighting system.

## Point light

A point light radiates light from a single point in all directions.

### Attributes:

- `pos: vec3` - The light's position in the world
- `rot: quat` - The light's rotation, has no effect
- `radius: float` - The radius of the light's effect
- `intensity: float` - The intensity of the light
- `falloff: float` - The factor by which the light's intensity fades with distance
- `color: <>` - The color of the light presented as `<TO BE DETERMINED>`
