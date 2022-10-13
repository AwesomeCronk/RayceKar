# RayceKar
RayceKar is a graphics and game engine developed to make full use of pure ray marching graphics. It uses OpenGL 4.4+ and GLFW.  

## Quirks
Let's get this over with first off, because they're probably gonna be deal-breakers for a lot of people. That said, I made/am making this engine because I don't like how most of the game dev world handles certain things. The biggest ones I can think of are listed below:

### Z is up
In typical 3d game development, X and Z are coplanar to the ground and Y represents the vertical axis (think gravity). As I understand, this is because of how computer graphics developed, where X and Y were axes on the (vertical) screen. Z seems to represent the depth of the screen, since it was the third axis to be represented and X and Y were taken. In anything real life, X and Y are coplanar to the ground and Z represents the vertical axis. Millimg machines, 3d printers, and pretty much any other 3 axis machine works this way.

### <0, 0> is lower-left
When computers that had operating systems were first in the works, they worked on a command-line, text-only interface, where the first lines of text (how english works) were at the top of the screen. Programmers got used to working like that and, as graphical interfaces developed, they continued to work top-down, with pixel `<0, 0>` being upper-left, just like character `<0, 0>` used to be.
Well in math and pretty much eveerywhere else in real life, we refer to going up as "increasing altitude", so it fits that going up on the screen ought to be increasing Y! Also OpenGL puts `<0, 0>` at the lower-left of everything `vec2`-based, so it was easier to just switch GLFW around.
